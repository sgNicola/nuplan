import sqlite3
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import pandas as pd
from typing import Generator, List, Optional, Set, Tuple, Type, Union, Dict
from ruamel.yaml import YAML
from math import ceil

def execute_many(query: str, params: Tuple, db_file: str):
    """
    Execute a SQL query on a SQLite database and yield the results row by row.
    :param query: The SQL query string.
    :param params: Parameters for the query.
    :param db_file: Path to the SQLite database file.
    :yield: Rows from the query result.
    """
    with sqlite3.connect(db_file) as conn:
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = conn.cursor()
        cursor.execute(query, params)
        for row in cursor.fetchall():
            yield row

def get_db_scenario_info(log_file: str) -> Generator[Tuple[str, int], None, None]:
    """
    Get the scenario types and their occurrence counts from a single database file.
    :param log_file: The path to the SQLite database file.
    :return: A generator of (scenario_tag, count) tuples.
    """
    query = """
    SELECT  type,
            COUNT(*) AS cnt
    FROM scenario_tag
    GROUP BY type
    ORDER BY cnt DESC;
    """

    for row in execute_many(query, (), log_file):
        yield (row["type"], row["cnt"])

def get_lidarpc_tokens_with_scenario_tag_from_db(log_file: str) -> Generator[Tuple[str, str], None, None]:
    """
    Get the LidarPc tokens that are tagged with a scenario from the DB, sorted by scenario_type in ascending order.
    :param log_file: The log file to query.
    :return: A generator of (scenario_tag, token) tuples where `token` is tagged with `scenario_tag`
    """
    query = """
    SELECT  st.type,
            lp.token
    FROM lidar_pc AS lp
    LEFT OUTER JOIN scenario_tag AS st
        ON lp.token=st.lidar_pc_token
    WHERE st.type IS NOT NULL
    ORDER BY st.type ASC NULLS LAST;
    """

    for row in execute_many(query, (), log_file):
        yield (str(row["type"]), row["token"].hex())

