#!/bin/bash

# Create directory structure for Lambda Layer
mkdir -p lambda_layer/python

# Install Python packages to the layer directory
pip install -r requirements-lambda.txt -t lambda_layer/python

echo "Lambda Layer created successfully at ./lambda_layer/"
