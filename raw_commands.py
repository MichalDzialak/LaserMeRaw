from command_codes import *
from connection_manager import LaserConnection

class RawCommand:
    def __init__(self, manager: LaserConnection):
        self.manager=manager



    def cmd_raw_disable_laser(self):
        return self.manager.send_command(DISABLE_LASER)

    def cmd_raw_reset(self):
        self.manager.send_command(RESET)

    def cmd_raw_enable_laser(self):
        return self.manager.send_command(ENABLE_LASER)

    def cmd_raw_execute_list(self):
        return self.manager.send_command(EXECUTE_LIST)

    def cmd_raw_set_pwm_pulse_width(self, s1: int, v1: int):
        return self.manager.send_command(SET_PWM_PULSE_WIDTH, s1, v1)

    def cmd_raw_get_version(self):
        return self.manager.send_command(GET_REGISTER, 1)

    def cmd_raw_get_serial_no(self):
        return self.manager.send_command(GET_SERIAL_NUMBER)

    def cmd_raw_get_list_status(self):
        return self.manager.send_command(GET_LIST_STATUS)

    def cmd_raw_get_xy_position(self):
        return self.manager.send_command(GET_XY_POSITION)

    def cmd_raw_set_xy_position(self, x, y):
        return self.manager.send_command(SET_XY_POSITION, int(x), int(y))

    def cmd_raw_laser_signal_off(self):
        return self.manager.send_command(LASER_SIGNAL_OFF)

    def cmd_raw_laser_signal_on(self):
        return self.manager.send_command(LASER_SIGNAL_ON)

    def cmd_raw_write_correction_line(self, dx, dy, nonfirst):
        """
        3 parameters
        Writes a single line of a correction table. 1 entries.
        dx, dy, first, 0.
        Does not read reply.
        :param dx:
        :param dy:
        :param nonfirst: either 0x0000 for first entry or 0x0100 for non-first.
        :return:
        """
        self.manager.send_command(WRITE_CORRECTION_LINE, dx, dy, nonfirst, read_reply=False)

    def cmd_raw_reset_list(self):
        return self.manager.send_command(RESET_LIST)

    def cmd_raw_restart_list(self):
        return self.manager.send_command(RESTART_LIST)

    def cmd_raw_write_correction_table(self, has_table: bool):
        """
        1 parameter

        If the parameter is true, no table needs to be sent.

        :param has_table:
        :return: value response
        """
        return self.manager.send_command(WRITE_CORRECTION_TABLE, int(has_table))

    def cmd_raw_set_control_mode(self, s1: int, value: int): #################
        return self.manager.send_command(SET_CONTROL_MODE, int(s1), int(value))

    def cmd_raw_set_delay_mode(self, s1: int, value: int): #################
        return self.manager.send_command(SET_DELAY_MODE, int(s1), int(value))

    def cmd_raw_set_max_poly_delay(self, s1: int, value: int): #################
        return self.manager.send_command(SET_MAX_POLY_DELAY, int(s1), int(value))

    def cmd_raw_set_end_of_list(self, a=0, b=0):
        """
        No parameters 
        :return: value response
        """
        # It does so have parameters, in the pcap...
        return self.manager.send_command(SET_END_OF_LIST, a, b)

    def cmd_raw_set_first_pulse_killer(self, s1: int, value: int):
        return self.manager.send_command(SET_FIRST_PULSE_KILLER, s1, value)

    def cmd_raw_set_laser_mode(self, s1: int, value: int):
        return self.manager.send_command(SET_LASER_MODE, s1, value)

    def cmd_raw_set_timing(self, s1: int, value: int):
        return self.manager.send_command(SET_TIMING, s1, value)

    def cmd_raw_set_standby(self, v1: int, v2: int, v3: int, value: int):
        return self.manager.send_command(SET_STANDBY, v1, v2, v3, value)

    def cmd_raw_set_pwm_half_period(self, s1: int, value: int):
        return self.manager.send_command(SET_PWM_HALF_PERIOD, s1, value)

    def cmd_raw_stop_execute(self):
        return self.manager.send_command(STOP_EXECUTE)

    def cmd_raw_stop_list(self):
        return self.manager.send_command(STOP_LIST)

    def cmd_raw_write_port(self, v1: int = 0, s1: int = 0, value: int = 0):
        """
        3 parameters.
        variable, stack, value
        :param v1:
        :param s1:
        :param value:
        :return: value response
        """
        return self.manager.send_command(WRITE_PORT, v1, s1, value)

    def cmd_raw_write_analog_port_1(self, s1: int, value: int):
        """
        2 parameters.
        stack, value
        :param s1:
        :param value:
        :return: value response
        """
        return self.manager.send_command(WRITE_ANALOG_PORT_1, s1, value)

    def cmd_raw_write_analog_port_2(self, s1: int, value: int):
        """
        3 parameters.
        0, stack, value
        :param s1:
        :param value:
        :return: value response
        """
        return self.manager.send_command(WRITE_ANALOG_PORT_2, 0, s1, value)

    def cmd_raw_write_analog_port_x(self, v1: int, s1: int, value: int):
        """
        3 parameters.
        variable, stack, value
        :param v1:
        :param s1:
        :param value:
        :return: value response
        """
        return self.manager.send_command(WRITE_ANALOG_PORT_X, v1, s1, value)

    def cmd_raw_read_port(self):
        """
        No parameters
        :return: Status Information
        """
        return self.manager.send_command(READ_PORT)

    def cmd_raw_set_axis_motion_param(self, v1: int, s1: int, value: int):
        """
        3 parameters.
        variable, stack, value
        :return: value response
        """
        return self.manager.send_command(SET_AXIS_MOTION_PARAM, v1, s1, value)

    def cmd_raw_set_axis_origin_param(self, v1: int, s1: int, value: int):
        """
        3 parameters.
        variable, stack, value
        :return: value response
        """
        return self.manager.send_command(SET_AXIS_ORIGIN_PARAM, v1, s1, value)

    def cmd_raw_goto_axis_origin(self, v0: int):
        """
        1 parameter
        variable
        :param v0:
        :return: value response
        """
        return self.manager.send_command(GO_TO_AXIS_ORIGIN, v0)

    def cmd_raw_move_axis_to(self, axis, coord):
        """
        This typically accepted 1 32 bit int and used bits 1:8 and then 16:24 as parameters.
        :param axis: axis being moved
        :param coord: coordinate being matched
        :return: value response
        """
        return self.manager.send_command(MOVE_AXIS_TO, axis, coord)

    def cmd_raw_get_axis_pos(self, s1: int, value: int):
        """
        2 parameters
        stack, value
        :param s1:
        :param value:
        :return: axis position?
        """
        return self.manager.send_command(GET_AXIS_POSITION, s1, value)

    def cmd_raw_get_fly_wait_count(self, b1: bool):
        """
        1 parameter
        bool
        :param b1:
        :return: flywaitcount?
        """
        return self.manager.send_command(GET_FLY_WAIT_COUNT, int(b1))

    def cmd_raw_get_mark_count(self, p1: bool):
        """
        1 parameter
        bool
        :param p1:
        :return: markcount?
        """
        return self.manager.send_command(GET_MARK_COUNT, int(p1))

    def cmd_raw_set_fpk_param_2(self, v1, v2, v3, s1):
        """
        4 parameters
        variable, variable, variable stack
        :param v1:
        :param v2:
        :param v3:
        :param s1:
        :return:  value response
        """
        return self.manager.send_command(SET_FPK_2E, v1, v2, v3, s1)

    def cmd_raw_set_fiber_config(self, p1, p2):
        """
        Calls fiber_config_2 with setting parameters
        :param p1:
        :param p2:
        :return:
        """
        self.cmd_raw_fiber_config_1(0, p1, p2)

    def cmd_raw_get_fiber_config(self):
        """
        Calls fiber_config_1 with getting parameters.

        :return:
        """
        self.cmd_raw_fiber_config_1(1, 0, 0)

    def cmd_raw_fiber_config_1(self, p1, p2, p3):
        """
        Seen to call both a get and set config value.

        :param p1:
        :param p2:
        :param p3:
        :return:
        """
        return self.manager.send_command(FIBER_CONFIG_1, p1, p2, p3)

    def cmd_raw_fiber_config_2(self, v1, v2, v3, s1):
        return self.manager.send_command(FIBER_CONFIG_2, v1, v2, v3, s1)

    def cmd_raw_lock_input_port(self, p1):
        """
        p1 varies based on call., 1 for get, 2, for enable, 4 for clear
        :param p1:
        :return:
        """
        self.manager.send_command(LOCK_INPUT_PORT, p1)

    def cmd_raw_clear_lock_input_port(self):
        self.cmd_raw_lock_input_port(0x04)

    def cmd_raw_enable_lock_input_port(self):
        self.cmd_raw_lock_input_port(0x02)

    def cmd_raw_get_lock_input_port(self):
        self.cmd_raw_lock_input_port(0x01)

    def cmd_raw_set_fly_res(self, p1, p2, p3, p4):
        """
        On-the-fly settings.
        :param p1:
        :param p2:
        :param p3:
        :param p4:
        :return:
        """
        return self.manager.send_command(SET_FLY_RES, p1, p2, p3, p4)

    def cmd_raw_fiber_open_mo(self, s1: int, value: int):
        """
        2 parameters
        stack, value
        :param s1:
        :param value:
        :return: value response
        """
        return self.manager.send_command(FIBER_OPEN_MO, s1, value)

    def cmd_raw_get_st_mo_ap(self):
        """
        No parameters
        :return: value response
        """
        return self.manager.send_command(FIBER_GET_StMO_AP)

    def cmd_raw_get_user_data(self):
        """
        No parameters
        :return: user_parameters
        """
        return self.manager.send_command(GET_USER_DATA)

    def cmd_raw_get_fly_pulse_count(self):
        """

        :return: fly pulse count
        """
        return self.manager.send_command(GET_FLY_PULSE_COUNT)

    def cmd_raw_get_fly_speed(self, p1, p2, p3, p4):
        """
        :param p1:
        :param p2:
        :param p3:
        :param p4:
        :return:
        """
        self.manager.send_command(GET_FLY_SPEED, p1, p2, p3, p4)

    def cmd_raw_enable_z(self):
        """
        No parameters. Autofocus on/off
        :return: value response
        """
        return self.manager.send_command(ENABLE_Z)

    def cmd_raw_enable_z_2(self):
        """
        No parameters
        Alternate command. Autofocus on/off
        :return: value response
        """
        return self.manager.send_command(ENABLE_Z_2)

    def cmd_raw_set_z_data(self, v1, s1, v2):
        """
        3 parameters
        variable, stack, variable
        :param v1:
        :param s1:
        :param v2:
        :return: value response
        """
        return self.manager.send_command(SET_Z_DATA, v1, s1, v2)

    def cmd_raw_set_spi_simmer_current(self, v1, s1):
        """
        2 parameters
        variable, stack
        :param v1:
        :param s1:
        :return: value response
        """
        return self.manager.send_command(SET_SPI_SIMMER_CURRENT, v1, s1)

    def cmd_raw_is_lite_version(self):
        """
        no parameters.
        Only called for true.
        :return: value response
        """
        return self.manager.send_command(IS_LITE_VERSION, 1)

    def cmd_raw_get_mark_time(self):
        self.manager.send_command(GET_MARK_TIME, 3)

    def cmd_raw_set_fpk_param(self, v1, v2, v3, s1):
        """
        Probably "first pulse killer" = fpk
        4 parameters
        variable, variable, variable, stack
        :param v1:
        :param v2:
        :param v3:
        :param s1:
        :return: value response
        """
        return self.manager.send_command(SET_FPK_PARAM, v1, v2, v3, s1)