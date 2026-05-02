import sys
from system import *




if __name__=="__main__":
    


    file = sys.argv[1]
    parser = Parser(file)


    try:
        system = parser.parse()
    except ParserError as e:
        print(e)
        exit(1)

    for zone in system.zones:
        print(zone.name, zone.zone_type, zone.x, zone.y, zone.color, zone.capacity)
    print("=" * 40)
    for connection in system.connections:
        print(connection.start_zone.name, connection.end_zone.name, connection.max_capacity)
    print("=" * 40)
    for drone in system.drones:
        print(drone.id, drone.current_zone.name)