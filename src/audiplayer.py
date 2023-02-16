#!/usr/bin/python3
"""
    File: audiplayer.py
    Lite Player klass for AudiNotes.
    Date: Mon, 13/02/2023
    Author: Coolbrother
"""

import time
import numpy as np
from collections import deque
import audiportdriver as aupor
import audimetronome as aumet
import auditrack as autra
import auditools as autol

def beep():
    print("\a")

#-------------------------------------------

class AudiPlayer(object):
    """ Play and record manager """
    def __init__(self, parent=None):
        self._parent = parent
        self._audio_driver = None
        self._channels =2
        self._rate =44100
        self._buf_size = 1024
        self._curtrack = None
        self._pos =0
        self._playing =0
        self._recording =0
        self._paused =0
        self._wiring =0
        self._deq_data = deque()
        self._data_size = self._buf_size * self._channels
        self._sample_unit = self._rate * self._channels
        self._input_latency =0
        self._output_latency =0
        self._shift_samples =0 # shifting samples number for latency
        self._rec_startpos =0
        self._rec_endpos =0
        self._rec_mode =0 # replace mode
        self._rec_shifting =0 # recalculate rec track basec on latency value
        self._clicktrack = aumet.AudiMetronome()
        self._start_playing =0
        self._start_clicking =0
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
        self._audio_driver = aupor.AudiPortDriver()
        self._audio_driver.init_devices(input_device_index, output_device_index)
        self._audio_driver.set_audio_callback(self._audio_callback)
        self._audio_driver.open()
        self._channels = self._audio_driver._channels
        self._rate = self._audio_driver._rate
        self._buf_size = self._audio_driver._buf_size
        self._input_latency = self._audio_driver._input_latency
        self._output_latency = self._audio_driver._output_latency
        lat_ms = self._input_latency + self._output_latency # latency in msec
        self._shift_samples = int(lat_ms * self._rate * self._channels) # in samples
        self._curtrack = autra.AudiTrack()
        # arr = gen_sine_table(freq=440, rate=44100, channels=2, _len=5)

        # """
        # C game
        note_lst = [
                60, 62, 64, 65, 
                67, 69, 71, 72,
                72, 74, 76, 77, 
                79, 81, 83, 84
                ]
        # """

        arr = autol._gen_notes(note_lst, 0.5, 1)
        self._curtrack.set_data(arr)
        self._curtrack.set_looping(1)
        self._rec_mode =1
        self._clicktrack.set_bpm(bpm=120)

    
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
       
        if self._start_playing:
            if self._clicktrack._active:
                self._clicktrack.set_position(curpos)
            self._start_playing =0
        elif self._start_clicking:
            self._clicktrack.set_position(curpos)
            self._start_clicking =0


        # """
        if self._playing:
            # debug(f"curpos: {curpos}, curlen: {curlen}")
            if curpos < curlen:
                curtrack.write_sound_data(out_data, data_count)
            else:
                if self._playing and not self._recording:
                    self.pause()
                    pos = self.samples_to_sec(curpos)
                    msg = f"Paused at: {pos:.3f} Secs"
                    self.notify(msg)
        # """
        
        if self._recording:
            rec_data = np.frombuffer(in_data, dtype=np.float32)
            self._deq_data.append(rec_data)
            if curpos + data_count >= curlen and self._curtrack._looping:
                # debug(f"curpos: {curpos}, curlen: {curlen}")
                self.stop_record()
                # self.arrange_track()
                pass
        elif self._wiring:
            out_data = in_data

        
        # for the metronome at last, to prevent apply effects on it.
        if self._clicktrack._active:
            self._clicktrack.write_sound_data(out_data, data_count)
     
        # beep()
        if not isinstance(out_data, bytes):
            return (out_data.tobytes(), flag_continue)
        
        return (out_data, flag_continue)

    #-----------------------------------------

    def get_data(self, arr, start, stop):
        """ 
        Note: deprecated function
        returns slice array *
        """
        try:
            return arr[start:start+stop]
        except IndexError:
            return np.array([])

    #-----------------------------------------

    def init_track(self):
        """
        init current track
        from AudiPlayer object
        """

        # """
        # C game
        note_lst = [
                60, 62, 64, 65, 
                67, 69, 71, 72,
                # 72, 74, 76, 77, 
                # 79, 81, 83, 84
                ]
        # """

        arr = autol._gen_notes(note_lst, 0.5, 1)
        self._curtrack.set_data(arr)
        self._curtrack.set_looping(1)
        self._rec_mode =1
        self._clicktrack.set_bpm(bpm=120)

    
    #-------------------------------------------

    def replace_data(self, play_data, rec_data):
        """
        returns replacing array by another
        from AudiPlayer object
        """
        
        play_len = play_data.size
        rec_len = rec_data.size
        if play_len < rec_len:
            # Just replacing play_data by rec_data
            return rec_data
        elif play_len >= rec_len:
            # take play_len as longest track
            final_data = np.zeros(play_len, dtype=np.float32)
            # Adding rec_data to the final_data
            for i in range(rec_len):
                final_data[i] = rec_data[i]
            # Adding the rest for play_data to the final_data
            for i in range(rec_len, play_len):
                final_data[i] = play_data[i]
            
            return final_data

    #-------------------------------------------

    def merge_data(self, play_data, rec_data, vol):
        """
        returns array with merging arrays together
        from AudiPlayer object
        """
        
        play_len = play_data.size
        rec_len = rec_data.size
        final_data = np.array([])
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
        
        return final_data

    #-------------------------------------------

    def arrange_track(self):
        """ 
        arranging recorded takes with play_track track
        Note: When recorded data is too long, this function consume too time to execute, 
        therefore, audio_callback function set Status Error 6, certainely, Underflow.
        Use a separate thread must be better.
        """
        
        vol =0.8 # atenuation
        finished =0
        shift_samples =0
        deq_data = self._deq_data
        len_deq = len(deq_data)
        if not len_deq: return
        print("Arranging track...")
        curtrack = self._curtrack
        if not curtrack: return
        play_data = curtrack.get_data()
        play_len = play_data.size
        # extract recorded samples for latency
        if self._rec_shifting:
            shift_samples = self._shift_samples
        if self._rec_startpos > 0 and self._rec_startpos <= play_len:
            # copy play_data part
            if self._rec_mode == 0: # replace mode
                part_data = play_data[shift_samples:self._rec_startpos]
            else:
                if self._rec_startpos > shift_samples:
                    self._rec_startpos -= shift_samples
                part_data = np.zeros(self._rec_startpos)
            # part_data = part_data[1764:]
            # using deq appendleft method for better performance than a list, no need to create a new list
            deq_data.appendleft(part_data)
        # creating rec_data to adding part_data and the deque items
        rec_data = np.concatenate(deq_data)
        if curtrack._looping:
            rec_data = rec_data[:play_len]
        rec_data = rec_data[shift_samples:]
        rec_len = rec_data.size

        # maybe resets position after recording?
        if rec_len >= play_len:
            finished =1
        
        if self._rec_mode == 0: # replace mode
            final_data = self.replace_data(play_data, rec_data)
            curtrack.set_data(final_data)
            
            """
            if play_len < rec_len:
                # Just replacing play_data by rec_data
                curtrack.set_data(rec_data)
            elif play_len >= rec_len:
                # take play_len as longest track
                final_data = np.zeros(play_len, dtype=np.float32)
                # Adding rec_data to the final_data
                for i in range(rec_len):
                    final_data[i] = rec_data[i]
                # Adding the rest for play_data to the final_data
                for i in range(rec_len, play_len):
                    final_data[i] = play_data[i]
                curtrack.set_data(final_data)
            """

        elif self._rec_mode == 1: # mix mode
            final_data = self.merge_data(play_data, rec_data, vol)
            curtrack.set_data(final_data)
 
            """
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
            """

        if  finished and not curtrack._looping:
            curtrack.set_position(rec_len)
            pass
        # time.sleep(3)
    
    #-----------------------------------------


    def play(self):
        # temporary
        clicked =0
        
        """
        pos = self.get_position()
        if pos == 0:
            if self._clicktrack._active:
                self._clicktrack.stop_click()
                clicked =1
        """

        self._playing =1
        self._start_playing =1
        if not self.is_running():
            self.start_driver()
        print("Playing...")

        """
        if clicked:
            self._clicktrack.start_click()
        """

    #-----------------------------------------

    def pause(self):
        """
        pause player
        from Player object
        """

        self._playing =0
        self._start_playing =0
        self._paused =1
        if self._recording:
            self.stop_record()
        
    #-----------------------------------------
     
    def stop(self):
        self._playing =0
        self._start_playing =0
        if self._recording:
            self.stop_record()
        
        self._wiring =0
        self._curtrack.set_position(0)
        if self._clicktrack._active:
            self._clicktrack.stop_click()
            self._start_clicking =0
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
        self._rec_startpos = self.get_position()
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

    def get_bpm(self):
        """
        returns the bpm object
        from AudiPlayer object
        """

        return self._clicktrack._bpm

    #-----------------------------------------


    def set_bpm(self, bpm):
        """
        sets the metronome bpm
        from AudiPlayer object
        """

        state =0
        if self._clicktrack._active: 
            self._clicktrack.stop_click()
            state =1
        self._clicktrack.set_bpm(bpm)
        if state:
            self._clicktrack.start_click()

        return self._clicktrack._bpm
    
#-----------------------------------------



    def toggle_click(self):
        """
        change metronome click state
        from AudiPlayer object
        """

        if self._clicktrack._active: 
            self._clicktrack.stop_click()
            self._start_clicking =0
        else: 
            self._clicktrack.start_click()
            self._start_clicking =1
            if not self.is_running():
                self.start_driver()

        return self._clicktrack._active
    
    #-----------------------------------------

    def toggle_loop(self):
        """
        change looping state
        from AudiPlayer object
        """

        if not self._curtrack: return 0
        return self._curtrack.toggle_loop()
    
    #-----------------------------------------

    def toggle_mute(self):
        """
        change muted state
        from AudiPlayer object
        """

        if not self._curtrack: return 0
        return self._curtrack.toggle_mute()
    
    #-----------------------------------------

    def samples_to_sec(self, val):
        """ 
        convert samples number to seconds
        """

        return val / float(self._rate * self._channels)
   
    #------------------------------------------------------------------------------
    
#========================================

if __name__ == "__main__":
    pl = AudiPlayer()
    _len = pl.get_length()
    print(f"Player len: {_len}")
    input("It's OK...")
#-----------------------------------------
