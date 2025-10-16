from mne.io import read_raw_edf

def read_edf(filename):
    return read_raw_edf(
            filename,
            eog=None,
            misc=None,
            stim_channel="auto",
            exclude=(),
            infer_types=False,
            include=None,
            preload=False,
            units=None,
            encoding="utf8",
            verbose=None,
        )

