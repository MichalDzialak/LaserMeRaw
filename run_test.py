from connection_manager import *
from machine import *
from commands import LaserCommand
from laser_job import *
import math
import random
from hologram import mat

if __name__ == "__main__":
    manager = LaserConnection()
    manager.open()
    laser = Machine(manager)

    settings = LaserSettings()
    settings.cor_file = "110.cor"
    settings.pwm_pulse_width = 200
    laser.setup(settings, 65535, 65535)

    cmd = LaserCommand(laser)

    cmd.light_on()
    cmd.set_xy_position(0x8000, 0x9000)

    job_settings = JobSettings(0, 0)
    job = LaserJob(laser, manager, job_settings)

    x_0 = 0x8000
    y_0 = 0x8000
    job.travel(x_0, y_0)

    scale = 20
    for i in range(256):
        job.travel(x_0 + scale * i, y_0)
        for j in range(256):
            if mat[i, j]:
                for _ in range(1):
                    job.laser_control(True)
                    job.mark(x_0 + scale * i, y_0 + scale * j)
                    job.laser_control(False)

    job.execute()
    cmd.light_on()

    manager.close()
