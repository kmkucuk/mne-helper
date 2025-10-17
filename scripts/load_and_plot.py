import mne._fiff
from mne._fiff._digitization import DigPoint
from pyeeg.io.loader import read_raw_data
from pyeeg.io.fetch_sample import fetch_sample_file
import mne
import numpy as np
import math
import logging
from mne._fiff.constants import FIFF
from pyeeg.utils.constants import NON_STANDARD_CHANNEL_TYPES, MNE_DEFAULT_MONTAGES



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
    
def check_pos_distance(montage_pos, data_pos) -> float:        
    """Get similarity ratios between montage electrode positions and data positions.

    Returns
    -------
    float: distance between two vectors
    """
    if any(np.isnan(data_pos)):
        logger.warning(f'Channel position coordinates include a NAN value {data_pos}')    
        return np.nan
    elif isinstance(data_pos, np.ndarray or list) and isinstance(montage_pos, np.ndarray or list):        
        return np.linalg.norm(data_pos - montage_pos)
    else:
        logger.error(f"Position types are not fit for similartiy estimation: data-type {type(data_pos)}, montage-type {type(montage_pos)}")
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

def create_similarity_dict(data_chan_info):
    """Initializes a similarity dict 
    :param data_chan_info: mne.raw.info instance (info of your raw_data)
    Returns
    -------
    dict
    """ 
    loc_similarity_dict = {}      
    for montage_name in MNE_DEFAULT_MONTAGES:
           
        loc_similarity_dict[montage_name] = {}
        loc_similarity_dict[montage_name]['chan_names'] = dict(zip(list(data_chan_info.keys()), [''] * len(list(data_chan_info.keys()))))
        loc_similarity_dict[montage_name]['chan_positions'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_similarity_dict[montage_name]['chan_similarity'] = dict(zip(list(data_chan_info.keys()), [[None, None, None]] * len(list(data_chan_info.keys())))) 
        loc_similarity_dict[montage_name]['similarity_score'] = []
        loc_similarity_dict[montage_name]['total_similarity_score'] = []

    return loc_similarity_dict


def similarity_pipeline(data_chan_info, similarity_method="position"):
    loc_similarity_dict = create_similarity_dict(data_chan_info) 
    for montage_name in MNE_DEFAULT_MONTAGES:
        if similarity_method == "position":
            loc_similarity_dict = position_matching_similarity(data_chan_info, montage_name, loc_similarity_dict)
        elif similarity_method == "channel_name":
            loc_similarity_dict = name_matching_similarity(data_chan_info, montage_name, loc_similarity_dict)
        else:
            logger.critical(f"Wrong similarity method {similarity_method}, please enter a valid method ''position'' or ''channel_name''")
            raise ValueError("Wrong similarity method")
    return loc_similarity_dict
    
def name_matching_similarity(data_chan_info, montage_name, loc_similarity_dict):
    montage = mne.channels.make_standard_montage(montage_name)    
    mchpos = montage._get_ch_pos()    
    for ch_name, pos_val in data_chan_info.items():          
        empty_pos = np.empty((3))
        empty_pos.fill(np.nan)            
        if ch_name in montage.ch_names:           
            ch_reg = ch_name
            ch_pos = mchpos[ch_name]            
            similarity_score = check_pos_distance(mchpos[ch_name], pos_val)
        else:
            ch_reg = ch_name
            ch_pos = empty_pos              
            similarity_score = empty_pos

        loc_similarity_dict[montage_name]['chan_names'][ch_name] = ch_reg
        loc_similarity_dict[montage_name]['chan_positions'][ch_name] = ch_pos 
        loc_similarity_dict[montage_name]['chan_similarity'][ch_name] = similarity_score

    loc_similarity_dict[montage_name]['similarity_score'] = []
    loc_similarity_dict[montage_name]['total_similarity_score'] = []
    loc_similarity_dict[montage_name]['viable'] = True
    return loc_similarity_dict

def position_matching_similarity(data_chan_info, montage_name, loc_similarity_dict):
    montage = mne.channels.make_standard_montage(montage_name)    
    mchpos = montage._get_ch_pos()        
    mchnames = list(mchpos.keys())
    similarity_matrix = np.ones(shape=(len(data_chan_info), len()))
    total_sim_score = np.zeros(shape=(len(data_chan_info), 1))
    simi = 0
    for ch_name, pos_val in data_chan_info.items():          
        ch_sim_scores = np.zeros(shape=(len(mchpos), 1))
        mchnames = list(mchpos.keys())
        chi=0        
        for mnt_ch_name, mpos_val in mchpos.items():
            ch_sim_scores[chi] = check_pos_distance(mpos_val, pos_val)         
            chi += 1
        
        best_chan_indx = np.argmin(ch_sim_scores)
        best_chan_name = mchnames[best_chan_indx]        
        same_min_distances = np.where(ch_sim_scores==ch_sim_scores[best_chan_indx])[0]
        if len(same_min_distances) > 1:
            print(f"There are more than one minimum values in similarity estimations {montage_name}, {ch_name}, {same_min_distances}, {mchnames[same_min_distances[0]], mchnames[same_min_distances[1]]}")
            logger.error(f"There are more than one minimum values in similarity estimations {montage_name}, {ch_name}, {same_min_distances}, {mchnames[same_min_distances[0]], mchnames[same_min_distances[1]]}")        
            loc_similarity_dict[montage_name]['viable'] = False
        loc_similarity_dict[montage_name]['chan_names'][ch_name] = best_chan_name
        loc_similarity_dict[montage_name]['chan_positions'][ch_name] = mchpos[best_chan_name] 
        loc_similarity_dict[montage_name]['chan_similarity'][ch_name] = ch_sim_scores[best_chan_indx]        
        total_sim_score[simi] = ch_sim_scores[best_chan_indx]
        simi += 1

        # del mchpos[best_chan_name]
        # if len(mchpos) == 0:
        #     break

    loc_similarity_dict[montage_name]['similarity_score'] = np.mean(total_sim_score) * 1000
    print(f"Similarity score of {montage_name}: {loc_similarity_dict[montage_name]['similarity_score']}")
    return loc_similarity_dict

def resolve_duplicates(similarity_dict_montage, montage):
    vec = []
    for key, val in similarity_dict_montage['chan_names'].items(): 
        vec.append(val)
    duplicates = find_duplicates(vec)

    if len(duplicates) > 0:
        similarity_dict_montage
    else:
        
        pass
def find_duplicates(array):
    # Initialize an empty set to store seen elements
    s = set()

    # List to store duplicates
    dup = []

    for n in array:
        if n in s:
            dup.append(n)
        else:
            s.add(n)

    return dup

sample_file = fetch_sample_file('BRAINVISION')
montage = mne.channels.make_standard_montage('biosemi32')    
raw_data = read_raw_data(sample_file)
raw_data.load_data()
raw_data.info = adjust_nonstd_chans(raw_data.info)
raw_data.info = adjust_nonstd_chans_dig(raw_data.info)
data_chan_info = get_chanlocs(raw_data.info)
similarity_dict = similarity_pipeline(data_chan_info, similarity_method='position')
a=0

raw_data.rename_channels(chdict['biosemi32']['changed_names'])
raw_data.set_montage('biosemi32')
raw_data.plot(block=True)
a=0

#
