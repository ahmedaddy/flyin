import heapq
from graph import Graph
from typing import Optional


class PathFinder:
    @staticmethod
    def find_path(graph: Graph, start_hub_id, end_hub_id):
        hq = heapq
        distances = {zone: float('inf') for zone in graph.zones}
        distances[start_hub_id] = 0
        visited = set()
        # 0, 0
        route: list[tuple[float, str]] = []
        hq.heappush(route, (0, start_hub_id))
        parent: dict[str, Optional[str]] = {start_hub_id: None}
        while route:
            cost, zone_name = hq.heappop(route)
            if zone_name == end_hub_id:
                path: list[str] = []
                current = end_hub_id
                while current is not None:
                    path.append(current)
                    current = parent[current]
                path.reverse()
                return (cost, path)
            if zone_name in visited:
                continue
            visited.add(zone_name)
            for zone in graph.get_neighbors(zone_name):
                new_cost = cost + zone.cost
                if new_cost < distances[zone.neighbor]:
                    distances[zone.neighbor] = new_cost
                    hq.heappush(route, (new_cost, zone.neighbor))
                    parent[zone.neighbor] = zone_name

        # Reconstruct path from start to end
        # print("Parent", parent)

    def find_two_paths(graph: Graph, start_hub_id, end_hub_id):
        cost, path = PathFinder.find_path(graph, start_hub_id, end_hub_id)
        if not path:
            return []
        i = 0
        second = None
        for i in range(len(path) - 1):
            zone1 = path[i]
            zone2 = path[i + 1]
            removed_links = graph.remove_connection(zone1, zone2)
            result = PathFinder.find_path(
                graph, start_hub_id, end_hub_id
            )
            if result is None:
                graph.restore_connection(removed_links)
                continue
            second_cost, second_path = result
            if second_path == path:
                continue
            graph.restore_connection(removed_links)
            if second_cost and second_path != path:
                if second is None or second_cost < second[0]:
                    second = (second_cost, second_path)
        result = [(cost, path)]
        if second is not None:
            result.append(second)
        return result
