import mne._fiff
from mne._fiff._digitization import DigPoint
from pyeeg.io.loader import read_raw_data
from pyeeg.io.fetch_sample import fetch_sample_file
import mne
import numpy as np
import math
import logging
from mne._fiff.constants import FIFF
from pyeeg.utils.constants import NON_STANDARD_CHANNEL_TYPES
from mne._fiff.constants import CHANNEL_LOC_ALIASES

logger = logging.getLogger(__name__)
handler = logging.FileHandler('test.log')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def check_position_match(montage_pos, data_pos) -> bool:      
    """Checks if two positions match on all coordinates.

    Returns
    -------
    bool 
    """      
    if any(np.isnan(data_pos)):
            logger.warning(f'Channel position coordinates include a NAN value {data_pos}')    
            return False
    else:
        position_match = True
        for mpos, dpos in zip(montage_pos, data_pos):    
                if math.copysign(1, mpos) == 1:
                    position_match = position_match and ((dpos <= mpos * 1.015) and (dpos >= mpos * 0.985))
                else:
                    position_match = position_match and ((dpos >= mpos * 1.015) and (dpos <= mpos * 0.985))
                if not position_match:
                     break
        return position_match
    
def check_position_similarity(montage_pos, data_pos, std_out=False) -> list:        
    """Get similarity ratios between montage electrode positions and data positions.

    Returns
    -------
    list or ndarray: standardized or direct ratio of difference in position values    
    """
    empty_pos = np.empty((3))
    if any(np.isnan(data_pos)):
        logger.warning(f'Channel position coordinates include a NAN value {data_pos}')    
        return empty_pos.fill(np.nan)
    elif isinstance(data_pos, np.ndarray or list) and isinstance(montage_pos, np.ndarray or list):        
        if std_out:
             divisor = 2
        else:
             divisor = data_pos
        return np.absolute(np.divide(np.subtract(data_pos, montage_pos), divisor))
    else:
        logger.error(f"Position types are not fit for similartiy estimation: data-type {type(data_pos)}, montage-type {type(montage_pos)}")
        return empty_pos.fill(np.nan)
    

def get_chanlocs(data_info):    
    """ Extract only EEG channel names and locations.

    Returns
    -------
    dict: {channel names:  location}
    """
    if "chs" not in data_info:
        logger.error(f"data.info does not have ''chs'' key")
        return None
    data_chan_info = {}    
    for dchan in data_info['chs']:            
        if dchan['kind'] == FIFF.FIFFV_EEG_CH:
            data_chan_info[dchan['ch_name']] = dchan['loc'][0:3]
            if any(np.isnan(dchan['loc'][0:3])):
                 logger.warning(f"Channel position values are NAN at {dchan['ch_name']} electrode")
    return data_chan_info 

def adjust_nonstd_chans(data_info):
    indx = 0
    for dchan in data_info['chs']:
        if dchan['ch_name'] in NON_STANDARD_CHANNEL_TYPES:
             data_info['chs'][indx]['kind'] = NON_STANDARD_CHANNEL_TYPES[dchan['ch_name']]
        indx += 1
    return data_info

def adjust_nonstd_chans_dig(data_info):
     # adjusted nonstd channels 
     # find in dig by locations
     # change electrode kind

     # if chan does not exist in dig, add the chan
    for cchan in data_info['chs']:
        if cchan['ch_name'] in NON_STANDARD_CHANNEL_TYPES:
            digindx = -1
            for dchan in data_info['dig']:
                digindx += 1
                pos_match = check_position_match(dchan['r'], cchan['loc'][0:3])
                if pos_match:
                    data_info['dig'][digindx]['kind'] = cchan['kind']
                    break                     
            if not pos_match:
                data_info['dig'].append(DigPoint(data_info['dig'][digindx].copy()))
                data_info['dig'][-1]['r'] = cchan['loc'][0:3]       
    return data_info
     
def get_cardinal_chan_count(data_info):
        count = 0 
        for digi in data_info['dig']:
            if digi['kind'] == FIFF.FIFFV_POINT_CARDINAL:
                count += 1
        return count

all_montage = ['standard_1005', 'standard_1020', 'standard_alphabetic', 'standard_postfixed', 'standard_prefixed', 'standard_primed', 'biosemi16', 'biosemi32', 'biosemi64', 'biosemi128', 'biosemi160', 'biosemi256', 'easycap-M1', 'easycap-M10', 'easycap-M43', 'EGI_256', 'GSN-HydroCel-32', 'GSN-HydroCel-64_1.0', 'GSN-HydroCel-65_1.0', 'GSN-HydroCel-128', 'GSN-HydroCel-129', 'GSN-HydroCel-256', 'GSN-HydroCel-257', 'mgh60', 'mgh70', 'artinis-octamon', 'artinis-brite23', 'brainproducts-RNP-BA-128']
sample_file = fetch_sample_file('EEGLAB')
raw_data = read_raw_data(sample_file)
raw_data.load_data()
raw_data.info = adjust_nonstd_chans(raw_data.info)
raw_data.info = adjust_nonstd_chans_dig(raw_data.info)
data_chan_info = get_chanlocs(raw_data.info)

def estimate_montage_similarity(data_chan_info, montage_name):
    chdict = {} 
    mchpos = montage._get_ch_pos()    
    chdict[montage_name] = {}
    chdict[montage_name]['changed_names'] = dict(zip(list(data_chan_info.keys()), [''] * len(list(data_chan_info.keys()))))
    chdict[montage_name]['changed_positions'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 

    


def main():
    # #of position difference & #of channel count difference
    chdict = {}
    for mname in all_montage:
        montage = mne.channels.make_standard_montage(mname)
        
        mchpos = montage._get_ch_pos()    
        chdict[mname] = {}
        chdict[mname]['changed_names'] = dict(zip(list(data_chan_info.keys()), [''] * len(list(data_chan_info.keys()))))
        chdict[mname]['changed_positions'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys()))))            
        pos_difference = 0
        for ch_name, pos_val in data_chan_info.items():               
                position_match = False
                if ch_name in montage.ch_names:                    
                    chdict[mname]['changed_names'][ch_name] = ch_name
                    position_match = check_position_match(mchpos[ch_name], pos_val)
                    if position_match:                        
                        chdict[mname]['changed_positions'][ch_name] = mchpos[ch_name]     
                    else:
                        chdict[mname]['changed_positions'][ch_name] = {"error": f"Positions did not match data: {pos_val}, montage: {mchpos[ch_name]}"}     
                        pos_difference += 1
                else:
                    for mchname, mposi in mchpos.items():
                        position_match = check_position_match(mposi, pos_val)                      
                        if position_match:
                            chdict[mname]['changed_names'][ch_name] = mchname
                            chdict[mname]['changed_positions'][ch_name] = mposi
                            break
                    if not position_match:
                            pos_difference +=1
                            chdict[mname]['changed_positions'][ch_name] = {"error": f"No matching positions were found {pos_val}"}     
        chdict[mname]["position_difference"] = pos_difference



raw_data.rename_channels(chdict['biosemi32']['changed_names'])
raw_data.set_montage('biosemi32')
raw_data.plot(block=True)
a=0

