import re

from google.cloud import storage
from pandas import DataFrame, read_csv

from src.utils.data import FILENAME_PATTERN, HEADER_SIZE, ObservationType
from src.utils.factory import FileFactory


class GCloudStorage:
    def __init__(self) -> None:
        self.client = storage.Client(project="injuries-backend")
        self.bucket_name = "injuries-backend.appspot.com"
        self.bucket = self.client.bucket(self.bucket_name)

    def write(self, path, data):
        blob = self.bucket.blob(path)
        with blob.open('w') as f:
            f.write(data)

    def read(self, path):
        blob = self.bucket.blob(path)
        data = None
        with blob.open('r') as f:
            data = f.read()

        return data

    def list(self):
        files = self.client.list_blobs(self.bucket_name)
        files = [file.name for file in files]
        return files

    def clear(self):
        files = self.list()
        geneartion_match_precondition = None
        for file in files:
            blob = self.bucket.blob(f"{file}")
            blob.reload()
            geneartion_match_precondition = blob.generation
            blob.delete(if_generation_match=geneartion_match_precondition)


class FileHandler:
    file_factory = FileFactory()
    file_storage = GCloudStorage()

    def extract_file(self, raw_file: str):
        match_filename = re.search(FILENAME_PATTERN, raw_file)
        if match_filename:
            file_name = match_filename.group(1)
            file_path = f"{file_name}.exp"
            if file_path in self.file_storage.list():
                raise FileExistsError
            return self.file_factory.build_file(file_path, raw_file)

    def save_file(self, file_path: str, file_data: str):
        if not file_data:
            raise ValueError("Missing data.")

        try:
            self.file_storage.write(file_path, file_data)
        except Exception as ex:
            raise ex

    def clear_files(self):
        try:
            self.file_storage.clear()
        except FileNotFoundError:
            raise FileNotFoundError("Missing file.")
        except PermissionError:
            raise PermissionError("No permission to delete.")
        except Exception as ex:
            raise ex("An error ocurred.")

    def get_file(self, file_name: str):
        file_path = f"{file_name}"
        try:
            file_data = self.file_storage.read(file_path)
        except Exception:
            raise FileNotFoundError(f"No file with name {file_name}.")

        return self.file_factory.build_file(file_path, file_data)

    def get_files(self):
        return self.file_storage.list()

    def get_data(self, file_name: str) -> DataFrame:
        """
        Returns a Pandas DataFrame from a `.exp` file.
        """
        file_path = f"gs://{self.file_storage.bucket_name}/{file_name}"
        try:
            df = read_csv(file_path, sep="\t", skiprows=[x for x in range(HEADER_SIZE)])
        except Exception as ex:
            raise ex
        return df


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
