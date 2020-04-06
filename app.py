from flask import Flask
from pandas import DataFrame
from covid19mdb.csse import get_csse_info
from covid19mdb.forecast_logistic import get_forecast_logistic_info

app = Flask(__name__)


@app.route('/', methods = ["GET", "POST"])
def hello():
    return 'Hello World!'


@app.route("/info/<country>/<date>/", methods = ["GET", "POST"])
def info(country, date):
    country = str(country).lower()
    date = int(date)
    csse_info = get_csse_info(countries=[country], dates=[".*"])
    csse_info = {idx: item for idx, item in enumerate(csse_info) if item["DATE"] <= date}
    forecast_logistic_info = get_forecast_logistic_info(countries=[country], dates=[str(date)])[0]
    forecast_logistic_info["past_fit"] = "-".join([str(_) for _ in forecast_logistic_info["past_fit"]])
    forecast_logistic_info["forecast"] = "-".join([str(_) for _ in forecast_logistic_info["forecast"]])
    return {"past": csse_info, "prediction": forecast_logistic_info}