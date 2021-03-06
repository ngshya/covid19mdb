import os
import re
from pandas import read_csv, to_datetime, merge, concat, DataFrame
from pymongo import ReplaceOne
from .mongo import get_collection


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
    dtf_data["DATE"] = to_datetime(dtf_data["DATE"]).dt.strftime("%Y%m%d")
    dtf_data["COUNTRY"] = dtf_data["COUNTRY"].str.lower()
    dtf_world = dtf_data.groupby(["DATE"])\
        .agg({type_n: "sum"})\
        .reset_index(drop=False)
    dtf_world["COUNTRY"] = "world"
    dtf_data = concat((dtf_data, dtf_world))
    dtf_data["_id"] = dtf_data["COUNTRY"] \
        + "_" + dtf_data["DATE"]
    dtf_data= dtf_data.loc[:, ["_id", "COUNTRY", "DATE", type_n]]
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
    dtf_data = merge(dtf_data_tot, dtf_data_rec, on=["_id", "COUNTRY", "DATE"], how="outer")
    dtf_data = merge(dtf_data, dtf_data_dea, on=["_id", "COUNTRY", "DATE"], how="outer")
    dtf_data = dtf_data.fillna(0)

    collection = get_collection(db="covid-19", collection="csse")
    update_objects = list()
    for j in range(dtf_data.shape[0]):
        dict_tmp = dtf_data.iloc[j, ].to_dict()
        dict_tmp["DATE"] = int(dict_tmp["DATE"])
        dict_tmp["T"] = int(dict_tmp["T"])
        dict_tmp["R"] = int(dict_tmp["R"])
        dict_tmp["D"] = int(dict_tmp["D"])
        update_objects.append(
            ReplaceOne( {'_id': dict_tmp['_id']},  dict_tmp, upsert=True)
        )
    collection.bulk_write(update_objects)


def get_csse_info(countries=[".*"], dates=[".*"]):
    countries = [s.lower() for s in countries]
    dates = [s.lower() for s in dates]
    regex= re.compile("^("+"|".join(countries)+")_("+"|".join(dates)+")")
    collection = get_collection(db="covid-19", collection="csse")
    response = list(collection.find({"_id": regex}))
    return response