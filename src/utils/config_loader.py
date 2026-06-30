import os
import yaml


class Config:
    def __init__(
        self,
        config_file=os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "config.yaml"
        ),
    ):
        self.config = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.config = yaml.safe_load(f)

    def ensure_directories(self):
        """
        Initializes directories based on the 'project.directory_paths'
        configuration. This method is idempotent.
        """
        dir_paths = self.get("project.directory_paths")
        if not isinstance(dir_paths, dict):
            return

        project_root = os.path.join(os.path.dirname(__file__), "..")

        for _, details in dir_paths.items():
            # Check if details is a dictionary and has the required keys
            if (
                isinstance(details, dict)
                and details.get("is_dir")
                and details.get("create")
            ):
                # Safely get the path, defaulting to an empty string if not found
                path_value = details.get("path", "")
                if path_value:  # Proceed only if path is not empty
                    dir_path = os.path.join(project_root, path_value)
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                        print(f"Created directory: {dir_path}")

    def get(self, key_path, default=None):
        keys = key_path.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default

        # If the retrieved value is a directory path object, return the path
        if isinstance(val, dict) and "path" in val:
            return val["path"]
        return val


# Global config instance
config = Config()
