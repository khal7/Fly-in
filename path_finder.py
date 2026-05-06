from system import System, Zone, ParserError


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

    def find_path(self, start_zone: Zone, end_zone: Zone) -> list[Zone]:
        needs_exploration = [(0, start_zone)]
        previous: dict[Zone, Zone] = {}
        visited = []
        costs = {start_zone: 0}

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
                return full_path
            else:
                visited.append(current_zone)
            neighbors = self.get_neighbors(current_zone)
            for neighbor in neighbors:
                if neighbor.zone_type == "restricted":
                    new_cost = cost + 2
                elif neighbor.zone_type == "blocked":
                    continue
                elif neighbor.zone_type == "priority":
                    new_cost = cost + 0.5
                else:
                    new_cost = cost + 1
                if new_cost < costs.get(neighbor, float('inf')):
                    costs[neighbor] = new_cost
                    previous[neighbor] = current_zone
                    needs_exploration.append((new_cost, neighbor))
        raise ParserError("no path found from start to goal")
