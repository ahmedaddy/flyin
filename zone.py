from enum import Enum


class ZoneType(Enum):
    """
    An enumeration representing different zones for the drone delivery system.
    """
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class Zone:
    def __init__(
        self, _id, x, y, capacity=1, hub_type=None, color=None, z_type=None
            ):
        self.id = _id
        self.x = x
        self.y = y
        self.capacity = capacity
        self.hub_type = hub_type
        self.color = color
        self.z_type = z_type


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone, max_link_capacity: int):
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity


class HubType(Enum):
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"


class ZoneFactory:
    @staticmethod
    def create(hub_type: HubType, base: dict):
        # print(base)
        return Zone(
            _id=base["id"],
            x=base["x"],
            y=base["y"],
            capacity=base['max_drones'] if 'max_drones' in base else 1,
            hub_type=hub_type,
            color=base['color'] if 'color' in base else None,
            z_type=base['zone'] if 'zone' in base else ZoneType.NORMAL.value
        )
