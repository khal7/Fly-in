import sys
from system import *
from path_finder import *




if __name__=="__main__":
    


    file = sys.argv[1]
    parser = Parser(file)


    try:
        system = parser.parse()
    except ParserError as e:
        print(e)
        exit(1)
    path = PathFinder(system)
    get_path = path.find_path(system.start_zone, system.end_zone)
    similation = Simulation(system)
    similation.run(get_path)

    # for zone in get_path:
    #     print(zone.name)
    # for zone in system.zones:
    #     print(zone.name, zone.zone_type, zone.x, zone.y, zone.color, zone.capacity)
    # print("=" * 40)
    # for connection in system.connections:
    #     print(connection.start_zone.name, connection.end_zone.name, connection.max_capacity)
    # print("=" * 40)
    # for drone in system.drones:
    #     print(drone.id, drone.current_zone.name)