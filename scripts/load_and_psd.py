from pyeeg.io.loader import read_raw_data
from pyeeg.io.getdir import fetch_sample_file

from pyeeg.preprocess.segmentation import segment_data_continuous

SAMPLE_FILE = 'BRAINVISION'
sample_file = fetch_sample_file(SAMPLE_FILE)
raw_data = read_raw_data(sample_file)
raw_data.filter(l_freq=0.1, h_freq=40)
reject = dict(eeg=100e-6)
cont_epochs = segment_data_continuous(raw_data, reject=reject)

spectrum = cont_epochs.compute_psd() 
sp_data = spectrum.get_data() # get data in numpy format

print('data type', type(raw_data))
print('data type', type(cont_epochs))
print('data type', type(spectrum))
print('data type', type(sp_data))


a=0