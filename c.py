from drone import Drone
from pathfinding import find_two_shortest_paths
from parsing import DroneMap
from graph import Graph
from typing import Dict, List, Union
import heapq


def simulate(
        drone_map: DroneMap,
        graph: Graph) -> List[Dict[int, Union[str, None]]]:
    # Drone ID counter
    i = 1

    # List containing all drone objects
    drones = []

    # Start and destination zones
    start = drone_map.start
    end = drone_map.end

    # Compute the two shortest paths between start and end
    paths = find_two_shortest_paths(graph, start, end)

    # Convert paths into a priority queue (min-heap)
    heapq.heapify(paths)

    # Assign drones to paths
    while i < drone_map.nb_drones + 1:
        # Get currently cheapest path
        cost, path = heapq.heappop(paths)

        # Create drone using that path
        drones.append(Drone(i, graph, start, end, path))

        # Artificially increase path cost so that future drones
        # are distributed more evenly across available paths
        cost += cost // 2

        # Reinsert modified path into heap
        heapq.heappush(paths, (cost, path))

        i += 1

    # Track how many drones are currently inside each zone
    drones_zones = {zone_name: 0 for zone_name in drone_map.zones.keys()}
    drones_zones[start] = drone_map.nb_drones

    # Track current position of every drone
    drones_positions = {drone.id: start for drone in drones}

    # Stores positions after each turn
    history = []

    # Initial state (turn 0)
    history.append(dict(drones_positions))

    turns = 1

    # Continue simulation until all drones reach destination
    while drones_zones[end] != drone_map.nb_drones:
        print(f"Turn {turns}: ", end="")

        # Track how many drones use each connection this turn
        conn_capacity = {}

        # Process every drone
        for drone in drones:

            # Handle drones currently travelling through
            # a restricted zone (takes one extra turn)
            if drone.in_transit:
                if (
                    drones_zones[
                        drone.transit_destination
                    ] < drone_map.zones[
                        drone.transit_destination
                    ].max_drones
                ):
                    # Drone arrives at destination zone
                    drone.in_transit = False
                    drone.move()

                    print(
                        f"D{drone.id}-{drone.transit_destination}",
                        end=" "
                    )

                    drones_zones[drone.zone] += 1
                    drone.transit_destination = None
                    drones_positions[drone.id] = drone.zone
                    continue

            # Ignore drones already at final destination
            if drone.zone == end:
                continue

            # Next zone in the drone's assigned path
            next_zone = drone.path[drone.index + 1]

            # Find maximum allowed traffic on this connection
            max_capacity: int = 0

            for link in graph.connections[drone.zone]:
                if link.neighbor == next_zone:
                    max_capacity = link.max_link_capacity
                    break

            # Restricted zones require a transit phase
            if drone_map.zones[next_zone].zone == "restricted":

                # Check zone occupancy and link capacity
                if (
                    drones_zones[next_zone]
                    < drone_map.zones[next_zone].max_drones
                    and conn_capacity[(drone.zone, next_zone)]
                    < max_capacity
                ):
                    current_zone = drone.zone

                    # Enter transit state
                    drone.in_transit = True
                    drone.transit_destination = next_zone

                    drones_zones[drone.zone] -= 1

                    print(
                        f"D{drone.id}-({current_zone}-{next_zone})",
                        end=" "
                    )

                    drones_positions[
                        drone.id
                    ] = f"{current_zone}-{next_zone}"

                else:
                    continue

            # Normal zone movement
            else:
                # Check destination zone capacity and link capacity
                if (
                    drones_zones[next_zone]
                    < drone_map.zones[next_zone].max_drones
                    and conn_capacity[(drone.zone, next_zone)]
                    < max_capacity
                ):
                    # Consume one unit of link capacity
                    conn_capacity[(drone.zone, next_zone)] += 1

                    drones_zones[drone.zone] -= 1

                    # Move drone immediately
                    drone.move()

                    print(f"D{drone.id}-{drone.zone}", end=" ")

                    drones_zones[drone.zone] += 1
                    drones_positions[drone.id] = drone.zone
                else:
                    continue

        # Save positions after current turn
        history.append(dict(drones_positions))

        print()
        turns += 1

    # Return complete simulation history
    return history