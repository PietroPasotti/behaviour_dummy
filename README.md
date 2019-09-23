# behaviour_dummy

Little behaviour snippet drawn from my (for now private) PyShip project.

Intended usage: 
- define AI-controlled classes such as ship.Ship and inherit from ai.command.ControllableObject
- create Behaviours for that class (ai.behaviours.Behaviour subclasses)
- in your AI-controlled class call regularly ControllableObject.update() and magically watch it do what it should.

Note: this is extracted hard out of context from the PyShip project: large portions of it contain references to methods 
and code that are not there (aka NameError).
