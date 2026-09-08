from __future__ import annotations
from rich.console import Console
from rich.text import Text
from typing import TYPE_CHECKING
from class_definition import System, Zone, Connection, SimulationError
if TYPE_CHECKING:
    from path_finder import PathFinder

console = Console()


class Simulation:
    def __init__(self, system: System, pathfinder: PathFinder):
        self.system = system
        self.pathfinder = pathfinder

    def check_connection(
            self,
            zone_a: Zone,
            zone_b: Zone) -> Connection:
        for connection in self.system.connections:
            if (connection.start_zone == zone_a
                and connection.end_zone == zone_b) or (
                    connection.start_zone == zone_b
                    and connection.end_zone == zone_a):
                return connection
        raise SimulationError("Connection not found")

    def assign_path_to_drones(self) -> None:
        if self.system.start_zone is None or self.system.end_zone is None:
            raise SimulationError("Start or end zone is not defined")
        paths = self.pathfinder.find_all_paths(
            self.system.start_zone, self.system.end_zone)
        path_index = 0
        assigned = 0
        for drone in self.system.drones:
            if paths[path_index][1][2] > assigned:
                assigned += 1
                drone.path = paths[path_index][0]
            else:
                path_index += 1
                if path_index >= len(paths):
                    path_index = 0
                assigned = 1
                drone.path = paths[path_index][0]

    def moving_drones(self) -> None:
        assert self.system.start_zone is not None
        assert self.system.end_zone is not None
        turn = 0
        for drone in self.system.drones:
            self.system.start_zone.current_drones.append(drone)
        while not all(
                drone.current_zone == self.system.end_zone
                for drone in self.system.drones
        ):
            movements = []
            used_this_turn: dict[Connection, int] = {}
            arriving = []
            # 1. Finish transits and free their connections.
            for drone in self.system.drones:
                if drone.status != "moving":
                    continue
                drone.turns_remaining -= 1
                if drone.turns_remaining == 0:
                    assert drone.next_zone is not None
                    connection = self.check_connection(
                        drone.current_zone,
                        drone.next_zone
                    )
                    connection.currently_in.remove(drone)
                    arriving.append(drone)
            # 2. Move drones that were already waiting.
            # Drones arriving this turn cannot move again.
            for drone in self.system.drones:
                if drone in arriving:
                    continue
                if drone.status != "waiting":
                    continue
                if drone.current_zone == self.system.end_zone:
                    continue
                indx = drone.path.index(drone.current_zone)
                if indx + 1 >= len(drone.path):
                    continue
                next_zone = drone.path[indx + 1]
                connection = self.check_connection(
                    drone.current_zone,
                    next_zone
                )
                in_flight = len(connection.currently_in)
                crossed_now = used_this_turn.get(connection, 0)
                if in_flight + crossed_now >= connection.max_capacity:
                    continue
                if next_zone.zone_type == "restricted":
                    used_this_turn[connection] = crossed_now + 1
                    drone.current_zone.current_drones.remove(drone)
                    connection.currently_in.append(drone)
                    drone.next_zone = next_zone
                    drone.turns_remaining = 1
                    drone.status = "moving"
                    movements.append(
                        (drone, f"{drone.id}-{connection.name}", next_zone)
                    )
                else:
                    if len(next_zone.current_drones) >= next_zone.capacity:
                        continue
                    used_this_turn[connection] = crossed_now + 1
                    drone.current_zone.current_drones.remove(drone)
                    next_zone.current_drones.append(drone)

                    movements.append(
                        (drone, f"{drone.id}-{next_zone.name}", next_zone)
                    )
                    drone.current_zone = next_zone
            # 3. Finish the transits that were freed above.
            for drone in arriving:
                assert drone.next_zone is not None
                next_zone = drone.next_zone
                if len(next_zone.current_drones) >= next_zone.capacity:
                    connection = self.check_connection(
                        drone.current_zone,
                        next_zone
                    )
                    connection.currently_in.append(drone)
                    drone.turns_remaining = 1
                    continue
                next_zone.current_drones.append(drone)

                movements.append(
                    (drone, f"{drone.id}-{next_zone.name}", next_zone)
                )
                drone.current_zone = next_zone
                drone.next_zone = None
                drone.status = "waiting"
            movements.sort(
                key=lambda movement: self.system.drones.index(movement[0])
            )
            turn += 1
            if movements:
                output = Text()
                for drone, movement, zone in movements:
                    color = zone.color if zone.color else "white"
                    try:
                        Text("test", style=color)
                    except Exception:
                        color = "white"
                    output.append(drone.id, style="white")
                    output.append(movement[len(drone.id):] + " ", style=color)
                console.print(output)
        print(f"Number of turns: {turn}")
