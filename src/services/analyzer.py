import pandas as pd

from src.services.extractor import File
from src.utils.data import MEASUREMENT_BINS, MEASUREMENT_RATE, columns
from src.utils.helper import angle_to_rad


class Observation:
    name: str
    angle: pd.DataFrame
    angvel_deg: pd.DataFrame
    angvel_rad: pd.DataFrame
    angaccel_deg: pd.DataFrame

    def __init__(self, file: File) -> None:
        self.name = file.file_name
        self.angle = (
            file.file_handler.get_data(file.file_path)[columns]
            .rolling(window=MEASUREMENT_BINS, center=True)
            .mean()
            .dropna()
            .abs()
        )
        self.angvel_deg = (
            self.angle.diff()
            .dropna()
        ) / MEASUREMENT_RATE
        self.angvel_rad = (
            angle_to_rad(
                self.angle.diff()
                .dropna()
            )
            / MEASUREMENT_RATE
        )
        self.angaccel_deg = (
            self.angvel_deg.diff()
            .dropna()
            / MEASUREMENT_RATE
        )


class Hanging(Observation):
    def __init__(self, file: File) -> None:
        super().__init__(file)


class Wing(Observation):
    def __init__(self, file: File) -> None:
        super().__init__(file)
