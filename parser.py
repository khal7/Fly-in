from class_definition import System, Zone, Drone, Connection, ParserError


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
                    elif line.startswith("start_hub:"):
                        if nb == 0:
                            raise ParserError("nb_drones should be on top")
                        if system.start_zone is not None:
                            raise ParserError("duplicate start_hub")
                        zone = self.get_zone(line)
                        zone.capacity = float("inf")

                        system.start_zone = zone
                        system.zones.append(zone)
                    elif line.startswith("end_hub:"):
                        if nb == 0:
                            raise ParserError("nb_drones should be on top")
                        if system.end_zone is not None:
                            raise ParserError("duplicate end_hub")
                        zone = self.get_zone(line)
                        zone.capacity = float("inf")
                        system.end_zone = zone
                        system.zones.append(zone)

                    elif line.startswith("hub:"):
                        if nb == 0:
                            raise ParserError("nb_drones should be on top")
                        z = self.get_zone(line)
                        for zn in system.zones:
                            if z.name == zn.name:
                                raise ParserError("duplicate zone name")
                        system.zones.append(z)
                    elif line.startswith("nb_drones:"):
                        if nb != 0:
                            raise ParserError("duplicate nb_dones")
                        nb = self.drone_nb(line)
                    elif line.startswith("connection:"):
                        if nb == 0:
                            raise ParserError("nb_drones should be on top")
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
                    id=f"D{i + 1}", current_zone=system.start_zone)
                system.drones.append(drone)

            return system

    def drone_nb(self, line: str) -> int:
        try:
            splitted_line = line.split()
            res = int(splitted_line[1])
            if res < 1:
                raise ParserError("nb_drones must be a positive integer")
            return res
        except (ValueError, IndexError):
            raise ParserError("Invalid nb_drones format")

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
            connection = Connection(name=ln[1],
                                    start_zone=start_z,
                                    end_zone=end_z,
                                    max_capacity=int(max_capacity))
            return connection
        except ParserError:
            raise
        except (ValueError, IndexError):
            raise ParserError("invalid connection format")
