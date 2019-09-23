import pytest
from pyship.core import init
from pyship.pcos import Ship, Fleet
from pyship.core import Player, SystemMap
from pyship.ai.command import Command, CommandQueue
from pyship.utils.graphics import point
from pyship import Player, Asteroid, components, init
import pytest


@pytest.fixture
def items():
    p = Player()
    s = Ship(model='fighter')
    f = Fleet(system=SystemMap()).add(s)
    p.give_fleet(f)
    return p,s,f

def test_create_command(items):
    p,s,f = items
    assert len(p.commands.outgoing) == 0
    assert len(s.commands.incoming) == 0

    assert s.goingto is None
    cmd = p.emit_command(s.goto, lambda:s.goingto == point(10,10), point(10,10))
    assert cmd.action == s.goto
    assert cmd.args[0] == point(10,10)
    assert cmd.is_done is False

    # command is not executed yet
    assert s.goingto is None

    # but is there
    assert len(p.commands.outgoing) == 1
    assert len(s.commands.incoming) == 1
    assert cmd in p.commands.outgoing
    assert cmd in s.commands.incoming

    assert p.commands.outgoing._commands == s.commands.incoming._commands

    s.update()
    # now command is run
    assert s.goingto == point(10,10)
    assert cmd.is_done

    # and the comm queues are empty
    assert len(p.commands.outgoing) == 0
    assert len(s.commands.incoming) == 0

def test_command_priority(items):
    p,s,f = items
    # ship commands herself
    cmda = s.emit_command(s.goto, None, point(10,10))
    assert s.commands.incoming.get_next_command(keep=True) is cmda

    # fleet commands ship
    cmdb = f.emit_command(s.goto, None, (12,12))
    assert s.commands.incoming.get_next_command(keep=True) is cmdb

    # player commands ship
    cmdc = p.emit_command(s.goto, None, (14,14))
    assert s.commands.incoming.get_next_command(keep=True) is cmdc

    assert cmda.priority > cmdb.priority > cmdc.priority

def test_command_order(items):
    p,s,f = items
    cmda = s.emit_command(s.goto, None, point(10,10))
    cmdb = s.emit_command(s.goto, None, point(10,10))
    assert s.commands.incoming.get_next_command(keep=True) is cmda # first received = first executed

    cmdc = s.emit_command(s.goto, None, point(10,10), priority=True)
    assert s.commands.incoming.get_next_command(keep=True) is cmdc # unless prioritised

def test_command_order_combined(items):
    p,s,f = items
    cmda = s.emit_command(s.goto, None, point(10,10))
    cmdb = s.emit_command(s.goto, None, point(10,10))
    # first come first serve
    assert s.commands.incoming.get_next_command(keep=True) is cmda

    # player orders ship -> gets priority
    cmdc = p.emit_command(s.goto, None, point(10,10))
    assert s.commands.incoming.get_next_command(keep=True) is cmdc

    # cmdd is given with priority -> overrules cmdc
    cmdd = p.emit_command(s.goto, None, point(10,10), priority=True)
    assert s.commands.incoming.get_next_command(keep=True) is cmdd

    # s gets order: bottom of the queue
    cmde = s.emit_command(s.goto, None, point(10,10))
    # p gives another order but without priority -> gets queued
    cmdf = p.emit_command(s.goto, None, point(10,10))
    # fleet gives order: will be queued after all p orders
    cmdf = f.emit_command(s.goto, None, point(10,10))

    assert s.commands.incoming.get_next_command(keep=True) is cmdd

def test_command_completion(items):
    p,s,f = items
    isgoing = lambda:s.goingto == point(10,10)
    cmd = s.emit_command(s.goto, isgoing, point(10,10))
    assert cmd.is_done is False
    assert cmd.completion_check is isgoing

    s.goto(point(10,10))
    assert cmd.is_done
