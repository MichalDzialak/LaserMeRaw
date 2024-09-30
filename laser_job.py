from connection_manager import LaserConnection
from machine import Machine
import math

# TODO: setting checker
# User-settable min/max values for different parameters,
# ideally everything. Something like frequency 10khz-4MHz, power 0-90%

# TODO: check delays and time constants
# How do negative TCs work? Swapper order for things or does LMC support negative values

# TODO: check units
# Accurate mm/s, q-sw freq/pulse width

# TODO: user-friendly wrapper
# Draw lines, polygons, etc
# Real-world units for X and Y
# No setups other than params, just init() then line(x1,x2,y1,y2)
# Settings handled by layers? layer-specific power/etc, auto-switched in the background


class Operation:
    def __init__(self, data):
        self.data = data


class JobSettings:
    def __init__(self, x_origin, y_origin):
        self.start_x = x_origin
        self.start_y = y_origin

        self.cut_speed = 100
        self.travel_speed = 4000
        self.q_switch_frequency = 20
        self.power = 90
        self.jump_delay = 10
        self.laser_control = None
        self.laser_on_delay = 0x1000
        self.laser_off_delay = 0x1000
        self.poly_delay = 0x0256
        self.mark_end_delay = 2000
        self.laser_on_tc = 200
        self.laser_off_tc = 200
        self.q_switch_period = 20


class JobState:
    def __init__(self):
        self.last_x = None
        self.last_y = None
        self.start_x = None
        self.start_y = None
        self.ready = False
        self.cut_speed = None
        self.travel_speed = None
        self.q_switch_frequency = None
        self.q_switch_period = None
        self.power = None
        self.laser_state = None


class LaserJob:
    def __init__(
        self, machine: Machine, manager: LaserConnection, job_settings: JobSettings
    ):
        self.machine = machine
        self.manager = manager
        self.job_settings = job_settings
        self.job_state = JobState()
        self.operations = []
        self.job_state.last_x = self.job_settings.start_x
        self.job_state.last_y = self.job_settings.start_y

        self.set_qswitch_freq(job_settings.q_switch_frequency)
        self.set_power(job_settings.power)
        self.set_travel_speed(job_settings.travel_speed)
        self.set_cut_speed(job_settings.cut_speed)
        self.set_laser_on_delay(job_settings.laser_on_delay)
        self.set_laser_off_delay(job_settings.laser_off_delay)
        self.set_polygon_delay(job_settings.poly_delay)
        self.write_port(
            1
        )  # VERY FUCKING IMPORTANT FOR SOME FUCKING REASON FOR FUCKS SAGE GOD I FUCKIGN HATE THIS

    def packet_generator(self):
        buf = bytearray([0] * 0xC00)  # Create a packet.
        eol = bytes([0x02, 0x80] + [0] * 10)  # End of Line Command
        i = 0
        for op in self.operations:
            buf[i : i + 12] = self._serialize_op(op)
            i += 12
            if i >= 0xC00:
                i = 0
                yield buf
        while i < 0xC00:
            buf[i : i + 12] = eol
            i += 12
        yield buf

    def execute(self):
        self.machine.execute_job(self)

    def _serialize_op(self, operation):
        op_len = len(operation.data)
        if op_len > 6:
            raise Exception(f"Invalid operation: {operation.data}")
        buf = bytearray([0] * 12)

        for x in range(op_len):
            buf[x * 2] = int(operation.data[x]) & 0xFF
            buf[1 + (x * 2)] = int(operation.data[x] & 0xFF00) >> 8
        return buf

    def _convert_speed_mm_to_galvo(self, speed_mm) -> int:
        return int(speed_mm * self.machine.galvo_units_per_mm_x)

    def ready(self):
        self.operations.append(Operation([0x8051]))
        self.job_state.ready = True

    def wait(self, delay_us):
        if delay_us > 65535 or delay_us < 0:
            raise Exception(
                f"Delay time too long or you're trying to create a non-causal engraving: {delay_us}"
            )
        self.operations.append(Operation([0x8004, int(delay_us * 10)]))

    def laser_control(self, enable: bool):
        if self.job_state.laser_state == enable:
            return
        self.job_state.laser_state = enable

        if enable:
            self.operations.append(Operation([0x8021, 0x0001]))
            self.wait(self.job_settings.laser_on_tc)
        else:
            self.wait(self.job_settings.laser_off_tc)
            self.operations.append(Operation([0x8021, 0x0000]))

    def set_travel_speed(self, speed_mm_per_s):  # TODO: check min and max
        if self.job_state.travel_speed == speed_mm_per_s:
            return
        self.job_state.travel_speed = speed_mm_per_s

        op = Operation([0x8006, self._convert_speed_mm_to_galvo(speed_mm_per_s)])
        self.operations.append(op)
        self.job_state.travel_speed = speed_mm_per_s

    def set_cut_speed(self, speed_mm_per_s):  # TODO: check min and max
        if self.job_state.cut_speed == speed_mm_per_s:
            return
        self.job_state.cut_speed = speed_mm_per_s

        op = Operation([0x800C, self._convert_speed_mm_to_galvo(speed_mm_per_s)])
        self.operations.append(op)
        self.job_state.cut_speed = speed_mm_per_s

    # TODO: capture some data for reversing the parameters
    # def set_qswitch_period(self, period_ns):  # 0x801B
    #    self.ready()
    #    op = Operation([0x801A, 2000])
    #    self.operations.append(op)
    #    self.job_state.q_switch_period = period_ns

    # def set_frequency(self, frequency_kHz: float):
    #    op = Operation([0x801B, int(round(1.0 / (frequency_kHz * 1e3) / 50e-9))])
    #    self.operations.append(op)

    def set_qswitch_freq(self, freq):
        self.operations.append(Operation([0x801B, freq]))

    def set_power(self, power: float):
        if power < 0 or power > 100:
            raise Exception(f"Power less than 0 or larger than 100%: {power}")
        op = Operation([0x8012, int(round(power * 40.95))])
        print(f"power={int(round(power * 40.95))}")
        self.operations.append(op)
        self.job_state.power = power

    def travel(self, x, y):
        dist = int(
            math.sqrt(
                (self.job_state.last_x - x) ** 2 + (self.job_state.last_y - y) ** 2
            )
        )
        op = Operation([0x8001, y, x, 0, dist])
        self.operations.append(op)
        self.job_state.last_x = x
        self.job_state.last_y = y

    def mark(self, x, y):
        self.ready()
        dist = int(
            math.sqrt(
                ((self.job_state.last_x - x) ** 2) + ((self.job_state.last_y - y) ** 2)
            )
        )
        op = Operation([0x8005, y, x, 0, dist])

        self.operations.append(op)
        self.job_state.last_x = x
        self.job_state.last_y = y

    def write_port(self, data):
        op = Operation([0x8011, data])
        self.operations.append(op)

    def set_laser_on_delay(self, delay_us):  # TODO:check units
        op = Operation([0x8007, delay_us])
        self.operations.append(op)

    def set_laser_off_delay(self, delay_us):  # TODO:check units
        op = Operation([0x8008, delay_us])
        self.operations.append(op)

    def set_polygon_delay(self, delay_us):  # TODO:check units
        op = Operation([0x800F, delay_us])
        self.operations.append(op)

    def set_mark_end_delay(self, delay_us):  # TODO:check units
        op = Operation([0x8004, delay_us])
        self.operations.append(op)

    def set_jump_delay(self, delay_us):  # TODO:check units
        op = Operation([0x800D, delay_us])
        self.operations.append(op)
