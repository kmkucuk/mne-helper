import typing
import pywt
import numpy as np

from pyeeg.utils.logger import logger
from pyeeg.utils.constants import DEFAULT_WAVELET_PARAMETERS

def array_w_steps(array=None, count=None, method='lin') -> typing.List:
    if isinstance(array, list):        
        if len(array) != 2:
            logger.critical("Array for stepping must be at length of two")
            raise ValueError("Array for stepping must be at length of two")
    elif not isinstance(array, float or int):
        logger.critical("Single values for frequency and cycles should be numeric (int or float)")
        raise TypeError("Single values for frequency and cycles should be numeric (int or float)")
    steps = np.ndarray((1, count))
    if method == 'lin':
        steps[:] = np.round(np.linspace(array[0], array[1], count), 1)
    elif method == 'log':
        steps[:] = np.round(np.log10(np.logspace(array[0], array[1], count)), 1)
    else:
        logger.error("Incorrect array-step method for steps")
        raise ValueError("Incorrect array-step method for steps ") 
    return steps

def cwt_on_epochs(epoch_data, wavelet_parameters=DEFAULT_WAVELET_PARAMETERS):
    
    if isinstance(epoch_data._raw_sfreq, float):
        srate = epoch_data._raw_sfreq
    elif len(epoch_data._raw_times) > 1:
        srate = 1 / np.diff(epoch_data._raw_times).mean()
    else:
        logger.error("Failed to get sampling rate: could not find sampling rate or times")
        raise ValueError("Failed to get sampling rate: could not find sampling rate or times")
    
    freqs = array_w_steps(wavelet_parameters['f_range'], wavelet_parameters['f_count'], wavelet_parameters['f_steps']) 
    scale = pywt.frequency2scale(wavelet_parameters['wavelet'], freqs / srate)
    
    tmp_data = epoch_data._get_data().copy()

    cwtmatr, freqs = pywt.cwt(chirp, scale, wavelet_parameters['wavelet'], sampling_period=1/srate)


def create_wavelet_w_cycles(freq_range=None, 
                            cycle_range=None,
                            freq_count=None,
                            freq_steps='lin', 
                            cycle_steps='log',
                            return_wavefun=False) -> typing.Dict:
    """NOT USED AT THE MOMENT 29.10.2025"""
    if freq_range is None:
        logger.error("Frequency range was not entered")
        raise ValueError("Please enter a center frequency (i.e. 4) or a range of frequncies (i.e. [4, 10])")
    if cycle_range is None:
        logger.error("Cycle range was not entered")
        raise ValueError("Please enter a cycle (i.e. 4) or a range of cycles (i.e. [4, 10])")    
    
    freqs = array_w_steps(freq_range, freq_count, freq_steps)
    cycles = array_w_steps(cycle_range, freq_count, cycle_steps)
    # "cmorB-C" where B is the cycle (bandwidth) and C is center frequency
    wavelets = [f"cmor{x:.1f}-{y:.1f}" for x in cycles for y in freqs]
    wave_dict = {}
    wave_dict['wavelets'] = dict(zip(list(wavelets), [[]] * len(wavelets)))
    if return_wavefun:
        for wavei in wavelets:    
                # wavefun arg scales srate [-8, 8]s / 2**10
                [psi, x] = pywt.ContinuousWavelet(wavei).wavefun(10) 
                wave_dict['wavelets'][wavei] = psi
        wave_dict['times'] = x
    
    wave_dict['frequencies'] = freqs
    wave_dict['cycles'] = cycles    
    return wave_dict


