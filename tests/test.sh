#!/bin/bash

# Navigate to the module directory
cd ../

# Remove __pycache__ folders
find . -type d -name "__pycache__" -exec rm -rf {} +

# Reinstall the module
pip install --upgrade --force-reinstall .

# Navigate to the tests directory and run the test script
cd tests
python3 -m unittest