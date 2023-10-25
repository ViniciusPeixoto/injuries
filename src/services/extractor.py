import os
import re

from pandas import DataFrame, read_csv

from src.utils.data import FILENAME_PATTERN, HEADER_SIZE, ObservationType
from src.utils.factory import FileFactory


class FileHandler:
    file_factory = FileFactory()

    def extract_file(self, raw_file: str):
        match_filename = re.search(FILENAME_PATTERN, raw_file)
        if match_filename:
            file_name = match_filename.group(1)
            file_path = os.path.join("files/", file_name + ".exp")
            if os.path.exists(file_path):
                raise FileExistsError
            return self.file_factory.build_file(file_path, raw_file)

    def save_file(self, file_path: str, file_data: str):
        if not file_data:
            raise ValueError("Missing data.")

        with open(file_path, "w") as f:
            try:
                f.write(file_data)
            except Exception as ex:
                raise ex

    def clear_files(self):
        path = "files/"
        try:
            files = os.listdir(path)
            for file in files:
                file_path = os.path.join(path, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as ex:
                    raise ex("An error ocurred.")
        except FileNotFoundError:
            raise FileNotFoundError("Missing file.")
        except PermissionError:
            raise PermissionError("No permission to delete.")
        except Exception as ex:
            raise ex("An error ocurred.")

    def get_file(self, file_name: str):
        file_path = f"files/{file_name}"
        try:
            with open(file_path, "r") as file:
                file_data = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"No file with name {file_name}.")

        return self.file_factory.build_file(file_path, file_data)

    def get_files(self):
        return [
            file
            for file in os.listdir("files/")
            if os.path.isfile(os.path.join("files/", file))
        ]

    def get_data(self, file_path: str) -> DataFrame:
        """
        Returns a Pandas DataFrame from a `.exp` file.
        """
        return read_csv(file_path, sep="\t", skiprows=[x for x in range(HEADER_SIZE)])


class File:
    file_path: str
    file_name: str
    file_ext: str
    file_type: ObservationType
    file_data: str
    file_handler = FileHandler()

    def __init__(self, path: str, data: str) -> None:
        self.file_path = path
        self.file_name = path.split("/")[-1].split(".")[0]
        self.file_ext = path.split(".")[-1]
        self.file_data = data

        if "asa" in self.file_name:
            self.file_type = ObservationType.wing
        elif "pendura" in self.file_name:
            self.file_type = ObservationType.hanging
        else:
            raise ValueError("File is neither `asa` nor `pendura`.")

    def save(self) -> None:
        self.file_handler.save_file(self.file_path, self.file_data)
