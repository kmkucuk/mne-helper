
import mne

raw_data.rename_channels(chdict['biosemi32']['changed_names'])
raw_data.set_montage('biosemi32')
raw_data.plot(block=True)
a=0
