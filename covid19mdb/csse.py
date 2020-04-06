import os
import re
from pandas import read_csv, to_datetime, merge, concat, DataFrame
from pymongo import MongoClient, ReplaceOne


def get_csse_data(url, dates=None):
    if dates is None:
        usecols = None
    else:
        usecols = ["Province/State", "Country/Region", "Lat", "Long"] + dates
    dtf_data = read_csv(
        filepath_or_buffer=url,
        sep=",",
        usecols=usecols,
        low_memory=True
    )
    return dtf_data


def csse_data(url, type_n, dates=None):
    dtf_data = get_csse_data(
    url=url, 
    dates=dates
    )
    array_cols = list(set(dtf_data) - set(["Province/State", "Lat", "Long"]))
    dtf_data = dtf_data.loc[:, array_cols]\
        .rename({"Country/Region": "COUNTRY"}, axis=1)\
        .groupby(["COUNTRY"])\
        .agg("sum")\
        .reset_index(drop=False)\
        .melt('COUNTRY', var_name='DATE', value_name=type_n)
    dtf_data["DATE"] = to_datetime(dtf_data["DATE"])
    dtf_world = dtf_data.groupby(["DATE"])\
        .agg({type_n: "sum"})\
        .reset_index(drop=False)
    dtf_world["COUNTRY"] = "World"
    dtf_data = concat((dtf_data, dtf_world))
    dtf_data["_id"] = dtf_data["COUNTRY"].str.lower() \
        + "_" + dtf_data["DATE"].dt.strftime("%Y%m%d")
    dtf_data= dtf_data.loc[:, ["_id", type_n]]
    return dtf_data


def update_csse_mdb():
    # TODO: values as input parameters
    dtf_data_tot = csse_data(
        url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"\
            + "csse_covid_19_data/csse_covid_19_time_series/"\
            + "time_series_covid19_confirmed_global.csv", 
        type_n="T"
    )
    dtf_data_rec = csse_data(
        url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"\
            + "csse_covid_19_data/csse_covid_19_time_series/"\
            + "time_series_covid19_recovered_global.csv", 
        type_n="R"
    )
    dtf_data_dea = csse_data(
        url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"\
            + "csse_covid_19_data/csse_covid_19_time_series/"\
            + "time_series_covid19_deaths_global.csv", 
        type_n="D"
    )
    dtf_data = merge(dtf_data_tot, dtf_data_rec, on="_id", how="outer")
    dtf_data = merge(dtf_data, dtf_data_dea, on="_id", how="outer")
    dtf_data = dtf_data.fillna(0)

    mdb_user = os.environ["mdb_user"]
    mdb_password = os.environ["mdb_pwd"]

    client = MongoClient('mongodb://'+mdb_user+':'+mdb_password\
        +'@ds263018.mlab.com:63018/covid-19', retryWrites=False)
    db = client["covid-19"]
    db.list_collection_names()
    collection = db["csse"]
    update_objects = list()
    for j in range(dtf_data.shape[0]):
        dict_tmp = dtf_data.iloc[j, ].to_dict()
        dict_tmp["T"] = int(dict_tmp["T"])
        dict_tmp["R"] = int(dict_tmp["R"])
        dict_tmp["D"] = int(dict_tmp["D"])
        update_objects.append(
            ReplaceOne( {'_id': dict_tmp['_id']},  dict_tmp, upsert=True)
        )
    collection.bulk_write(update_objects)


def get_csse_info(countries=[".*"], dates=[".*"]):
    countries = [s.lower() for s in countries]
    regex= re.compile("^("+"|".join(countries)+")_("+"|".join(dates)+")")
    mdb_user = os.environ["mdb_user"]
    mdb_password = os.environ["mdb_pwd"]
    client = MongoClient('mongodb://'+mdb_user+':'+mdb_password\
        +'@ds263018.mlab.com:63018/covid-19', retryWrites=False)
    db = client["covid-19"]
    db.list_collection_names()
    collection = db["csse"]
    out = collection.find({"_id": regex})
    #out = DataFrame(out)
    return out