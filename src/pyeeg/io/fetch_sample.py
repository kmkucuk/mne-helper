
from dotenv import load_dotenv
import os

def fetch_sample_file(datatype = 'EDF'):
    """Loads the sample data with the given data type"""    
    load_dotenv()
    print(f"Sampe file is an {datatype} file")
    return  os.getenv(f"{datatype}_TEST_FILE")
    