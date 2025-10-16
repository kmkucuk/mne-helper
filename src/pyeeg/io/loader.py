from mne.io import read_raw


def read_raw_data(filename):
    return read_raw(filename,
                    preload=True,
                    verbose=None)