from zone import Zone, Connection
from zone import ZoneType


class Link:
    def __init__(self, neighbor, cost, max_link_capacity):
        self.neighbor = neighbor
        self.cost = cost
        self.max_link_capacity = max_link_capacity


class Graph:
    def __init__(self):
        self.zones: dict[str, Zone] = {}
        self.connections: dict[str, list[Link]] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.id] = zone
        if zone.id not in self.connections:
            self.connections[zone.id] = []

    def get_cost(self, zone_id: str):
        zone = self.zones.get(zone_id)
        if zone.z_type == ZoneType.NORMAL.value:
            return 1.0
        elif zone.z_type == ZoneType.PRIORITY.value:
            return 0.9
        elif zone.z_type == ZoneType.RESTRICTED.value:
            return 2.0
        else:
            return float("inf")

    def add_connection(self, connection: Connection):
        zone_a = connection.zone_a.id
        zone_b = connection.zone_b.id

        cost_to_zone_a = self.get_cost(zone_a)
        cost_to_zone_b = self.get_cost(zone_b)
        link_1 = Link(zone_b, cost_to_zone_b, connection.max_link_capacity)
        link_2 = Link(zone_a, cost_to_zone_a, connection.max_link_capacity)
        self.connections[zone_a].append(link_1)
        self.connections[zone_b].append(link_2)

    def get_neighbors(self, zone_id: str) -> list[Link]:
        return self.connections.get(zone_id, 1)

    def get_zones(self):
        print(self.zones)

    def remove_connection(
        self, zone1: str, zone2: str
    ) -> list[tuple[str, Link]]:
        removed = []
        for link in self.connections[zone1]:
            if link.neighbor == zone2:
                removed.append((zone1, link))
                self.connections[zone1].remove(link)
                break

        for link in self.connections[zone2]:
            if link.neighbor == zone1:
                removed.append((zone2, link))
                self.connections[zone2].remove(link)
                break
        return removed

    def restore_connection(self, removed: list[str, Link]) -> None:
        for zone, link in removed:
            self.connections[zone].append(link)
