from costume_error import *


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
                 zone_type: str = "normal",
                 current_drones: list[Drone] = None,
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

    def parse(self):
        with open(self.file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    pass
                elif not line:
                    pass
                elif line.startswith("nb_drones"):
                    nb = self.drone_nb(line)
                    for i in range(nb):
                        drone = Drone(
                            id=f"D-{i}", current_zone=System.start_zone)
                        System.drones.append(drone)

                elif line.startswith("start_hub") or \
                        line.startswith("end_hub") or \
                        line.startswith("hub"):
                    zone = self.get_zone(line)
                    System.zones.append(zone)
                elif line.startswith("connection"):
                    connection = self.get_connection(line)
                else:
                    print("I will raise an error here")

    def drone_nb(self, line: str) -> int:
        try:
            l = line.split()
            res = int(l[1])
            if res < 1:
                raise ParserError("nb_drones must be a positive integer")
            return res
        except ValueError:
            raise ParserError("nb_drones must be a positive integer")

    def get_zone(self, line: str) -> Zone:
        my_dict = {}

        start = line.find("[") + 1
        end = line.find("]")
        config = line[start:end]
        l = line.split()
        for element in config.split():
            res = element.split("=")
            my_dict[res[0]] = res[1]

        zone = Zone(name=l[1], x=int(l[2]), y=int(l[3]),
                    capacity=int(my_dict.get("max_drones", 1)),
                    zone_type=my_dict.get("zone", "normal"),
                    color=my_dict.get("color", None))
        return zone

    def get_connection(self, line: str) -> Connection:
        ...


class PathFinder():
    def __init__(self, system: System):
        self.system = system


class Simulation:
    def __init__(self,  system: System):
        self.system = system
