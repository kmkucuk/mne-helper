from pyeeg.utils.constants import NON_STANDARD_CHANNEL_TYPES, MNE_DEFAULT_MONTAGES, INVALID_POS_SCORE
from pyeeg.utils.logger import logger
from mne._fiff._digitization import DigPoint
from mne.channels import make_standard_montage
from mne._fiff.constants import FIFF
import mne
import numpy as np
import math


def check_position_match(montage_pos, data_pos) -> bool:      
    """Checks if two positions match on all coordinates.

    Returns
    -------
    bool 
    """      
    if any(np.isnan(data_pos)):
            logger.info(f'Channel position coordinates include a NAN value {data_pos}')    
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
    
def check_pos_distance(montage_pos, data_pos) -> float:        
    """Get position difference between montage electrode and data electrode positions.

    Returns
    -------
    float: distance between two vectors
    """
    if any(np.isnan(data_pos)):
        logger.info(f'Channel position coordinates include a NAN value {data_pos}')    
        return np.nan
    elif isinstance(data_pos, np.ndarray or list) and isinstance(montage_pos, np.ndarray or list):        
        return np.linalg.norm(data_pos - montage_pos)
    else:
        logger.info(f"Position types are not fit for similartiy estimation: data-type {type(data_pos)}, montage-type {type(montage_pos)}")
        return np.nan
    

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
                 logger.info(f"Channel position values are NAN at {dchan['ch_name']} electrode")
    return data_chan_info 

def adjust_chan_kind(data_info):
    data_info = adjust_nonstd_chans(data_info)
    data_info = adjust_nonstd_chans_dig(data_info)
    return data_info

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
     
def get_cardinal_chan_count(data_info) -> int:
        count = 0 
        for digi in data_info['dig']:
            if digi['kind'] == FIFF.FIFFV_POINT_CARDINAL:
                count += 1
        return count

