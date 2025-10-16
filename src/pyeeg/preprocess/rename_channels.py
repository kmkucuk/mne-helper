from mne import channels as mc

mc.get_builtin_montages()
montage = mc.make_standard_montage('brainproducts-RNP-BA-128')


channel_mapping = dict(zip(raw_data.info.ch_names, montage.ch_names))
raw_data.set_montage(montage)


def find_montage_by_chan_count(info, montage):
    """
    info: mne.info object
    montage: electrode montage object (e.g. mne.channels.make_standard_montage["standard"])
    """
    montdat['dig'][0]['r']
    mont.dig[0]["r"]

    
    pass


def main():
    pass

if __name__ == "main":
    main()