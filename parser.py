from zone import ZoneFactory, HubType, Connection, ZoneType


class Parser:
    """
    A class to parse the input data for the drone delivery system.
    """
    def __init__(self):
        """
        Initializes the Parser with default values for the number of drones,
        start hub, hubs, end hub, and connections.
        """
        self.nb_drones = 1
        self.start_hub = None
        self.hubs = []
        self.end_hub = None
        self.connections = []

    def parse(self, data):
        """
        Parses the input data and populates the attributes of the Parser class.
        Args:
            data (str): The input data as a string.
        Returns:
            dict: A dictionary containing the parsed information, including the
            number of drones, start hub, hubs, end hub, and connections.
        """
        # Example parsing logic
        lines = data.splitlines()
        manager = ParserManager()
        for i, line in enumerate(lines):
            if line.startswith("#") or line.strip() == "":
                continue
            elif line.startswith("nb_drones"):
                try:
                    parse = manager.parser["drone_count"]
                    self.nb_drones = parse.parse(line)
                except ValueError as e:
                    raise ValueError(
                        f"Error line {i + 1}: parsing drone count: {e}")
            elif line.startswith("start_hub"):
                try:
                    parse = manager.parser["start_hub"]
                    res = parse.parse(line)
                    res['max_drones'] = self.nb_drones
                    self.start_hub = ZoneFactory.create(
                        HubType.START_HUB, res
                    )
                except ValueError as e:
                    raise ValueError(f"Error: parsing start hub: {e}")
            elif line.startswith("hub"):
                try:
                    parse = manager.parser["hub"]
                    res = parse.parse(line)
                    self.hubs.append(ZoneFactory.create(
                        HubType.HUB, res
                    ))
                    # Store or process the hub information as needed
                except ValueError as e:
                    raise ValueError(f"Error line {i + 1}: parsing hub: {e}")
            elif line.startswith("end_hub"):
                try:
                    parse = manager.parser["end_hub"]
                    res = parse.parse(line)
                    res['max_drones'] = self.nb_drones
                    self.end_hub = ZoneFactory.create(
                        HubType.END_HUB, res
                    )
                    # Store or process the end hub information as needed
                except ValueError as e:
                    raise ValueError(
                        f"Error line {i + 1}: parsing end hub: {e}")
            elif line.startswith("connection"):
                try:
                    parse = manager.parser["connection"]
                    res = parse.parse(line)
                    # print(res)
                    zone_a = next(
                        (
                            z for z in self.hubs
                            if z.id == res['zone_a']
                        ),
                        None
                    )
                    if zone_a is None:
                        if res['zone_a'] == self.start_hub.id:
                            zone_a = self.start_hub
                        elif res['zone_a'] == self.end_hub.id:
                            zone_a = self.end_hub
                    zone_b = next(
                        (
                            z for z in self.hubs
                            if z.id == res['zone_b']
                        ),
                        None
                    )
                    if zone_b is None:
                        if res['zone_b'] == self.start_hub.id:
                            zone_b = self.start_hub
                        elif res['zone_b'] == self.end_hub.id:
                            zone_b = self.end_hub
                    if not zone_a:
                        raise ValueError(
                            f"Error: Connection references unknown hub: "
                            f"{res['zone_a']}"
                        )
                    if not zone_b:
                        raise ValueError(
                            f"Error: Connection references unknown hub: "
                            f"{res['zone_b']}"
                        )

                    self.connections.append(
                        Connection(
                            zone_a,
                            zone_b,
                            res.get('max_link_capacity', 1)
                        )
                    )
                except ValueError as e:
                    raise ValueError(
                        f"Error line {i + 1}: parsing connection: {e}")
            else:
                raise ValueError(
                    f"Error line {i + 1}: Unknown line type: {line}")
        # check if the ids are unique
        hubIds = {hub.id for hub in self.hubs}
        if len(hubIds) != len(self.hubs):
            raise ValueError("Error: Duplicate hub names found.")
        if self.start_hub.id in hubIds:
            raise ValueError("Error: Start hub ID must be unique.")
        if self.end_hub.id in hubIds:
            raise ValueError("Error: End hub ID must be unique.")
        if self.start_hub.id == self.end_hub.id:
            raise ValueError("Error: Start and end hub IDs must be unique.")
        for hub in self.hubs:
            x, y = hub.x, hub.y
            if self.start_hub.x == x and self.start_hub.y == y:
                raise ValueError(
                    "Error: Start hub coordinates must be unique."
                    )
            if self.end_hub.x == x and self.end_hub.y == y:
                raise ValueError("Error: End hub coordinates must be unique.")
        if (self.start_hub.x == self.end_hub.x and
                self.start_hub.y == self.end_hub.y):
            raise ValueError(
                "Error: Start and end hub coordinates must be unique."
                )
        if (self.end_hub.z_type == 'blocked' or
                self.start_hub.z_type == 'blocked'):
            raise ValueError(
                "Error: Start and end hubs cannot be in blocked zones."
                )
        # check unique hubs coordinates
        hubscoordunique = {(hub.x, hub.y) for hub in self.hubs}
        if len(hubscoordunique) != len(self.hubs):
            raise ValueError("Error: Duplicate hub coordinates found.")
        if self.start_hub.z_type == "blocked":
            raise ValueError("Error: Start hub cannot be in a blocked zone.")
        if self.end_hub.z_type == "blocked":
            raise ValueError("Error: End hub cannot be in a blocked zone.")
        return {
            "nb_drones": self.nb_drones,
            "start_hub": self.start_hub,
            "hubs": self.hubs,
            "end_hub": self.end_hub,
            "connections": self.connections
        }

    def get_connections(self):
        """
        Returns the list of connections.
        Returns:
            list: A list of connections, where each connection is represented
            as a dictionary containing the connection information.
        """
        return self.connections

    def get_hubs(self):
        """
        Returns the list of hubs.
        Returns:
            list: A list of hubs, where each hub is represented as a dictionary
            containing the hub information.
        """
        return self.hubs


