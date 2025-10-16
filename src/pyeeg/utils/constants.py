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