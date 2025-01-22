import os
import pandas as pd
import yaml
from collections import defaultdict
from ruamel.yaml import YAML
from typing import Any, Dict, List, Optional, Tuple
from utils.loadyamlconfig import LoadYamlConfig
from utils.cachecount import CacheCount
import argparse

def diff_scenario_types(scenario_filter_types, scenario_type_counts):
    cache_scenario_types = scenario_type_counts.keys()  # 获取 scenario_type_counts 的场景类型
    in_filter_not_in_cache = set(scenario_filter_types) - set(cache_scenario_types)
    in_cache_not_in_filter = set(cache_scenario_types) - set(scenario_filter_types)
    
    print("Scenario types in scenario_filter but not in cache:")
    print(in_filter_not_in_cache)
    
    print("\nScenario types in cache but not in scenario_filter:")
    print(in_cache_not_in_filter)
    
    return in_filter_not_in_cache

def get_resample_scenarios(scenario_type_counts):
    df = pd.DataFrame(list(scenario_type_counts.items()), columns=['scenario_type', 'count'])
    
    filtered_scenarios = df[df["count"] < 1000]
    scenario_dict = (filtered_scenarios
                     .set_index("scenario_type")["count"]
                     .apply(lambda x: 1000 - (x))  # 对 count 除以 2
                     .to_dict())
                     
    print("Scenario types with count less than 1000:")
    print(scenario_dict)
    
    return scenario_dict

def generate_scenario_filter_yaml(filtered_scenarios, template_path, output_path):
    """
    Generates a scenario_filter config YAML file with filtered scenarios written under `scenario_tokens`,
    while preserving the original format, including null fields, indentation, empty lines, and field order.

    :param filtered_scenarios: A dictionary where keys are scenario types and values are lists of tokens.
    :param template_path: Path to the template YAML file.
    :param output_path: Path to save the generated YAML file.
    """
    # Initialize ruamel.yaml
    yaml = YAML()
    yaml.preserve_quotes = True  # Preserve quotes and formatting

    # Load the template YAML file
    with open(template_path, 'r', encoding='utf-8') as template_file:
        scenario_filter_config = yaml.load(template_file)

    # Flatten all tokens from filtered_scenarios into a single list
    all_types = set()  # Use a set to avoid duplicates
    for types in filtered_scenarios.keys():
        all_types.add(types)

    # Update the `scenario_types` field in the config
    scenario_filter_config['scenario_types'] = [f'{types}' for types in all_types]

    # Write the updated YAML back to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        yaml.dump(scenario_filter_config, output_file)

    print(f"YAML file successfully generated at: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process planner type and generate resample scenarios.")
    parser.add_argument("--planner", type=str, default='planTF',  # Default to 'planTF' if not provided
                        help="Specify the planner type (e.g., planTF or Gameformer)."
    )
    args = parser.parse_args()
    
    configloader = LoadYamlConfig('InD.yaml')
    scenario_filter_types = configloader.get_scenario_type()
    # Example usage:
    # Determine the cache path and method based on the planner
    if args.planner == "planTF":
        cache = CacheCount('exp/InD_train')
        scenario_type_counts = cache.get_scenario_type_counts()
    elif args.planner == "Gameformer":
        cache = CacheCount('exp/gameInD/train')
        scenario_type_counts = cache.extract_and_count_scenario_types()
    else:
        raise ValueError(f"Unsupported planner type: {args.planner}")
    miss_cache=diff_scenario_types(scenario_filter_types, scenario_type_counts)
    resample_scenarios = get_resample_scenarios(scenario_type_counts)
    for scenario in miss_cache:
        resample_scenarios[scenario] =1000
        
    template_path = 'template.yaml'
    output_path = 'resample.yaml'             # Path to save the generated YAML file
    # Generate the YAML
    generate_scenario_filter_yaml(resample_scenarios, template_path, output_path)