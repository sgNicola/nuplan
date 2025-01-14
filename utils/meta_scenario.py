import pandas as pd


def count_scenario_types(
    file_path, column_name="file_name", output_file=None, scenario_type_index=6, delimiter="/"
):
    """
    Counts the number of occurrences for each scenario_type in a given CSV file.

    Parameters:
        file_path (str): Path to the CSV file.
        column_name (str): Name of the column containing file paths (default: "file_name").
        output_file (str): Path to save the output CSV file with counts (default: None, no file saved).
        scenario_type_index (int): Index of the scenario_type in the file path after splitting (default: 6).
        delimiter (str): Delimiter used in the file path (default: "/").

    Returns:
        pandas.Series: A Series object with scenario_type counts.
    """
    # Read the CSV file
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found. Please check the path.")
    except Exception as e:
        raise ValueError(f"Error reading the CSV file: {e}")

    # Check if the column exists
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the CSV file.")

    # Extract scenario_type
    try:
        df["scenario_type"] = df[column_name].apply(
            lambda x: x.split(delimiter)[scenario_type_index]
        )
    except IndexError:
        raise IndexError(
            f"The index {scenario_type_index} is out of range. Please check the file path structure and index value."
        )

    # Count occurrences of each scenario_type
    scenario_counts = df["scenario_type"].value_counts()

    # Print the counts
    print("Scenario type counts:")
    print(scenario_counts)

    # Save the result to a file if output_file is provided
    if output_file:
        scenario_counts.to_csv(output_file, header=["count"])
        print(f"Counts saved to {output_file}.")

    return scenario_counts


# Example usage
if __name__ == "__main__":
    # Path to the input CSV file
    # file_path = "/home/sgwang/nuplan/exp/InD/metadata/InD_metadata_node_0.csv"  # Replace with your actual file path
    file_path = "/home/sgwang/nuplan/exp/cache_pdm_open/metadata/cache_pdm_open_metadata_node_0.csv"
    # Call the function
    try:
        scenario_counts = count_scenario_types(
            file_path=file_path,
            column_name="file_name",  # Column containing the file paths
            output_file="open_scenario_type_counts.csv",  # Output file path (optional)
            scenario_type_index=7,  # Index of scenario_type in the file path
            delimiter="/"  # Delimiter used in file paths
        )
    except Exception as e:
        print(f"Error: {e}")