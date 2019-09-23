import random
import attr
from . import ShipBehaviour, Behaviour, mark


@attr.s
class Aggressive(ShipBehaviour):
    """Endless search and target loop.
    Spawns alternate Search and ApproachAndAttack behaviours, forever."""
    found = attr.ib(init=False, default=None)

    @mark.transition(post='kill', root=True) # need to mark the root, because this graph is cyclic
    def search(self):
        candidates = self.agent.scan()
        if candidates:
            self.found = sorted(candidates, key=lambda x: self.agent.distance(x))[0]
            self.skip(self.kill) # jump to kill routine

    @mark.transition(post='search')
    def kill(self):
        # choose a more specific sub-behaviour to implement
        aggressive_sub = ApproachAndAttack(self.agent, self.found)
        # delegate execution
        self.delegate(aggressive_sub)


@attr.s
class ApproachAndAttack(Behaviour):
    # needs to be a concrete behaviour and not a shipbehaviour: it requires arguments other than agent.
    # lock on a target; approach and attack until death comes.
    target = attr.ib(init=True)

    def get_possible_targets(self):
        return self.agent.engaged_targets

    def enemyoutofrange(self):
        return self.enemyinrange() == 0

    def enemyinrange(self):
        ranges = [h.range for h in self.agent.hardpoints]
        dist = self.agent.pos - self.target.pos # fix
        inrange = [r for r in ranges if r < dist]
        return len(inrange) / len(ranges) == 0

    @mark.transition(pre='enemyoutofrange', post='approach')
    @mark.transition(pre='enemyinrange', post='attack')
    def choosetarget(self):
        self.target = self.agent

    @mark.transition(pre='enemyoutofrange', post='approach')
    @mark.transition(pre='enemyinrange', post='attack')
    @mark.transition(pre='enemydestroyed', post=None)
    def approach(self):
        self.agent.move(self.target.pos)

    @mark.transition(pre='enemydestroyed', post=None)
    def attack(self):
        self.agent.attack(self.target)
