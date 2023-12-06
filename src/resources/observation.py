import json
from typing import List

import falcon

import src.exceptions.http_exceptions as exc
from src.services.analyzer import Hanging, Observation, Wing
from src.services.extractor import FileHandler
from src.utils.data import ObservationType, units


class ObservationResource:
    observations: List[Observation] = []
    file_handler = FileHandler()

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        if not self.observations:
            raise exc.NotFound(description="Não há experimentos para serem analisados.")

        subject = req.get_param("subject")
        column = req.get_param("column")
        if not all((subject, column)):
            raise exc.InvalidRequest(
                description="Não foram selecionado parâmetros a serem analisados."
            )

        body = {}
        for observation in self.observations:
            threshold = 60 if isinstance(observation, Hanging) else 25
            indexes = observation.angle.index.tolist()
            angles = observation.angle[column]
            try:
                df = getattr(observation, subject)[column]
            except ValueError:
                raise exc.InvalidRequest(
                    description=f"Experimento não possui parâmetro {subject}."
                )
            except KeyError:
                raise exc.InternalError(
                    title="Erro de Dataframe",
                    description=f"Dataframe não possui coluna {column}.",
                )
            frames_max = df.sort_values(ascending=False).index.tolist()
            frame_max = frames_max[0]
            for frame in frames_max:
                if angles.loc[frame] > threshold:
                    frame_max = frame
                    break
            val_max = df.loc[frame_max]
            angle = angles.loc[frame_max]
            body[observation.name] = {
                "data": [
                    list(pair) for pair in zip(indexes, df.values.flatten().tolist())
                ],
                "extra": {
                    "val_max": f"{round(val_max, 3)} {units[subject]}",
                    "angle": f"{round(angle, 3)} °",
                },
            }
        resp.text = json.dumps(body)
        resp.status = falcon.HTTP_OK
        resp.content_type = falcon.MEDIA_JSON

    def on_get_clear(self, req: falcon.Request, resp: falcon.Response):
        try:
            self.file_handler.clear_files()
            self.observations.clear()
        except Exception as ex:
            raise exc.InternalError(
                title="Erro de Arquivos",
                description=f"Erro ao tentar limpar os arquivos: {ex.__str__()}.",
            )
        resp.text = json.dumps({"Sucesso": "Arquivos foram apagados com sucesso."})
        resp.status = falcon.HTTP_OK

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        body = req.get_media()
        if not body:
            raise exc.InvalidRequest(
                description="Não há um documento JSON válido no corpo de requisição."
            )

        files = body.get("arquivos")
        if files is None:
            raise exc.InvalidRequest(
                description="Faltando argumento `arquivos` na requisição, que deve ser uma lista de strings."
            )
        elif (
            not isinstance(files, list)
            or len(files) == 0
            or not all(isinstance(file, str) for file in files)
        ):
            raise exc.InvalidRequest(
                description="`arquivos` deve ser uma lista de strings"
            )

        for filename in files:
            try:
                file = self.file_handler.get_file(filename)
            except FileNotFoundError:
                raise exc.NotFound(
                    description=f"O arquivo {filename} não existe, ou ainda não foi carregado."
                )
            except ValueError:
                raise exc.FileNameError(
                    description=f"O nome do arquivo não traz informações suficientes sobre o experimento. \
                        {filename} não possui `asa` nem `pendura`."
                )
            if file.file_type == ObservationType.wing:
                try:
                    self.observations.append(Wing(file))
                except Exception as ex:
                    self.observations.clear()
                    raise exc.InternalError(
                        title="Erro de Dataframe",
                        description=f"Não foi possível gerar os dados para o experimento: {ex.__str__()}",
                    )
            elif file.file_type == ObservationType.hanging:
                try:
                    self.observations.append(Hanging(file))
                except Exception as ex:
                    self.observations.clear()
                    raise exc.InternalError(
                        title="Erro de Dataframe",
                        description=f"Não foi possível gerar os dados para o experimento: {ex.__str__()}",
                    )
        resp.text = json.dumps(
            {"Sucesso": f"Foram criados {len(self.observations)} experimentos"}
        )
        resp.status = falcon.HTTP_CREATED
