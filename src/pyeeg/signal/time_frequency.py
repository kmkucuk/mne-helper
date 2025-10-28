import typing
import pywt
import numpy as np

from pyeeg.utils.logger import logger

def cwt_on_epochs(data, sampling_freq=None):
    pass

def array_w_steps(array=None, count=None, method='lin') -> typing.List:
    if isinstance(array, list):
        if len(array) == 2:
            pass
    steps = np.ndarray((1, count))
    if method == 'lin':
        steps[:] = np.round(np.linspace(array[0], array[1], count), 1)
    elif method == 'log':
        steps[:] = np.round(np.log10(np.logspace(array[0], array[1], count)), 1)
    else:
        logger.error("Incorrect array-step method for steps")
        raise ValueError("Incorrect array-step method for steps ") 
    return steps[0].tolist()

def create_wavelet(freq_range=None, 
                   cycle_range=None,
                   freq_count=None,
                   cycle_count=None,
                   freq_steps='lin', 
                   cycle_steps='log') -> typing.Dict:
    
    if freq_range is None:
        logger.error("Frequency range was not entered")
        raise ValueError("Please enter a center frequency (i.e. 4) or a range of frequncies (i.e. [4, 10])")
    if cycle_range is None:
        logger.error("Cycle range was not entered")
        raise ValueError("Please enter a cycle (i.e. 4) or a range of cycles (i.e. [4, 10])")    
    
    freqs = array_w_steps(freq_range, freq_count, freq_steps)
    cycles = array_w_steps(cycle_range, cycle_count, cycle_steps)

    # "cmorB-C" where B is the cycle (bandwidth) and C is center frequency
    wavelets = [f"cmor{x:.1f}-{y:.1f}" for x in cycles for y in freqs]
    wave_dict = dict(zip(list(wavelets), [[]] * len(wavelets)))
    
    for wavei in wavelets:
        [psi, x] = pywt.ContinuousWavelet(wavei).wavefun(10)    
        wave_dict[wavei] = psi
    wave_dict['times'] = x
    return wave_dict
