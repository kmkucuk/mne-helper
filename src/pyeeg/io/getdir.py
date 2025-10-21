
from dotenv import load_dotenv
import os

def fetch_sample_file(datatype = 'EDF'):
    """Loads the sample data with the given data type"""    
    load_dotenv()
    print(f"Sampe file is an {datatype} file")
    return  os.getenv(f"{datatype}_TEST_FILE")

def find_folder(start_dir=None, target_folder=None):
    # Start from the given directory or the current working directory
    current_dir = os.path.abspath(start_dir or os.getcwd())

    while True:
        # Construct the candidate path
        candidate = os.path.join(current_dir, target_folder)

        # Check if the "log" folder exists here
        if os.path.isdir(candidate):
            return candidate

        # Move one level up
        parent_dir = os.path.dirname(current_dir)

        # If we reach the root without finding it
        if parent_dir == current_dir:
            return None

        current_dir = parent_dir


def set_logdir(log_file):
    """Gets log dir """    
    load_dotenv()
    log_dir = find_folder(target_folder=os.getenv("LOG_DIR"))
    print(f"Found folder {log_dir}")
    return log_dir+ f"/{log_file}"
