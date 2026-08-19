from __future__ import annotations
from typing import Optional


class ParserError(Exception):
    pass


class SimulationError(Exception):
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
                 name: str,
                 start_zone: Zone,
                 end_zone: Zone,
                 max_capacity: int = 1,
                 currently_in: Optional[list[Drone]] = None

                 ):
        self.name = name
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
