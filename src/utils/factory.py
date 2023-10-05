class FileFactory:
    def build_file(self, path: str, data: str):
        from src.services.extractor import File
        return File(path, data)
