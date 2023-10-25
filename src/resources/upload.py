import json

import falcon

import src.exceptions.http_exceptions as exc
from src.services.extractor import FileHandler


class UploadResource:
    file_handler = FileHandler()

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        uploaded_file = req.get_media()
        if not uploaded_file:
            raise exc.InvalidRequest(
                description="Não há um documento JSON válido no corpo de requisição."
            )

        files_data = (part.get_data().decode("utf-8") for part in uploaded_file)
        saved_files = []
        for raw_file in files_data:
            try:
                file = self.file_handler.extract_file(raw_file)
            except FileExistsError:
                raise exc.DuplicatedFileError(
                    description="Já existe um arquivo com o mesmo nome. \
                        Certifique-se que não está tentando analisar o mesmo arquivo novamente."
                )
            try:
                file.save()
                saved_files.append(file.file_name)
            except Exception as ex:
                raise exc.InternalError(
                    title="Erro de Armazenamento",
                    description=f"Não foi possível salvar os arquivos. Detalhes: {ex.__str__()}",
                )
        resp.text = json.dumps(
            {
                "Sucesso": f"Foram salvos {len(saved_files)} arquivos.",
                "Arquivos": saved_files,
            }
        )
        resp.status = falcon.HTTP_CREATED

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        files = self.file_handler.get_files()
        singular = len(files) == 1

        if files:
            resp.text = json.dumps(
                {
                    "Sucesso": f"Há {len(files)} arquivo{'s' if singular else ''} salvo{'s' if singular else ''}.",
                    "Arquivos": files,
                }
            )
        else:
            resp.text = json.dumps(
                {
                    "Erro": "Não há arquivos salvos."
                }
            )
        resp.status = falcon.HTTP_OK
