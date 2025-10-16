from mne.io.eeglab import read_raw_eeglab

def read_eeglab(filename):
    return read_raw_eeglab(
        filename,
        eog=(),
        preload=False,
        uint16_codec=None,
        montage_units="auto",
        verbose=None,
    )