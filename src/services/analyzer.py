import pandas as pd

from src.services.extractor import File
from src.utils.data import (
    MEASUREMENT_RATE,
    MEASUREMENT_BINS,
    columns
)
from src.utils.helper import angle_to_rad


class Observation:
    name: str
    data: pd.DataFrame
    angvel_deg: pd.DataFrame
    angvel_rad: pd.DataFrame
    angaccel_rad: pd.DataFrame

    def __init__(self, file: File) -> None:
        self.name = file.file_name
        self.data = (
            file.file_handler
            .get_data(file.file_path)[columns]
            .rolling(window=MEASUREMENT_BINS, center=True)
            .mean()
            .dropna()
            .abs()
        )
        self.angvel_deg = (
            self.data.diff()
            .rolling(window=MEASUREMENT_BINS, center=True)
            .mean()
            .dropna()
        ) / MEASUREMENT_RATE
        self.angvel_rad = (
            angle_to_rad(
                self.data.diff()
                .rolling(window=MEASUREMENT_BINS, center=True)
                .mean()
                .dropna()
            )
            / MEASUREMENT_RATE
        )
        self.angaccel_rad = (
            self.angvel_rad.diff()
            .dropna()
            .rolling(window=MEASUREMENT_BINS, center=True)
            .mean()
            / MEASUREMENT_RATE
        )


class Hanging(Observation):
    def __init__(self, path: str) -> None:
        super().__init__(path)


class Wing(Observation):
    def __init__(self, path: str) -> None:
        super().__init__(path)
