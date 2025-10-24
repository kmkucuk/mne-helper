from mne import viz as v


def plot_raw(raw_data):
    return v.plot_raw(raw_data, 
               events=None, 
               duration=10.0, 
               start=0.0, 
               n_channels=20, 
               bgcolor='w', 
               color=None, 
               bad_color='lightgray', 
               event_color='cyan', 
               scalings=None, 
               remove_dc=True, 
               order=None, 
               show_options=False, 
               title=None, 
               show=True, 
               block=False, 
               highpass=None, 
               lowpass=None, 
               filtorder=4, 
               clipping=1.5, 
               show_first_samp=False, 
               proj=True, 
               group_by='type', 
               butterfly=False, 
               decim='auto', 
               noise_cov=None, 
               event_id=None, 
               show_scrollbars=True, 
               show_scalebars=True, 
               time_format='float', 
               precompute=None, 
               use_opengl=None, 
               picks=None,
               theme=None, 
               overview_mode=None, 
               splash=True, 
               verbose=None)




