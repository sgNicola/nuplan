#!/bin/bash
# Download, unzip, and remove zip files for mini
wget https://d1qinkmu0ju04f.cloudfront.net/public/nuplan-v1.1/nuplan-v1.1_mini.zip
unzip nuplan-v1.1_mini.zip
rm nuplan-v1.1_mini.zip
echo "All downloads and extractions completed!"