import json

import falcon

from src.services.extractor import FileHandler


class UploadResource:
    file_handler = FileHandler()

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        uploaded_file = req.stream
        if not uploaded_file:
            resp.body = json.dumps({"Erro": "Não há um documento JSON válido no corpo de requisição."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        files_data = (
            uploaded_file
            .read(req.content_length or 0)
            .decode("utf-8")
            .split("--X-INSOMNIA-BOUNDARY")
            [1:-1]
        )
        saved_files = []
        for raw_file in files_data:
            try:
                file = self.file_handler.extract_file(raw_file)
            except FileExistsError:
                resp.body = json.dumps({
                    "Erro": "Já existe um arquivo com o mesmo nome. Certifique-se que não está tentando analisar o\
                            mesmo arquivo novamente."
                })
                resp.status = falcon.HTTP_BAD_REQUEST
                return
            try:
                file.save()
                saved_files.append(file.file_name)
            except Exception as ex:
                resp.body = json.dumps({
                    "Erro": "Não foi possível salvar os arquivos.",
                    "Detalhes": ex.__str__()
                })
                resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
                return
        resp.body = json.dumps({
            "Sucesso": f"Foram salvos {len(saved_files)} arquivos.",
            "Arquivos": saved_files
        })
        resp.status = falcon.HTTP_CREATED
