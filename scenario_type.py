import os
from collections import Counter

def count_scenario_types(base_dir):
    scenario_counts = Counter()
    
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            path_parts = os.path.join(root, dir_name).split(os.sep)
            if len(path_parts) >= 8:
                scenario_type = path_parts[7]
                scenario_counts[scenario_type] += 1
    
    return scenario_counts


if __name__ == "__main__":
    base_dir = "/home/sgwang/nuplan/exp/InD/"
    scenario_counts = count_scenario_types(base_dir)
    
    for scenario_type, count in scenario_counts.items():
        print(f"{scenario_type}: {count}")