class DroneCountParser:

    def parse(self, line):
        """
        Parses the drone count line and returns the number
        of drones as an integer.
        Args:
            line (str): The input line containing the drone count.
        Returns:
            int: The number of drones.
        Raises:
            ValueError: If the line format is invalid or
            the drone count is not an integer.
        """
        if line.strip().count('#') >= 1:
            line = line.split('#', 1)[0]
        line = ParserManager.parse_line_name(line)
        try:
            count = int(line.strip())
        except ValueError:
            raise ValueError("Drone count must be an integer")
        if count <= 0:
            raise ValueError("Drone count must be a positive integer")
        return count


class StartHubParser():
    """
    A class to parse the start hub line and return a dictionary
    containing the start hub information, including its ID,
    coordinates, and any additional metadata.
    """
    def parse(self, line: str) -> dict:
        """
        Parses the start hub line and returns a dictionary containing
        the start hub information, including its ID, coordinates,
        and any additional metadata.
        Args:
            line (str): The input line containing the start hub information.
        Returns:
            dict: A dictionary containing the start hub information.
        Raises:
            ValueError: If the line format is invalid or the required
            information is missing.
        """
        if line.strip().count('#') >= 1:
            line = line.split('#', 1)[0]
        parts = ParserManager.parse_line_name(line)
        parts = parts.strip().split(' ')
        if len(parts) < 3:
            raise ValueError(
                "Start hub line not correctly formatted."
                )
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError("Start hub coordinates must be integers.")
        obj = {
            "id": parts[0],
            "x": x,
            "y": y,
        }
        if len(parts) > 3:
            allowed = ['color', 'zone', 'max_drones']
            obj2 = ParserManager.parse_metadata(parts[3:], allowed)
            return obj | obj2
        return obj


class HubParser:
    """
    A class to parse the hub line and return a dictionary
    containing the hub information, including its ID,
    coordinates, and any additional metadata.
    """
    def parse(self, line: str) -> dict:
        """
        Parses the hub line and returns a dictionary containing
        the hub information, including its ID, coordinates,
        and any additional metadata.
        Args:
            line (str): The input line containing the hub information.
        Returns:
            dict: A dictionary containing the hub information.
        Raises:
            ValueError: If the line format is invalid or the required
            information is missing.
        """
        if line.strip().count('#') >= 1:
            line = line.split('#', 1)[0]
        parts = ParserManager.parse_line_name(line)
        parts = parts.strip().split(' ')
        if len(parts) < 3:
            raise ValueError("Hub line not correctly formatted.")
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError("Hub coordinates must be integers.")
        obj = {
            "id": parts[0],
            "x": x,
            "y": y,
            "color": None,
            "max_drones": 1,
        }
        if len(parts) > 3:
            allowed = ['color', 'zone', 'max_drones']
            obj2 = ParserManager.parse_metadata(parts[3:], allowed)
            return obj | obj2
        return obj


class EndHubParser:
    """
    A class to parse the end hub line and return a dictionary
    containing the end hub information, including its ID,
    coordinates, and any additional metadata.
    """
    def parse(self, line: str) -> dict:
        """
        Parses the end hub line and returns a dictionary containing
        the end hub information, including its ID, coordinates,
        and any additional metadata.
        Args:
            line (str): The input line containing the end hub information.
        Returns:
            dict: A dictionary containing the end hub information.
        Raises:
            ValueError: If the line format is invalid or the required
        """
        if line.strip().count('#') >= 1:
            line = line.split('#', 1)[0]
        parts = ParserManager.parse_line_name(line)
        parts = parts.strip().split(' ')
        if len(parts) < 2:
            raise ValueError("End hub line not correctly formatted.")
        if not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError("End hub coordinates must be integers.")

        obj = {
            "id": parts[0],
            "x": int(parts[1]),
            "y": int(parts[2]),
            "color": None,
        }
        if len(parts) > 3:
            allowed = ['color', 'zone', 'max_drones']
            obj2 = ParserManager.parse_metadata(parts[3:], allowed)
            return obj | obj2
        return obj


