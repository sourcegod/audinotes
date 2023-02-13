#! /usr/bin/python3

"""
    File: auditools.py
    Audio tools functions for AudiNotes.
    Date: Mon, 13/02/2023
    Author: Coolbrother
"""
import numpy as np

def _mid2freq(note):
    """
    return freq number from note midi number
    """

    return 440.0 * pow(2, (note - 69) / 12.0)

#-------------------------------------------


def _gen_sine_table(freq=440, rate=44100, channels=1, _len=5):
    """ returns array of sine wave """
    # Note IMPORTANT: dont forget to enclose in parenthesis (rate * channels)
    # because I searched the problem during a whole night
    incr = (2 * np.pi * freq ) / (rate * channels)
    nbsamples = _len * rate * channels
    x = np.arange(nbsamples) # in dtype float64
    arr = np.sin(incr * x)
    
    """
    Note: to convert array mono to interleave stereo array
    _arr = np.zeros((arr.size * _channels), arr.dtype)
    _arr[0::2] = arr
    _arr[1::2] = arr
    """

    """
    Note: to convert 1D array stereo to 2D array stereo 
    like (in_data) array in recording callback
    result = np.frombuffer(in_data, dtype=np.float32)
    result = np.reshape(result, (frames_per_buffer, 2))
    # to access to the channels use:
    left_channel = result[:, 0]
    right_channel = result[:, 1]
    """

    # Note: IMPORTANT to convert it in the right format for pyaudio module
    # _arr = np.float32(_arr) 
    
    return np.float32(arr)

#-------------------------------------------

def _gen_notes(note_lst, _len=0.5, count=1):
    """
    generate notes for tests
    """

    arr_lst = []
    
    """
    # C game
    note_lst = [
            60, 62, 64, 65, 
            67, 69, 71, 72,
            72, 74, 76, 77, 
            79, 81, 83, 84
            ]
    """

    for _ in range(count):
        for note in note_lst:
            freq = _mid2freq(note)
            arr = _gen_sine_table(freq=freq, rate=44100, channels=2, _len=_len)
            arr_lst.append(arr)
        
    arr = np.concatenate(arr_lst)
    return arr

#-------------------------------------------

def _gen_array(arr, num=1, channels=1):
    """ 
    Note: deprecated function
    -- generator for returning slice of numpy array 
    """
    
    for i in range(arr.shape[0] // num * channels):
        yield arr[num*i:num*(i+1)]

#-------------------------------------------


