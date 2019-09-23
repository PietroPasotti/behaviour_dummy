import pytest
import attr
from ai.behaviour import TransitionModel, Behaviour, mark
from ai.command import ControllableObject
from ship import Ship

class _1(Behaviour):
    def _validate(self):
        assert False
    # invalid because its own validation fails

class _2(Behaviour):
    _agentclass = 'Test'
    @mark.transition(post='b')
    def a(self):
        pass

    @mark.transition(post='a')
    def b(self):
        pass
    # invalid because it has no root

class _3(Behaviour):
    _agentclass = 'Test'
    # invalid because it has no actions defined


invalidbs = [_1,_2,_3]


@attr.s
class SampleBehaviour(Behaviour):
    _agentclass = 'Test'
    _p = attr.ib()
    p = property(lambda self: self._p)
    q = property(lambda self: not self._p)

    @mark.transition(post='b', pre='p') # if p holds, next behaviour is b; else is c
    @mark.transition(post='c', pre='q')
    def a(self):
        pass

    @mark.action
    def b(self):
        pass

    @mark.action
    def c(self):
        pass


class Test(ControllableObject):
    # should autoload SampleBehaviour(self) in self.behaviours upon init
    pass


def test_behaviour_agentclass_collection():
    t = Test()
    assert isinstance(t.behaviours[0], SampleBehaviour), 'should collect SampleBehaviour in self.behaviours'


@pytest.fixture
def ship():
    s = Ship()


def test_give_behaviour_validation(ship):
    for ib in invalidbs:
        with pytest.raises(Behaviour.ValidationError):
            ship.add_behaviour(ib) # these all fail

    beh = ship.add_behaviour(SampleBehaviour) # goes ok
    assert beh in ship.behaviours
