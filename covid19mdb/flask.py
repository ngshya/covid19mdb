from flask import Blueprint
from flask import Flask
routes = Blueprint('routes', __name__)


@routes.route('/status/', methods = ["GET", "POST"])
def api_status():
    return "200"


def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app