from enum import Enum

# CONSTANTS
MEASUREMENT_RATE = 0.100251
MEASUREMENT_BINS = 10
HEADER_SIZE = 8
FILENAME_PATTERN = r"\n(\w+?)\t(\d+-\d+-\d+)\t(\d+:\d+:\d+:\d+)\t"

# VARIABLES
columns = ["hum thor elev DIR", "hum thor elev ESQ", "scap ur DIR", "scap ur ESQ"]
units = {"angle": "°", "angvel_deg": "°/s", "angvel_rad": "rad/s", "angaccel_rad": "rad/s²"}


class ObservationType(Enum):
    wing = 1
    hanging = 2
