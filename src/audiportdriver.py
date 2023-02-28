#!/usr/bin/python3 
"""
    File: audiportdriver.py
    portdriver module
    Portaudio module with pyaudio

    Last update: Wed, 15/02/2023
    Modifying the audio buffer size from 1024 to 256 for better performance, 
    less latencywhen recording.
    Note: 
    -- With Default Soundcard,
    buf_size=1024: latency=0.046 msec
    buf_size=256: latency=0.021 msec 
    
    -- With Scarlett 2i2 Soundcard,
    buf_size=1024: latency=0.023 msec
    buf_size=256: latency=0.012 msec 

    Last update: Tue, 14/02/2023
    Version: 0.3
    -- Updating: change file name from portdriver.py to audiportdriver.py
    -- Change klass name from PortDriver to AudiPortDriver
    -- Adding functions: get_input_latency, get_output_latency

    Last update: Wed, 01/02/2023
    Version: 0.2
    -- Adding functions:
    is_running, query_devices, print_devices


    
    Date: Tue, 31/01/2023
    Author: Coolbrother
"""
import pyaudio

class AudiPortDriver(object):
    """ PortAudio driver manager  """
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._stream = None
        # Better latency with 256: 0.012 msec for Scarlett 2i2 Soundcard
        self._buf_size = 256 # 1024
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
        self._opened = False
        self._input_latency =0
        self._output_latency =0

    #-------------------------------------------

    def __del__(self):
        self._pa.terminate()
        print("Terminate the Audio Driver")

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
        # get stream latency
        if self._stream:
            self._opened = True
            self._input_latency = self._stream.get_input_latency()
            self._output_latency = self._stream.get_output_latency()

    #-----------------------------------------

    def get_input_latency(self):
        if self._stream:
            return self._stream.get_input_latency()

        return 0

    #-----------------------------------------

    def get_output_latency(self):
        if self._stream:
            return self._stream.get_output_latency()

        return 0

    #-----------------------------------------

    def start_engine(self):
        if self._stream and not self._running:
            self._stream.start_stream()
            print("Starting Engine...")
            self._running = True
        if self._stream:
            input_latency = self._stream.get_input_latency()
            output_latency = self._stream.get_output_latency()
            print(f"Input latency: {input_latency:.3f}, output latency: {output_latency:.3f}")
        
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
            self._stream = None
            self._opened = False
            print("Closing the Stream")
        
        print("Closing the driver")

    #-----------------------------------------

    def init_params(self, channels, rate, format):
        """ 
        initialize default params
        """

        self._channels = channels
        self._rate = rate


    #-------------------------------------------


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

    def is_opened(self):
        return self._opened

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
        
        print("Devices latencies")
        print(f"input latency: {self._input_latency:.3f}, output latency: {self._output_latency:.3f}")

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
    _audio_driver = AudiPortDriver()
    _audio_driver.print_devices()
    stream = _audio_driver.open()
    print("After opening stream")
    input_latency = _audio_driver.get_input_latency()
    output_latency = _audio_driver.get_output_latency()
    print(f"input latency: {input_latency:.3f}, output latency: {output_latency:.3f}")

#-----------------------------------------

if __name__ == "__main__":
    main()
    input("Tapez Enter...")
#-----------------------------------------
