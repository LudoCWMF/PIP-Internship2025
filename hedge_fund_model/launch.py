import subprocess
import sys
import os

def launch_app():
    """Launch the Streamlit app."""
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to app.py
    app_path = os.path.join(current_dir, 'app.py')
    
    # Launch the Streamlit app
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path])

if __name__ == '__main__':
    launch_app() 