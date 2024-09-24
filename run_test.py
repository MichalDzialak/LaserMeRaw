from connection_manager import *
from machine import *
from commands import LaserCommand
import math
import random

if __name__ == "__main__":
    manager = LaserConnection()
    manager.open()
    laser = Machine(manager)

    settings = LaserSettings()
    settings.cor_file = "110.cor"
    settings.pwm_pulse_width = 200
    laser.setup(settings, 159, 159)

    cmd = LaserCommand(laser)

    cmd.light_on()

    for i in range(2000):

        cmd.light_on()
        cmd.set_xy_position(75, 75)
        time.sleep(0.05)
        cmd.light_off()
        cmd.set_xy_position(95, 95)
        time.sleep(0.05)
        cmd.light_on()
        time.sleep(0.05)
        cmd.light_off()

    manager.close()