def get_scenario_type_token_map(db_files: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Get a map from scenario types to lists of all instances for a given scenario type in the database.
    :param db_files: db files to search for available scenario types.
    :return: dictionary mapping scenario type to list of db/token pairs of that type.
    """
    available_scenario_types = defaultdict(list)
    for db_file in db_files:
        for tag, token in get_lidarpc_tokens_with_scenario_tag_from_db(db_file):
            available_scenario_types[tag].append((db_file, token))

    return available_scenario_types


def aggregate_scenario_counts(db_dir: str) -> Dict[str, int]:
    """
    Aggregate scenario counts across multiple SQLite database files.
    :param db_dir: Directory containing multiple `.db` files.
    :return: A dictionary with scenario types as keys and their total counts as values.
    """
    scenario_counts = defaultdict(int)

    # Iterate over all `.db` files in the directory
    for db_file in os.listdir(db_dir):
        if db_file.endswith(".db"):  # Ensure we only process `.db` files
            db_path = os.path.join(db_dir, db_file)

            # Get scenario counts for the current database
            for scenario_type, count in get_db_scenario_info(db_path):
                scenario_counts[scenario_type] += count

    return scenario_counts

def save_to_yaml(data: dict, output_file: str):
    """
    Save the scenario counts to a YAML file.
    :param data: A dictionary with scenario types as keys and their total counts as values.
    :param output_file: The path to the output YAML file.
    """
    # Convert defaultdict to regular dictionary
    data = dict(data)
    with open(output_file, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
    print(f"Scenario counts saved to {output_file}")

def plot_scenario_distribution(scenario_counts: Dict[str, int]):
    """
    Plot the distribution of scenario types based on their counts.
    :param scenario_counts: A dictionary with scenario types as keys and their counts as values.
    """
    # Convert the dictionary to two lists for plotting
    scenario_types = list(scenario_counts.keys())
    counts = list(scenario_counts.values())

    # Sort by counts (descending order) for better visualization
    sorted_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)
    sorted_scenario_types = [scenario_types[i] for i in sorted_indices]
    sorted_counts = [counts[i] for i in sorted_indices]

    # Create a DataFrame for Seaborn compatibility
    data = pd.DataFrame({
        "Scenario Type": sorted_scenario_types,
        "Count": sorted_counts
    })

    # Plot the distribution
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x="Count",
        y="Scenario Type",
        data=data,
        hue="Scenario Type",  # Assign `Scenario Type` to `hue`
        palette="viridis",
        dodge=False,  # Prevent split bars since `hue` is just for color
        legend=False  # Disable the legend
    )
    plt.title("Distribution of Scenario Types", fontsize=16)
    plt.xlabel("Count", fontsize=14)
    plt.ylabel("Scenario Type", fontsize=14)
    plt.tight_layout()
    plt.show()

def load_scenario_counts(yaml_file: str) -> dict:
    """
    Load scenario counts from a YAML file.
    :param yaml_file: Path to the YAML file.
    :return: A dictionary with scenario types as keys and counts as values.
    """
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)  # Load YAML content safely
    
    return data, total_count

def total_count(data):
    """
    Calculate the total count of scenarios.
    :param data: A dictionary with scenario types as keys and counts as values.
    :return: The total count of scenarios.
    """
    return sum(data.values())

def categorize_scenarios_by_count(scenario_counts: Dict[str, int]) -> Dict[str, List[str]]:
    """
    Categorize scenarios into four categories based on their counts.
    Categories:
    - "0-500": Scenarios with counts between 0 and 500 (inclusive).
    - "500-1000": Scenarios with counts between 501 and 1000 (inclusive).
    - "1000-2000": Scenarios with counts between 1001 and 2000 (inclusive).
    - "2000+": Scenarios with counts greater than 2000.

    :param scenario_counts: A dictionary with scenario types as keys and their total counts as values.
    :return: A dictionary with categories as keys and lists of scenario types as values.
    """
    # Initialize the categories
    categorized_scenarios = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": []
    }
    # Iterate through the scenario counts and categorize them
    for scenario_type, count in scenario_counts.items():
        if 0 <= count <= 500:
            categorized_scenarios["A"].append(scenario_type)
        elif 501 <= count <= 1000:
            categorized_scenarios["B"].append(scenario_type)
        elif 1001 <= count <= 10000:
            categorized_scenarios["C"].append(scenario_type)
        elif 10001 <= count <= 50000:
            categorized_scenarios["D"].append(scenario_type)
        else:  # count > 2000
            categorized_scenarios["E"].append(scenario_type)
    return categorized_scenarios

def evenly_split_scenarios(scenarios: List[str], num_groups: int) -> List[List[str]]:
    """
    Evenly split a list of scenarios into a specified number of groups.

    :param scenarios: A list of scenario tokens to be split.
    :param num_groups: The number of groups to split into.
    :return: A list of lists, each containing an even subset of scenarios.
    """
    group_size = ceil(len(scenarios) / num_groups)
    return [scenarios[i:i + group_size] for i in range(0, len(scenarios), group_size)]

def generate_scenario_filter_yaml(filtered_scenarios: List[str], template_path: str, output_path: str):
    """
    Generates a scenario_filter config YAML file with filtered scenarios written under `scenario_types`,
    while preserving the original format, including null fields, indentation, empty lines, and field order.

    :param filtered_scenarios: A list of scenario types (tokens) to include in the YAML file.
    :param template_path: Path to the template YAML file.
    :param output_path: Path to save the generated YAML file.
    """
    # Initialize ruamel.yaml
    yaml = YAML()
    yaml.preserve_quotes = True  # Preserve quotes and formatting

    # Load the template YAML file
    with open(template_path, 'r', encoding='utf-8') as template_file:
        scenario_filter_config = yaml.load(template_file)

    # Update the `scenario_types` field in the config
    scenario_filter_config['scenario_types'] = filtered_scenarios

    # Write the updated YAML back to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        yaml.dump(scenario_filter_config, output_file)

    print(f"YAML file successfully generated at: {output_path}")
    
def process_and_generate_yaml_files(
    scenario_counts: Dict[str, int],
    template_path: str,
    output_dir: str
):
    """
    Categorize scenarios into groups, generate YAML files for Group A,
    and split the combined groups (B, C, D, E) into four evenly distributed YAML files.

    :param scenario_counts: A dictionary with scenario types as keys and their total counts as values.
    :param template_path: Path to the template YAML file.
    :param output_dir: Directory to save the generated YAML files.
    """
    # Categorize scenarios
    categorized_scenarios = categorize_scenarios_by_count(scenario_counts)

    # 1. Generate YAML file for Group A
    group_a = categorized_scenarios["A"]
    if group_a:  # Only generate if Group A is not empty
        output_path_a = os.path.join(output_dir, "scenario_filter_group_A.yaml")
        generate_scenario_filter_yaml(group_a, template_path, output_path_a)
        print(f"Generated YAML for Group A with {len(group_a)} scenarios.")

    # 2. Combine groups B, C, D, and E into a single list
    combined_scenarios = (
        categorized_scenarios["B"] +
        categorized_scenarios["C"] +
        categorized_scenarios["D"] +
        categorized_scenarios["E"]
    )

    # 3. Evenly split the combined scenarios into 4 groups
    scenario_groups = evenly_split_scenarios(combined_scenarios, 4)

    # 4. Generate YAML files for each of the 4 groups
    for idx, group in enumerate(scenario_groups):
        if group:  # Only generate if the group is not empty
            output_path = os.path.join(output_dir, f"scenario_filter_group_{idx + 1}.yaml")
            generate_scenario_filter_yaml(group, template_path, output_path)
            print(f"Generated YAML for Group {idx + 1} with {len(group)} scenarios.")

if __name__ == "__main__":
    # Use NUPLAN_DATA_ROOT environment variable
    # db_directory = os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/trainval")
    db_directory = os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/test")
    # Aggregate scenario counts across all `.db` files
    total_scenario_counts = aggregate_scenario_counts(db_directory)

    # Print results
    print("\nAggregated Scenario Counts:")
    for scenario_type, count in sorted(total_scenario_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"Scenario Type: {scenario_type}, Total Count: {count}")

    print(f"\nTotal Scenario Count: {total_count(total_scenario_counts)}")
    # Save to YAML
    output_yaml_path = "train_scenario_counts.yaml"
    save_to_yaml(total_scenario_counts, output_yaml_path)
    template_path = "/home/sgwang/nuplan/template.yaml"
    output_dir = "/home/sgwang/nuplan/scenario_filter"
    process_and_generate_yaml_files(total_scenario_counts, template_path, output_dir)