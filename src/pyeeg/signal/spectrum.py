import numpy as np
import mne
import scipy
import typing
import scipy.fftpack

from pyeeg.utils.logger import logger

def get_psd_data(spect_data, freq_range=[0, np.inf]) -> typing.Tuple[np.ndarray, np.ndarray]:
    """
    Retrieves power and frequencies from psd dta.

    Args:
        spect_data (mne.time_frequency.spectrum.EpochsSpectrum): mne psd object
        freq_range (array-like): range of frequencies [lowerf, higherf]

    Returns:
        data (np.ndarray) shape(epochs, channels, frequencies)
        frequencies (np.ndarray) shape(1, frequencies)
    """        
    if len(freq_range) == 1:
        return spect_data.get_data(fmin=freq_range, fmax=freq_range, return_freqs=True) 
    elif len(freq_range) == 2:
        if freq_range[0] >= freq_range[1]:
            return spect_data.get_data(fmin=freq_range[0], fmax=freq_range[1], return_freqs=True) 
        else:
            logger.error(f"First frequency should be lower or equal to the second frequency: {freq_range}")
            raise ValueError(f"First frequency should be lower or equal to the second frequency: {freq_range}")            
    else:
        logger.error(f"Frequency argument can have minimum of 1 element and maximum of 2 elements: {freq_range}")
        raise ValueError(f"Frequency argument can have minimum of 1 element and maximum of 2 elements: {freq_range}")

def fft_on_epochs(data, sampling_freq=None):  
    data_shape = list(np.shape(data))
    if sampling_freq is None:
        logger.error("Please enter a valid sampling frequency")
        raise ValueError("Please enter a valid sampling frequency: fft_on_epochs(data, sampling_freq=int)")
    elif len(data_shape) != 3:
        logger.error("Data should be in 3d (epochs, channels, time)")
        raise ValueError("Data should be in 3d (epochs, channels, time)")
    else:
        N = data_shape[-1]
        fft_result = scipy.fftpack.fftn(data)    
        freqs = scipy.fftpack.fftfreq(N, d=1/sampling_freq)
        fft_positive = fft_result[:, :, 0:N//2]
        freqs_positive = freqs[:, 0:N//2]
        fft_mag = np.abs(fft_positive) / N
        if N % 2 == 0:
            fft_mag[:, :, 1:-1] *= 2.0
        else:
            fft_mag[:, :, 1:] *= 2.0
        return fft_mag, freqs_positive

def stft_on_epochs(data):
    data_shape = list(np.shape(data))

    if len(data_shape) != 3:
        logger.error("Data should be in 3d (epochs, channels, time)")
        raise ValueError("Data should be in 3d (epochs, channels, time)")
    elif (data_shape[2] % 2) != 0:
        logger.error(f"Length of time dimension should be even, instead: {data_shape[2]}")
        raise ValueError(f"Length of time dimension should be even, instead: {data_shape[2]}")
    else:
        fft_shape = tuple([data_shape[0], data_shape[1], int(data_shape[-1]/2)])
        stft_data = np.zeros(fft_shape)    
        for epi in range(0, data_shape[0]):
            stft_data[epi, :, :] = mne.time_frequency.stft(data)    
        return stft_data