import os
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.stats import entropy
from omegaconf import DictConfig  # Assuming DictConfig is from `omegaconf`

class ComputePostScore:
    def __init__(self, df: pd.DataFrame, cfg: DictConfig):
        self.df = df
        self.post_score = cfg.post_score  # Config key for score column

    def get_energy_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute raw ood_score as the log sum of exponentials for each array
            raw_ood_score = [np.log(np.sum(np.exp(j))) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_msp_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the maximum softmax probability for each array
            raw_score = [np.max(F.softmax(torch.tensor(x), dim=0).numpy()) for x in i]
            ood_score.append(raw_score)
        self.df['score'] = ood_score
        return self.df

    def get_mean_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the mean for each array
            raw_ood_score = [np.mean(j) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_exp_mean_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the exponential mean for each array
            raw_ood_score = [np.log(np.mean(np.exp(j))) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_var_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the variance for each array
            raw_ood_score = [np.var(j) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_plus_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the sum of variance and mean for each array
            raw_ood_score = [(np.var(j) + np.mean(j)) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_min_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute the difference between max and mean for each array
            raw_ood_score = [(np.max(j) - np.mean(j)) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def get_entropy_score(self) -> pd.DataFrame:
        ood_score = []
        for i in self.df[self.post_score]:
            # Compute entropy for each array
            raw_ood_score = [entropy(j) for j in i]
            ood_score.append(raw_ood_score)
        self.df['score'] = ood_score
        return self.df

    def calculate_average_ood_score(self) -> pd.DataFrame:
        # Compute mean of scores
        self.df['ood_score_avg'] = self.df['score'].apply(lambda x: np.mean(x))
        return self.df

    def calculate_max_ood_score(self) -> pd.DataFrame:
        # Compute max of scores
        self.df['ood_score_max'] = self.df['score'].apply(lambda x: np.max(x))
        return self.df

    def calculate_min_ood_score(self) -> pd.DataFrame:
        # Compute min of scores
        self.df['ood_score_min'] = self.df['score'].apply(lambda x: np.min(x))
        return self.df

    def calculate_std_ood_score(self) -> pd.DataFrame:
        # Compute standard deviation of scores
        self.df['ood_score_std'] = self.df['score'].apply(lambda x: np.std(x))
        return self.df

    def calculate_var_ood_score(self) -> pd.DataFrame:
        # Compute variance of scores
        self.df['ood_score_var'] = self.df['score'].apply(lambda x: np.var(x))
        return self.df


if __name__ == "__main__":
# Initialize the ReportProcessor class
    CONFIG_PATH = 'config'
    CONFIG_NAME = 'runner_report'
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    hydra.initialize(config_path=CONFIG_PATH)
    cfg = hydra.compose(config_name=CONFIG_NAME)
    processor = ReportProcessor(
        cfg
    )
    # Read and merge all data
    result_df = processor.read_metric_reports()