class ConnectionParser:
    """
    A class to parse the connection line and return a dictionary
    containing the connection information, including its ID
    and any additional metadata.
    """
    def parse(self, line: str) -> dict:
        """
        Parses the connection line and returns a dictionary containing
        the connection information, including its ID
        and any additional metadata.
        Args:
            line (str): The input line containing the connection information.
        Returns:
            dict: A dictionary containing the connection information.
        Raises:
            ValueError: If the line format is invalid or the required
            information is missing.
        """
        parts = ParserManager.parse_line_name(line)
        parts = parts.strip().split(' ')
        if parts[0].count("-") != 1:
            raise ValueError(
                "Error: Connection must be in the format 'hub1-hub2'."
            )
        zone_a, zone_b = parts[0].split('-')
        obj = {
            "zone_a": zone_a,
            "zone_b": zone_b
        }
        start, end = parts[0].split("-")
        # print(start, end)
        # access the created connections and check
        # if the start and end hubs exist
        if start == end:
            raise ValueError("Error: connection can't link a hub to itself")
        if len(parts) > 1:
            allowed = ['max_link_capacity']
            obj2 = ParserManager.parse_metadata(parts[1:], allowed)
            return obj | obj2
        return obj


class ParserManager:
    """
    A class to manage different parsers for various
    line types in the input data.
    """
    def __init__(self):
        """
        Initializes the ParserManager with
        a dictionary of parsers for different line types.
        """
        self.parser = {
            "drone_count": DroneCountParser(),
            "start_hub": StartHubParser(),
            "hub": HubParser(),
            "end_hub": EndHubParser(),
            "connection": ConnectionParser(),
        }

    @staticmethod
    def parse_line_name(line: str) -> str:
        """
        Parses the line name from the given line.
        Args:
            line (str): The input line.
        Returns:
            str: The line name extracted from the line.
        Raises:
            ValueError: If the line format is invalid or
            the line name cannot be extracted.
        """
        parts = line.split(":", 1)
        valid_names = [
            "nb_drones", "start_hub", "hub", "end_hub", "connection"
        ]
        if (len(parts) < 2 or parts[0].strip() == "" or
                parts[0].strip() not in valid_names):
            raise ValueError("Error: Line malformed.")
        return parts[1]

    @staticmethod
    def parse_metadata(parts: list, allowed_metada: list[str]) -> dict:
        """
        Parses the metadata from the given parts of
        a line and returns a dictionary
        containing the metadata information.
        Args:
            parts (list): A list of strings representing the parts of a line.
        Returns:
            dict: A dictionary containing the parsed metadata information.
        Raises:
            ValueError: If the metadata format is invalid or the required
            information is missing.
        """
        obj = {}

        meta_data_parts = " ".join(parts).strip()

        if not meta_data_parts.startswith("["):
            raise ValueError(
                "Metadata must start with '['."
            )

        if not meta_data_parts.endswith("]"):
            raise ValueError(
                "Metadata must end with ']'."
            )
        meta_data_parts = meta_data_parts[1:-1].strip()

        # normalize spaces around '='
        tokens = meta_data_parts.replace("=", " = ").split()

        i = 0
        numeric_keys = {"max_drones", "max_link_capacity"}
        while i < len(tokens):
            if i + 2 >= len(tokens):
                raise ValueError(
                    f"Invalid metadata format near: {' '.join(tokens[i:])}"
                )

            key = tokens[i]
            equal = tokens[i + 1]
            value = tokens[i + 2]

            if equal != "=":
                raise ValueError(
                    f"Expected '=' after '{key}', got '{equal}'."
                )
            if key.lower() not in allowed_metada:
                raise ValueError(f"Invalid metadata key: {key}.")

            if key == "zone":
                try:
                    ZoneType(value.lower())
                    obj[key] = value.lower()
                except ValueError:
                    raise ValueError(
                        f"Invalid zone value: {value}. "
                        f"Valid values are {[e.value for e in ZoneType]}"
                    )
            elif key in numeric_keys:
                try:
                    obj[key] = int(value)
                except ValueError:
                    raise ValueError(
                        f"Invalid value for {key}: {value}. "
                        "Must be an integer."
                    )
            else:
                obj[key] = value

            i += 3
        return obj
