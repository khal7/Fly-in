from __future__ import annotations
from typing import Optional



class ParserError(Exception):
    pass


class System:
    def __init__(self, start_zone: Optional[Zone] = None,
                 end_zone: Optional[Zone] = None) -> None:
        self.zones: list[Zone] = []
        self.drones: list[Drone] = []
        self.connections: list[Connection] = []
        self.start_zone: Optional[Zone] = start_zone
        self.end_zone: Optional[Zone] = end_zone


class Connection:
    def __init__(self,
                 start_zone: Zone,
                 end_zone: Zone,
                 max_capacity: int = 1,
                 currently_in: Optional[list[Drone]] = None
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
                 turns_remaining: int = 0,
                 next_zone: Optional[Zone] = None
                 ) -> None:
        self.current_zone = current_zone
        self.id = id
        self.path = path if path else []
        self.status = status
        self.turns_remaining = turns_remaining
        self.next_zone = next_zone



class Zone:
    def __init__(self, name: str,
                 x: int,
                 y: int,
                 capacity: int = 1,
                 zone_type: str = "normal",
                 current_drones: Optional[list[Drone]] = None,
                 color: Optional[str] = None
                 ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.capacity = capacity
        self.current_drones = current_drones if current_drones else []
        self.zone_type = zone_type
        self.color = color


class Parser:
    def __init__(self, file: str) -> None:
        self.file = file

    def parse(self) -> System:
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
                        zone.capacity = 99999

                        system.start_zone = zone
                        system.zones.append(zone)
                    elif line.startswith("end_hub"):
                        if system.end_zone is not None:
                            raise ParserError("duplicate end_hub")
                        zone = self.get_zone(line)
                        zone.capacity = 99999
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
                    id=f"D{i+1}", current_zone=system.start_zone)
                system.drones.append(drone)

            return system

    def drone_nb(self, line: str) -> int:
        try:
            splitted_line = line.split()
            res = int(splitted_line[1])
            if res < 1:
                raise ParserError("nb_drones must be a positive integer")
            return res
        except ValueError:
            raise ParserError("nb_drones must be a positive integer")

    def get_zone(self, line: str) -> Zone:
        allowed_type = ["normal", "blocked", "restricted", "priority"]
        allowed_config_zone = ["zone", "color", "max_drones"]
        try:
            my_dict = {}
            ln = line.split()
            if "[" in line:
                start = line.find("[") + 1
                end = line.find("]")
                config = line[start:end]
                for element in config.split():
                    res = element.split("=")
                    my_dict[res[0]] = res[1]
            for key in my_dict:
                if key not in allowed_config_zone:
                    raise ParserError(f"invalid metadata key: {key}")
            if my_dict.get("zone", "normal") not in allowed_type:
                raise ParserError("invalid zone type")

            if int(my_dict.get("max_drones", 1)) < 1:
                raise ParserError("max_drones should be positive integer")
            zone = Zone(name=ln[1], x=int(ln[2]), y=int(ln[3]),
                        capacity=int(my_dict.get("max_drones", 1)),
                        zone_type=my_dict.get("zone", "normal"),
                        color=my_dict.get("color", None))
            return zone
        except ParserError:
            raise
        except (ValueError, IndexError):
            raise ParserError("invalid zone format")

    def get_connection(self, line: str, system: System) -> Connection:

        allowed_config = ["max_link_capacity"]
        try:
            ln = line.split()
            zone_list = ln[1].split("-")
            max_capacity = 1
            if "[" in line:
                start = line.find("[") + 1
                end = line.find("]")
                config = line[start:end]
                key, value = config.split("=")
                if key not in allowed_config:
                    raise ParserError(f"invalid metadata key: {key}")
                max_capacity = int(value)
                if max_capacity < 1:
                    raise ParserError(
                        "max_link_capacity must be positive integer")

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


