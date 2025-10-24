import numpy as np
import mne

from pyeeg.io.loader import read_raw_data
from pyeeg.io.writers import write_metadata
from pyeeg.io.getdir import fetch_sample_file

from pyeeg.preprocess.segmentation import create_epoch_dict, get_meta_data, select_event, segment_data_markers, plot_segmented_data

from pyeeg.utils.logger import initialize_logger
from pyeeg.utils.constants import DEFAULT_SEGMENTATION_WINDOW


logger = initialize_logger()

SAMPLE_FILE = 'BRAINVISION'

sample_file = fetch_sample_file('BRAINVISION')
raw_data = read_raw_data(sample_file)
raw_data.filter(l_freq=0.1, h_freq=40)
epoch_dict = create_epoch_dict()
epoch_dict = get_meta_data(raw_data, epoch_dict)
epoch_dict = select_event(epoch_dict)
epochs = segment_data_markers(raw_data, epoch_dict)
fig = plot_segmented_data(epochs, epoch_dict)

if SAMPLE_FILE == 'BRAINVISION':
    freq_avg = epochs['Stimulus/Frequent'].average()
    rare_avg = epochs['Stimulus/Rare'].average()
    rare_avg.plot()
    rare_avg.plot_topomap(times=[0.1, 0.2, 0.3], average=0.05)
    rare_avg.plot_joint()


