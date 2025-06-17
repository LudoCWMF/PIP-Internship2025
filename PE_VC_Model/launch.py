import subprocess
import webbrowser
import time
import sys
import os

# Path to your Streamlit app
APP_PATH = os.path.join(os.path.dirname(__file__), 'app.py')

# Start Streamlit app as a subprocess
proc = subprocess.Popen([
    sys.executable, '-m', 'streamlit', 'run', APP_PATH
])

# Wait a moment for the server to start
url = 'http://localhost:8501'
time.sleep(2)  # You may increase this if your machine is slow

# Open the web browser
webbrowser.open(url)

# Wait for the Streamlit process to finish
proc.wait() 