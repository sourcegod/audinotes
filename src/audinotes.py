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

import os, sys, time
import readline
import audiplayer as aupla
import audimixer as aumix

_DEBUG =1
_help = """ Help on AudiNotes Player
  b: forward
  k: toggle click
  h, ?: print this help
  l: toggle loop
  p, t, space: toggle play pause
  q, Q: quit
  r: toggle record
  R: toggle record mode (replace, mix)
  v: stop
  w: rewind
  x: toggle mute
  z: wiring
  <: goto start
  >: goto end

  bpm VAL: set bpm
  dev: display devices infomations
  eng, engine on/off: toggle audio engine
  init: init track
  sta, status: display player status and position in secs
  test: testing

"""

def debug(msg="", title="", bell=True):
    if _DEBUG:
        if title: msg = f"{title}: {msg}"
        print(msg)
        if bell: print("\a")
    
#------------------------------------------------------------------------------

def beep():
    print("\a")

#-------------------------------------------

class MainApp(object):
    """ Main application manager """
    def __init__(self):
        self.mixer = None
        self.player = None
        self.audio_driver = None

    #------------------------------------------------------------------------------

    def clear_screen(self, numlines=100):
        """
        simply clear the screen for Windows or Linux plateform
        from MainApp object
        """

        os.system('cls||clear')

    #------------------------------------------------------------------------------

    def display(self, msg):
        """
        display message
        from MainApp object
        """

        print(msg)

    #------------------------------------------------------------------------------

    def init_app(self, input_device_index, output_device_index):
        self.mixer = aumix.AudiMixer()
        self.mixer.init(channels=1, rate=44100, format=None, input_device_index=input_device_index, output_device_index=output_device_index)
        self.audio_driver = self.mixer.audio_driver

        self.player = aupla.AudiPlayer(parent=self)
        self.player.init_player(self.mixer)
        # pl.start_engine()
        self.clear_screen()

    #------------------------------------------------------------------------------

    def change_engine(self, param=None):
        if param is None: return
        if param == "on":
            self.mixer.start_driver()
        elif param == "off":
            self.mixer.stop_driver()

    #-------------------------------------------

    def print_devices(self):
        """
        display devices info
        from MainApp object
        """

        self.mixer.print_devices()

    #-------------------------------------------

    def change_bpm(self, bpm, adding=0):
        if self.mixer is None: return
        cur_bpm = self.player.get_bpm()
        if type(bpm) == str:
            if bpm[0] in ('+', '-'): adding=1
        bpm = float(bpm)
        if adding == 1: # is incremental
            bpm += cur_bpm

        cur_bpm = self.player.set_bpm(bpm)
        msg = f"Bpm: {cur_bpm}"
        self.display(msg)

    #-------------------------------------------

    def set_audio_devices(self, input_index, output_index):
        if self.mixer is None: return
        if input_index is not None: input_index = int(input_index)
        if output_index is not None: output_index = int(output_index)
        (in_index, out_index) = self.mixer.set_audio_devices(input_index, output_index)
        msg = f"Set Audio devices: ({in_index}, {out_index})"
        self.display(msg)

    #-------------------------------------------

    def main(self, input_device_index, output_device_index):
        self.init_app(input_device_index, output_device_index)
        msg = "Press '?' or 'h' for help"
        
        self.display(msg)
        sav_str = ''

        try:
            while 1:

                key = param1 = param2 = param3 = None
                val_str = input("-> ")
                if val_str == '': val_str = sav_str
                else: sav_str = val_str

                if val_str == " ":
                    key = val_str
                else:
                    lst = val_str.split()
                    len_lst = len(lst)
                    if len_lst >0: key = lst[0]
                    if len_lst >1: param1 = lst[1]
                    if len_lst >2: param2 = lst[2]
                    if len_lst >3: param3 = lst[3]

                
                if key in ('q', 'Q'):
                    self.player.close()
                    self.display("Quit...")
                    break

                elif key == 'b': # Forward
                    pos = self.player.forward()
                    pos = self.player.samples_to_sec(pos)
                    msg = f"Time at: {pos:.3f} Secs"
                    self.display(msg)
                elif key in (' ', 't', 'p'):
                    if not self.player.is_playing():
                        msg = "Play"
                        self.player.play()
                    else:
                        self.player.pause()
                        pos = self.player.get_position()
                        pos = self.player.samples_to_sec(pos) # convert to sec
                        msg = f"Pause at: {pos:.3f} secs"
                    self.display(msg)
                elif key == 'k':
                    val = self.player.toggle_click()
                    if val: msg = "Start Clicking"
                    else: msg = "Stop Clicking"
                    self.display(msg)
                elif key == 'l':
                    val = self.player.toggle_loop()
                    if val: msg = "Start Looping"
                    else: msg = "Stop Looping"
                    self.display(msg)
                elif key == 'r':
                    # toggle record
                    val = self.player.toggle_record()
                    if val: msg = "Start Record"
                    else: msg = "Stop Record"
                    self.display(msg)

                elif key == 'R':
                    # toggle record mode
                    val = self.player.toggle_rec_mode()
                    if val == 0:
                        msg = "Record mode Replace"
                    else:
                        msg = "Record mode Mix"
                    self.display(msg)
                elif key == 'v':
                    self.player.stop()
                    pos = self.player.get_position()
                    pos = self.player.samples_to_sec(pos)
                    msg = f"Stop at: {pos:.3f} Secs"
                    self.display(msg)
                elif key == 'w': # Rewind
                    pos = self.player.rewind()
                    pos = self.player.samples_to_sec(pos)
                    msg = f"Time at: {pos:.3f} Secs"
                    self.display(msg)
                elif key == 'x':
                    val = self.player.toggle_mute()
                    if val: msg = "Muted On"
                    else: msg = "Muted Off"
                    self.display(msg)
                elif key == 'z': # wiring
                    self.player.recwire()
                elif key == '<': # goto start
                    pos = self.player.goto_start()
                    pos = self.player.samples_to_sec(pos)
                    msg = f"Goto Start at: {pos:.3f} Secs"
                    self.display(msg)
                elif key == '>': # goto End
                    pos = self.player.goto_end()
                    pos = self.player.samples_to_sec(pos)
                    msg = f"Goto End at: {pos:.3f} Secs"
                    self.display(msg)
                elif key in ('?', 'h',):
                    self.display(_help)

                elif key == 'bpm':
                    # change bpm
                    if not param1: param1 = "120"
                    self.change_bpm(param1, adding=0) # can be incremental or decremental with (+, -)
                    
                elif key == 'dev':
                    if param1 is None:
                        self.print_devices()
                    else:
                        self.set_audio_devices(param1, param2)
                elif key in ('eng', 'engine'):
                    self.change_engine(param1)
                elif key == 'init':
                    self.player.init_track()
                elif  key in ('sta', 'status'): # Status
                    state = self.player.get_state()
                    pos = self.player.get_position()
                    pos = self.player.samples_to_sec(pos)
                    # start_loop = self.player.get_start_loop()
                    # end_loop = self.player.get_end_loop()
                    msg = f"{state}, Position: {pos:.3f} Secs"
                    self.display(msg)
                elif key == 'test':
                    self.test()
                 
                else:
                    msg = "Command not found"
                    self.display(msg)
        finally:
            # save history file
            pass

    #----------------------------------------

    def test(self):
        """
        testing function
        from MainApp object
        """
        
        self.display("Testing...")

        lat_ms = self.player._input_latency + self.player._output_latency # latency in msec
        rate = self.player._rate
        channels = self.player._channels
        shift_samples = int(lat_ms * rate * channels) # in samples
        print(f"lat_ms: {lat_ms}, rate: {rate}, channels: {channels}")
        print(f"Shift Samples: {shift_samples}")
        # self.player.init_track()

    #----------------------------------------

#========================================


if __name__ == "__main__":
    input_device_index =6 # External Soundcard
    # output_device_index =5 # Default output Soundcard
    output_device_index =6 # External Soundcard
    app = MainApp()
    app.main(input_device_index, output_device_index)
#----------------------------------------
