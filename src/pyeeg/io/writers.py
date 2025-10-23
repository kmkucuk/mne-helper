from pyeeg.io.getdir import set_exportdir

def write_metadata(metadata, fname):
    """
    Writes mne metadata to a csv file.

    Args:
        metadata (pandas.DataFrame): dataframe
        fname (str): csv file name .

    Returns:
        Nothing
    """
    metadata.to_csv(set_exportdir(fname +'.csv'))    