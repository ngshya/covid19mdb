from covid19mdb.csse import update_csse_mdb
from covid19mdb.forecaster_logistic import update_forecast_logistic_mdb

if __name__ == "__main__":
    update_csse_mdb()
    update_forecast_logistic_mdb()