import falcon
from falcon_cors import CORS

from src.resources.observation import ObservationResource
from src.resources.upload import UploadResource


def create_routes(app: falcon.App):
    # Observations
    app.add_route("/observations", ObservationResource())

    # Upload
    app.add_route("/upload", UploadResource())

    # Actions
    app.add_route("/observations/clear", ObservationResource(), suffix="clear")

    return app


def run():
    app = falcon.App()
    cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)
    app.add_middleware(cors.middleware)

    return create_routes(app)


app = application = run()
