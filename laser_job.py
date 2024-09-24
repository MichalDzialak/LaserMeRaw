
from connection_manager import LaserConnection
from machine import Machine

#TODO: setting checker
#

class Operation:
    def __init__(self, data, len):
        self.data=data
        self.len=len

class JobSettings:
    def __init__(self, x_origin, y_origin):
        self._last_x = x_origin
        self._last_y = y_origin
        self._start_x = x_origin
        self._start_y = y_origin
        

        self.cut_speed = None
        self.travel_speed = None
        self.q_switch_frequency = None
        self.power = None
        self.jump_delay = None
        self.laser_control = None
        self.laser_on_delay = None
        self.laser_off_delay = None
        self.poly_delay = None
        self.mark_end_delay = None
        self.laser_on_tc = None
        self.laser_off_tc = None

class LaserJob:
    def __init__(self, machine: Machine, manager: LaserConnection, job_settings: JobSettings):
        self.machine=machine
        self.manager=manager
        self.job_settings=job_settings
        self.operations = []

    def _convert_speed_mm_to_galvo(self, speed_mm)->int:

        return 69

    def job_ready(self)->None:
        op=Operation([0x8051],1)
        self.operations.append(op)

    def job_wait(self, delay_us): #de
        op=Operation([0x8004, int(delay_us*10)], 2)
        self.operations.append(op)

    def job_laser_control(self, enable: bool):
        if enable:
            op=Operation([0x8021,0x0001],2) # laserControl
            self.operations.append(op)
            self.job_wait(self.job_settings.laser_on_tc)
        else:
            self.job_wait(self.job_settings.laser_off_tc)
            op=Operation([0x8021,0x0002],2) # laserControl
            self.operations.append(op)
    
    def job_set_travel_speed(self, speed): #TODO: check min and max
        #self.job_ready()
        op=Operation([0x8006, self._convert_speed_mm_to_galvo(speed)])
        self.operations.append([op])

    def job_set_travel_speed(self, speed): #TODO: check min and max
        #self.job_ready()
        op=Operation([0x8006, self._convert_speed_mm_to_galvo(speed)])
        self.operations.append([op])

