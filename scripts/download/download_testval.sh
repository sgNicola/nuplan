#!/bin/bash
# Download,unzip, and remove zip files 
files=("val" "test")

for file in "${files[@]}"; do
    echo "Downloading $file..."
    wget https://motional-nuplan.s3.amazonaws.com/public/nuplan-v1.1/nuplan-v1.1_${file}.zip
    unzip nuplan-v1.1_${file}.zip
    rm nuplan-v1.1_${file}.zip
done

echo "All downloads and extractions completed!"