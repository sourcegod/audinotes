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
  S: stop the Engine
  T: start the Engine
  v: stop
  w: rewind
  x: toggle mute
  z: wiring
  <: goto start
  >: goto end

  bpm: set bpm
  bpmd: dec bpm
  bpmi: inc bpm
  dev: display devices infomations
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

    def start_engine(self):
        self.mixer.start_driver()

    #-------------------------------------------
    
    def stop_engine(self):
        # self.player.stop()
        self.mixer.stop_driver()

    #-------------------------------------------
 
    def print_devices(self):
        """
        display devices info
        from MainApp object
        """

        self.mixer.print_devices()

    #-------------------------------------------


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
            elif val_str == 'k':
                val = self.player.toggle_click()
                if val: msg = "Start Clicking"
                else: msg = "Stop Clicking"
                self.display(msg)
            elif val_str == 'l':
                val = self.player.toggle_loop()
                if val: msg = "Start Looping"
                else: msg = "Stop Looping"
                self.display(msg)
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
            elif val_str == 'x':
                val = self.player.toggle_mute()
                if val: msg = "Muted On"
                else: msg = "Muted Off"
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

            elif val_str == 'bpm':
                # Set bpm
                bpm = self.player.set_bpm(120)
                msg = f"Set bpm: {bpm}"
                self.display(msg)
            elif val_str == 'bpmd':
                # Dec bpm
                bpm = self.player.get_bpm()
                bpm = self.player.set_bpm(bpm - 10)
                msg = f"Dec bpm: {bpm}"
                self.display(msg)
            elif val_str == 'bpmi':
                # inc bpm
                bpm = self.player.get_bpm()
                bpm = self.player.set_bpm(bpm + 10)
                msg = f"Inc bpm: {bpm}"
                self.display(msg)
            elif val_str == 'dev':
                self.print_devices()
            elif val_str == 'engsta':
                self.start_engine()
            elif val_str == 'engsto':
                self.stop_engine()
            elif val_str == 'init':
                self.player.init_track()
            elif  val_str in ('sta', 'status'): # Status
                state = self.player.get_state()
                pos = self.player.get_position()
                pos = self.player.samples_to_sec(pos)
                # start_loop = self.player.get_start_loop()
                # end_loop = self.player.get_end_loop()
                msg = f"{state}, Position: {pos:.3f} Secs"
                self.display(msg)
            elif val_str == 'test':
                self.test()
             
            else:
                msg = "Command not found"
                self.display(msg)

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
