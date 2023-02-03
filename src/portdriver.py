#!/usr/bin/python3 
"""
    File: portdriver.py
    portdriver module
    Portaudio module with pyaudio

    Last update: Wed, 01/02/2023
    Version: 0.2
    -- Adding functions:
    is_running, query_devices, print_devices


    
    Date: Tue, 31/01/2023
    Author: Coolbrother
"""
import pyaudio

class PortDriver(object):
    """ PortAudio driver manager  """
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self._buf_size = 1024
        self._rate =44100
        self._channels =2 # FIX: work fine with channels 2
        # Format work with paInt16 or paFloat32, for default Soundcard.
        # self._format = pyaudio.paInt16
        self._format = pyaudio.paFloat32
        self._input_device_index = None
        self._output_device_index = None
        self._default_input_index = None
        self._default_output_index = None
        self._callback_func = None
        self._running = False

    #-------------------------------------------

    def open(self):
        try:
            self._stream = self._pa.open(
                            format = self._format, 
                            channels = self._channels, 
                            rate = self._rate, # wf.getframerate(),
                            input_device_index = self._input_device_index,
                            output_device_index = self._output_device_index,
                            input = True,
                            output = True,
                            stream_callback = self._callback_func,
                            start = False,
                            frames_per_buffer = self._buf_size
                            )
        except OSError as err:
            print("[PortAudio Error]: error to open input or output device index", err)
            self._stream = None

        if self._stream is None:
            self._output_device_index = self._default_output_index
            self._input_device_index = self._default_input_index
            try:
                self._stream = self._pa.open(
                                format = self._format, 
                                channels = self._channels, 
                                rate = self._rate, # wf.getframerate(),
                                input_device_index = self._input_device_index,
                                output_device_index = self._output_device_index,
                                input = True,
                                output = True,
                                stream_callback = self._callback_func,
                                start = False,
                                frames_per_buffer = self._buf_size
                                )
            except OSError as err:
                print("[PortAudio Error]: error to open input or output device index", err)
                self._stream = None

    #-----------------------------------------

    def start_engine(self):
        if self._stream and not self._running:
            self._stream.start_stream()
            print("Starting Engine...")
            self._running = True
        
    #-----------------------------------------

    def stop_engine(self):
        self._running = False
        if self._stream:
            self._stream.stop_stream()
            print("Stopping Engine...")

    #-----------------------------------------

    def close(self):    
        if self._stream:
            self._stream.close()
            print("Closing the Stream")
        
        self._pa.terminate()
        print("Closing the driver")

    #-----------------------------------------

    def init_devices(self, input_device_index=None, output_device_index=None):
        """ initialize default devices index """
        self._input_device_index = input_device_index
        self._output_device_index = output_device_index
        self._default_input_index = self._pa.get_default_input_device_info().get('defaultInputDevice')
        self._default_output_index = self._pa.get_default_output_device_info().get('defaultOutputDevice')

    #-------------------------------------------

    def is_running(self):
        return self._running

    #-------------------------------------------

    def set_audio_callback(self, audio_callback):
        self._callback_func = audio_callback

    #-------------------------------------------

    def get_driver_names(self):
        """ return list of host api names
        """

        lst = []
        count =0
        count = self._pa.get_host_api_count()
        for i in range(count):
            dic = self._pa.get_host_api_info_by_index(i)
            try:
                    name = dic.get('name')
                    lst.append((i, name))
            except KeyError:
                pass

        return lst

    #-----------------------------------------
       
    def get_device_list(self):
        """ return list containing all devices info in a dictionary
        """
        lst = []
        count = self._pa.get_device_count()
        for i in range(count):
            lst.append(self._pa.get_device_info_by_index(i))
        
        return lst
    #-----------------------------------------

    def query_devices(self):
        """
        Returns list of dict with devices info
        from PortAudioDriver object
        """
        
        lst = []
        for  (index, item) in enumerate(self.get_device_list()):
            mark = ""
            host_index = item['hostApi']
            host_name = self.get_driver_names()[host_index][1]
            if item['name'] == "default": mark = "*"
            dic = {}
            dic['index'] = f"{mark} {item['index']}" 
            dic['name'] = f"{item['name']}"
            dic['hostName'] = f"{host_name}" 
            dic['maxInputChannels'] = f"{item['maxInputChannels']} In"
            dic['maxOutputChannels'] = f"{item['maxOutputChannels']} Out"
            lst.append(dic.copy())

            """
            print(f"{mark} {item['index']} {item['name']},", 
                f"{host_name} ({item['maxInputChannels']} In, {item['maxOutputChannels']} Out)")
            """
            
        return lst
    #-----------------------------------------

    def print_devices(self):
        print("Devices list")
        dic_lst = self.query_devices()
        for dic in dic_lst:
            index = dic['index']
            name = dic['name']
            hostName = dic['hostName']
            maxInputChannels = dic['maxInputChannels']
            maxOutputChannels = dic['maxOutputChannels']
            print(f"{index} {name},", \
                    f"{hostName} ({maxInputChannels}, {maxOutputChannels}")

    #-----------------------------------------


    def get_default_input_device(self):
        """ return tuple containing indexes input for both channels  
        """

        return self._pa.get_default_input_device_info().get('defaultInputDevice')

    #-----------------------------------------

    def get_default_output_device(self):
        """ return tuple containing indexes output for both channels  
        """

        return _pa.get_default_input_device_info().get('defaultOutputDevice')

    #-----------------------------------------

#========================================

def main():
    _audio_driver = PortDriver()
    _audio_driver.print_devices()

#-----------------------------------------

if __name__ == "__main__":
    main()
    input("Tapez Enter...")
#-----------------------------------------
