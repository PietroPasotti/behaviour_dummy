"""
Provides the abstract agent behaviour classes, a mapping from ControllableObject classes (agents) to Behaviour subclasses (behaviours).
Each agent gets thus assigned the set of all behaviours that are to be made available to it.
"""


import random
import attr
from enum import Enum
from functools import wraps


Transition = attr.make_class('Transition', ['pre', 'weight', 'post'])


def get_behaviours(cls):
    groups = [b for b in Behaviour.__subclasses__() if b._agentclass == cls.__name__]
    return [a for b in groups for a in b.__subclasses__()]


class mark:
    """Collection of decorators to help the definition of behaviours."""

    @staticmethod
    def trace(f):
        """Marks behaviour methods that we want to trace -- for following the graph traversal (debug)"""
        @wraps(f)
        def wrapper(self,*args,**kwargs):
            self.trace.append(f)
            f(self,*args,**kwargs)
        return wrapper

    @staticmethod
    def action(f):
        """"Marks behaviour methods that represent transition model nodes"""
        @wraps(f)
        def wrapper(self,*args,**kwargs):
            self.__class__.actions.append(f)
            f(self,*args,**kwargs)
        return wrapper

    @staticmethod
    def transition(pre=None, weight=None, post=None, root=False):
        """"
        Marks behaviour methods that are part of the transition model graph.
        pre: method name to call to determine whether this transition should be selected.
        post: the next node in the behaviour graph.
        weight: attach a probability weight (any number) to the transition.
        pass root=True to signal that this node is the root: to override the
        default root-finder (necessary foor cyclic, rootless behaviours)
        """
        def partial(f):
            @wraps(f)
            @mark.action # transition entails action and trace by default
            @mark.trace
            def wrapper(self,*args,**kwargs):

                if root and not self.__root:
                    print(f'setting __root to {f}')
                    self.__root = f
                elif self.__root:
                    raise TypeError(f'cannot override: {self.__root.__name__} is {self}.root already')

                pre = getattr(self.__class__, pre)
                post = getattr(self.__class__, post)
                weight = weight if weight else 0.5
                self.__class__.tm.add(f, Transition(pre, weight, post))
                f(self,*args,**kwargs)
                # self.validate()
            return wrapper
        return partial

    @staticmethod
    def abort(f):
        """"
        registers global abort conditions checker methods within the behaviour
        """
        f = wraps(f)(mark.action(mark.trace(f))) # we stack action and trace decorators
        f.__self__.tm.abort_condition = f
        return f

    @staticmethod
    def update(f):
        """"
        registers an update method to the underlying transition model
        """
        assert f.__self__.tm.__update is None, f'__update already defined for {f.__self__}'
        f.__self__.tm.update = f
        return f


@attr.s
class TransitionModel:
    """a behaviour execution graph"""
    transitions = attr.ib(factory=dict, init=False)
    __root = attr.ib(default=None, init=False)
    __update = attr.ib(default=None, init=False)

    def _find_root(self):
        return [a for a in self.transitions if self.get_transitions_to(a) == []][0]

    @property
    def root(self):
        if not self.__root:
            self.__root = self._find_root()
        return self.__root

    def _find_leaves(self):
        return [a for a in self.transitions if self.get_transitions_from(a) == [None]]

    @property
    def leaves(self):
        return self._find_leaves()

    @property
    def actions(self):
        return list(self.transitions.keys()) + [self.leaves]

    def add(self, action, conditions, weight, post):
        if action not in self.transitions:
            self.transitions[action] = {}
        self.transitions[action].update({condition: post for condition in conditions})

    def get_transitions_to(self, action):
        for ori, ts in self.transitions.items():
            for condition, post in ts:
                if post == action:
                    yield (ori, condition)

    def get_transitions_from(self, action):
        for ts in self.transitions[action]:
            for condition, post in ts:
                yield (condition, post)

    def update(self):
        if hasattr(self.__update):
            return self.__update()

    def step(self, current_state=None):
        # if step is called without arguments we are at the root
        if current_state is None:
            print(f"{self}: started")
            current_state = self.root

        # terminate if we reach a leaf node
        if current_state in self.leaves:
            print(f"{self}: completed")

        self.update()

        candidates = self.get_transitions_from(current_state)

        choicemap = {post: weight for pre, weight, post in candidates}
        for pre, post in candidates:
            # we preuate candidates based on their own pre rule
            choicemap[post] = choicemap.get(post,0) + pre()

        # sort choicemap by cumulative preuation of transition conditions
        ranking = sorted(choicemap.items(), key=lambda x: choicemap[x[0]])

        top = [el for el in ranking if el[1] == ranking[-1][1]]
        if len(top) > 1:
            # if there is more than one best choice, we choose randomly
            return random.choice(top)
        else:
            # return best choice
            return top[0]

    def validate(self):
        assert len(self._root) == 1
        assert len(self._exit) == 1


@attr.s
class Behaviour:
    """
    A behaviour is a script for an agent to follow.
    Its intended usage is to control the agent by queuing commands to the agent's
    own internal command queue.
    When the agent can, it will execute those commands.
    When a Behaviour is evaluated it will determine, given the circumstances,
    what the best next action is.
    Behaviours have an enter and an exit states, which are the root and leaves of the graph.

    Behaviours can delegate to other behaviours, meaning they will step the other
    behaviour until its halt flag goes true. At that point they will resume stepping
    themselves. The halt flag has therefore no effect on self, but only on higher-level
    behaviours that self is delegated to.
    """

    class ValidationError(TypeError):
        """raised when behaviour validation fails"""
        pass

    _agentclass = None # the class for which this behaviour (subclass) is meant

    agent = attr.ib(init=True) # the actor behind this behaviour
    tm = attr.ib(factory=TransitionModel, init=False, repr=False)
    transitions = property(lambda self: self.tm.transitions)
    trace = attr.ib(factory=list, init=False, repr=False)
    state = attr.ib(default=None, init=False)

    # flag to terminate behaviour execution
    _halted = attr.ib(default=False, init=False)

    def step(self):
        """
        steps the underlying transition model.
        If a sub_behaviour is present, it takes control.
        """
        if self.sub and not self.sub._halted:
            return self.sub.step()

        self.state = self.tm.step(self.state)

    def skip(self, state):
        """allows to override transition rules"""
        self.state = state

    def delegate(self, sub_behaviour):
        self.sub = sub_behaviour

    def halt(self):
        """gives control back to super-behaviour if present -- or has no effect whatsoever"""
        self._halted = True

    def update(self):
        """subclass this method to write belief management or precondition checking
        (i.e. decide whether to halt()) or delegate()"""
        pass

    def validate(self):
        for cls in self.__class__.mro():
            if hasattr(cls, '_validate'):
                try:
                    cls._validate(self)
                except AssertionError as e:
                    raise Behaviour.ValidationError(f'{self} failed validation at {cls} level: {e}')
