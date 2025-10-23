from pyeeg.io.loader import read_raw_data
from pyeeg.io.getdir import fetch_sample_file

sample_file = fetch_sample_file('BRAINVISION')
raw_data = read_raw_data(sample_file)
raw_data.load_data()
raw_data.plot(block=True)