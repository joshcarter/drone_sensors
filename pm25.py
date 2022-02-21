import time, struct, pigpio

# Adapted from:
# https://github.com/adafruit/Adafruit_CircuitPython_PM25
class PM25:
    def __init__(self, rx_pin, reset_pin = None):
        self._buffer = bytearray(32)
        self.aqi_reading = {
            "pm10-std": None,
            "pm25-std": None,
            "pm100-std": None,
            "pm10-env": None,
            "pm25-env": None,
            "pm100-env": None,
            "prt-03um": None,
            "prt-05um": None,
            "prt-10um": None,
            "prt-25um": None,
            "prt-50um": None,
            "prt-100um": None,
        }
        
        self._pi = pigpio.pi()
        self._rx = rx_pin
        self._reset = reset_pin

        if reset_pin:
            self._pi.set_mode(reset_pin, pigpio.OUTPUT)
            self._pi.write(reset_pin, 0)
            time.sleep(0.01)
            self._pi.write(reset_pin, 1)
            # it takes at least a second to start up
            time.sleep(1)

        self._pi.set_mode(rx_pin, pigpio.INPUT)
        self._pi.bb_serial_read_open(rx_pin, 9600, 8)
        # pigpio.exceptions = False

    def _read_into_buffer(self) -> None:
        while True:
            (count, data) = self._pi.bb_serial_read(self._rx)

            # print(f'{count} bytes: {data}')

            if count >= 32 and data[0] == 0x42:
                break

            time.sleep(0.25)
                
        self._buffer = data[:32]

    def read(self) -> dict:
        """Read any available data from the air quality sensor and
        return a dictionary with available particulate/quality data"""
        self._read_into_buffer()
        # print([hex(i) for i in self._buffer])

        # check packet header
        if not self._buffer[0:2] == b"BM":
            raise RuntimeError("Invalid PM2.5 header")

        # check frame length
        frame_len = struct.unpack(">H", self._buffer[2:4])[0]
        if frame_len != 28:
            raise RuntimeError("Invalid PM2.5 frame length")

        checksum = struct.unpack(">H", self._buffer[30:32])[0]
        check = sum(self._buffer[0:30])
        if check != checksum:
            raise RuntimeError("Invalid PM2.5 checksum")

        # unpack data
        (
            self.aqi_reading["pm10-std"],
            self.aqi_reading["pm25-std"],
            self.aqi_reading["pm100-std"],
            self.aqi_reading["pm10-env"],
            self.aqi_reading["pm25-env"],
            self.aqi_reading["pm100-env"],
            self.aqi_reading["prt-03um"],
            self.aqi_reading["prt-05um"],
            self.aqi_reading["prt-10um"],
            self.aqi_reading["prt-25um"],
            self.aqi_reading["prt-50um"],
            self.aqi_reading["prt-100um"],
        ) = struct.unpack(">HHHHHHHHHHHH", self._buffer[4:28])

        return self.aqi_reading
        
    def stop(self):
        self._pi.bb_serial_read_close(self._rx)
        self._pi.stop()
