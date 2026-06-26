from parser import Parser
from utils import Utils
from graph import Graph
from simulation import Simulation
import sys


def main():
    parser = Parser()
    map_file = sys.argv[1]

    data = Utils.Read_file(map_file)
    if data == "":
        return
    try:
        result = parser.parse(data)
        graph = Graph()
        # Add all zones to the graph first
        graph.add_zone(result["start_hub"])
        for hub in result["hubs"]:
            graph.add_zone(hub)
        graph.add_zone(result["end_hub"])
        # Then add connections
        for conn in result["connections"]:
            # print("Zone A :", conn.zone_a.id, "Zone B :", conn.zone_b.id)
            graph.add_connection(conn)
        # graph.get_zones()
        # path = path.find_path(
        #     graph, result['start_hub'].id, result['end_hub'].id)
        # print(path)
        sim = Simulation()
        sim.simulate(graph, result['nb_drones'],
                     result['start_hub'].id,
                     result['end_hub'].id)
        # print(graph.connections['start'])
        # graph.get_zones()
        # neighbors = graph.get_neighbors(result["start_hub"].id)
        # print("Neighbors of start hub:")
        # for neighbor in neighbors:
        #     print(f"  - {neighbor.neighbor}")
        # print(result)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
