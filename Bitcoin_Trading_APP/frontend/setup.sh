#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y python3-dev build-essential

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt 