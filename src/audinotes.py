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
  w: rewind
  v: stop
  z: wiring
  <: goto start
  >: goto end
  dev: display devices infomations
  sta, status: display player status and position in secs

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

    def write_sound(self, out_data, data_count):
        """
        writing curdata to the out_data
        from AudiTrack object
        """

        curdata = self._buf_arr
        if not curdata.size: return
        pos = self._pos
        _len = self._len
        
        if self._muted or self._arm_muted:
            # dont write any data, just increment curpos
            for i in range(data_count):
                if pos < _len:
                    pos += 1
        else:
            for i in range(data_count):
                if pos < _len:
                    out_data[i] = curdata[pos]
                    pos += 1
        self._pos = pos
    
    #-----------------------------------------
#========================================

class AudiPlayer(object):
    """ Play and record manager """
    def __init__(self, parent=None):
        self._parent = parent
        self._audio_driver = None
        self._channels =2
        self._rate =44100
        self._buf_size = 1024
        self._play_track = None
        # self._play_track = get_sine_table(freq=440, rate=44100, channels=2, _len=5)
        self._curtrack = None
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

    def notify(self, msg):
        """
        Send message to the parent object 
        from AudiPlayer object
        """

        if self._parent:
            self._parent.display(msg)
    #-------------------------------------------
    
    def init_player(self, input_device_index, output_device_index):
        self._audio_driver = pdv.PortDriver()
        self._audio_driver.init_devices(input_device_index, output_device_index)
        self._audio_driver.set_audio_callback(self._audio_callback)
        self._audio_driver.open()
        self._channels = self._audio_driver._channels
        self._rate = self._audio_driver._rate
        self._buf_size = self._audio_driver._buf_size
        self._curtrack = AudiTrack()
        arr = get_sine_table(freq=440, rate=44100, channels=2, _len=5)
        self._curtrack.set_data(arr)

    
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
            
        data_count = frame_count  * self._channels
        out_data = np.zeros(data_count, dtype=np.float32)
        # print(f"frame_count: {frame_count}")
        
        curtrack = self._curtrack
        curdata = curtrack.get_data()
        curpos = curtrack._pos
        curlen = curtrack._len
        # Test recording before playing to be faster
        if self._recording:
            rec_data = np.frombuffer(in_data, dtype=np.float32)
            self._deq_data.append(rec_data)
        elif self._wiring:
            out_data = in_data

        if self._playing:
            if curpos < curlen:
                curtrack.write_sound(out_data, data_count)
            else:
                if self._playing and not self._recording:
                    self.pause()
                    pos = self.samples_to_sec(curpos)
                    msg = f"Paused at: {pos:.3f} Secs"
                    self.notify(msg)

        # beep()
        if not isinstance(out_data, bytes):
            return (out_data.tobytes(), flag_continue)
        
        return (out_data, flag_continue)

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
        curtrack = self._curtrack
        if not curtrack: return
        play_data = curtrack.get_data()
        # play_data = self._play_data
        play_len = play_data.size
        if self._rec_pos > 0 and self._rec_pos <= play_len:
            # copy play_data part
            if self._rec_mode == 0: # replace mode
                part_data = play_data[:self._rec_pos]
            else:
                part_data = np.zeros(self._rec_pos)
            lst.append(part_data)
        lst.extend([self._deq_data.popleft() for i in range(len_deq)])
        # creating rec_data to adding part_track and the deque items
        rec_data = np.concatenate(lst)
        rec_len = rec_data.size
        
        if self._rec_mode == 0: # replace mode
            if play_len < rec_len:
                # Just replacing play_data by rec_data
                curtrack.set_data(rec_data)
                # self._play_data = rec_data
            elif play_len >= rec_len:
                # print(f"voici play_len: {play_len}, rec_len: {rec_len}")
                # take play_len as longest track
                final_data = np.zeros(play_len, dtype=np.float32)
                # Adding rec_data to the final_data
                for i in range(rec_len):
                    final_data[i] = rec_data[i]
                # Adding the rest for play_data to the final_data
                for i in range(rec_len, play_len):
                    final_data[i] = play_data[i]
                curtrack.set_data(final_data)
       
        elif self._rec_mode == 1: # mix mode
            if play_len < rec_len:
                # take rec_len as longest track
                final_data = np.zeros(rec_len, dtype=np.float32)
                # Adding play_data + rec_data to the final_data
                for i in range(play_len):
                    final_data[i] = (play_data[i] + rec_data[i]) * vol
                # Adding the rest of rec_data to the final_data
                for i in range(play_len, rec_len):
                    final_data[i] = rec_data[i] * vol
            elif play_len >= rec_len:
                # take play_len as longest track
                final_data = np.zeros(play_len, dtype=np.float32)
                # Adding rec_data + play_data to the final_data
                for i in range(rec_len):
                    final_data[i] = (rec_data[i] + play_data[i]) * vol
                # Adding the rest of play_data to the final_data
                for i in range(rec_len, play_len):
                    final_data[i] = play_data[i] * vol
            curtrack.set_data(final_data)
 
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
        self._curtrack.set_position(0)
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

    def get_state(self):
        """ 
        Returns player state
        """

        msg = ""
        if self._playing and not self._recording: msg = "Playing"
        elif self._recording: msg = "Recording"
        elif self._paused: msg = "Paused"
        else: msg = "Stopped"

        return msg
   
    #-----------------------------------------



    def start_record(self):
        if not self._curtrack: return
        self._rec_pos = self.get_position()
        if self._rec_mode == 0: # replace mode
            self._curtrack.set_arm_muted(1)
        self._playing =1
        self._recording =1
        self._rewing =0
        if not self.is_running():
            self.start_driver()
        print("Recording...")
        
    #-----------------------------------------

    def stop_record(self):
        print("Stop Recording...")
        self._recording =0
        self._curtrack.set_arm_muted(0)
        self.arrange_track()
        if len(self._deq_data):
            self._deq_data.clear()
        
    #-----------------------------------------
    
    def toggle_record(self):
        """
        Returns recording state
        """
        
        if not self._recording:
            self.start_record()
        else:
            self.stop_record()
        
        return self._recording
    
    #-----------------------------------------

    def toggle_rec_mode(self):
        """
        Returns recording mode state
        """
        
        self._rec_mode = not self._rec_mode

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

        if not self._curtrack: return 0
        return self._curtrack._pos

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

        if not self._curtrack: return
        state =0
        if self._playing:
            state =1
        
        self._curtrack.set_position(pos)
        if state:
            time.sleep(0.1)
            self.play()
            pass
        
    #-----------------------------------------

    def get_length(self, unit=0):
        """ 
        returns total length in samples
        position in frames samples, second, or bytes
        from Audioplayer 
        """

        if not self._curtrack: return 0
        return self._curtrack._len

       
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

