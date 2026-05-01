from __future__ import annotations
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
        system = System()
        nb = 0
        line_nb = 0
        with open(self.file, 'r') as file:
            for line in file:
                line_nb += 1
                line = line.strip()
                try:
                    if line.startswith("#"):
                        pass
                    elif not line:
                        pass
                    elif line.startswith("start_hub"):
                        if system.start_zone is not None:
                            raise ParserError("duplicate start_hub")
                        zone = self.get_zone(line)

                        system.start_zone = zone
                        system.zones.append(zone)
                    elif line.startswith("end_hub"):
                        if system.end_zone is not None:
                            raise ParserError("duplicate end_hub")
                        zone = self.get_zone(line)
                        system.end_zone = zone
                        system.zones.append(zone)
                    elif line.startswith("hub"):
                        z = self.get_zone(line)
                        for zn in system.zones:
                            if z.name == zn.name:
                                raise ParserError("duplicate zone name")
                        system.zones.append(z)
                    elif line.startswith("nb_drones"):
                        nb = self.drone_nb(line)
                    elif line.startswith("connection"):
                        connect = self.get_connection(line, system)
                        for c in system.connections:
                            if (c.start_zone == connect.start_zone and
                                c.end_zone == connect.end_zone) or \
                                (c.start_zone == connect.end_zone and
                                 c.end_zone == connect.start_zone):
                                raise ParserError("duplicate connection")
                        system.connections.append(connect)
                    else:
                        raise ParserError(f"unknown keyword on line: {line}")
                except ParserError as e:
                    raise ParserError(f"Error in line: {line_nb}: {e}")
            if system.start_zone is None:
                raise ParserError("missing start_hub")
            if system.end_zone is None:
                raise ParserError("missing end_hub")
            if nb == 0:
                raise ParserError("missing nb_drones")
            for i in range(nb):
                drone = Drone(
                    id=f"D-{i}", current_zone=system.start_zone)
                system.drones.append(drone)

            return system

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
        allowed_type = ["normal", "blocked", "restricted", "priority"]
        allowed_config_zone = [...]
        allowed_config_connection = [...]
        try:
            my_dict = {}
            start = line.find("[") + 1
            end = line.find("]")
            config = line[start:end]
            l = line.split()
            for element in config.split():
                res = element.split("=")
                my_dict[res[0]] = res[1]
            if my_dict.get("zone", "normal") not in allowed_type:
                raise ParserError("invalid zone type")
            
            if int(my_dict.get("max_drones", 1)) < 1:
                raise ParserError("max_drones can't be negative")
            zone = Zone(name=l[1], x=int(l[2]), y=int(l[3]),
                        capacity=int(my_dict.get("max_drones", 1)),
                        zone_type=my_dict.get("zone", "normal"),
                        color=my_dict.get("color", None))
            return zone
        except ParserError:
            raise
        except (ValueError, IndexError):
            raise ParserError("invalid zone format")

    def get_connection(self, line: str, system: System) -> Connection:
        try:
            l = line.split()
            zone_list = l[1].split("-")
            max_capacity = 1
            if "[" in line:
                start = line.find("[") + 1
                end = line.find("]")
                config = line[start:end]
                _, value = config.split("=")
                max_capacity = int(value)
                if max_capacity < 1:
                    raise ParserError("max_link_capacity must be positive integer")

            start_z = None
            end_z = None
            for zone in system.zones:
                if zone.name == zone_list[0]:
                    start_z = zone
                elif zone.name == zone_list[1]:
                    end_z = zone
            if start_z is None or end_z is None:
                raise ParserError("zone not found in connection")
            connection = Connection(start_zone=start_z,
                                    end_zone=end_z,
                                    max_capacity=int(max_capacity))
            return connection
        except ParserError:
            raise
        except (ValueError, IndexError):
            raise ParserError("invalid connection format")


class PathFinder():
    def __init__(self, system: System):
        self.system = system


class Simulation:
    def __init__(self,  system: System):
        self.system = system
