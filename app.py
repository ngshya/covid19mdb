from flask import Flask
from covid19mdb.csse import get_csse_info

app = Flask(__name__)


@app.route('/', methods = ["GET", "POST"])
def hello():
    return 'Hello World!'


@app.route("/info/<countries>/<dates>/", methods = ["GET", "POST"])
def info(countries, dates):
    if countries == "all":
        countries = [".*"]
    else:
        countries = countries.split("-")
    if dates == "all":
        dates = [".*"]
    else:
        dates = dates.split("-")
    return get_csse_info(countries=countries, dates=dates)