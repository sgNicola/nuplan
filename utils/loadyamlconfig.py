import yaml

class LoadYamlConfig:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.config = self.load_config()

    def load_config(self):
        """Load the YAML configuration file."""
        with open(self.yaml_file, "r") as file:
            return yaml.safe_load(file)

    def get_scenario_type(self):
        """Load scenario types from the configuration."""
        return self.config.get("scenario_types", [])

    def get_train_log(self):
        """Get training data from the configuration."""
        return self.config.get("log_splits", {}).get("train", [])

    def get_validation_log(self):
        """Get validation data from the configuration, if available."""
        return self.config.get("log_splits", {}).get("validation", [])

    def get_test_log(self):
        """Get test data from the configuration, if available."""
        return self.config.get("log_splits", {}).get("test", [])

    def get_config(self):
        """Return the entire configuration."""
        return self.config