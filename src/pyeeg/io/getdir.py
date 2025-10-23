
from dotenv import load_dotenv
import os

def fetch_sample_file(datatype = 'EDF') -> str:
    """Loads the sample data with the given data type"""    
    load_dotenv()
    print(f"Sampe file is an {datatype} file")
    return  os.getenv(f"{datatype}_TEST_FILE")

def find_folder(start_dir=None, target_folder=None) -> str:
    """Finds a folder by going upwards in directory """    
    current_dir = os.path.abspath(start_dir or os.getcwd())

    while True:
        candidate = os.path.join(current_dir, target_folder)
        if os.path.isdir(candidate):
            return candidate

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None

        current_dir = parent_dir

def set_logdir(log_file) -> str:
    """Gets log dir """    
    load_dotenv()
    log_dir = find_folder(target_folder=os.getenv("LOG_DIR"))
    print(f"Found log folder: {log_dir}")
    return log_dir+ f"/{log_file}"

def set_exportdir(export_file) -> str:
    load_dotenv()    
    export_dir = find_folder(target_folder='data') + '/' + os.getenv('EXPORT_DATA_DIR')    
    return export_dir + f"/{export_file}"