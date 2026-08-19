import sys
from models import ParserError, SimulationError
from path_finder import PathFinder
from parser import Parser
from system import Simulation


if __name__ == "__main__":

    file = sys.argv[1]
    parser = Parser(file)

    try:
        system = parser.parse()
    except ParserError as e:
        print(e)
        exit(1)
    path = PathFinder(system)
    similation = Simulation(system, path)
    try:
        similation.assign_path_to_drones()
        similation.moving_drones()
    except SimulationError as e:
        print(e)
        exit(1)
