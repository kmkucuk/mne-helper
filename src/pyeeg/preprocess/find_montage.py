import numpy as np
import math

from mne._fiff._digitization import DigPoint
from mne.channels import make_standard_montage
from mne._fiff.constants import FIFF

from pyeeg.utils.constants import NON_STANDARD_CHANNEL_TYPES, MNE_DEFAULT_MONTAGES, INVALID_POS_SCORE
from pyeeg.utils.logger import logger

def check_position_match(montage_pos, data_pos) -> bool:      
    """
    Checks if electrode positions of montage and data match on x, y, z.

    Args:
        montage_pos (array-like) shape (1, 3): Electrode position of montage.
        data_pos (array-like) shape (1, 3): Electrode position of data.

    Returns:
        position_match (bool)
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
    """
    Get distance between montage and data electrode positions.

    Args:
        montage_pos (array-like) shape (1, 3): Electrode position of montage.
        data_pos (array-like) shape (1, 3): Electrode position of data.

    Returns:
        (float): Cartesian distance between two coordinates of shape (1, 3)
    """     
    if any(np.isnan(data_pos)):
        logger.info(f'Channel position coordinates include a NAN value {data_pos}')    
        return np.nan
    elif isinstance(data_pos, np.ndarray or list) and isinstance(montage_pos, np.ndarray or list):        
        return np.linalg.norm(data_pos - montage_pos)
    else:
        logger.info(f"Position types are not fit for similartiy estimation: data-type {type(data_pos)}, montage-type {type(montage_pos)}")
        return np.nan
    

def get_chanlocs(data_info) -> dict | None:    
    """
    Extract EEG channel names and locations only if they are EEG channel types.

    Args:
        data_info (mne.raw.info) shape (1, 3): MNE raw data info object        

    Returns:
       data_chan_info (dict): Dictionary of channel name and position mapping.
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
    """
    Add/Modify the type of channels with no standard correspondance in standard montages. 

    Args:
        data_info (mne.raw.info) shape (1, 3): MNE raw data info object        

    Returns:
       data_info (ne.raw.info): 
    """    
    data_info = adjust_nonstd_chans(data_info)
    data_info = adjust_nonstd_chans_dig(data_info)
    return data_info

def adjust_nonstd_chans(data_info):
    """
    Modify the type of channels with no standard correspondance in standard montages. 

    Args:
        data_info (mne.raw.info) shape (1, 3): MNE raw data info object        

    Returns:
       data_info (ne.raw.info): 
    """      
    indx = 0
    for dchan in data_info['chs']:
        if dchan['ch_name'] in NON_STANDARD_CHANNEL_TYPES:
             data_info['chs'][indx]['kind'] = NON_STANDARD_CHANNEL_TYPES[dchan['ch_name']]
        indx += 1
    return data_info