class MainApp(object):
    """ Main application manager """
    def __init__(self):
        self.player = None
        pass

    #------------------------------------------------------------------------------

    def display(self, msg):
        print(msg)

    #------------------------------------------------------------------------------

    def init_app(self, input_device_index, output_device_index):
        self.player = AudiPlayer(parent=self)
        self.player.init_player(input_device_index, output_device_index)
        # pl.start_driver()

    #------------------------------------------------------------------------------
 
    def main(self, input_device_index, output_device_index):
        self.init_app(input_device_index, output_device_index)
        msg = "Press '?' or 'h' for help"
        
        self.display(msg)
        sav_str = ''
        while 1:
            val_str = input("-> ")
            if val_str == '': val_str = sav_str
            else: sav_str = val_str

            if val_str in ('q', 'Q'):
                self.player.close()
                self.display("Quit...")
                break

            elif val_str == 'b': # Forward
                pos = self.player.forward()
                pos = self.player.samples_to_sec(pos)
                msg = f"Time at: {pos:.3f} Secs"
                self.display(msg)
            elif val_str in (' ', 't', 'p'):
                if not self.player.is_playing():
                    msg = "Play"
                    self.player.play()
                else:
                    self.player.pause()
                    pos = self.player.get_position()
                    pos = self.player.samples_to_sec(pos) # convert to sec
                    msg = f"Pause at: {pos:.3f} secs"
                self.display(msg)
            elif val_str == 'T':
                self.player.start_driver()
            elif val_str == 'r':
                # toggle record
                val = self.player.toggle_record()
                if val: msg = "Start Record"
                else: msg = "Stop Record"
                self.display(msg)

            elif val_str == 'R':
                # toggle record mode
                val = self.player.toggle_rec_mode()
                if val == 0:
                    msg = "Record mode Replace"
                else:
                    msg = "Record mode Mix"
                self.display(msg)
            elif val_str == 'S':
                self.player.stop_driver()
            elif  val_str in ('sta', 'status'): # Status
                state = self.player.get_state()
                pos = self.player.get_position()
                pos = self.player.samples_to_sec(pos)
                # start_loop = self.player.get_start_loop()
                # end_loop = self.player.get_end_loop()
                msg = f"{state}, Position: {pos:.3f} Secs"
                self.display(msg)
                # self.self.display(msg)
            elif val_str == 'v':
                self.player.stop()
                pos = self.player.get_position()
                pos = self.player.samples_to_sec(pos)
                msg = f"Stop at: {pos:.3f} Secs"
                self.display(msg)
            elif val_str == 'w': # Rewind
                pos = self.player.rewind()
                pos = self.player.samples_to_sec(pos)
                msg = f"Time at: {pos:.3f} Secs"
                self.display(msg)
            elif val_str == 'z': # wiring
                self.player.recwire()
            elif val_str == '<': # goto start
                pos = self.player.goto_start()
                pos = self.player.samples_to_sec(pos)
                msg = f"Goto Start at: {pos:.3f} Secs"
                self.display(msg)
            elif val_str == '>': # goto End
                pos = self.player.goto_end()
                pos = self.player.samples_to_sec(pos)
                msg = f"Goto End at: {pos:.3f} Secs"
                self.display(msg)
            elif val_str in ('?', 'h',):
                self.display(_help)
            elif val_str == 'dev':
                self.player.print_devices()


    #----------------------------------------

#========================================


if __name__ == "__main__":
    input_device_index =6 # External Soundcard
    # output_device_index =5 # Default output Soundcard
    output_device_index =6 # External Soundcard
    app = MainApp()
    app.main(input_device_index, output_device_index)
#----------------------------------------