def create_position_dict(data_chan_info) -> dict:
    """Initializes a position dict 
    :param data_chan_info: mne.raw.info instance (info of your raw_data)
    Returns
    -------
    dict
    """ 
    loc_position_dict = {}      
    for montage_name in MNE_DEFAULT_MONTAGES:
           
        loc_position_dict[montage_name] = {}
        loc_position_dict[montage_name]['chan_names'] = dict(zip(list(data_chan_info.keys()), [''] * len(list(data_chan_info.keys()))))
        loc_position_dict[montage_name]['chan_positions'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_position_dict[montage_name]['chan_position'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_position_dict[montage_name]['position_score'] = []
        loc_position_dict[montage_name]['total_position_score'] = []
        loc_position_dict[montage_name]['invalid'] = False      

    return loc_position_dict


def position_pipeline(data_chan_info, position_method="position") -> dict:
    loc_position_dict = create_position_dict(data_chan_info) 
    for montage_name in MNE_DEFAULT_MONTAGES:
        if position_method == "position":
            loc_position_dict = position_matching_position(data_chan_info, montage_name, loc_position_dict)
        elif position_method == "channel_name":
            loc_position_dict = name_matching_position(data_chan_info, montage_name, loc_position_dict)
        else:
            logger.critical(f"Wrong position method {position_method}, please enter a valid method ''position'' or ''channel_name''")
            raise ValueError("Wrong position method")
    return loc_position_dict
    
def name_matching_position(data_chan_info, montage_name, loc_position_dict) -> dict:
    montage = make_standard_montage(montage_name)    
    mchpos = montage._get_ch_pos()    
    for ch_name, pos_val in data_chan_info.items():          
        empty_pos = np.empty((3))
        empty_pos.fill(np.nan)            
        if ch_name in montage.ch_names:           
            ch_reg = ch_name
            ch_pos = mchpos[ch_name]            
            position_score = check_pos_distance(mchpos[ch_name], pos_val)
        else:
            ch_reg = ch_name
            ch_pos = empty_pos              
            position_score = empty_pos

        loc_position_dict[montage_name]['chan_names'][ch_name] = ch_reg
        loc_position_dict[montage_name]['chan_positions'][ch_name] = ch_pos 
        loc_position_dict[montage_name]['chan_position'][ch_name] = position_score

    loc_position_dict[montage_name]['position_score'] = []
    loc_position_dict[montage_name]['total_position_score'] = []
    loc_position_dict[montage_name]['invalid'] = False
    return loc_position_dict

def position_matching_position(data_chan_info, montage_name, loc_position_dict) -> dict:
    montage = make_standard_montage(montage_name)    
    mchpos = montage._get_ch_pos()        
    mchnames = list(mchpos.keys())
    dchannames = list(data_chan_info.keys())
    position_matrix = np.ones(shape=(len(data_chan_info), len(mchnames)))
    total_sim_score = np.ones(shape=(len(data_chan_info), 1))
    
    for datai in range(0, len(data_chan_info)):
        for montagei in range(0, len(mchnames)):
            position_matrix[datai, montagei] = check_pos_distance(data_chan_info[dchannames[datai]], mchpos[mchnames[montagei]])         

    rows, cols = position_matrix.shape
    for rowi in range(0, rows):
        match_chan_indx = find_min_matrix(position_matrix, rowi)
        if match_chan_indx == None:
            loc_position_dict[montage_name]['invalid'] = True
        else:
            loc_position_dict[montage_name]['chan_names'][dchannames[rowi]] = mchnames[match_chan_indx]
            loc_position_dict[montage_name]['chan_positions'][dchannames[rowi]] = mchpos[mchnames[match_chan_indx]] 
            loc_position_dict[montage_name]['chan_position'][dchannames[rowi]] = position_matrix[rowi, match_chan_indx]     
            total_sim_score[rowi] = position_matrix[rowi, match_chan_indx]

    if loc_position_dict[montage_name]['invalid']:
        loc_position_dict[montage_name]['position_score'] = round(np.mean(total_sim_score) * 100, 5)
    else:
        loc_position_dict[montage_name]['position_score'] = INVALID_POS_SCORE
    loc_position_dict = get_matched_chan_ratio(loc_position_dict, montage_name)
    print(f"\n{montage_name}:\n{loc_position_dict[montage_name]['position_score']}, {loc_position_dict[montage_name]['match_info']}")
    return loc_position_dict

def get_scoreboard(loc_position_dict) -> list:
    score_vector = []
    key_vector = []
    for key, val in loc_position_dict.items():
        score_vector.append(val["position_score"])
        key_vector.append(key)

    ordered_vector = np.sort(score_vector)
    ordered_key = []
    for score in ordered_vector:
        order_index = np.where(score==score_vector)[0][0]
        ordered_key.append(key_vector[order_index])
    
    return ordered_key

def select_best_montage(loc_position_dict, ordered_key, show_n_montages = 5) -> str:
    indx = 1
    for montage_name in ordered_key[0:show_n_montages]:
        print(f"\n ({indx}){montage_name}:\n{loc_position_dict[montage_name]['position_score']}, {loc_position_dict[montage_name]['match_info']}")
        indx += 1
    print(f"\nType in the number of montage you want to select: ")
    while True:
        montage_index = input()
        if montage_index.isnumeric():
            montage_index = int(montage_index)
            montage_index -= 1 # subtract 1 for py indexing
            if montage_index > show_n_montages:
                print(f"\nPlease select between montages between 1 and {show_n_montages}")            
            elif montage_index < 0:
                print(f"\nPlease select a number 1 or above")
            elif loc_position_dict[ordered_key[montage_index]]['position_score'] == INVALID_POS_SCORE:
                print(f"\nMontage you selected is not valid for the data you have, please select another.")
            else:
                break           
        else:
            print(f"\nPlease type in a number, not a string: {montage_index}")

    print(f"\n*********")
    print(f"Selected {ordered_key[montage_index]} montage")
    print(f"\n*********")
    return ordered_key[montage_index]

def find_min_matrix(matrix, start_row=0): 
    min_col = np.argmin(matrix[start_row, :])
    same_min_cols = np.where(matrix[start_row, :]==matrix[start_row, min_col])[0]
    if len(same_min_cols) > 1:
        logger.info("More than one montage channels have the same position for this data channel")
        return None
    else:
        min_row = np.argmin(matrix[:, min_col])
        same_min_rows = np.where(matrix[:, min_col]==matrix[min_row, min_col])[0]
        if len(same_min_rows) > 1:
            logger.info("More than one data channels have the same position for this montage channel")
            return None
        else:                                    
            if start_row == min_row:
                return min_col
            
def get_matched_chan_ratio(position_dict, montage_name):
    dupvals, dupkeys = resolve_duplicates(position_dict, montage_name)
    match_count = len(position_dict[montage_name]['chan_names']) - len(dupkeys)
    position_dict[montage_name]['match_count'] = match_count
    position_dict[montage_name]['match_info'] = f"{match_count}/{len(position_dict[montage_name]['chan_names'])}"
    return position_dict

def remove_unmatched_chans(position_dict, montage_name):
    dupvals, dupkeys = resolve_duplicates(position_dict, montage_name)
    for key in dupkeys:
        del position_dict[montage_name][key]

def resolve_duplicates(position_dict, montage_name):
    vec = []
    for key, val in position_dict[montage_name]['chan_names'].items(): 
        vec.append(val)
    return find_duplicates(vec)

def find_duplicates(array):
    s = set()

    dup = []
    dupindx = []
    indx = 0
    for n in array:
        indx += 1
        if n in s:
            dup.append(n)
            dupindx.append(indx)
        else:
            s.add(n)

    return dup, dupindx