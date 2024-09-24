from connection_manager import *
from raw_commands import *

class LaserSettings():
    def __init__(self,
                cor_file=None,
                first_pulse_killer=200,
                pwm_half_period=125,
                pwm_pulse_width=125,
                standby_param_1=2000,
                standby_param_2=20,
                timing_mode=1,
                delay_mode=1,
                laser_mode=1,
                control_mode=0,
                fpk2_p1=0xFFB,
                fpk2_p2=1,
                fpk2_p3=409,
                fpk2_p4=100,
                fly_res_p1=0,
                fly_res_p2=99,
                fly_res_p3=1000,
                fly_res_p4=25):
        
        self.cor_file=cor_file
        self.first_pulse_killer=first_pulse_killer
        self.pwm_half_period=pwm_half_period
        self.pwm_pulse_width=pwm_pulse_width
        self.standby_param_1=standby_param_1
        self.standby_param_2=standby_param_2
        self.timing_mode=timing_mode
        self.delay_mode=delay_mode
        self.laser_mode=laser_mode
        self.control_mode=control_mode
        self.fpk2_p1=fpk2_p1
        self.fpk2_p2=fpk2_p2
        self.fpk2_p3=fpk2_p3
        self.fpk2_p4=fpk2_p4
        self.fly_res_p1=fly_res_p1
        self.fly_res_p2=fly_res_p2
        self.fly_res_p3=fly_res_p3
        self.fly_res_p4=fly_res_p4