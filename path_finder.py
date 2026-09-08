from system import System, Zone, Connection
from class_definition import ParserError


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

    def find_path(self, start_zone: Zone, end_zone: Zone,
                  extra_cost: dict[Zone, int]) -> tuple[Zone, ...]:
        needs_exploration: list[tuple[float, Zone]] = [(0.0, start_zone)]
        previous: dict[Zone, Zone] = {}
        visited = []
        costs: dict[Zone, float] = {start_zone: 0.0}
        while needs_exploration:
            cheapest = min(needs_exploration, key=lambda x: x[0])
            needs_exploration.remove(cheapest)
            cost, current_zone = cheapest
            if current_zone in visited:
                continue
            elif current_zone == end_zone:
                full_path = []
                current = end_zone
                while current != start_zone:
                    full_path.append(current)
                    current = previous[current]
                full_path.append(start_zone)
                full_path.reverse()
                return tuple(full_path)
            else:
                visited.append(current_zone)
            neighbors = self.get_neighbors(current_zone)
            for neighbor in neighbors:
                if neighbor.zone_type == "blocked":
                    continue
                if neighbor.zone_type == "restricted":
                    new_cost = cost + 2 + extra_cost.get(neighbor, 0)
                elif neighbor.zone_type == "priority":
                    new_cost = cost + 0.5 + extra_cost.get(neighbor, 0)
                else:
                    new_cost = cost + 1 + extra_cost.get(neighbor, 0)
                if new_cost < costs.get(neighbor, float('inf')):
                    costs[neighbor] = new_cost
                    previous[neighbor] = current_zone
                    needs_exploration.append((new_cost, neighbor))
        raise ParserError("Error: no path found from start to goal")

    def get_n_priority(self, path: tuple) -> int:
        count = 0
        for zone in path:
            if zone.zone_type == "priority":
                count += 1
        return count

    def get_connection(
            self, zone_a: Zone,
            zone_b: Zone
    ) -> Connection:
        for connection in self.system.connections:
            if ((connection.start_zone == zone_a and
                 connection.end_zone == zone_b) or (
                connection.start_zone == zone_b and
                    connection.end_zone == zone_a)):
                return connection
        raise ParserError("Connection not found")

    def capacity_zone_link(self, path: tuple) -> int | float:

        min_capacity = float("inf")
        for i in range(len(path) - 1):
            con = self.get_connection(path[i], path[i + 1])
            if min_capacity > con.max_capacity:
                min_capacity = con.max_capacity
            if min_capacity > path[i + 1].capacity:
                min_capacity = path[i + 1].capacity
        return min_capacity

    def path_cost(self, path: tuple) -> int:
        count = 0
        for zone in path:
            if zone == self.system.start_zone:
                continue
            if zone.zone_type == "restricted":
                count += 2
            else:
                count += 1
        return count

    def find_all_paths(self, start_zone: Zone, end_zone: Zone) -> list:
        extra_cost: dict[Zone, int] = {}
        path_info = {}
        first_path = None

        while True:
            try:
                p = self.find_path(start_zone, end_zone, extra_cost)
            except ParserError as e:
                print(e)
                exit(1)

            if p in path_info:
                break
            if first_path is None:
                first_path = p
            elif len(p) > len(first_path) + 1:
                break
            path_info[p] = (
                self.path_cost(p),
                self.get_n_priority(p),
                self.capacity_zone_link(p))
            for zone in p:
                if (zone == self.system.start_zone
                        or zone == self.system.end_zone):
                    continue
                extra_cost[zone] = extra_cost.get(zone, 0) + 10
        return sorted(
            path_info.items(), key=lambda item: (
                item[1][0], -item[1][1], -item[1][2]))
