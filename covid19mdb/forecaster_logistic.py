from pandas import DataFrame
from .mongo import get_collection
from .logistic import ModelLogistic


def forecast_logistic_country(country, today, n_forecast):
    country = country.lower()
    today = int(today)
    n_forecast = int(n_forecast)
    collection = get_collection(db="covid-19", collection="csse")
    dtf_data = DataFrame(
        collection.find({"COUNTRY": "italy", "DATE": {"$lte": today}})
    )
    if dtf_data.shape[0] <= 3:
        return None
    dtf_data = dtf_data.sort_values(["DATE"])
    model = ModelLogistic()
    model.fit(dtf_data["T"].values)
    dict_forecast = model.forecast(n_forecast=n_forecast)
    dict_forecast["past_fit"] = [int(_) for _ in dict_forecast["past_fit"]]
    dict_forecast["forecast"] = [int(_) for _ in dict_forecast["forecast"]]
    return dict_forecast


def update_forecast_logistic_mdb():
    collection_csse = get_collection(db="covid-19", collection="csse")
    collection_forecast_logistic = get_collection(
        db="covid-19", 
        collection="forecast_logistic"
    )
    array_idx = collection_csse.distinct("_id")
    for _id in array_idx:
        if collection_forecast_logistic.find_one({"_id": _id}) is None:
            print(_id + " not found. Forecasting...")
            country, today = _id.split("_")
            today = int(today)
            dict_forecast = forecast_logistic_country(
                country=country, 
                today=today, 
                n_forecast=30
            )
            dict_forecast["_id"] = _id
            dict_forecast["COUNTRY"] = country
            dict_forecast["DATE"] = today
            collection_forecast_logistic.insert_one(dict_forecast)