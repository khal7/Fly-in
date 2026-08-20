import sys
from models import ParserError, SimulationError
from path_finder import PathFinder
from parser import Parser
from system import Simulation


if __name__ == "__main__":
    try:
        file = sys.argv[1]
        parser = Parser(file)
    except IndexError:
        print("Error: no map file provided")
        exit(1)

    try:
        system = parser.parse()
    except ParserError as e:
        print(e)
        exit(1)
    except KeyboardInterrupt:
        print("\nThe program interrupted by user")
        exit(1)
    path = PathFinder(system)
    similation = Simulation(system, path)
    try:
        similation.assign_path_to_drones()
        similation.moving_drones()
    except SimulationError as e:
        print(e)
        exit(1)
