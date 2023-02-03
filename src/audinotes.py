#! /usr/bin/python
"""
    File: audinotes.py
	Test unlimited recording on PyAudio
    Inspired from playrec module.
    Note: Work fine.
    with: output_device_index =15: default output Soundcard with only output
    input_device_index =0: default Input Soundcard, with only input
    output_device_index =6: Eternal output Soundcard
    input_device_index =6: External input Soundcard
    
    Last update: Fri, 03/02/2023
    See changelog

   
    Last update: Wed, 01/02/2023
    Version: 0.1
    
	Date: samedi, 26/07/14 02/43/56
    Author: Coolbrother

"""
#-------------------------------------------

import time
import sys
import numpy as np
from collections import deque
import readline
import portdriver as pdv

_help = """ Help on Player
  b: forward
  ?, h: print this help
  p, t, space: toggle play pause
  q, Q: quit
  r: toggle record
  R: toggle record mode (replace, mix)
  S: stop the Engine
  T: start the Engine
  u: status
  w: rewind
  v: stop
  z: wiring
  <: goto start
  >: goto end
  dev: display devices infomations

"""

def beep():
    print("\a")

#-------------------------------------------

def get_sine_table(freq=440, rate=44100, channels=1, _len=5):
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

def gen_array(arr, num=1, channels=1):
    """ 
    Note: deprecated function
    -- generator for returning slice of numpy array 
    """
    
    for i in range(arr.shape[0] // num * channels):
        yield arr[num*i:num*(i+1)]

#-------------------------------------------

class Player(object):
    """ Play and record manager """
    def __init__(self):
        self._audio_driver = None
        self._channels =2
        self._rate =44100
        self._buf_size = 1024
        self._play_track = None
        self._play_track = get_sine_table(freq=440, rate=44100, channels=2, _len=5)
        self._pos =0
        self._playing =0
        self._recording =0
        self._paused =0
        self._mixing =0
        self._wiring =0
        self._deq_data = deque()
        self._data_size = self._buf_size * self._channels
        self._sample_unit = self._rate * self._channels
        self._rec_pos =0
        self._rec_mode =0 # replace mode
        pass

    #-------------------------------------------

    def init_player(self, input_device_index, output_device_index):
        self._audio_driver = pdv.PortDriver()
        self._audio_driver.init_devices(input_device_index, output_device_index)
        self._audio_driver.set_audio_callback(self._audio_callback)
        self._audio_driver.open()
        self._channels = self._audio_driver._channels
        self._rate = self._audio_driver._rate
        self._buf_size = self._audio_driver._buf_size

    
    #-------------------------------------------

    def start_driver(self):
        self._audio_driver.start_engine()
        beep()

    #-------------------------------------------
    
    def stop_driver(self):
        self._audio_driver.stop_engine()
        beep()

    #-------------------------------------------
     
    def close(self):
        """ Close the player """
        self.stop()
        self._audio_driver.stop_engine()
        self._audio_driver.close()

    #-------------------------------------------

    def is_running(self):
        return self._audio_driver.is_running()

    #-------------------------------------------

    def print_devices(self):
        """
        display devices info
        from Player object
        """

        self._audio_driver.print_devices()

    #-------------------------------------------

    def _audio_callback(self, in_data, frame_count, time_info, status):
        flag_continue =0 # pyaudio.paContinue
        if status:
            print(f"Status Error: {status}")
            beep()
            
        data_size = frame_count  * self._channels
        data = np.zeros(data_size, dtype=np.float32)
        # print(f"frame_count: {frame_count}")
        if self._playing:
            play_data = self.get_data(self._play_track, self._pos, data_size)
            # check that callback continue with enough array data
            if play_data.size >= data_size:
                data = play_data
                self._pos += play_data.size
            else:
                # self.stop()
                pass
        if self._recording and self._rec_mode == 0: # record in replace mode
            rec_data = np.frombuffer(in_data, dtype=np.float32)
            self._deq_data.append(rec_data)
            
            """
            for i in range(rec_data.size):
                if self._pos < self._play_track.size:
                    self._play_track[self._pos] = rec_data[i]
                    self._pos += 1
                else:
                    self.stop()
            """

        elif self._recording and self._rec_mode == 1: # rec in merge mode
            
            """
            play_data = self.get_data(self._play_track, self._pos, data_size)
            # check that callback continue with enough array data
            if play_data.size >= data_size:
                data = play_data
                self._pos += play_data.size
            else:
                pass
            """
            rec_data = np.frombuffer(in_data, dtype=np.float32)
            self._deq_data.append(rec_data)

        elif self._wiring:
            data = in_data

        # beep()
        if not isinstance(data, bytes):
            return (data.tobytes(), flag_continue)
        
        return (data, flag_continue)

    #-----------------------------------------

    def get_data(self, arr, start, stop):
        """ returns slice array """
        try:
            return arr[start:start+stop]
        except IndexError:
            return np.array([])

    #-----------------------------------------

    def arrange_track(self):
        """ arranging recorded takes with play_track track"""
        
        lst = []
        vol =0.5 # atenuation
        len_deq = len(self._deq_data)
        if not len_deq: return
        print("Arranging track...")
        play_track = self._play_track
        play_len = self._play_track.size
        if self._rec_pos > 0 and self._rec_pos <= play_len:
            # copy play_track part
            if self._rec_mode == 0: # replace mode
                part_track = play_track[:self._rec_pos]
            else:
                part_track = np.zeros(self._rec_pos)
            lst.append(part_track)
        lst.extend([self._deq_data.popleft() for i in range(len_deq)])
        # creating rec_track to adding part_track and the deque items
        rec_track = np.concatenate(lst)
        # rec_len = self._rec_pos + (len_deq * self._data_size)
        rec_len = rec_track.size
        
        if self._rec_mode == 0: # replace mode
            if play_len < rec_len:
                # Just replacing play_track by rec_track
                self._play_track = rec_track
            elif play_len >= rec_len:
                # take play_len as longest track
                final_track = np.zeros(play_len, dtype=np.float32)
                # Adding rec_track to the final_track
                for i in range(rec_len):
                    final_track[i] = rec_track[i]
                # Adding the rest for play_track to the final_track
                for i in range(rec_len, play_len):
                    final_track[i] = play_track[i]
                    self._play_track = final_track
       
        elif self._rec_mode == 1: # mix mode
            if play_len < rec_len:
                # take rec_len as longest track
                final_track = np.zeros(rec_len, dtype=np.float32)
                # Adding play_track + rec_track to the final_track
                for i in range(play_len):
                    final_track[i] = (play_track[i] + rec_track[i]) * vol
                # Adding the rest for play_track to the final_track
                for i in range(play_len, rec_len):
                    final_track[i] = rec_track[i] * vol
            elif play_len >= rec_len:
                # take play_len as longest track
                final_track = np.zeros(play_len, dtype=np.float32)
                # Adding rec_track + play_track to the final_track
                for i in range(rec_len):
                    final_track[i] = (rec_track[i] + play_track[i]) * vol
                # Adding the rest of play_track to the final_track
                for i in range(rec_len, play_len):
                    final_track[i] = play_track[i] * vol
            self._play_track = final_track
 
    #-----------------------------------------


    def play(self):
        self._playing =1
        if not self.is_running():
            self.start_driver()
        print("Playing...")

    #-----------------------------------------

    def pause(self):
        """
        pause player
        from Player object
        """

        self._playing =0
        self._paused =1
        if self._recording:
            self.stop_record()
        
    #-----------------------------------------
     
    def stop(self):
        self._playing =0
        if self._recording or self._mixing:
            self.stop_record()
        
        self._mixing =0
        self._wiring =0
        self._pos =0
        print("Stopped...")
        
    #-----------------------------------------
    
    def is_playing(self):
        """
        returns playing state
        from AudioPlayer object
        """
        
        return self._playing

    #-----------------------------------------

    def is_paused(self):
        """
        returns paused state
        from AudioPlayer object
        """
        
        return self._paused

    #-----------------------------------------

    def is_recording(self):
        """
        returns recording state
        from AudioPlayer object
        """
        
        return self._recording

    #-----------------------------------------


    def start_record(self):
        self._rec_pos = self.get_position()
        if self._rec_mode == 0: # replace mode
            self._playing =0
        else:
            self._playing =1
        self._recording =1
        self._mixing =0
        self._rewing =0
        if not self.is_running():
            self.start_driver()
        print("Recording...")
        
    #-----------------------------------------

    def stop_record(self):
        print("Stop Recording...")
        self._recording =0
        self._mixing =0
        self.arrange_track()
        if len(self._deq_data):
            self._deq_data.clear()
        
    #-----------------------------------------

    def toggle_rec_mode(self):
        """
        Returns toggle recording mode
        """
        
        self._rec_mode = not self._rec_mode

        """
        self._rec_pos = self.get_position()
        self._playing =0
        self._recording =0
        self._rec_mode =1 # overdub mode
        self._mixing =1
        self._rewing =0
        if not self.is_running():
            self.start_driver()
        print("Mixing...")
        """

        return self._rec_mode
        
    #-----------------------------------------

    def recwire(self):
        """
        send directly the recording to the output playback
        """

        self._playing =0
        self._recording =0
        self._mixing =0
        self._wiring =1
        if not self.is_running():
            self.start_driver()
        print("Wiring...")
        
    #-----------------------------------------

    def get_position(self, unit=0):
        """ 
        return position 
        position in frames samples, second, or bytes
        from AudioPlayer object
        """

        return self._pos
   
    #-----------------------------------------

    def set_position(self, pos, unit=0):
        """
        sequence player position
        # setposition function take frames samples number
        # frames samples, seconds or bytes
        # unit=0: for frames samples
        # unit=1: for seconds
        # unit=2: for bytes
        from AudioPlayer object
        """

        state =0
        # first convert pos to frames
        if self._playing:
            state =1
        
        if pos >=0 and pos <= self.get_length():
            self._pos = pos

        if state:
            time.sleep(0.1)
            # self.start_seq()
            pass
        
    #-----------------------------------------

    def get_length(self, unit=0):
        """ 
        returns total length in samples
        position in frames samples, second, or bytes
        from Audioplayer 
        """

        return self._play_track.size
       
    #-----------------------------------------

    def rewind(self, step=1):
        """
        rewind the player, 
        step in sec
        from AudioPlayer object
        """
        
        step = step * self._sample_unit
        pos = self.get_position(0) # in frames
        # debug("Dans seq_player, rewind, pos: %.2f" %(pos))
        (div, rest) = divmod(pos, self._sample_unit)    
        if rest:
            pos = div * self._sample_unit
        else:
            pos -= step
        
        self.set_position(pos, 0) # in frames
        
        return pos

    #-----------------------------------------

    def forward(self, step=1):
        """
        forward the player, 
        step in sec
        from AudioPlayer object
        """

        step = step * self._sample_unit
        pos = self.get_position(0) # in frames
        # debug("Dans seq_player, forward, pos: %.2f" %(pos))
        
        (div, rest) = divmod(pos, self._sample_unit)    
        if rest:
            pos = (div + 1 ) * self._sample_unit
        else:
            pos += step
 
        self.set_position(pos, 0) # in frames

        return pos

    #-----------------------------------------
     
    def goto_start(self):
        """
        goto start player
        from AudioPlayer 
        """
        
        pos =0
        self.set_position(pos)
        
        return pos

    #-----------------------------------------

    def goto_end(self):
        """
        goto end player
        from AudioPlayer 
        """
        
        pos = self.get_length()
        self.set_position(pos)

        return pos

    #-----------------------------------------

    def samples_to_sec(self, val):
        """ 
        convert samples number to seconds
        """

        return val / float(self._rate * self._channels)
   
    #------------------------------------------------------------------------------
    
#========================================

def display(msg):
    print(msg)
#------------------------------------------------------------------------------

def main(input_device_index, output_device_index):
    pl = Player()
    pl.init_player(input_device_index, output_device_index)
    # pl.start_driver()
    
    msg = "Press '?' or 'h' for help"
    display(msg)
    sav_str = ''
    while 1:
        val_str = input("-> ")
        if val_str == '': val_str = sav_str
        else: sav_str = val_str

        if val_str in ('q', 'Q'):
            pl.close()
            display("Quit...")
            break

        elif val_str == 'b': # Forward
            pos = pl.forward()
            pos = pl.samples_to_sec(pos)
            msg = f"Time at: {pos:.3f} Secs"
            display(msg)
        elif val_str in (' ', 't', 'p'):
            if not pl.is_playing():
                msg = "Play"
                pl.play()
            else:
                pl.pause()
                pos = pl.get_position()
                pos = pl.samples_to_sec(pos) # convert to sec
                msg = f"Pause at: {pos:.3f} secs"
            display(msg)
        elif val_str == 'T':
            pl.start_driver()
        elif val_str == 'r':
            # toggle record
            if not pl.is_recording():
                pl.start_record()
                msg = "Record"
            else:
                pl.stop_record()
                msg = "Stop Record"
            display(msg)
        elif val_str == 'R':
            # toggle record mode
            val = pl.toggle_rec_mode()
            if val == 0:
                msg = "Record mode Replace"
            else:
                msg = "Record mode Mix"
            display(msg)
        elif val_str == 'S':
            pl.stop_driver()
        elif  val_str == 'u': # Status
            pos = pl.get_position()
            pos = pl.samples_to_sec(pos)
            # start_loop = self.player.get_start_loop()
            # end_loop = self.player.get_end_loop()
            msg = f"Position: {pos:.3f} Secs"
            display(msg)
            # self.display(msg)
        elif val_str == 'v':
            pl.stop()
            pos = pl.get_position()
            pos = pl.samples_to_sec(pos)
            msg = f"Stop at: {pos:.3f} Secs"
            display(msg)
        elif val_str == 'w': # Rewind
            pos = pl.rewind()
            pos = pl.samples_to_sec(pos)
            msg = f"Time at: {pos:.3f} Secs"
            display(msg)
        elif val_str == 'z': # wiring
            pl.recwire()
        elif val_str == '<': # goto start
            pos = pl.goto_start()
            pos = pl.samples_to_sec(pos)
            msg = f"Goto Start at: {pos:.3f} Secs"
            display(msg)
        elif val_str == '>': # goto End
            pos = pl.goto_end()
            pos = pl.samples_to_sec(pos)
            msg = f"Goto End at: {pos:.3f} Secs"
            display(msg)
        elif val_str in ('?', 'h',):
            display(_help)
        elif val_str == 'dev':
            pl.print_devices()


#----------------------------------------

if __name__ == "__main__":
    input_device_index =6 # External Soundcard
    # output_device_index =5 # Default output Soundcard
    output_device_index =6 # External Soundcard
    main(input_device_index, output_device_index)
#----------------------------------------
