from pyeeg.io.loader import read_raw_data
from pyeeg.io.getdir import fetch_sample_file
from pyeeg.preprocess.find_montage import adjust_chan_kind, get_chanlocs, position_pipeline


sample_file = fetch_sample_file('EEGLAB')
raw_data = read_raw_data(sample_file)
raw_data.load_data()
raw_data.info = adjust_chan_kind(raw_data.info)
data_chan_info = get_chanlocs(raw_data.info)
position_dict = position_pipeline(data_chan_info, position_method='position')