import serial
import logging

class DroneConnection:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            logging.info(f"Successfully connected to drone on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to drone: {e}")
            self.serial = None

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            logging.info("Disconnected from drone.")

    def is_connected(self):
        return self.serial is not None and self.serial.is_open