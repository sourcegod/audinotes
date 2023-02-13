#! /usr/bin/python3

"""
    File: auditrack.py
    Lite Track klass for AudiNotes.
    Date: Mon, 13/02/2023
    Author: Coolbrother
"""
import numpy as np

class AudiTrack(object):
    """ Track audio object """
    def __init__(self):
        self.id = id
        self._active =0
        self._muted =0
        self._arm_muted =0
        self._buf_arr = np.array([], dtype=np.float32)
        self._pos =0
        self._len =0
        self._looping =0


    #-------------------------------------------

    def get_data(self):
        """
        returns numpy array
        """

        return self._buf_arr

    #-------------------------------------------

    def set_data(self, arr):
        """
        set data to the track
        from Track object
        """

        if arr is not None:
            self._buf_arr = arr
            self._len = self._buf_arr.size
            # self._pos =0

    #-----------------------------------------
    
    def get_length(self, unit=0):
        """
        return total track length 
        from track object
        """

        return self._len
    
    #-----------------------------------------
    
    def init_position(self):
        """
        init track position 
        from track object
        """
        
        self.set_position(0, 0) # in frames
        
    #-----------------------------------------

    def get_position(self, unit=0):
        """
        return track position
        from Track object
        """

        return self._pos

    #-----------------------------------------

    def set_position(self, pos, unit=0):
        """
        set track position 
        from track object
        """

        if pos <0: pos =0
        elif pos > self._len: pos = self._len
        
        self._pos = pos

    #-----------------------------------------

    def is_active(self):
        """
        returns active state for this track
        from Track object
        """
        
        return self._active

    #-----------------------------------------

    def set_active(self, active):
        """ 
        set active state for this track
        from Track object
        """

        self._active = active

    #-----------------------------------------

    def get_mute(self):
        return (self._leftmute, self._rightmute)
    
    #-----------------------------------------

    def is_muted(self):
        return self._muted
    
    #-----------------------------------------
 
    def set_muted(self, muted=0, chanside=2):
        # set channel mute
        val =0 if muted else 1 # ternary operator
        if chanside == 0: # left channel side
            self._leftmute = val
        elif chanside == 1: # right channel side
            self._rightmute = val
        elif chanside == 2: # both channel side
            self._leftmute = val
            self._rightmute = val

        self._muted = muted

    #-----------------------------------------

    def toggle_mute(self):
        """
        toggle muted state
        from AudiTrack object
        """

        self._muted = not self._muted
        
        return self._muted

    #-----------------------------------------

    def is_arm_muted(self):
        """
        return internal mute state for armed track
        from Track object
        """
        
        return self._arm_muted

    #-----------------------------------------

    def set_arm_muted(self, arm_muted=0):
        """
        set internal mute state for armed track
        from Track object
        """
        
        self._arm_muted  = arm_muted

    #-----------------------------------------

    def set_looping(self, looping):
        """
        set looping state
        from AudiTrack object
        """

        self._looping = looping

    #-----------------------------------------

    def is_looping(self):
        """
        returns looping state
        from AudiTrack object
        """

        return self._looping

    #-----------------------------------------

    def toggle_loop(self):
        """
        toggle looping state
        from AudiTrack object
        """

        self._looping = not self._looping
        
        return self._looping

    #-----------------------------------------


    def write_sound_data(self, out_data, data_count):
        """
        writing curdata to the out_data
        from AudiTrack object
        """

        vol =0.5
        curdata = self._buf_arr
        if not curdata.size: return
        pos = self._pos
        _len = self._len
        
        if self._muted or self._arm_muted:
            # dont write any data, just increment curpos
            for i in range(0, data_count, 2):
                if pos +1 >= _len: # End of buffer
                    if self._looping:
                        pos =0
                else: # pos < _len
                    pos += 2

        else: # not muted, not armed
            for i in range(0, data_count, 2):
                if pos +1 >= _len: # End of buffer
                    if self._looping:
                        pos =0
                else: # pos < _len
                    # attenuate amplitude data before adding it, cause others data are allready attenuated
                    val = curdata[pos] * vol
                    out_data[i] = (out_data[i] + val)
                    out_data[i+1] = (out_data[i+1] + val)
                    pos += 2
        self._pos = pos
    
    #-----------------------------------------

#========================================

if __name__ == "__main__":
    tra = AudiTrack()
    _len = tra._len
    print(f"Track len: {_len}")
    input("It's OK...")
#-----------------------------------------
