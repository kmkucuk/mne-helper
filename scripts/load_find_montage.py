from pyeeg.io.loader import read_raw_data
from pyeeg.io.getdir import fetch_sample_file
from pyeeg.preprocess.find_montage import adjust_chan_kind, get_chanlocs, position_pipeline, select_best_montage, get_scoreboard
import mne.viz as viz

sample_file = fetch_sample_file('BRAINVISION')
raw_data = read_raw_data(sample_file)
raw_data.load_data()
raw_data.plot(block=True)
raw_data.info = adjust_chan_kind(raw_data.info)
data_chan_info = get_chanlocs(raw_data.info)
position_dict = position_pipeline(data_chan_info, position_method='position')
ordered_keys = get_scoreboard(position_dict)
selected_montage = select_best_montage(position_dict, ordered_keys)
raw_data.rename_channels(position_dict[selected_montage]['chan_names'])
raw_data.set_montage(selected_montage)
raw_data.plot(block=True)
a=0 