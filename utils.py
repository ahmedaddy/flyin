class Utils:
    @staticmethod
    def Read_file(file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                try:
                    return f.read()
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    return ""
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return ""
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")
            return ""
