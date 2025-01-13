import yaml
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict
import os

# Custom constructor for defaultdict
def construct_defaultdict(loader, node):
    args, kwargs = loader.construct_sequence(node)
    return defaultdict(*args, **kwargs)

def load_scenario_counts(yaml_file: str) -> defaultdict:
    with open(yaml_file, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data

def plot_scenario_distribution(scenario_counts: dict):
    # Convert to DataFrame
    scenario_types = list(scenario_counts.keys())
    counts = list(scenario_counts.values())
    data = pd.DataFrame({
        "Scenario Type": scenario_types,
        "Count": counts
    })

    # Sort by count
    data = data.sort_values(by="Count", ascending=False)

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x="Count", y="Scenario Type", data=data, palette="viridis")
    plt.title("Distribution of Scenario Types", fontsize=16)
    plt.xlabel("Count", fontsize=14)
    plt.ylabel("Scenario Type", fontsize=14)
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    yaml_file = "scenario_counts.yaml"
    total_scenario_counts = load_scenario_counts(yaml_file)
    plot_scenario_distribution(total_scenario_counts)