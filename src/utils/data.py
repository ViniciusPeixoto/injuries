from enum import Enum

# CONSTANTS

MEASUREMENT_RATE = 0.100251
MEASUREMENT_BINS = 100
HEADER_SIZE = 12
FILENAME_PATTERN = r'filename="([^"]+)"'

# VARIABLES
columns = ["hum thor elev DIR", "hum thor elev ESQ", "scap ur DIR", "scap ur ESQ"]


class ObservationType(Enum):
    wing = 1
    hanging = 2
