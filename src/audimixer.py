#!/usr/bin/python3
"""
    File: audimixer.py
    Mixer V2
    Lite Mixer klass to manage audio drivers
    Date: Thu, 16/02/2023
    Author: Coolbrother
"""

import audiportdriver as aupor

def beep():
    print("\a")

#-------------------------------------------

class AudiMixer(object):
    """ Singleton object
    Mixer object to manage audio drivers 
    """
    __single_instance = None
    @staticmethod
    def get_instance():
        """ Static access method """
        if AudiMixer.__single_instance is None:
            AudiMixer()
        return AudiMixer.__single_instance

    def __init__(self, audio_driver=None):
        if AudiMixer.__single_instance != None:
            raise exception("This Klass is a singleton klass.")
        else:
            AudiMixer.__single_instance = self
        
        self.audio_driver = None
        # self._audio_driver = AlsaAudioDriver()
        if audio_driver is None or audio_driver == "port":
            self.audio_driver = aupor.AudiPortDriver()
        # must be the same as buf_size in PortAudio Driver
        self._buf_size =512
        self._channels =1 # TODO: why nchannels not been initialized by init function?
        self._rate = 44100
        self._format =0
    #-----------------------------------------

    def init(self, channels=2, rate=44100, format=None, input_device_index=None, output_device_index=None):
        if self.audio_driver is None: return
        
        self._channels = channels
        self._rate = rate
        if format is None: format = self._format
        else: self._format = format
        
        # self.audio_driver.set_callback(self._audio_callback)
        self.audio_driver.init_params(channels, rate, format)
        self.audio_driver.init_devices(input_device_index, output_device_index)

    #-----------------------------------------

    def set_audio_callback(self, audio_callback):
        if self.audio_driver is None: return
        self.audio_driver.set_audio_callback(audio_callback)

    #-----------------------------------------

    def open(self):
        if self.audio_driver is None: return
        self.audio_driver.open()

    #-----------------------------------------

    def start_driver(self):
        if self.audio_driver is None: return
        self.audio_driver.start_engine()
        beep()

    #-------------------------------------------
    
    def stop_driver(self):
        if self.audio_driver is None: return
        self.audio_driver.stop_engine()
        beep()

    #-------------------------------------------
     
    def close(self):
        """ Close the mixer """
        if self.audio_driver is None: return
        self.audio_driver.stop_engine()
        self.audio_driver.close()

    #-------------------------------------------

    def is_running(self):
        if self.audio_driver is None: return
        return self.audio_driver.is_running()

    #-------------------------------------------

    def print_devices(self):
        """
        display devices info
        from Mixer object
        """

        if self.audio_driver is None: return
        self.audio_driver.print_devices()

    #-------------------------------------------


#========================================


if __name__ == "__main__":
    app = AudiMixer()
    app.init()
    input("It's OK...")

#-----------------------------------------
