*This project has been created as part of the 42 curriculum by khabouou.*

# Description

## Fly-in

Fly-in is a Python pathfinding and drone simulation project.

The goal is to find suitable paths between a starting zone and a destination, then simulate multiple drones travelling through those paths while respecting zone and connection constraints.

The map is represented as a graph containing different types of zones:

* Normal zones
* Restricted zones
* Priority zones
* Blocked zones

Zones can have a maximum number of drones (`max_drones`), while connections can have a maximum number of drones in transit (`max_link_capacity`).

# Algorithm

## Pathfinding

The project uses a weighted Dijkstra-style algorithm.

Each zone type has a different cost:

* Normal: `1`
* Restricted: `2`
* Priority: `0.5`
* Blocked: not traversable

The algorithm finds the lowest-cost path and reconstructs it using previous-zone information.

To find alternative paths, the cost of zones used by previously discovered paths is increased. This encourages the algorithm to explore different routes.

Paths longer than one zone beyond the shortest path are rejected.

The remaining paths are ranked by:

1. Path cost
2. Number of priority zones
3. Minimum capacity along the path

## Drone Simulation

The simulation runs turn by turn.

Each drone follows its assigned path while respecting:

* Zone capacity (`max_drones`)
* Connection capacity (`max_link_capacity`)
* Restricted-zone transit time
* Drone movement state

Restricted zones require multiple turns of transit. When a drone finishes a transit, the connection is freed immediately, allowing another drone to use it during the same turn.

# Visual Representation

The simulation uses the `rich` library to display drone movements in the terminal.

Zone colors from the map are used when displaying movements, making it easy to distinguish different zones and follow the drones' progress.

Example:

```text id="q7m2vf"
D1-waypoint1 D2-waypoint1
D1-waypoint2
D2-waypoint2
```

Each line represents one turn.

# Instructions

## Installation

Python 3 is required.

Create and activate a virtual environment:

```text id="z7k8qp"
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependency:

```text id="6f3rqa"
pip install rich
```

## Execution

Run the program with a map file:

```text id="7b1j9d"
python3 main.py maps/easy/01_linear_path.txt
```

Other maps can be found in the `maps/` directory.

## Type Checking

```text id="j3v5kc"
mypy .
```

## Code Style

```text id="t8n2mx"
flake8 --exclude=.venv .
```

# Example

Input:

```text id="e1h4zs"
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue zone=restricted]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Output:

```text id="m6z8kp"
D1-waypoint1
D1-waypoint1-waypoint2 D2-waypoint1
D1-waypoint2 D2-waypoint1-waypoint2
D1-goal D2-waypoint2
D2-goal
Number of turns: 5
```

# Resources

* Python Documentation — https://docs.python.org/3/
* Dijkstra's Algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* Graph Theory — https://en.wikipedia.org/wiki/Graph_theory
* Rich Documentation — https://rich.readthedocs.io/
* Mypy Documentation — https://mypy.readthedocs.io/
* Flake8 Documentation — https://flake8.pycqa.org/

## AI Usage

AI was used as a learning and debugging assistant during development.
It was used for:

* Deepen my understanding of Dijkstra's algorithm.
* Help with debugging
* Code review: spotting unused variables, dead code, and inconsistent type annotations.
* README: correcting spelling mistakes and structuring this document.

The final implementation was tested manually using the project's different map scenarios.
