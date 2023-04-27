import glob
import os
import sys

try:
    sys.path.append(glob.glob('../**/*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random


def try_spawn_random_vehicle_at(world, transform, recursion=0):
    blueprints = world.get_blueprint_library().filter('vehicle.*')
    blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
    blueprints = [x for x in blueprints if not x.id.endswith('isetta')]
    blueprint = random.choice(blueprints)

    if blueprint.has_attribute('color'):
        color = random.choice(blueprint.get_attribute('color').recommended_values)
        blueprint.set_attribute('color', color)
    blueprint.set_attribute('role_name', 'autopilot')
    vehicle = world.try_spawn_actor(blueprint, transform)

    if vehicle is not None:
        print('spawned %r at %s' % (vehicle.type_id, transform.location))
    else:
        if recursion > 20:
            print('WARNING: vehicle not spawned, NONE returned')
        else:
            return try_spawn_random_vehicle_at(world, transform, recursion + 1)

    return vehicle
