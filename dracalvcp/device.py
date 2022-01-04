import serial
import threading
from contextlib import suppress
from libscrc import xmodem


class Device:
    """Atmospheric-sensor device."""
    DEFAULT_TIMEOUT = 2

    def __init__(self, comport, product=None, serial_id=None):
        """Open a connection to a device via comport."""
        # Initialize serial device
        self.serial_device = serial.Serial(comport, baudrate=115200, timeout=self.DEFAULT_TIMEOUT)

        # Product / serial ID
        self.product = product
        self.serial_id = serial_id
        
        # Data
        self.data_lock = threading.Lock()
        self.press_initialized = threading.Event()
        self.press = None
        self.temp_initialized = threading.Event()
        self.temp = None
        self.hum_initialized = threading.Event()
        self.hum = None
        self.co2_initialized = threading.Event()
        self.co2 = None
        
        # Start reader thread
        self.stop_reader_thread = threading.Event()
        self.reader_thread_handle = threading.Thread(target=self.reader_thread)
        self.reader_thread_handle.start()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        """Close the connection to the device."""
        # Join reader thread
        self.stop_reader_thread.set()
        self.reader_thread_handle.join()
        
        # Close serial connection
        self.serial_device.close()

    def send_string(self, string):
        """Send a string to the device."""
        self.serial_device.write((string+'\r').encode('ascii'))
  
    def receive_string(self):
        """Receive string from a device."""
        return self.serial_device.readline().decode('ascii').rstrip()

    def reader_thread(self):
        """Start main loop of reader."""
        # Reader main loop
        while not self.stop_reader_thread.is_set():
            # Read data
            string_in = self.receive_string()
            if string_in != '':
                with suppress(IndexError):  # Suppress IndexErrors while parsing
                    # Parse data
                    frame = string_in.split(',')
                    line_type = frame[0]
                    product = frame[1]
                    serial_id = frame[2]
                    # message = frame[3]
                    data = {U: D for D, U, in zip(frame[4:-2:2], frame[5:-1:2])}
                    crc16_received = int(frame[-1][1:], 16)
                    crc16_computed = xmodem(string_in[:-5].encode('ascii'))

                    if crc16_received != crc16_computed:
                        # Invalid checksum
                        pass
                    elif (self.product is not None) and (self.product != product):
                        # Invalid product ID
                        pass
                    elif (self.serial_id is not None) and (self.serial_id != serial_id):
                        # Invalid serial ID
                        pass
                    elif line_type == 'D':
                        # Data
                        with self.data_lock:
                            if 'Pa' in data:
                                self.press = int(data['Pa'])
                                self.press_initialized.set()
                            if 'C' in data:
                                self.temp = float(data['C'])
                                self.temp_initialized.set()
                            if '%' in data:
                                self.hum = float(data['%'])
                                self.hum_initialized.set()
                            if 'ppm' in data:
                                self.co2 = float(data['ppm'])
                                self.co2_initialized.set()

    def get_press(self):
        """Get atmospheric pressure.

        Returns: pressure (Pa)
        """
        if not self.press_initialized.wait(timeout=self.DEFAULT_TIMEOUT):
            raise TimeoutError('Timeout while waiting for data!')
            
        with self.data_lock:
            return self.press
        
    def get_temp(self):  # (°C)
        """Get atmosperhic temperature.

        Returns: temperature (°C)
        """
        if not self.temp_initialized.wait(timeout=self.DEFAULT_TIMEOUT):
            raise TimeoutError('Timeout while waiting for data!')
        
        with self.data_lock:
            return self.temp
        
    def get_hum(self):  # (%)
        """Get relative humdity.

        Returns: rel. humidity (%)
        """
        if not self.hum_initialized.wait(timeout=self.DEFAULT_TIMEOUT):
            raise TimeoutError('Timeout while waiting for data!')
        
        with self.data_lock:
            return self.hum
        
    def get_co2(self):
        """Get carbon dioxide concentration.

        Returns: carbon dioxide concentration (ppm)
        """
        if not self.co2_initialized.wait(timeout=self.DEFAULT_TIMEOUT):
            raise TimeoutError('Timeout while waiting for data!')
        
        with self.data_lock:
            return self.co2
        