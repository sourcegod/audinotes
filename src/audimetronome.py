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
    
    def __init__(self, bpm=100):
        self._active =0
        self._mode =0 # dynamic mode
        self._looping =0
        self._bpm = bpm
        self._rate =44100
        self._channels =2
        self._curpos =0
        self._index =0
        # can use gen_sine_table function for generating array
        self._tonelen =0.060 # in sec
        tempo = float(60 / bpm)
        val = tempo - self._tonelen
        self._blanklen = int(val * self._rate * self._channels) # in nbsamples
        tone1 =  self.gen_sine_table(880, self._rate, self._tonelen) # tone 1
        tone2 =  self.gen_sine_table(440, self._rate, self._tonelen) # tone 2
        self._blank = np.zeros([]) # empty, not necessary
        self._objlist = [tone1, None, tone2, None,
                tone2, None, tone2, None
                ]
        self._objlen = len(self._objlist)

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
        self._curpos =0
        
    #----------------------------------------

    def write_sound_data(self, out_data, count):
        """
        write sound data
        from AudiMetronome object
        """

        vol =0.5
        curdata = self._objlist[self._index]
        if curdata is None: curlen = self._blanklen
        else: curlen = curdata.size
        pos = self._curpos
        for i in range(count):
            if pos >= curlen:
                self._next_obj()
                curdata = self._objlist[self._index]
                if curdata is None: curlen = self._blanklen
                else: curlen = curdata.size
                pos = self._curpos
            
            if pos < curlen and curdata is None:
                # blank click, so do nothing
                # out_data[i] =0
                pos += 1

            elif pos < curlen:
                val = curdata[pos] * vol # isolate the atenuation
                out_data[i] = (out_data[i] + val)
                pos += 1
        self._curpos = pos

    #----------------------------------------

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
        
        if bpm >0 and bpm <= 1000:
            self.gen_click(bpm)
            self._bpm = bpm

    #----------------------------------------

    def gen_click(self, bpm, mode=0):
        """
        change blank len value belong the bpm 
        generate the arrays for clicks
        mode 0: for dynamic blank,
        mode 1: for static array for beats
        from AudiMetronome object
        """

        tempo = (60 / bpm) # in sec
        # substract tone len
        val = tempo - self._tonelen
        # calculate nbsamples for the blank beat
        self._blanklen = int(val * self._rate * self._channels)

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
        self._curpos =0
        self._active =0
       
    #----------------------------------------

#========================================

if __name__ == "__main__":
    met = AudiMetronome()
    bpm = met.get_bpm()
    print(f"Bpm is: {bpm}")
    input("Press Enter...")
