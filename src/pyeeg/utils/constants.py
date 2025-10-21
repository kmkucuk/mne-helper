from mne._fiff.constants import FIFF


# EEG channels have different FIFF types in:
# raw_data.info['chs']: FIFF.FIFFV_EEG_CH 
# raw_data.info['dig]: FIFF.FIFFV_POINT_EEG

NON_STANDARD_CHANNEL_TYPES = {
    'A1': FIFF.FIFFV_MISC_CH,
    'A2': FIFF.FIFFV_MISC_CH,    
    'EOG': FIFF.FIFFV_EOG_CH,
    'VEOG': FIFF.FIFFV_EOG_CH,
    'HEOG': FIFF.FIFFV_EOG_CH,
    'EOGV': FIFF.FIFFV_EOG_CH,
    'EOGH': FIFF.FIFFV_EOG_CH
}

INVALID_POS_SCORE = 999 # assigned to invalid distances in find_montage()

MNE_DEFAULT_MONTAGES = ['standard_1005', 'standard_1020', 'standard_alphabetic', 'standard_postfixed', 'standard_prefixed', 'standard_primed', 'biosemi16', 'biosemi32', 'biosemi64', 'biosemi128', 'biosemi160', 'biosemi256', 'easycap-M1', 'easycap-M10', 'easycap-M43', 'EGI_256', 'GSN-HydroCel-32', 'GSN-HydroCel-64_1.0', 'GSN-HydroCel-65_1.0', 'GSN-HydroCel-128', 'GSN-HydroCel-129', 'GSN-HydroCel-256', 'GSN-HydroCel-257', 'mgh60', 'mgh70', 'artinis-octamon', 'artinis-brite23', 'brainproducts-RNP-BA-128']