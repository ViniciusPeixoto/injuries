from falcon.errors import (HTTPBadRequest, HTTPInternalServerError,
                           HTTPNotFound, HTTPUnprocessableEntity)
from falcon.util.deprecation import deprecated_args


class InvalidRequest(HTTPBadRequest):
    @deprecated_args(allowed_positional=0)
    def __init__(self, description=None, headers=None, **kwargs):
        super().__init__(
            title="Requisição Inválida",
            description=description,
            headers=headers,
            **kwargs,
        )


class DuplicatedFileError(HTTPBadRequest):
    @deprecated_args(allowed_positional=0)
    def __init__(self, description=None, headers=None, **kwargs):
        super().__init__(
            title="Arquivos Duplicados",
            description=description,
            headers=headers,
            **kwargs,
        )


class NotFound(HTTPNotFound):
    @deprecated_args(allowed_positional=0)
    def __init__(self, description=None, headers=None, **kwargs):
        super().__init__(
            title="Arquivos Não Encontrados",
            description=description,
            headers=headers,
            **kwargs,
        )


class InternalError(HTTPInternalServerError):
    @deprecated_args(allowed_positional=0)
    def __init__(self, title=None, description=None, headers=None, **kwargs):
        super().__init__(
            title=title,
            description=description,
            headers=headers,
            **kwargs,
        )


class FileNameError(HTTPUnprocessableEntity):
    @deprecated_args(allowed_positional=0)
    def __init__(self, title=None, description=None, headers=None, **kwargs):
        super().__init__(
            title="Nome do Arquivo Inválido",
            description=description,
            headers=headers,
            **kwargs,
        )
