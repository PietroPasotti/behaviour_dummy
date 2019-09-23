from os import path


# core game map generation parameters
map_gen_params = {
    "seed": 'pietro', # random seed for the procedural world
    "preload_window_padding": 0.5, # padding around view radius of fleets within which assets are preloaded
    "asteroid_field_density": 0.85 # threshold to crop perlin noise: at that

}

# noise and smoothing parameters for asteroid generation
asteroid_gen_params = {
    "frequency": 0.2, # how dense the plot map is
    "grow_rounds": 3, # iterations of growth phase algorithm
    "grow_factor": 2,
    "shrink_rounds": 1,
    "shrink_factor": 5,
    "shape_bound": (7,15) # max/min height and width
    }

# Forces rtrees to be re-evaluated instead of being pulled from memory.
rtree_force_regen = False

# triggers lazy loading of saved ship models instead of randomly generating new ones
ship_loading = True

# Value constraint of the default compositeobject constructor
default_ship_value = 1000

# default model for CompositeObject constructor
default_ship_model = 'fighter'

# defines priority rules for command execution. If the ship's AI determines that the best target to shoot at is A, but fleet thinks it's B, the ship will shoot B (if fleet precedes ship in this setting).
command_priority_order = ['player', 'aiplayer', 'colony', 'colonyfleet', 'fleet', 'ship']

# auto-equips picked-up scrap (always succeeds if component, food... but slots only succeed if there is an empty slot)
autoequip_pickup_ifempty = False

# auto-swaps picked-up scrap if better than existing slot (puts in storage the worse one)
autoequip_pickup_slot_ifbetter = False

# number of tiles 'out of view' that we render
render_distance = 4

tile_size = 50

# determines the default fight behaviour: on 'focus', all cannons focus on a single ship. On 'spread', cannons attack evenly every available target
default_fight_shotmap_policy = 'focus'

# determines the default fight behaviour: who to destroy first. Only applicable if shotmap policy is 'focus'.
# 'high defense/attack/speed' focuses on targets in range that have (so far as the fleet knows) high def/attack/speed.
# 'low hull' focuses on the target that has so far received the most damage
default_fight_priority_policy = 'high defense'

# rate at which a depleted asteroid's production decreases (actual_rate = base_mining_rate / (depleted_mining_rate * [number of times the asteroid was mined after being depleted]))
depleted_mining_rate = 0.02
# 'normal' rate at which an asteroid becomes depleted (runs out of resources) for mining an asteroid: when a ship mines it.
asteroid_mining_depletion_rate = 1
# reduced depletion rate for when asteroids are being deep-mined (by colonies)
asteroid_deep_mining_depletion_rate = 0.005

# default importance of component types (for ai behaviour in autorepair, aiming, power-up)
default_priority_seq = ['cockpits', 'engines', 'hardpoints', 'armors', 'thrusters', 'cargobays']

# number of scans after which tracked objects will stop being visible after trace is lost, to give ships a chance to regain it without them 'blinking' all time due to chance.
tracking_timeout = 2

# distance at which ships can pick up pods and objects
pickup_range = 2

# millisecs - how much does it take to perform certain actions
timers = {
    # ship : scan for objects in the void
    'scan': 100,
    # ship : mining speed. (is reduced on depleted asteroids)
    'mine': 1000,
    # workshop: baseline construction speed (depends also on value of item to build and quality of the workshop(s))
    'build': 50000,
    # frequency at which every ship's building status is recomputed
    'building_update_timer': 10000,

    # frequency at which every ship's fight status is recomputed (it still happens automatically if a target is destroyed)
    'fight_update_timer': 10000,

    # frequency at which a ship recomputes the mining behaviour
    'mining_update_timer': 1000,
    # for colonies
    'colony_mining_update_timer': 50000,

    # millisecs rate at which ships/fleet scan their surroundings
    'scan_rate': 5000,
    # rate at which a ship's population will need food -- or begin to starve
    'pop_timer': 10000000
    }


# if random() < this number, the slot is jettisoned upon component destruction, else disappears forever.
slot_survival_chance = 0.3

# HIDDEN determines whether the game window is full size or hidden
# (for testing backend functions without letting your boss know)
HIDDEN = True

# when MODE is false, we get size of game screen from:
WIDTH = 2048
HEIGHT = 1624

# game fps
FPS = 75
# game window title
TITLE = "Colony"

# data filenames
PLAYER_IMG = "playership.png"
SUN_IMG = "sun.png"
EARTH_IMG = "earth.png"
MOON_IMG = "moon.png"
BG_MUSIC = "space.flac"

loggerformat = '%(name)s:%(levelname)s:%(lineno)d: %(message)s'
_debuglevel = {
    'compositeobject':  0,
    'fleet':            0,
    'component':        0,
    'randomobject':     0,
    '__main__' :        1,
}

# value to which all randomly generated stats are to be rounded at
roundval = 2

game_folder = path.dirname(__file__)
models_folder = path.join(game_folder, 'data')
assets_folder = path.join(game_folder, 'assets')
planets_folder = path.join(assets_folder, 'planets')
