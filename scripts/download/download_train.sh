#!/bin/bash

# Array of city datasets
cities=("boston" "pittsburgh" "singapore")

# Download, unzip, and remove zip files for each city
# for city in "${cities[@]}"; do
#     echo "Processing $city..."
#     wget https://motional-nuplan.s3.amazonaws.com/public/nuplan-v1.1/nuplan-v1.1_train_${city}.zip
#     unzip nuplan-v1.1_train_${city}.zip
#     rm nuplan-v1.1_train_${city}.zip
#     rm LICENSE
# done

for split in {1..6}; do
    wget https://motional-nuplan.s3.amazonaws.com/public/nuplan-v1.1/nuplan-v1.1_train_vegas_${split}.zip
    unzip nuplan-v1.1_train_vegas_${split}.zip
    rm nuplan-v1.1_train_vegas_${split}.zip
    rm LICENSE
done 