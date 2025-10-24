import os
from pyeeg.io.eeglab import read_eeglab
from dotenv import load_dotenv


def eeglab_test():
    """Test function for EDF file reading functionality."""
    # Load environment variables from .env file (if it exists)
    load_dotenv()
    FILE_TYPE = ["EEGLAB .set/.fdt"]
    # Set default values for environment variables
    RAW_DATA_DIR = os.getenv("RAW_DATA_DIR")
    EEG_SAMPLING_RATE = float(os.getenv("EEG_SAMPLING_RATE"))
    EEG_LOW_PASS = float(os.getenv("EEG_LOW_PASS"))
    EEG_HIGH_PASS = float(os.getenv("EEG_HIGH_PASS"))
    EEGLAB_TEST_FILE = os.getenv("EEGLAB_TEST_FILE")

    print(f"Testing {FILE_TYPE} file: {EEGLAB_TEST_FILE}")
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print(f"EEG sampling rate: {EEG_SAMPLING_RATE}")
    print(f"EEG frequency range: {EEG_LOW_PASS} - {EEG_HIGH_PASS} Hz")
    
    try:
        # Test reading the EDF file
        raw_data = read_eeglab(EEGLAB_TEST_FILE)
        print(f"Successfully loaded {FILE_TYPE} file!")
        print(f"Number of channels: {raw_data.info['nchan']}")
        print(f"Sampling frequency: {raw_data.info['sfreq']} Hz")
        print(f"Channel names: {raw_data.ch_names[:5]}...")  # Show first 5 channels
        return True
    except Exception as e:
        print(f"Error reading {FILE_TYPE} file: {e}")
        return False


if __name__ == "__main__":
    eeglab_test()