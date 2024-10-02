from raw_commands import RawCommand
from connection_manager import LaserConnection
from machine import Machine
import struct


class LaserCommand:
    def __init__(self, machine: Machine):
        self.machine = machine
        self.manager = machine.manager
        self.commander = machine.commander
        self._write_port = 0x0000

    def port_toggle(self, bit):
        self._write_port ^= 1 << bit
        self.commander.cmd_raw_write_port(self._write_port)

    def port_on(self, bit):
        self._write_port |= 1 << bit
        self.commander.cmd_raw_write_port(self._write_port)

    def port_off(self, bit):
        self._write_port = ~((~self._write_port) | (1 << bit))
        self.commander.cmd_raw_write_port(self._write_port)

    def get_port(self, bit=None):
        if bit is None:
            return self._write_port
        return (self._write_port >> bit) & 1

    def light_on(self):
        self.port_on(bit=8)  # 0x100

    def light_off(self):
        self.port_off(bit=8)

    def read_port(self):
        port = self.raw_read_port()
        if port[0] & 0x8000 and self.machine._footswitch_callback:
            callback = self.machine._footswitch_callback
            self.machine._footswitch_callback = None
            callback(port)

        return port

    def disable_laser(self):
        self.commander.cmd_raw_disable_laser()

    def reset_machine(self):
        self.commander.cmd_raw_reset()

    def enable_laser(self):
        self.commander.cmd_raw_enable_laser()

    def execute_buffered_job(self):
        self.commander.cmd_raw_execute_list()

    def set_pwm_width(self, width):
        self.commander.cmd_raw_set_pwm_pulse_width(width, 0)

    def get_serial_number(self):
        return self.commander.cmd_raw_get_serial_no()

    def get_list_status(self):
        return self.commander.cmd_raw_get_list_status()

    def get_xy_position(self):
        (x_raw, y_raw) = self.commander.cmd_raw_get_xy_position()
        return (
            x_raw * self.machine.mm_per_galvo_unit_x,
            y_raw * self.machine.galvo_units_per_mm_y,
        )

    def set_xy_position(self, x: int, y: int):
        (x_raw, y_raw) = (
            x * self.machine.galvo_units_per_mm_x,
            y * self.machine.galvo_units_per_mm_y,
        )
        if x > 2**16 or y > 2**16:
            raise Exception("XY position out of range!")
        self.commander.cmd_raw_set_xy_position(x_raw, y_raw)

    def set_laser_signal(self, enable: bool):
        (
            self.commander.cmd_raw_laser_signal_on()
            if enable
            else self.commander.cmd_raw_laser_signal_off()
        )

    def reset_buffered_job(self):
        self.commander.cmd_raw_reset_list()

    def restart_buffered_job(self):
        self.commander.cmd_raw_restart_list()

    def set_end_of_job(self, unk_a, unk_b):
        self.commander.cmd_raw_restart_list()

    def set_axis_settings_and_origin(self, min_speed, max_speed, acceleration_ms):
        self.commander.cmd_raw_set_axis_motion_param(min_speed, max_speed, 0)
        self.commander.cmd_raw_set_axis_origin_param(acceleration_ms, 0, 0)

    def move_axis_absolute(self, position):
        packed = struct.pack("i", abs(position))
        if position < 0:
            packed = packed[:3] + bytes([packed[3] | 0x80])
        lower = struct.unpack("H", packed[:2])[0]
        upper = struct.unpack("H", packed[2:])[0]

        self.commander.cmd_raw_move_axis_to(lower, upper)
