from ai.carla import carla


def transform(vehicle, location):
    vector = vehicle.get_transform().transform(carla.Location(x=location.x, y=location.y, z=location.z))

    return carla.Location(x=vector.x, y=vector.y, z=vector.z)
