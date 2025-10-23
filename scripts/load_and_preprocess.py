from pyeeg.io.loader import read_raw_data
from pyeeg.io.writers import write_metadata
from pyeeg.io.getdir import fetch_sample_file, find_folder, set_exportdir
from pyeeg.utils.logger import logger
from pyeeg.utils.constants import DEFAULT_SEGMENTATION_WINDOW
import numpy as np
import mne

def describe_data(raw_data, time_window = DEFAULT_SEGMENTATION_WINDOW):
    if time_window[0] >= time_window[1]:
        logger.error(f"Invalid time window make sure first element is smaller than the second element {time_window}")
        return None
    else:
        all_events, all_event_id = mne.events_from_annotations(raw_data)

        metadata, events, event_id = mne.epochs.make_metadata(
            events=all_events,
            event_id=all_event_id,
            tmin=time_window[0],
            tmax=time_window[1],
            sfreq=raw_data.info["sfreq"],
        )
        print(f"\nEvent info extracted from {time_window[0]} to {time_window[1]} seconds.")
        return metadata, events, event_id

def show_event_list(event_id, events):    
    """
    Shows a list of mne metadata events with counts

    Args:
        event_id (dict): dict of event keys and codes
        events (np.ndarray): csv file name.

    Returns:
        Nothing
    """
    if not isinstance(event_id, dict):
        logger.critical("event_id is not dict type")
        raise TypeError("event_id must be dict type")
    if not isinstance(events, np.ndarray):
        logger.critical("events is not np.ndarray type")
        raise TypeError("events list must be np.ndarray type")        
    
    if len(event_id) > 0:
        print("Event\tCount")
        for i, (evntkey, evntval) in enumerate(event_id.items()):
            print(f"({i+1}) {evntkey}\t{np.count_nonzero(events[:, -1] == evntval)}")        
    elif len(event_id) < 1 and len(events) > 0:
        logger.error("Events don't have corresponding IDs in the data, cannot show event list.")
        return None
    elif len(events) < 1:
        logger.error("There are no events in the data.")
        return None
    else:
        logger.error("Unknown error related to event list in the data")
        return None

def select_event(event_id, events):
    print("\nPlease type in the numbers of events you want to segment the data with (e.g. 23 or 2 or 2345)")
    show_event_list(event_id, events)
    event_keys = list(event_id.keys())
    while True:
        selected_index = input()
        if selected_index.isnumeric():
            indices = []
            for chi in selected_index:
                indices.append(int(chi) - 1) # subtract 1 for py indexing            
            
            if max(indices) >= len(event_keys):
                print(f"\nPlease select events between 1 and {len(event_keys)}")            
            elif min(indices) < 0:
                print(f"\nPlease select a number 1 or above")
            else: 
                break           
        elif selected_index == 'e':
            print("Selection cancelled...")
            return False
        else:
            print(f"\nPlease type in a number, not a string: {selected_index}")

    selected_events = {}
    print("\n*********")
    print("Selected events:")
    for i in indices:
        selected_events[event_keys[i]] = event_id[event_keys[i]]
        print(event_keys[i])   
    
    print("*********")
    return selected_events

def segment_data(raw_data, event_key):
    pass

sample_file = fetch_sample_file('BRAINVISION')
raw_data = read_raw_data(sample_file)
raw_data.filter(l_freq=0.1, h_freq=40)
raw_data.plot(start=60)
metadata, all_events, all_event_id = describe_data(raw_data)
selected_events = select_event(all_event_id, all_events)



metadata_tmin, metadata_tmax = 0.0, 1.53


# auto-create metadata:
# this also returns a new events array and an event_id dictionary. we'll see
# later why this is important
metadata1, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info["sfreq"],
)

a=0


write_metadata(metadata1, 'metadata1')
row_events = [
    "stimulus/compatible/target_left",
    "stimulus/compatible/target_right",
    "stimulus/incompatible/target_left",
    "stimulus/incompatible/target_right",
]

metadata2, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info["sfreq"],
    row_events=row_events,
)

write_metadata(metadata2, 'metadata2')

keep_first = "response"
metadata3, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info["sfreq"],
    row_events=row_events,
    keep_first=keep_first,
)

write_metadata(metadata3, 'metadata3')

keep_first = ["stimulus","response"]
metadata4, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info["sfreq"],
    row_events=row_events,
    keep_first=keep_first,
)

write_metadata(metadata4, 'metadata4')
# extract events
a=0