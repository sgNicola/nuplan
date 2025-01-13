import sqlite3
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
from typing import Generator, Tuple, Dict
import pandas as pd
import shutil

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
            print(f"Processing {db_path}...")

            # Get scenario counts for the current database
            for scenario_type, count in get_db_scenario_info(db_path):
                scenario_counts[scenario_type] += count

    return scenario_counts

# def move_scenarios(db_dir: str, target_dir: str, scenario_types: list, max_scenario_types: int = 500):
#     """
#     Move database files containing specific scenario types to a target directory, 
#     with a limit on the number of unique scenario types moved.
#     :param db_dir: Directory containing `.db` files.
#     :param target_dir: Directory where matching `.db` files will be moved.
#     :param scenario_types: List of scenario types to check for.
#     :param max_scenario_types: Maximum number of unique scenario types to move.
#     """
#     # Ensure the target directory exists
#     os.makedirs(target_dir, exist_ok=True)

#     # Set to track unique scenario types that have been moved
#     moved_scenario_types: Set[str] = set()

#     # Iterate over all `.db` files in the directory
#     for db_file in os.listdir(db_dir):
#         if len(moved_scenario_types) >= max_scenario_types:
#             print(f"Reached the maximum unique scenario type limit of {max_scenario_types}. Stopping.")
#             break

#         if db_file.endswith(".db"):  # Ensure we only process `.db` files
#             db_path = os.path.join(db_dir, db_file)
#             print(f"Processing {db_path}...")

#             # Check if the database contains any of the target scenario types
#             move_file = False
#             for scenario_type, _ in get_db_scenario_info(db_path):
#                 if scenario_type in scenario_types and scenario_type not in moved_scenario_types:
#                     moved_scenario_types.add(scenario_type)  # Add to the set of moved types
#                     move_file = True

#                 # Stop processing if we have reached the limit
#                 if len(moved_scenario_types) >= max_scenario_types:
#                     break

#             # Move the file if at least one new unique scenario type is found
#             if move_file:
#                 target_path = os.path.join(target_dir, db_file)
#                 if not os.path.exists(target_path):  # Avoid overwriting files
#                     shutil.move(db_path, target_path)
#                     print(f"Moved {db_path} to {target_path}")
#                 else:
#                     print(f"File {db_file} already exists in {target_dir}, skipping.")

#     print(f"Total unique scenario types moved: {len(moved_scenario_types)}")

def move_scenarios(db_dir: str, target_dir: str, scenario_types: Dict[str, int], max_per_type: int = 500):
    """
    Move database files containing specific scenario types to a target directory, 
    stopping when scenario_type reaches its move limit (500 - count).
    :param db_dir: Directory containing `.db` files.
    :param target_dir: Directory where matching `.db` files will be moved.
    :param scenario_types: A dictionary of scenario types and their initial counts.
    :param max_per_type: The maximum allowed files to move for each scenario type.
    """
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Dictionary to track how many times each scenario type has been moved
    moved_counts: Dict[str, int] = defaultdict(int)

    # Iterate over all `.db` files in the directory
    for db_file in os.listdir(db_dir):
        if db_file.endswith(".db"):  # Ensure we only process `.db` files
            db_path = os.path.join(db_dir, db_file)
            print(f"Processing {db_path}...")

            # Check if the database contains any of the target scenario types
            move_file = False
            for scenario_type, _ in get_db_scenario_info(db_path):
                if scenario_type in scenario_types:
                    # Calculate remaining moves allowed for this scenario type
                    remaining_moves = max_per_type - scenario_types[scenario_type] - moved_counts[scenario_type]
                    if remaining_moves > 0:
                        moved_counts[scenario_type] += 1  # Increment the move count for this type
                        move_file = True
                        print(f"Scenario type '{scenario_type}' moved {moved_counts[scenario_type]}/{max_per_type - scenario_types[scenario_type]}")
                    else:
                        print(f"Scenario type '{scenario_type}' reached its move limit ({max_per_type - scenario_types[scenario_type]}). Skipping.")

            # Move the file if it contains at least one valid scenario type
            if move_file:
                target_path = os.path.join(target_dir, db_file)
                if not os.path.exists(target_path):  # Avoid overwriting files
                    shutil.move(db_path, target_path)
                    print(f"Moved {db_path} to {target_path}")
                else:
                    print(f"File {db_file} already exists in {target_dir}, skipping.")

    print(f"Total moved counts: {dict(moved_counts)}")

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

if __name__ == "__main__":
    # Use NUPLAN_DATA_ROOT environment variable
    db_directory = os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/trainval")
    # db_directory = os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/test")
    # Aggregate scenario counts across all `.db` files
    
    scenario_types = {'accelerating_at_crosswalk':30,'accelerating_at_traffic_light_with_lead':221, 'behind_bike':310,'behind_pedestrian_on_driveable':45,
    'changing_lane_to_left':18,'following_lane_with_lead':370, 'high_magnitude_jerk':12, 'near_multiple_pedestrians':248,
    'starting_protected_noncross_turn':39, 'starting_straight_stop_sign_intersection_traversal':385,
    'starting_straight_traffic_light_intersection_traversal':23,
    'starting_unprotected_noncross_turn':408,
    'stopping_at_stop_sign_no_crosswalk':160,
    'stopping_at_stop_sign_without_lead':479,
    'stopping_at_traffic_light_without_lead':365,
    'traversing_narrow_lane':12,
    }

    target_dir =  os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/resample")
    max_scenario_types = 500
    move_scenarios(db_directory, target_dir, scenario_types, max_scenario_types)
    # print("\nMove Scenario Counts:")
    total_scenario_counts = aggregate_scenario_counts(db_directory)
    # Print results
    print("\nAggregated Scenario Counts:")
    for scenario_type, count in sorted(total_scenario_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"Scenario Type: {scenario_type}, Total Count: {count}")

    print(f"\nTotal Scenario Count: {total_count(total_scenario_counts)}")
    # Save to YAML
    output_yaml_path = "update_trainval_scenario_counts.yaml"
    save_to_yaml(total_scenario_counts, output_yaml_path)