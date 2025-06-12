import os
import subprocess
import time
import webbrowser
import sys

# Path to your virtual environment's Streamlit
streamlit_cmd = "/Users/ludoferrario/PIP Internship/.venv/bin/streamlit"
frontend_dir = "/Users/ludoferrario/PIP Internship/Bitcoin Trading APP/frontend"

# Change to the frontend directory
os.chdir(frontend_dir)

# Start Streamlit in the background using the venv's streamlit
proc = subprocess.Popen([streamlit_cmd, "run", "app.py"])

# Wait a few seconds for the server to start
time.sleep(3)

# Open the default browser to the Streamlit app
webbrowser.open("http://localhost:8501")

# Wait for Streamlit to finish
proc.wait()