def adjust_nonstd_chans_dig(data_info):
    """
    Add/Modify the type of channels with no standard correspondance in standard montages. 

    Args:
        data_info (mne.raw.info) shape (1, 3): MNE raw data info object        

    Returns:
       data_info (ne.raw.info): 
    """  
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
    """
    Initialize a dictionary for all standard montages to store their overlaps with the data.

    Args:
        data_chan_info (dict): Dictionary of channel name and position mapping.    

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.
    """      
    loc_position_dict = {}      
    for montage_name in MNE_DEFAULT_MONTAGES:
           
        loc_position_dict[montage_name] = {}
        loc_position_dict[montage_name]['chan_names'] = dict(zip(list(data_chan_info.keys()), [''] * len(list(data_chan_info.keys()))))
        loc_position_dict[montage_name]['chan_positions'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_position_dict[montage_name]['ch_pos_score'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_position_dict[montage_name]['position_score'] = []
        loc_position_dict[montage_name]['total_position_score'] = []
        loc_position_dict[montage_name]['valid'] = True      

    return loc_position_dict


def position_pipeline(data_chan_info, position_method="position") -> dict:
    """
    Runs a electrode matching algorithm based on channel position or names.

    Args:
        data_chan_info (dict): Dictionary of channel name and position mapping.    
        position_method (str): Channel matching method ('channel_name' or 'position')

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.
    """       
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
    """
    Runs a electrode matching algorithm based on channel names.

    Args:
        data_chan_info (dict): Dictionary of channel name and position mapping.    
        montage_name (str): Name of the montage used for matching.

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.
    """     
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
        loc_position_dict[montage_name]['ch_pos_score'][ch_name] = position_score

    loc_position_dict[montage_name]['position_score'] = []
    loc_position_dict[montage_name]['total_position_score'] = []
    loc_position_dict[montage_name]['valid'] = True
    return loc_position_dict

def position_matching_position(data_chan_info, montage_name, loc_position_dict) -> dict:
    """
    Runs a electrode matching algorithm based on channel positions.

    Args:
        data_chan_info (dict): Dictionary of channel name and position mapping.    
        montage_name (str): Name of the montage used for matching.

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.
    """       
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
            loc_position_dict[montage_name]['valid'] = False
        else:
            loc_position_dict[montage_name]['chan_names'][dchannames[rowi]] = mchnames[match_chan_indx]
            loc_position_dict[montage_name]['chan_positions'][dchannames[rowi]] = mchpos[mchnames[match_chan_indx]] 
            loc_position_dict[montage_name]['ch_pos_score'][dchannames[rowi]] = position_matrix[rowi, match_chan_indx]     
            total_sim_score[rowi] = position_matrix[rowi, match_chan_indx]

    if loc_position_dict[montage_name]['valid']:
        loc_position_dict[montage_name]['position_score'] = round(np.mean(total_sim_score) * 100, 5)
    else:
        loc_position_dict[montage_name]['position_score'] = INVALID_POS_SCORE
    loc_position_dict = get_matched_chan_ratio(loc_position_dict, montage_name)
    # print(f"\n{montage_name}:\n{loc_position_dict[montage_name]['position_score']}, {loc_position_dict[montage_name]['match_info']}")
    return loc_position_dict

def get_scoreboard(loc_position_dict) -> list | bool:
    """
    Runs a electrode matching algorithm based on channel names.

    Args:
        loc_position_dict (dict): Dictionary storing each montage's overlap with data.       

    Returns:
       ordered_key (list): list of montage names sorted (ascending) based on position distances.
    """       
    score_vector = np.array([])
    key_vector = np.array([])
    for key, val in loc_position_dict.items():
        score_vector = np.append(score_vector, val["position_score"])
        key_vector = np.append(key_vector, key)

    order_index = np.argsort(score_vector)
    ordered_key = []
    for index in order_index:
        ordered_key.append(key_vector[index])
    
    if len(set(score_vector)) == 1:
        if list(set(score_vector))[0] == INVALID_POS_SCORE:
            logger.warning(f"Distance values for all montages are invalid for the data, please assign a montage manually if needed.")
            return False

    return ordered_key

def select_best_montage(loc_position_dict, ordered_key) -> str | bool:
    """
    Input function to select among montages listed by distances.

    Args:
        loc_position_dict (dict): Dictionary storing each montage's overlap with data.       
        ordered_key (list): list of montage names sorted (ascending) based on position distances.

    Returns:
        (str): name of the selected montage.
    """     
    if ordered_key == False:
        logger.warning(f"Cannot display montage distance values because none of the montages had applicable position values for your data.")
        return False
    
    for indx, montage_name in enumerate(ordered_key):
        print(f"\n({indx+1}){montage_name}: {loc_position_dict[montage_name]['position_score']}, {loc_position_dict[montage_name]['match_info']}")
        
    print(f"\nType in the number of montage you want to select: ")
    while True:
        montage_index = input()
        if montage_index.isnumeric():
            montage_index = int(montage_index)
            montage_index -= 1 # subtract 1 for py indexing
            if montage_index > len(ordered_key):
                print(f"\nPlease select between montages 1 and {len(ordered_key)}")            
            elif montage_index < 0:
                print(f"\nPlease select a number 1 or above")
            elif loc_position_dict[ordered_key[montage_index]]['position_score'] == INVALID_POS_SCORE:
                print(f"\nMontage is not valid for the data, please select another.")
            else:
                break           
        elif montage_index == 'e':
            print("Selection cancelled...")
            return False
        else:
            print(f"\nPlease type in a number, not a string: {montage_index}")

    print(f"\n*********")
    print(f"Selected {ordered_key[montage_index]} montage")
    print(f"\n*********")
    return ordered_key[montage_index]

def find_min_matrix(matrix, start_row=0) -> int | None: 
    """
    Selects the montage electrode with the smallest distance.

    Args:
        matrix (np.ndarray) shape (#data_chan, #montage_chan): Matrix of electrode distance values 
        start_row (list): index of data channel to start search from 

    Returns:
       min_col (int): index of montage channel with lowest distance score.
    """         
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
            
def get_matched_chan_ratio(loc_position_dict, montage_name) -> dict:
    """
    Registers number of matched channels and ratio to number of data channels

    Args:
        loc_position_dict (dict): Dictionary storing each montage's overlap with data.       
        montage_name (str): Name of the montage used for matching.

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.   
    """       
    dupvals, dupkeys = resolve_duplicates(loc_position_dict, montage_name)
    match_count = len(loc_position_dict[montage_name]['chan_names']) - len(dupkeys)
    loc_position_dict[montage_name]['match_count'] = match_count
    loc_position_dict[montage_name]['match_info'] = f"{match_count}/{len(loc_position_dict[montage_name]['chan_names'])}"
    return loc_position_dict

def remove_unmatched_chans(loc_position_dict, montage_name) -> dict:
    """
    Removes channels with no position or name match. 

    Args:
        loc_position_dict (dict): Dictionary storing each montage's overlap with data.       
        montage_name (str): Name of the montage used for matching.

    Returns:
       loc_position_dict (dict): Dictionary storing each montage's overlap with data.   
    """        
    dupvals, dupkeys = resolve_duplicates(loc_position_dict, montage_name)
    for key in dupkeys:
        del loc_position_dict[montage_name][key]
    return loc_position_dict

def resolve_duplicates(loc_position_dict, montage_name):
    vec = []
    for key, val in loc_position_dict[montage_name]['chan_names'].items(): 
        vec.append(val)
    return find_duplicates(vec)

def find_duplicates(array) -> tuple[str, str]:
    """
    Finds duplicate elements in array

    Args:
        array (list):        

    Returns:
       dup (list), dupindx (list): List of duplicate elements and their index. 
    """        
    s = set()
    dup = []
    dupindx = []    
    for indx, n in enumerate(array):        
        if n in s:
            dup.append(n)
            dupindx.append(indx)
        else:
            s.add(n)

    return dup, dupindx