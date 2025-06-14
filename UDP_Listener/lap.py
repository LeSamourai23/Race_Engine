from datetime import datetime
from utils import seconds_to_lap_time

class Lap:
    def __init__(self):
        # Nice title for lap
        self.title = "Lap"
        # Number of all lap ticks
        self.lap_ticks = 1
        # Lap time after crossing the finish line
        self.lap_finish_time = 0
        # Live time during a live lap
        self.lap_live_time = 0
        # Total number of laps
        self.total_laps = 0
        # Number of current lap
        self.number = 0
        # Aggregated number of instances where condition is true
        self.throttle_and_brake_ticks = 0
        self.no_throttle_and_no_brake_ticks = 0
        self.full_brake_ticks = 0
        self.full_throttle_ticks = 0
        self.tires_overheated_ticks = 0
        self.tires_spinning_ticks = 0
        # Data points with value for every tick
        self.data_throttle = []
        self.data_braking = []
        self.data_coasting = []
        self.data_speed = []
        self.data_time = []
        self.data_rpm = []
        self.data_gear = []
        self.data_tires = []
        # Positions on x,y,z
        self.data_position_x = []
        self.data_position_y = []
        self.data_position_z = []
        # Fuel
        self.fuel_at_start = 0
        self.fuel_at_end = -1
        self.fuel_consumed = -1
        # Boost
        self.data_boost = []
        # Yaw Rate
        self.data_rotation_yaw = []
        self.data_absolute_yaw_rate_per_second = []
        # Car
        self.car_id = 0

        # Always record was set when recording the lap, likely a replay
        self.is_replay = False
        self.is_manual = False

        self.lap_start_timestamp = datetime.now()
        self.lap_end_timestamp = -1

    def __str__(self):
        return "\n %s, %2d, %1.f, %4d, %4d, %4d" % (
            self.title,
            self.number,
            self.fuel_at_end,
            self.full_throttle_ticks,
            self.full_brake_ticks,
            self.no_throttle_and_no_brake_ticks,
        )

    def format(self):
        return "Lap %2d, %s (%d Ticks)" % (
            self.number,
            self.title,
            len(self.data_speed),
        )

    def get_speed_peaks_and_valleys(self):
        # Instead of using helper function, implement it directly here
        peaks, valleys = self.find_speed_peaks_and_valleys(width=100)

        peak_speed_data_x = []
        peak_speed_data_y = []

        valley_speed_data_x = []
        valley_speed_data_y = []

        for p in peaks:
            peak_speed_data_x.append(self.data_speed[p])
            peak_speed_data_y.append(p)

        for v in valleys:
            valley_speed_data_x.append(self.data_speed[v])
            valley_speed_data_y.append(v)

        return (
            peak_speed_data_x,
            peak_speed_data_y,
            valley_speed_data_x,
            valley_speed_data_y,
        )

    def find_speed_peaks_and_valleys(self, width=100):
        from scipy.signal import find_peaks
        inv_data_speed = [i * -1 for i in self.data_speed]
        peaks, _ = find_peaks(self.data_speed, width=width)
        valleys, _ = find_peaks(inv_data_speed, width=width)
        return list(peaks), list(valleys)

    def car_name(self) -> str:
        # Implement a basic version here
        if not hasattr(self, "car_id"):
            return "Car not logged"
        return f"CAR-ID-{self.car_id}"