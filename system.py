
import sys



class System:
    def __init__(self, start_zone=None, end_zone=None):
        self.zones = []
        self.drones = []
        self.connections = []
        self.start_zone = start_zone
        self.end_zone = end_zone


class Connection:
    def __init__(self,
                 start_zone: Zone,
                 end_zone: Zone,
                 max_capacity: int = 1,
                 currently_in: list[Drone] = None
                 ):
        self.max_capacity = max_capacity
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.currently_in = currently_in if currently_in else []




class Drone:
    def __init__(self,
                 current_zone: Zone,
                 id: str,
                 path: list[Zone] = [],
                 status: str = "waiting",
                 turns_remaining: int = 0
                 ):
        self.current_zone = current_zone
        self.id = id
        self.path = path if path else []
        self.status = status
        self.turns_remaining = turns_remaining


class Zone:
    def __init__(self, name: str,
                 x: int,
                 y: int,
                 capacity: int = 1,
                 current_drones: list[Drone] = None,
                 zone_type: str = "normal",
                 color: str = None
                 ):
        self.name = name
        self.x = x
        self.y = y
        self.capacity = capacity
        self.current_drones = current_drones if current_drones else []
        self.zone_type = zone_type
        self.color = color

class Parser:
    def __init__(self, file: str):
        self.file = file


class PathFinder():
    def __init__(self, system: System):
        self.system = system

class Simulation:
    def __init__(self,  system: System):
        self.system = system



if __name__=="__main__":
    


    file = sys.argv[1]

    parse = Parser(file)
    