import os
import pandas as pd
import yaml
from collections import defaultdict
from ruamel.yaml import YAML
from typing import Any, Dict, List, Optional, Tuple

class CacheCount:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def get_log_names_from_cache(self):
        log_names = [
            folder for folder in os.listdir(self.cache_dir)
            if os.path.isdir(os.path.join(self.cache_dir, folder))
        ]
        return log_names

    def get_all_scenario_tokens(self):
        scenario_tokens = []
        for log_name in os.listdir(self.cache_dir):
            log_name_path = os.path.join(self.cache_dir, log_name)
            if os.path.isdir(log_name_path):
                for scenario_type in os.listdir(log_name_path):
                    scenario_type_path = os.path.join(log_name_path, scenario_type)
                    if os.path.isdir(scenario_type_path):
                        for scenario_token in os.listdir(scenario_type_path):
                            scenario_token_path = os.path.join(scenario_type_path, scenario_token)
                            if os.path.isdir(scenario_token_path):
                                scenario_tokens.append(scenario_token)
        return scenario_tokens

    def get_scenario_type_counts(self):
        scenario_type_counts = defaultdict(int)
        for log_name in os.listdir(self.cache_dir):
            log_name_path = os.path.join(self.cache_dir, log_name)
            if os.path.isdir(log_name_path):
                for scenario_type in os.listdir(log_name_path):
                    scenario_type_path = os.path.join(log_name_path, scenario_type)
                    if os.path.isdir(scenario_type_path):
                        token_count = len([
                            token for token in os.listdir(scenario_type_path)
                            if os.path.isdir(os.path.join(scenario_type_path, token))
                        ])
                        scenario_type_counts[scenario_type] += token_count
        return scenario_type_counts
    
