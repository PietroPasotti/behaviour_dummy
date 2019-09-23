import attr
from collections import deque, defaultdict, namedtuple
import settings
from logger import getLogger
from .behaviours import get_behaviours


logger = getLogger(__name__)


command_dir = namedtuple('commands', 'incoming outgoing')


class ControllableObject:
    """
    Class for objects that are controllable (i.e. have some background AI-driven Behaviours
    that can be overridden by human control).
    """

    def __init__(self):
        self.behaviours = []
        self.commands = command_dir(CommandQueue(self), CommandQueue(self))
        self.executing = None
        try:
            pri = settings.command_priority_order.index(self.__class__.__name__.lower())
        except:
            error(f'command priority order for {self.__class__} unset')
            pri = 0
        self._cmd_priority = pri
        self.gather_behaviours()

    def gather_behaviours(self):
        b_factories = get_behaviours(self.__class__)
        for b in b_factories:
            self.add_behaviour(b)
        return self.behaviours

    def add_behaviour(self, b_factory):
        """instantiates a behaviour class with self as argument, adds it to self.behaviours,
        returns the instance."""
        b = b_factory(self)
        b.validate() # check that some preconditions hold
        self.behaviours.append(b)
        return b

    def execute_next_command(self):
        try:
            cmd = self.commands.incoming.get_next_command()
        except self.commands.incoming.EmptyQueueError as e:
            print(f'no commands: {self} is idling.')
            return

        cmd.execute()
        self.executing = cmd
        # inform the sender that the order has been carried out.
        cmd.source._handle_command_execution(cmd)
        return cmd

    def _handle_command_execution(self, cmd):
        """order has been carried out: remove it from pending orders"""
        self.commands.outgoing.remove(cmd)

    def emit_command(self, action, completion_check, *args, priority=False, **kwargs):
        cmd = Command(self, action, completion_check, *args, **kwargs)
        self.commands.outgoing.queue(cmd, priority=priority)
        cmd.subject.receive_command(cmd, priority=priority)
        return cmd

    def receive_command(self, cmd, priority=False):
        self.commands.incoming.queue(cmd, priority=priority)

    def update(self):
        if self.executing and self.executing.is_done:
            self.executing = None # await completion
        if self.executing is None:
            return self.execute_next_command()
        else:
            debug('{self} is still executing {self.executing}')



class Command:
    def __repr__(self):
        return f"<Cmd {self.source}:: {self.subject} {self.action.__name__} ({self.args})>"

    def __init__(self, source, action, completion_check, *args, **kwargs):
        """
        source: origin of the command
        action: a bound method of the recipient of the command
        completion_check: a function to execute to verify if the command has completed
        args, kwargs: arguments to be passed to action() call
        """

        assert hasattr(action, "__call__"), f"action needs to be a function, got {action} instead"
        assert hasattr(action, "__self__"), f'action needs to be a bound method, got {action} instead'
        if completion_check is not None:
            assert hasattr(completion_check, "__call__"), f"""completion check
            needs to be a function (or None), got {completion_check} instead"""

        self.source = source
        self.action = action
        self.completion_check = completion_check
        self.args = args
        self.kwargs = kwargs

    @property
    def is_done(self):
        return self.completion_check() if self.completion_check else True

    @property
    def priority(self):
        return self.source._cmd_priority

    @property
    def subject(self):
        """The subject of the command"""
        return self.action.__self__

    def execute(self):
        self.action(*self.args, **self.kwargs)


@attr.s
class CommandQueue:
    owner = attr.ib(init=True)
    _commands = attr.ib(factory=deque, init=False)

    class EmptyQueueError(StopIteration):
        pass

    def __repr__(self):
        return f"<Command Queue {repr(self._commands)}>"

    def __len__(self):
        return len(self._commands)

    def __getitem__(self, item):
        try:
            return self._commands[item]
        except IndexError:
            raise self.EmptyQueueError(f'Empty queue ({item})')

    def queue(self, cmd, priority=False):
        if priority:
            self._commands.appendleft(cmd)
            return
        self._commands.append(cmd)
        return cmd

    def remove(self, cmd):
        self._commands.remove(cmd)

    def get_next_command(self, keep=False):
        """
        queue gets executed from left to right by default
        but cmd.priority has the precedence. So if a higher priority command is queued to
        the right of a lower-priority one, it is going to be executed first.
        """

        if not self._commands:
            raise self.EmptyQueueError('Empty queue')

        maxprio = min([c.priority for c in self._commands])

        # among the top-priority command, we get the last given
        top_priority = [c for c in self if c.priority == maxprio]
        cmd = top_priority[0]

        if not keep:
            self.remove(cmd)
        return cmd

    def clear(self):
        self._commands = deque()
