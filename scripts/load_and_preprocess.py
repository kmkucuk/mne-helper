import numpy as np
import mne

from pyeeg.io.loader import read_raw_data
from pyeeg.io.writers import write_metadata
from pyeeg.io.getdir import fetch_sample_file

from pyeeg.utils.logger import logger
from pyeeg.utils.constants import DEFAULT_SEGMENTATION_WINDOW

def create_epoch_dict(time_window=DEFAULT_SEGMENTATION_WINDOW) -> dict:
    """
    Creates a template dictionary with metadata fields

    Args:
        time_window (array-like) shape (2, 1): Array specifying epoch time windows [tmin, tmax]

    Returns:
        epoch_dict (dict)
    """    
    epoch_dict = {}
    epoch_dict['metadata'] = []
    epoch_dict['events'] = []
    epoch_dict['event_id'] = []
    epoch_dict['selected_events'] = []
    epoch_dict['time_window'] = time_window
    return epoch_dict

def get_meta_data(raw_data, epoch_dict) -> dict:
    """
    Returns metadata and events of raw_data

    Args:
        raw_data (mne.raw): mne raw data object
        epoch_dict (dict): dictionary with metadata keys

    Returns:
        epoch_dict (dict): fills metadata, events, and event_id
    """
    if epoch_dict['time_window'][0] >= epoch_dict['time_window'][1]:
        logger.error(f"Invalid time window make sure first element is smaller than the second element {epoch_dict['time_window']}")
        return None
    else:
        all_events, all_event_id = mne.events_from_annotations(raw_data)

        metadata, events, event_id = mne.epochs.make_metadata(
            events=all_events,
            event_id=all_event_id,
            tmin=epoch_dict['time_window'][0],
            tmax=epoch_dict['time_window'][1],
            sfreq=raw_data.info['sfreq'],
        )
        print(f"\nEvent info extracted from {epoch_dict['time_window'][0]} to {epoch_dict['time_window'][1]} seconds.")
        epoch_dict['metadata'] = metadata
        epoch_dict['events'] = events
        epoch_dict['event_id'] = event_id
        return epoch_dict

def show_event_list(epoch_dict):    
    """
    Shows a list of mne metadata events with counts

    Args:
        epoch_dict (dict): dictionary containing metadata of raw_data         

    Returns:
        Nothing
    """
    if not isinstance(epoch_dict['event_id'], dict):
        logger.critical("event_id is not dict type")
        raise TypeError("event_id must be dict type")
    if not isinstance(epoch_dict['events'], np.ndarray):
        logger.critical("events is not np.ndarray type")
        raise TypeError("events list must be np.ndarray type")
    
    if len(epoch_dict['event_id']) > 0:
        print("Event\tCount")
        for i, (evntkey, evntval) in enumerate(epoch_dict['event_id'].items()):
            print(f"({i+1}) {evntkey}\t{np.count_nonzero(epoch_dict['events'][:, -1] == evntval)}")        
    elif len(event_id) < 1 and len(events) > 0:
        logger.error("Events don't have corresponding IDs in the data, cannot show event list.")
        return None
    elif len(events) < 1:
        logger.error("There are no events in the data.")
        return None
    else:
        logger.error("Unknown error related to event list in the data")
        return None

def select_event(epoch_dict) -> dict:
    """
    Returns epoch_dict after registering selected events for epoching

    Args:
        epoch_dict (dict): dictionary with metadata of mne raw data

    Returns:
        epoch_dict (dict): fills selected_events
    """    
    print("\nPlease type in the numbers of events you want to segment the data with (e.g. 23 or 2 or 2345)")
    show_event_list(epoch_dict)
    event_keys = list(epoch_dict['event_id'].keys())
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
        selected_events[event_keys[i]] = epoch_dict['event_id'][event_keys[i]]
        print(event_keys[i])       
    print("*********")
    
    epoch_dict['selected_events'] = selected_events
    return epoch_dict

def segment_data_markers(raw_data, epoch_dict) -> mne.epoch.Epochs:
    """
    Creates epoched data using selected events in epoch_dict

    Args:
        raw_data (mne.raw): mne raw data object
        epoch_dict (dict): dictionary with metadata of mne raw data

    Returns:
        mne.epoch.Epochs object
    """      
    return mne.Epochs(raw_data, 
                      epoch_dict['events'], 
                      event_id=epoch_dict['selected_events'], 
                      tmin=epoch_dict['time_window'][0], 
                      tmax=epoch_dict['time_window'][1], 
                      preload=True)

def plot_segmented_data(epochs, epoch_dict):
    """
    Plots selected epochs of raw data

    Args:
        epochs (mne.epochs.Epoch): Object containing epoched data
        epoch_dict (dict): dictionary with metadata of mne raw data

    Returns:
        fig (MNEFigure)
    """      
    if isinstance(epochs, mne.epochs.Epochs):
        fig = epochs.plot(events=epoch_dict['events'])
        return fig
    else:
        logger.error("'epochs' is not a mne.epochs.Epochs instance.")
        raise TypeError("'epochs' is not a mne.epochs.Epochs instance.")

def segment_data_continuous(raw_data, epoch_dict):
    pass



sample_file = fetch_sample_file('BRAINVISION')
raw_data = read_raw_data(sample_file)
raw_data.filter(l_freq=0.1, h_freq=40)
epoch_dict = create_epoch_dict()
epoch_dict = get_meta_data(raw_data, epoch_dict)
epoch_dict = select_event(epoch_dict)
epochs = segment_data_markers(raw_data, epoch_dict)
fig = plot_segmented_data(epochs, epoch_dict)
freq_avg = epochs['Stimulus/Frequent'].average()
rare_avg = epochs['Stimulus/Rare'].average()
rare_avg.plot_topomap(times=[0.1, 0.2, 0.3], average=0.05)
rare_avg.plot_joint()

# auto-create metadata:
# this also returns a new events array and an event_id dictionary. we'll see
# later why this is important
metadata1, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info['sfreq'],
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
    sfreq=raw_data.info['sfreq'],
    row_events=row_events,
)

write_metadata(metadata2, 'metadata2')

keep_first = "response"
metadata3, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info['sfreq'],
    row_events=row_events,
    keep_first=keep_first,
)

write_metadata(metadata3, 'metadata3')

keep_first = ['stimulus","response']
metadata4, events, event_id = mne.epochs.make_metadata(
    events=all_events,
    event_id=all_event_id,
    tmin=metadata_tmin,
    tmax=metadata_tmax,
    sfreq=raw_data.info['sfreq'],
    row_events=row_events,
    keep_first=keep_first,
)

write_metadata(metadata4, 'metadata4')
# extract events
a=0