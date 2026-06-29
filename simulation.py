from drone import Drone
from path_finder import PathFinder
from graph import Graph


class Simulation:
    @staticmethod
    def simulate(
        graph: Graph, nb_drones: int, start_hub_id: int, end_hub_id: int
    ):
        """
        Simulates the movement of drones from a start hub to an end hub.
        """
        paths = PathFinder.find_two_paths(graph, start_hub_id, end_hub_id)
        print(paths)
        if not paths:
            raise ValueError("No path found from start hub to end hub.")
        drones = []
        for i in range(nb_drones):
            # Assign drones to paths in a round-robin fashion
            path_index = i % len(paths)
            cost, path = paths[path_index]
            drones.append(Drone(i + 1, graph, start_hub_id, end_hub_id, path))
        # drones_positions = {drone.id: start_hub_id for drone in drones}
        drones_zones = {zone_name: 0 for zone_name in graph.zones.keys()}
        drones_zones[start_hub_id] = nb_drones
        turns = 1
        drones_positions = {drone.id: start_hub_id for drone in drones}
        history = []
        history.append(dict(drones_positions))
        # print(drones_zones)
        while drones_zones[end_hub_id] != nb_drones:
            moved_this_turn = False
            print(f"Turn {turns}:", end=" ")
            connection_capacity = {
                (zone1, zone2): 0
                for zone1 in graph.connections
                for link in graph.connections[zone1]
                for zone2 in [link.neighbor]
            }
            for drone in drones:
                # print(connection_capacity)
                if drone.zone == end_hub_id:
                    continue

                next_zone = drone.path[drone.position + 1]
                if drone.in_transit:
                    drone.in_transit = False
                    drone.move()
                    drones_zones[drone.zone] += 1
                    moved_this_turn = True
                    print(
                        f"D{drone.id}-{drone.transit_destination}", end=" "
                        )
                    drone.transit_destination = None
                    drones_positions[drone.id] = drone.zone
                    # print(drones_zones)
                    continue
                conn_max_capacity = 0
                for link in graph.connections[drone.zone]:
                    if link.neighbor == next_zone:
                        conn_max_capacity = link.max_link_capacity
                        break
                if graph.zones[next_zone].z_type == 'restricted':
                    if (
                        drones_zones[next_zone]
                        < graph.zones[next_zone].capacity
                        and
                        connection_capacity[(drone.zone, next_zone)]
                        < conn_max_capacity
                    ):
                        # print(connection_capacity[(drone.zone, next_zone)])

                        # print(conn_max_capacity)
                        current_zone = drone.zone
                        drone.in_transit = True
                        drone.transit_destination = next_zone
                        connection_capacity[(drone.zone, next_zone)] += 1
                        drones_zones[drone.zone] -= 1
                        moved_this_turn = True
                        drones_positions[drone.id] = f"{current_zone}-{next_zone}"
                        print(f"D{drone.id}-{current_zone}-{next_zone}", end=" ")

                else:
                    if (
                        drones_zones[next_zone]
                        < graph.zones[next_zone].capacity
                        and
                        connection_capacity[(drone.zone, next_zone)]
                        < conn_max_capacity
                    ):
                        connection_capacity[(drone.zone, next_zone)] += 1
                        drones_zones[drone.zone] -= 1
                        drone.move()
                        moved_this_turn = True
                        print(f"D{drone.id}-{drone.zone}", end=" ")
                        drones_positions[drone.id] = drone.zone
                        drones_zones[next_zone] += 1
                        # print(drones_zones)
                    else:
                        continue
                # print(connection_capacity)
            history.append(dict(drones_positions))
            print()
            if not moved_this_turn:
                raise ValueError(
                    "Simulation deadlock: no drone can move with current "
                    "path/capacity constraints."
                )
            turns += 1
        return history
