import json
import iso8601

FLOOD_INPUT = ""  # with trailing slash
FLOODING_THRESHOLD = 0.25  # in meters
FLOOD_OUTPUT = "flooded_cells.csv"
CONTEXT = None
TEMP_COORDS = {"lon1": -87.6400, "lat1": 31, "lon2": -80.0200, "lat2": 24.0000}


import os
import socket
import sys
import time
import math

from statistics import mean
import pymongo
from bson.json_util import loads, dumps
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder

MONGO_SERVER = None
MONGO_CLIENT = None
STATE_CONFIG = None


def my_trunc(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper


def flooding_conversion():
    global CONTEXT
    global MONGO_SERVER, MONGO_CLIENT, STATE_CONFIG

    if MONGO_CLIENT is None:
        # connect to the mongo database using that configuration
        MONGO_SERVER = SSHTunnelForwarder(("129.114.33.117", 22), ssh_username="cc",
                                          ssh_pkey="~/.ssh/dsworker_rsa",
                                          remote_bind_address=('127.0.0.1', 27017))
        MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
        MONGO_CLIENT = pymongo.MongoClient('127.0.0.1', MONGO_SERVER.local_bind_port)  # connect to mongo

    dsfr_handle = MONGO_CLIENT.ds_results.dsfr

    def _time_to_sec(time_str):
        return sum(x * int(t) for x, t in zip([3600, 60, 1], time_str.split(":")))

    def _cell_tuple(x_east_west, y_north_south):
        width = abs(TEMP_COORDS["lat1"] - TEMP_COORDS["lat2"])
        height = abs(TEMP_COORDS["lon1"] - TEMP_COORDS["lon2"])

        x_east_west = float(x_east_west)
        y_north_south = float(y_north_south)
        x = (float(CONTEXT["map_statistics"]["east"]) - x_east_west) / float(CONTEXT["map_statistics"]["ewres"])
        y = (float(CONTEXT["map_statistics"]["north"]) - y_north_south) / float(CONTEXT["map_statistics"]["nsres"])
        x_pct = int(x) / float(CONTEXT["map_statistics"]["cols"])
        y_pct = int(y) / float(CONTEXT["map_statistics"]["rows"])
        r_lon = my_trunc(TEMP_COORDS["lon2"] - (width * x_pct), 1)  # important to trunc and not round
        r_lat = my_trunc(TEMP_COORDS["lat1"] - (height * y_pct), 1)  # or the data will be distorted
        output = [r_lon, r_lat]
        return output

    # converts raw flood model output (water depths) into map info plus a list of flooded cells, if any

    # determine the most recent simulation
    with open(FLOOD_INPUT + "most_recent.txt") as file_handle:
        sim_id = file_handle.readline()
    result_folder = FLOOD_INPUT + sim_id + "/"

    # get the context
    with open(result_folder + "context.json") as file_handle:
        CONTEXT = json.load(file_handle)

    # write the context in simplified form
    outfile = open(result_folder + FLOOD_OUTPUT, "w")
    # outfile.write(CONTEXT["map_statistics"]["rows"] + "," +
    #               CONTEXT["map_statistics"]["cols"] + "\n")

    observations = dict()

    # iterate over the files
    file_list = [f for f in os.listdir(result_folder)
                 if os.path.isfile(os.path.join(result_folder, f)) and "_h_" in f]
    for this_file in file_list:
        print(this_file)
        with open(result_folder + this_file, "r") as result_file:
            raw_results = result_file.readlines()
        step_num = this_file.split("_")[-1].split(".")[0]
        step_num = int(step_num)
        timestamp = int(1530403200 +
                        step_num * _time_to_sec(CONTEXT["time"]["step_size"]))

        if timestamp not in observations:
            observations[timestamp] = dict()

        for result in raw_results:
            result = result.replace("\n", "")
            result = result.split("|")
            if len(result) >= 3:
                lon, lat = _cell_tuple(result[0], result[1])
                if lon not in observations[timestamp]:
                    observations[timestamp][lon] = dict()
                if lat not in observations[timestamp][lon]:
                    observations[timestamp][lon][lat] = []
                observations[timestamp][lon][lat].append(float(result[2]))

    # convert the hierarchical data into grid-based data
    dsir_id = ObjectId()
    json_list = []
    for ts in observations:
        print(ts)
        for lon in observations[ts]:
            for lat in observations[ts][lon]:
                    entry = {
                                "parent": dsir_id,
                                "model_type": "flood",
                                "timestamp": ts,
                                "coordinate": (lon, lat),
                                "observation": [mean(observations[ts][lon][lat])]
                    }
                    json_list.append(entry)

    megaresult = dsfr_handle.insert_many(json_list, ordered=False)
    MONGO_SERVER.stop()


def main():
    flooding_conversion()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
