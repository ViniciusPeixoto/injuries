import json
from typing import List

import falcon

from src.services.extractor import FileHandler
from src.services.analyzer import Observation, Wing, Hanging
from src.utils.data import ObservationType


class ObservationResource:
    observations: List[Observation] = []
    file_handler = FileHandler()

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        observation_names = [observation.name for observation in self.observations]
        resp.body = json.dumps({
            "Sucesso": f"Existem {len(self.observations)} experimentos prontos para análise.",
            "Experimentos": observation_names
        })
        resp.status = falcon.HTTP_OK

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        body = req.stream.read(req.content_length or 0)
        if not body:
            resp.body = json.dumps({"Erro": "Não há um documento JSON válido no corpo de requisição."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        body = json.loads(body.decode("utf-8"))
        if not body:
            resp.body = json.dumps({"Erro": "Não há um documento JSON válido no corpo de requisição."})
            resp.status = falcon.HTTP_BAD_REQUEST
            return

        files = body.get("arquivos")
        if files is None:
            resp.body = json.dumps({
                "Erro": "A requisição está montada de forma incorreta.",
                "Detalhes": "Faltando argumento `arquivos`, que deve ser uma lista de strings."
            })
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        elif (
            not isinstance(files, list)
            or len(files) == 0
            or not all(isinstance(file, str) for file in files)
        ):
            resp.body = json.dumps({
                "Erro": "A requisição está montada de forma incorreta.",
                "Detalhes": "`arquivos` deve ser uma lista de strings"
            })
            resp.status = falcon.HTTP_BAD_REQUEST
            return
        for filename in files:
            try:
                file = self.file_handler.get_file(filename)
            except FileNotFoundError:
                self.observations.clear()
                resp.body = json.dumps({
                    "Erro": "O arquivo informado não existe, ou ainda não foi carregado.",
                    "Arquivo": filename
                })
                resp.status = falcon.HTTP_NOT_FOUND
                return
            except ValueError:
                resp.body = json.dumps({
                    "Erro": "O nome do arquivo não traz informações suficientes sobre o experimento.",
                    "Detalhes": f"{filename} não possui `asa` nem `pendura`."
                })
                resp.status = falcon.HTTP_BAD_REQUEST
                return
            if file.file_type == ObservationType.wing:
                try:
                    self.observations.append(Wing(file))
                except Exception as ex:
                    self.observations.clear()
                    resp.body = json.dumps({
                        "Erro": "O arquivo não existe no caminho especificado.",
                        "Detalhes": ex.__str__()
                    })
                    resp.status = falcon.HTTP_NOT_FOUND
                    return
            elif file.file_type == ObservationType.hanging:
                try:
                    self.observations.append(Hanging(file))
                except Exception as ex:
                    self.observations.clear()
                    resp.body = json.dumps({
                        "Erro": "O arquivo não existe no caminho especificado.",
                        "Detalhes": ex.__str__()
                    })
                    resp.status = falcon.HTTP_NOT_FOUND
                    return
        resp.body = json.dumps({"Sucesso": f"Foram criados {len(self.observations)} experimentos"})
        resp.status = falcon.HTTP_CREATED