class Simulation:
    def __init__(self,  system: System, pathfinder: PathFinder):
        self.system = system
        self.pathfinder = pathfinder
    # 
    def check_connection(self, zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        for connection in self.system.connections:
            if (connection.start_zone == zone_a and connection.end_zone == zone_b) or \
                (connection.start_zone == zone_b and connection.end_zone == zone_a):
               return connection
        return None

    def run(self) -> None:
        turn = 1
        # adding all drones to the start zone
        for drone in self.system.drones:
            self.system.start_zone.current_drones.append(drone)
        while not all(drone.current_zone == self.system.end_zone for drone in self.system.drones):
            transit_output = {}
            moves = {}
            moved = set()
            reserved = {}
            for connection in self.system.connections:
                connection.currently_in = [d for d in connection.currently_in if d.turns_remaining > 0]
            for drone in self.system.drones:
                paths = []
                reserv_count = 0
                if drone.current_zone == self.system.end_zone:
                    continue
                try:
                    if drone.turns_remaining > 0:
                        drone.turns_remaining -= 1
                        if drone.turns_remaining == 0:
                            #drone.current_zone.current_drones.remove(drone)
                            drone.next_zone.current_drones.append(drone)
                            drone.current_zone = drone.next_zone
                            moved.add(drone)
                        continue
                   
                    paths = self.pathfinder.find_path(drone.current_zone, self.system.end_zone, reserved, self.system.start_zone)
                    # for path in paths:
                    #      print(f"{path.name}", end=" ")
                    # print("\n")
                    # print("=" * 20)
                    
                    if len(paths) < 2:
                        moves[drone] = None
                    else:
                        next_zone = paths[1]
                        moves[drone] = next_zone
                        reserved[next_zone] = reserved.get(next_zone, 0) + 1
                except ParserError:
                    moves[drone] = None
            # for zone, n in reserved.items():
            #     print(f"---------------- {zone.name}, {n}")
            # for drone, zone in moves.items():
            #     print(f"{drone.id} → {zone.name if zone else None} at {drone.current_zone.name}")
            # for drone, z in moves.items():
            #     print(f"ID: {drone.id if drone else None} next_zone: {z.name if z else None}")
            
            for d in self.system.drones:
                if d not in moves:
                    continue
                if d.current_zone == self.system.end_zone:
                    continue
                next_zone = moves[d]
                if next_zone is None:
                    continue
                connection = self.check_connection(d.current_zone, next_zone)
                if connection is None:
                    continue
                if len(connection.currently_in) >= connection.max_capacity:
                    continue
                
                if len(next_zone.current_drones) >= next_zone.capacity:
                    continue
                #print(f"D2 wants loop_a: connection={len(connection.currently_in)}/{connection.max_capacity} zone={len(next_zone.current_drones)}/{next_zone.capacity}")
                if next_zone.zone_type == "restricted":
                    transit_output[d] = f"{d.id}-{d.current_zone.name}-{next_zone.name}"
                    d.next_zone = next_zone
                    d.turns_remaining = 1
                    d.current_zone.current_drones.remove(d)
                    connection.currently_in.append(d)
                    moved.add(d)
                else:
                    connection.currently_in.append(d)
                    d.current_zone.current_drones.remove(d)
                    connection.currently_in.remove(d)
                    next_zone.current_drones.append(d)
                    d.current_zone = next_zone
                    moved.add(d)
            
                
            
                    
            output = []
            # for drone in self.system.drones:
            #      print(f"{drone.id} at {drone.current_zone.name} turns_remaining={drone.turns_remaining}")
            for d in moved:
                if d in transit_output:
                    output.append(transit_output[d])
                else:
                    output.append(f"{d.id}-{d.current_zone.name}")
            print(" ".join(output))
            # exit()
            # print(" ".join(f"{d.id}-{d.current_zone.name}" for d in moved))
                
            # if turn > 30:
            #     exit()
            turn += 1

    

            