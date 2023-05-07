class Scenario:
    waypoints = []

    def __init__(self, world):
        self.world = world
        self.actors = []

        # Use nearby CARLA spawnpoint
        self.use_spawnpoint = True

    def setup(self):
        pass

    def destroy(self):
        for actor in self.actors:
            actor.is_alive and actor.destroy()
