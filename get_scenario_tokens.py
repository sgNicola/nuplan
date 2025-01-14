import sqlite3
import os
from typing import Dict, List, Generator
from nuplan.database.nuplan_db.nuplan_scenario_queries import (
    get_lidarpc_tokens_with_scenario_tag_from_db,
    get_sensor_data_token_timestamp_from_db,
    get_sensor_token_map_name_from_db,
)
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


def execute_many(query_text: str, query_parameters: Any, db_file: str) -> Generator[sqlite3.Row, None, None]:
    """
    Runs a query with the provided arguments on a specified Sqlite DB file.
    This query can return any number of rows.
    :param query_text: The query to run.
    :param query_parameters: The parameters to provide to the query.
    :param db_file: The DB file on which to run the query.
    :return: A generator of rows emitted from the query.
    """
    # Caching a connection saves around 600 uS for local databases.
    # By making it stateless, we get isolation, which is a huge plus.
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(query_text, query_parameters)

        for row in cursor:
            yield row
    finally:
        cursor.close()
        connection.close()

def get_scenario_info_from_db(db_file: str) -> Dict[str, List[str]]:
    """
    Get the scenario types and their corresponding scenario tokens from a single database file.
    :param db_file: Path to the SQLite database file.
    :return: A dictionary where keys are scenario types and values are lists of scenario tokens.
    """
    query = """
    SELECT type AS type, token
    FROM scenario_tag;
    """

    scenario_info = {}

    for row in execute_many(query, (), db_file):
        scenario_type = row["type"]
        token = row["token"].hex()

        # Add scenario token to the appropriate scenario type
        if scenario_type not in scenario_info:
            scenario_info[scenario_type] = []
        scenario_info[scenario_type].append(token)

    return scenario_info

def get_scenario_info_from_all_dbs(db_dir: str, db_files: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Get scenario types and tokens from all `.db` files in the specified directory.
    :param db_dir: Directory containing the database files.
    :param db_files: List of `.db` files to process.
    :return: A nested dictionary where keys are database file names and values are dictionaries
             with scenario types and corresponding tokens.
    """
    all_scenario_info = {}

    for db_file in db_files:
        db_path = os.path.join(db_dir, db_file)
        if os.path.isfile(db_path) and db_file.endswith(".db"):
            print(f"Processing file: {db_file}")
            scenario_info = get_scenario_info_from_db(db_path)
            all_scenario_info[db_file] = scenario_info

    return all_scenario_info

# Example usage
if __name__ == "__main__":
    # Directory containing the `.db` files
    db_directory = os.path.join(os.environ["NUPLAN_DATA_ROOT"], "nuplan-v1.1/trainval")
    # List of `.db` files to process (could be filtered from os.listdir if needed)
    db_files = [file for file in os.listdir(db_directory) if file.endswith(".db")]
    # Get scenario information from all `.db` files
    all_scenarios = get_scenario_info_from_all_dbs(db_directory, db_files)

    # # # Print the results
    for db_file, scenario_data in all_scenarios.items():
        print(f"\nDatabase file: {db_file}")
        for scenario_type, tokens in scenario_data.items():
            print(f"  Scenario Type: {scenario_type}")
            print(f"    Tokens: {tokens}")