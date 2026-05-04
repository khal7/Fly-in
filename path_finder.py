from system import *





class PathFinder():
    def __init__(self, system: System):
        self.system = system


    def get_neighbors(self, current_zone: Zone) -> list[Zone]:
        neighbors = []
        for item in self.system.connections:
            if item.start_zone == current_zone:
                neighbors.append(item.end_zone)
            elif item.end_zone == current_zone:
                neighbors.append(item.start_zone)
        return neighbors

    def find_path(self):
        shortest_path = []