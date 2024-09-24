import usb.core
import usb.util
import time
import threading

from command_codes import *

class LaserConnection:
    def __init__(self):
        self._lock = threading.Lock()
        self._terminate_execution = False
        self._device=None
        self._chunk_size = 12*256
        self._ep_homi = 0x02  # endpoint for host out, machine in. (query status, send ops)
        self._ep_himo = 0x88  # endpoint for host in, machine out. (receive status reports)
        self.status = None
    
    def open(self, machine_index=0):
        devices=list(usb.core.find(find_all=True, idVendor=0x9588, idProduct=0x9899))
        if len(devices) == 0:
            raise Exception("No compatible engraver machine was found.")

        try:
            device = devices[machine_index]
        except IndexError:
            raise Exception("Invalid machine index %d"%machine_index)

        device.set_configuration()
        self._device = device

        time.sleep(0.05)  # We sacrifice this time at the altar of the unknown race condition
        return True
    
    def close(self):
        self.status = None

    def is_ready(self):
        self.send_command(READ_PORT, 0)
        return self.status & 0x20
    
    def send_command(self, opcode, *parameters, read_reply=True):
        query = bytearray([0] * 12)

        query[0] = opcode & 0x00FF
        query[1] = (opcode >> 8) & 0x00FF

        for n, parameter in enumerate(parameters):
            query[2 * n + 2] = parameter & 0x00FF
            query[2 * n + 3] = (parameter >> 8) & 0x00FF

        if self._device.write(self._ep_homi, query, 100) != 12:
            raise Exception("Failed to write command")

        if read_reply:
            response = self._device.read(self._ep_himo, 8, 100)
            if len(response) != 8:
                raise Exception("Invalid response")
            
            self.status = response[6] | (response[7] << 8)
            return response[2] | (response[3] << 8), response[4] | (response[5] << 8)
        else:
            return 0, 0
        
    def send_list_chunk(self, data):
        if len(data) != self._chunk_size:
            raise Exception("Invalid chunk size %d" % len(data))
        
        sent = self._device.write(self._ep_homi, data, 100)
        if sent != len(data):
            raise Exception("Could not send list chunk")
        
    def send_correction_entry(self, correction):
        """Send an individual correction table entry to the machine."""
        # This is really a command and should just be issued without reading.
        query = bytearray([0x10] + [0] * 11)
        query[2:2 + 5] = correction
        if self.device.write(self.ep_homi, query, 100) != 12:
            raise Exception("Failed to write correction entry")