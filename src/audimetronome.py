#! /usr/bin/python3

"""
    File: audimetronome.py
    MetronomeV5
    Efficient audio metronome for callback
    Date: Mon, 06/02/2023
    Author: Coolbrother
"""
import numpy as np
class AudiMetronome(object):
    """ 
    Metronome V5, very efficient and dynamic metronome
    Generating click with static array for tone and dynamic silence 
    Note: TODO: adding mode 1, for generating click with only static array
    and create get_data function to retrieve this array.
    Note: can derive from AudiTrack klass.

    """
    
    def __init__(self, bpm=100, mode=0):
        self._active =0
        self._mode = mode # 0: static mode, 2: dynamic mode
        self._looping =1
        self._bpm = bpm
        self._rate =44100
        self._channels =2
        self._pos =0
        self._len =0
        self._data_pos =0
        self._index =0
        self._buf_arr = np.array([], dtype=np.float32)
        self._blanklen =0 
        self._tone1 =  None
        self._tone2 = None
        self._tonelen =0
        self._blank_arr = np.zeros([]) # empty, not necessary
        self._objlist = []
        self._objlen =0
        self._data_len =0
        self._data_pos =0
        self.init_click()

    #----------------------------------------

    def gen_sine_table(self, freq, rate, _len):
        """ returns array of sine wave """
        incr = (2 * np.pi * freq) / (rate * self._channels)
        nbsamples = rate * _len * self._channels
        arr = np.arange(nbsamples)
        
        _arr = np.sin(incr * arr)
        return np.float32(_arr)
        
    #-------------------------------------------
     
    def _next_obj(self):
        # Note: efficient way to shift list
        self._index = (self._index +1) % self._objlen
        
        """
        if self._index >= self._objlen -1:
            self._index =0
        else: self._index += 1
        
        """
        self._pos =0
        
    #----------------------------------------

    def get_position(self, unit=0):
        """
        returns metronome position
        from Metronome object
        """

        return self._pos

    #-----------------------------------------

    def set_position(self, pos, unit=0):
        """
        set metronome position 
        from Metronome object
        """

        if pos <0: pos =0
        elif pos > self._len: pos = self._len
        self._data_pos = int(pos % self._data_len)
        
        self._pos = pos

    #-----------------------------------------

    def is_active(self):
        """
        returns active state for this track
        from AudiMetronome object
        """
        
        return self._active

    #-----------------------------------------

    def set_active(self, active):
        """ 
        set active state for this track
        from AudiMetronome object
        """

        self._active = active

    #-----------------------------------------


    def get_bpm(self):
        """ 
        returns the bpm 
        from AudiMetronome object
        """
        
        return self._bpm

    #----------------------------------------

    def set_bpm(self, bpm=100):
        """ 
        sets the bpm 
        from AudiMetronome object
        change blank len value belong the bpm 
        """
        
        if bpm >=30 and bpm <= 1000:
            self.gen_click(bpm)
            self._bpm = bpm

    #----------------------------------------
    
    def init_click(self):
        """
        init the metronome click
        from Metronome object
        """
        
        # can use gen_sine_table function for generating array
        self._tonelen =0.060 # in sec
        self._tempo = float(60 / self._bpm)
        val = self._tempo - self._tonelen
        self._blanklen = int(val * self._rate * self._channels) # in nbsamples
        self._tone1 =  self.gen_sine_table(880, self._rate, self._tonelen) # tone 1
        self._tone2 =  self.gen_sine_table(440, self._rate, self._tonelen) # tone 2
        self._blank_arr = np.zeros([]) # empty, not necessary
        self.gen_click(self._bpm, self._mode)
        

    #----------------------------------------
    

    def gen_click(self, bpm, mode=0):
        """
        change blank len value belong the bpm 
        generate the arrays for clicks
        mode 0: for dynamic blank,
        mode 1: for static array for beats
        from AudiMetronome object
        """

        self._mode = mode
        self._tempo = (60 / bpm) # in sec
        # substract tone len
        val = self._tempo - self._tonelen
        self._blanklen = int(val * self._rate * self._channels)
        # metronome's length must be determined by the longest track
        self._len = (self._tempo * self._rate * self._channels) * 4 * 4 # 4 beats multiply by 4 arbitrary bars

        if mode == 0: # static array mode
            # calculate nbsamples for the blank beat
            self._blank_arr = np.zeros(self._blanklen, dtype=np.float32)
            beat1 = np.concatenate([self._tone1, self._blank_arr])
            beat2 = np.concatenate([self._tone2, self._blank_arr])
            self._buf_arr = np.concatenate(
                    [beat1, beat2, beat2, beat2]
                    )
            # self._len = self._buf_arr.size 
            self._data_len = self._buf_arr.size

            
        elif mode == 2: # dynamic mode
            # substract tone len
            self._objlist = [self._tone1, None, self._tone2, None,
                self._tone2, None, self._tone2, None
                ]
            self._objlen = len(self._objlist)

    #----------------------------------------

    def start_click(self):
        """
        start stop the clicking
        from AudiMetronome object
        """
        
        self._active =1
      
    #----------------------------------------

    def pause_click(self):
        """
        stop the clicking without init values
        from AudiMetronome object
        """
        
        self._active =0
       
    #----------------------------------------

    def stop_click(self):
        """
        stop the clicking
        from AudiMetronome object
        """
        
        self._index =0
        self._pos =0
        self._active =0
       
    #----------------------------------------

    def write_sound_data(self, out_data, data_count):
        """
        write sound data
        from AudiMetronome object
        """

        vol =0.5
        if self._mode == 0: # static array mode
            curdata = self._buf_arr
            if not curdata.size: return
            _len = self._len
            pos = self._pos
            data_len = self._data_len
            data_pos = self._data_pos

            for i in range(0, data_count, 2):
                if pos >= _len: # End of buffer
                    # print(f"pos: {pos}, data_pos: {data_pos}, _len: {_len}")
                    if self._looping:
                        pos =0
                    else:
                        break
                if data_pos >= data_len: 
                    data_pos =0
                else:
                    # attenuate amplitude data before adding it, cause others data are allready attenuated
                    # print(f"data_pos: {data_pos}")
                    val = curdata[data_pos] * vol
                    out_data[i] = (out_data[i] + val)
                    out_data[i+1] = (out_data[i+1] + val)
                    pos += 2
                    data_pos +=2
            self._pos = pos
            self._data_pos = data_pos
 
        elif self._mode == 2: # dynamic mode
            curdata = self._objlist[self._index]
            if curdata is None: curlen = self._blanklen
            else: curlen = curdata.size
            pos = self._pos
            _len = self._len
            for i in range(0, data_count, 2):
                if pos >= curlen:
                    self._next_obj()
                    curdata = self._objlist[self._index]
                    if curdata is None: curlen = self._blanklen
                    else: curlen = curdata.size
                    pos = self._pos
                
                if pos < curlen and curdata is None:
                    # blank click, so do nothing
                    # out_data[i] =0
                    pos += 2

                elif pos < curlen:
                    val = curdata[pos] * vol # isolate the atenuation
                    out_data[i] = (out_data[i] + val)
                    out_data[i+1] = (out_data[i+1] + val)
                    pos += 2
            self._pos = pos

    #----------------------------------------


#========================================

if __name__ == "__main__":
    met = AudiMetronome()
    bpm = met.get_bpm()
    print(f"Bpm is: {bpm}")
    input("Press Enter...")
