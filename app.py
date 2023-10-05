import falcon

from src.resources.upload import UploadResource
from src.resources.observation import ObservationResource


def create_routes(app: falcon.App):
    # Observations
    app.add_route("/observations", ObservationResource())

    # Upload
    app.add_route("/upload", UploadResource())

    return app


def run():
    app = falcon.App()

    return create_routes(app)


app = application = run()
