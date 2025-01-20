import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import torch.nn as nn
from sklearn.mixture import GaussianMixture
from compute_test_features import load_scenario_features, get_array_features, get_ego_features
os.environ['PLANTF'] = '/home/sgwang/planTF'
class EncoderFeatureAnalyzer:
    def __init__(self, dim):
        self.norm = nn.LayerNorm(dim)
        
    def load_encoder_features(self, folder_path):
        encoder_features = []
        
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.pt'):
                file_path = os.path.join(folder_path, file_name)
                try:
                    features = torch.load(file_path)
                    encoder_features.append(features)
                except Exception as e:
                    print(f"Failed to load {file_path}: {e}")

        return encoder_features
    
    def get_ego_features(self, features):
        ego_features = []
        for feature in features:
            feature = feature[:,0]
            ego_features.append(feature)
        return ego_features
    
    def split_and_concat_features(self, features):
        # Convert to tensor
        # Split the tensor into a list of tensors each of size [128]
        all_features = []
        for feature in features:
            split_features = feature.split(1, dim=0)
            split_features = [f.squeeze(0) for f in split_features]
            all_features.extend(split_features)
        # Concatenate all tensors together as [:, 128]
        concatenated_features = torch.stack(all_features)
        return concatenated_features
    
    def get_other_features(self, features):
        other_features = []
        for feature in features:
            feature = feature[:,1:]
            other_features.append(feature)
        return other_features
    
    def compute_mean(self, features):
        means = []
        for feature in features:
            mean = torch.mean(feature, dim=0)
            means.append(mean)
        return means
    
    def compute_std(self, features):
        stds = []
        for feature in features:
            std = torch.std(feature, dim=0)
            stds.append(std)
        return stds
    
    def compute_min(self, features):
        mins = []
        for feature in features:
            min_val = torch.min(feature, dim=0).values
            mins.append(min_val)
        return mins
    
    def compute_max(self, features):
        maxs = []
        for feature in features:
            max_val = torch.max(feature, dim=0).values
            maxs.append(max_val)
        return maxs
    
    def concat_features(self, features):
        concat_features = []
        for feature in features:
            feature = feature.view(-1)
            concat_features.append(feature)
        return concat_features

    def compute_norm(self, features):
        norms = []
        for feature in features:
            encoder_feature = feature.clone().detach().cpu()
            x = self.norm(encoder_feature)
            norms.append(x)
        return norms
    
    def compute_gmm(self, features):
        gmm = GaussianMixture(n_components=2)
        gmm.fit(features)
        return gmm
    
    def calculate_mahalanobis_distance(self,features, new_sample):
        mean = np.mean(features, axis=0)
        cov_matrix = np.cov(features, rowvar=False)
        inv_cov_matrix = np.linalg.inv(cov_matrix)
        mahalanobis_dist = distance.mahalanobis(new_sample, mean, inv_cov_matrix)
        return mahalanobis_dist
    
    
def main():
    dim = 128
    analyzer = EncoderFeatureAnalyzer(dim)
    plantf_path = os.getenv('PLANTF')
    norm_path = os.path.join(plantf_path, 'inference_x')
    norm_features = analyzer.load_encoder_features(norm_path)
    norm_features = analyzer.get_ego_features(norm_features)
    concatenated_features = analyzer.split_and_concat_features(norm_features)
    
    scenario_path = os.path.join(plantf_path, 'encoder_features')
    scenarios =load_scenario_features(scenario_path)
    first_scenario = scenarios[0]
    scenario = list(first_scenario.values())[0]
    array_features = get_array_features(scenario)
    ego_features = get_ego_features(array_features)
    
    for ego_feature in ego_features:
        dist = analyzer.calculate_mahalanobis_distance(concatenated_features, ego_feature)
        print(dist)
        
if __name__ == '__main__':
    main()