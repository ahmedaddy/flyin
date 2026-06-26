from graph import Graph


class Drone:
    """
    Represents a drone moving through a path of zones.
    """
    def __init__(
            self, id: int, graph: Graph, start: str, end: str, path: list[str]
            ) -> None:
        self.id = id
        self.zone = start
        self.position = 0
        self.path = path
        self.in_transit: bool = False
        self.transit_destination: str | None = None

    def move(self) -> None:
        """
        Moves the drone to the next zone in its path.
        Stops if it already reached the end.
        """
        if self.position == len(self.path) - 1:
            return
        self.position += 1
        self.zone = self.path[self.position]
