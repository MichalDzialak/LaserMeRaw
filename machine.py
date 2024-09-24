import time
from connection_manager import *
from raw_commands import *
from laser_settings import *




class Machine:
    def __init__(self, manager: LaserConnection):
        self.commander=RawCommand(manager)
        self.manager=manager
        self._footswitch_callback=None
        self._footswitch_fire_once=False

    def setup(self, settings: LaserSettings, field_size_x:float, field_size_y:float):
        self.field_size_x=field_size_x
        self.field_size_y=field_size_y
        self.galvo_units_per_mm_x=(2**16)/field_size_x
        self.galvo_units_per_mm_y=(2**16)/field_size_y

        self.mm_per_galvo_unit_x=field_size_x/(2**16)
        self.mm_per_galvo_unit_y=field_size_y/(2**16)
        
        self.serial_number = self.commander.cmd_raw_get_serial_no()
        self.version = self.commander.cmd_raw_get_version()

        self.commander.cmd_raw_get_st_mo_ap()
        
        self.commander.cmd_raw_reset()

        # Load in-machine correction table
        cor_table = None
        if settings.cor_file is not None:
            cor_table = self._read_correction_file(settings.cor_file)
        self._send_correction_table(cor_table)

        self.commander.cmd_raw_enable_laser()
        self.commander.cmd_raw_set_control_mode(settings.control_mode,0)
        self.commander.cmd_raw_set_laser_mode(settings.laser_mode, 0)
        self.commander.cmd_raw_set_delay_mode(settings.delay_mode, 0)
        self.commander.cmd_raw_set_timing(settings.timing_mode, 0)
        self.commander.cmd_raw_set_standby(settings.standby_param_1, settings.standby_param_2, 0, 0)
        self.commander.cmd_raw_set_first_pulse_killer(settings.first_pulse_killer, 0)
        self.commander.cmd_raw_set_pwm_half_period(settings.pwm_half_period, 0)

        self.commander.cmd_raw_set_pwm_pulse_width(settings.pwm_pulse_width, 0)
        self.commander.cmd_raw_fiber_open_mo(0, 0)
        self.manager.send_command(GET_REGISTER, 0)

        # 0x0FFB is probably a 12 bit rendering of int12 -5
        self.commander.cmd_raw_set_fpk_param_2(settings.fpk2_p1, settings.fpk2_p2, settings.fpk2_p3, settings.fpk2_p4)
        self.commander.cmd_raw_set_fly_res(settings.fly_res_p1, settings.fly_res_p2, settings.fly_res_p3, settings.fly_res_p4)
        self.commander.cmd_raw_write_port(0x0000)
        self.commander.cmd_raw_enable_z()

        # We don't know what this does
        self.commander.cmd_raw_write_analog_port_1(0x07FF, 0)
        self.commander.cmd_raw_enable_z()




    def _read_correction_file(self, filename):
        table = []
        with open(filename, "rb") as f:
            f.seek(0x24)
            for j in range(65):
                for k in range(65):
                    dx = int.from_bytes(f.read(4), "little", signed=True)
                    dx = dx if dx >= 0 else -dx + 0x8000
                    dy = int.from_bytes(f.read(4), "little", signed=True)
                    dy = dy if dy >= 0 else -dy + 0x8000
                    table.append([dx & 0xFFFF, dy & 0xFFFF])
        return table


    def _send_correction_table(self, table=None):
        """Send the onboard correction table to the machine."""
        self.commander.cmd_raw_write_correction_table(True)
        if table is None:
            for n in range(65**2):
                self.commander.cmd_raw_write_correction_line(0,0,0 if n == 0 else 1)
        else:
            for n in range(65**2):
                self.commander.cmd_raw_write_correction_line(table[n][0], table[n][1],0 if n == 0 else 1)




    def is_ready(self):
        """Returns true if the laser is ready for more data, false otherwise."""
        self.read_port()
        return bool(self.manager.usb_connection.status & 0x20)




    def is_busy(self):
        """Returns true if the machine is busy, false otherwise;
           Note that running a lighting job counts as being busy."""
        self.read_port()
        return bool(self.manager.usb_connection.status & 0x04)
    



    def execute_job(self, job_list, loop_count=1, callback_finished=None):
        """Run a job. loop_count is the number of times to repeat the
           job; if it is inf, it repeats until aborted. If there is a job
           already running, it will be aborted and replaced. Optionally,
           calls a callback function when the job is finished.
           The loop job can either be regular data in multiples of 3072 bytes, or
           it can be a callable that provides data as above on command."""
        self._terminate_execution = False
        with self._lock:
            while self.is_busy():
                time.sleep(self.sleep_time)
                if self._terminate_execution:
                    return False
            while not self.is_ready():
                time.sleep(self.sleep_time)
                if self._terminate_execution:
                    return False

            self.port_on(bit=0)

            loop_index = 0
            while loop_index < loop_count:
                if job_list.tick is not None:
                    job_list.tick(job_list, loop_index)
                self.raw_reset_list()

                for packet in job_list.packet_generator():
                    while not self.is_ready():
                        if self._terminate_execution:
                            return False
                        time.sleep(self.sleep_time)
                    self.manager.usb_connection.send_list_chunk(packet)
                    self.commander.cmd_raw_set_end_of_list(0x8001, 0x8001)
                    self.commander.cmd_raw_execute_list()
                
                self.commander.cmd_raw_set_end_of_list(0, 0)
                self.commander.cmd_raw_set_control_mode(1,0)

                while self.is_busy():
                    if self._terminate_execution:
                        return False
                loop_index += 1
        if callback_finished is not None:
            callback_finished()
        return True




    def abort_job(self):
        self._terminate_execution = True
        with self._lock:
            self.commander.cmd_raw_stop_execute()
            self.commander.cmd_raw_fiber_open_mo(0,0)
            self.commander.cmd_raw_reset_list()
            self.manager.usb_connection.send_list_chunk(self._abort_list_chunk)

            self.commander.cmd_raw_set_end_of_list()
            self.commander.cmd_raw_execute_list()

            while self.is_busy():
                time.sleep(self.sleep_time)

            self.set_xy(0x8000, 0x8000)




    def set_footswitch_callback(self, callback_footswitch, fire_once=False):
        self._footswitch_callback = callback_footswitch
        self._footswitch_fire_once=fire_once
    #def get_condition(self):
    #    """Returns the 16-bit condition register value (from whatever
    #       command was run last.)"""
    #    return self.manager.usb_connection.status