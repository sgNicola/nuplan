import yaml
import pandas as pd


def load_yaml(file_path: str) -> pd.DataFrame:
    """
    Load a YAML file into a Pandas DataFrame.
    :param file_path: Path to the YAML file.
    :return: DataFrame with columns 'Scenario Type' and 'Count'.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return pd.DataFrame(data.items(), columns=["Scenario Type", "Count"])


def get_top_70_percent(data: pd.DataFrame):
    """
    Get the top 70% of scenarios based on cumulative count.
    :param data: DataFrame with 'Scenario Type' and 'Count' columns.
    :return: DataFrame containing the top 70% scenarios and their total count.
    """
    # Sort by count in descending order
    data = data.sort_values(by="Count", ascending=False).reset_index(drop=True)
    
    # Calculate cumulative percentage
    total_count = data["Count"].sum()
    data["Cumulative Count"] = data["Count"].cumsum()
    data["Cumulative Percentage"] = data["Cumulative Count"] / total_count

    # Filter top 70%
    top_70_data = data[data["Cumulative Percentage"] <= 0.9]
    top_70_total = top_70_data["Count"].sum()

    return top_70_data, top_70_total


def compare_scenarios(train_data: pd.DataFrame, test_data: pd.DataFrame):
    """
    Compare the train and test scenarios to find similarities and differences.
    :param train_data: DataFrame containing training scenarios.
    :param test_data: DataFrame containing testing scenarios.
    :return: Sets of common and unique scenario types.
    """
    train_types = set(train_data["Scenario Type"])
    test_types = set(test_data["Scenario Type"])

    # Find common and unique scenario types
    common_types = train_types.intersection(test_types)
    unique_to_train = train_types - test_types
    unique_to_test = test_types - train_types

    return common_types, unique_to_train, unique_to_test


def calculate_proportions(data: pd.DataFrame):
    """
    Calculate the total count and the proportion of each scenario type.
    :param data: DataFrame with 'Scenario Type' and 'Count' columns.
    :return: Total count and DataFrame with proportions.
    """
    total_count = data["Count"].sum()
    data["Proportion"] = data["Count"] / total_count
    return total_count, data


# Main analysis function
def analyze_scenarios(train_file: str, test_file: str):
    # Load YAML files
    train_data = load_yaml(train_file)
    test_data = load_yaml(test_file)

    # 1. Get top 70% scenarios for train and test data
    train_top_70, train_top_70_total = get_top_70_percent(train_data)
    test_top_70, test_top_70_total = get_top_70_percent(test_data)

    print("Top 70% Train Scenarios:")
    print(train_top_70)
    print(f"Total Count (Train, Top 70%): {train_top_70_total}\n")
    
    print("Top 70% Test Scenarios:")
    print(test_top_70)
    print(f"Total Count (Test, Top 70%): {test_top_70_total}\n")

    # 2. Compare train and test scenarios
    common_types, unique_to_train, unique_to_test = compare_scenarios(train_data, test_data)

    print("\nUnique Scenario Types (Train):")
    print(unique_to_train)
    print("\nUnique Scenario Types (Test):")
    print(unique_to_test)
    print()

    # 3. Calculate total counts and proportions
    train_total, train_data_with_proportions = calculate_proportions(train_data)
    test_total, test_data_with_proportions = calculate_proportions(test_data)

    print("Train Data with Proportions:")
    print(train_data_with_proportions)
    print(f"Total Count (Train): {train_total}")
    print("\nTest Data with Proportions:")
    print(test_data_with_proportions)
    print(f"Total Count (Test): {test_total}")

    # Calculate overall proportions
    grand_total = train_total + test_total
    train_percentage = train_total / grand_total
    test_percentage = test_total / grand_total

    print("\nOverall Statistics:")
    print(f"Train Total: {train_total} ({train_percentage:.2%})")
    print(f"Test Total: {test_total} ({test_percentage:.2%})")

    return {
        "train_top_70": train_top_70,
        "test_top_70": test_top_70,
        "common_types": common_types,
        "unique_to_train": unique_to_train,
        "unique_to_test": unique_to_test,
        "train_data_with_proportions": train_data_with_proportions,
        "test_data_with_proportions": test_data_with_proportions,
        "train_total": train_total,
        "test_total": test_total,
        "train_percentage": train_percentage,
        "test_percentage": test_percentage
    }


# Example usage
if __name__ == "__main__":
    # Example YAML file paths (replace with actual file paths)
    train_file = "train_scenarios.yaml"
    test_file = "test_scenarios.yaml"
    results = analyze_scenarios(train_file, test_file)