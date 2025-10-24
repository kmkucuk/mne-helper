import mne
import numpy as np
import logging

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
    logger.critical("I'm here bitch")
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
    elif len(epoch_dict['event_id']) < 1 and len(epoch_dict['events']) > 0:
        logger.error("Events don't have corresponding IDs in the data, cannot show event list.")
        return None
    elif len(epoch_dict['events']) < 1:
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

def segment_data_markers(raw_data, epoch_dict):
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

