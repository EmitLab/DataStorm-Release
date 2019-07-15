import copy
import json
import os
import subprocess
import sys
import matplotlib.pyplot as plt
import numpy as np

VERBOSE = False
SAVE_DISK = False


def log(my_string1, my_string2="", my_string3="", my_string4=""):
    my_string = str(my_string1) + str(my_string2) + str(my_string3) + str(my_string4)
    try:
        with open("hurricane_log.txt", "a") as errorlog:
            errorlog.write(json.dumps(str(my_string)) + "\n")
    except FileNotFoundError:
        print("No log file found.")


def get_range(start, end, step):
    return np.arange(start, end, step)


def test_eye(mu=0.0, sigma=1):
    lats = np.linspace(-10, 10, num=10)  # num_spatial_lat)
    lons = np.linspace(-10, 10, num=10)  # num_spatial_lon)

    lons_x, lats_y = np.meshgrid(lons, lats)

    lon_sq = np.square((lons_x - mu))
    lat_sq = np.square((lats_y - mu))

    log(lon_sq[0:5, 0:5])
    log(lat_sq[0:5, 0:5])

    lon_by_2 = lon_sq / (2 * sigma * sigma)
    lat_by_2 = lat_sq / (2 * sigma * sigma)

    exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))

    gaussian = 100 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

    np.savetxt('gaussian.csv', gaussian, fmt='%f', delimiter=',')


# def main(mu=0.0, sigma=1):
#     # trigger the job gateway to load the current job
#     command = ["/home/cc/job_gateway/venv/bin/python3",
#                "/home/cc/job_gateway/JobGateway.py",
#                "fetch_job"]
#     log("Calling JobGateway...")
#     try:
#         subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT)
#     except subprocess.CalledProcessError as cpe:
#         log("JobGateway returned exit code 1 on 'fetch_job'")
#         with open("/home/cc/error_log.txt", "w") as errorlog:
#             errorlog.write(json.dumps(str(cpe)))
#         return  # no job fetched
#     log("JobGateway fetched")
#     with open("/home/cc/job_gateway/context.json") as f:
#         data = json.load(f)
#
#     log(data)
#
#     record_list = []
#
#     # Preparing Timestamps
#     start_time = data['temporal']['begin']
#     end_time = data['temporal']['end']
#     time_step = 10800  # write a data output every 3 hours
#
#     time_stamps = get_range(start_time, end_time, time_step)
#     num_time = len(time_stamps)
#
#     log(time_stamps)
#
#     # Preparing timestamps
#     lat_start = data['spatial']['top']
#     lat_end = data['spatial']['bottom']
#     lat_step = data['spatial']['x_resolution']
#
#     lon_start = data['spatial']['left']
#     lon_end = data['spatial']['right']
#     lon_step = data['spatial']['y_resolution']
#
#     lat_grids = get_range(lat_start, lat_end, -lat_step)
#     lon_grids = get_range(lon_start, lon_end, lon_step)
#
#     num_spatial_lat = len(lat_grids)
#     num_spatial_lon = len(lon_grids)
#
#     log(num_time, num_spatial_lat, num_spatial_lon)
#
#     grid_lon, grid_lat = np.meshgrid(lon_grids, lat_grids)
#
#     log(grid_lon.shape)
#     log(grid_lat.shape)
#
#     # Hurricane Eye Diameter(DIA), Eye Center Location <lat, lon>
#
#     EYE_H2O = np.asarray([10, 16, 18, 20, 22, 24, 22, 15, 14, 12, 10, 8, 6, 5, 5, 5])
#     EYE_DIA = np.asarray(EYE_H2O / 2, dtype=int)
#     EYE_LAT = np.asarray([55, 50, 45, 40, 35, 34, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15])
#     EYE_LON = np.asarray([70, 66, 62, 58, 54, 50, 46, 42, 38, 34, 30, 26, 22, 18, 14, 10])
#
#     FILE_NAMES = ['20160701_0', '20160701_3', '20160701_6', '20160701_9',
#                   '20160701_12', '20160701_15', '20160701_18', '20160701_21',
#                   '20160702_0', '20160702_3', '20160702_6', '20160702_9',
#                   '20160702_12', '20160702_15', '20160702_18', '20160702_21']
#
#     if SAVE_DISK:
#         if not os.path.exists('./files/rain'):
#             os.makedirs('./files/rain')
#
#         if not os.path.exists('./files/lat'):
#             os.makedirs('./files/lat')
#
#         if not os.path.exists('./files/lng'):
#             os.makedirs('./files/lng')
#
#         if not os.path.exists('./files/U'):
#             os.makedirs('./files/U')
#
#         if not os.path.exists('./files/V'):
#             os.makedirs('./files/V')
#
#     gauss_size = 100
#
#     for t in range(0, num_time):
#
#         rain = np.zeros((num_spatial_lat, num_spatial_lon))
#         U = np.zeros((num_spatial_lat, num_spatial_lon))
#         V = np.zeros((num_spatial_lat, num_spatial_lon))
#
#         # 6 * np.random.sample((num_spatial_lat, num_spatial_lon)) - 3  # Picking numbers between [-3, 3]
#
#         ''' RAIN EXTRACTION '''
#
#         lb = (-1) * EYE_H2O[t]
#         ub = EYE_H2O[t]
#
#         lats = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lat)
#         lons = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lon)
#
#         lons_x, lats_y = np.meshgrid(lons, lats)
#
#         lon_sq = np.square((lons_x - mu))
#         lat_sq = np.square((lats_y - mu))
#
#         lon_by_2 = lon_sq / (2 * sigma * sigma)
#         lat_by_2 = lat_sq / (2 * sigma * sigma)
#
#         exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))
#
#         gaussian = 100 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val
#
#         if VERBOSE:
#             log(EYE_LAT[t], (EYE_LAT[t] + EYE_DIA[t]))
#             log(EYE_LON[t], (EYE_LON[t] + EYE_DIA[t]))
#
#         lb = 50 - int(EYE_DIA[t] / 2)
#         ub = lb + EYE_DIA[t]
#         rain[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = \
#             circularRain(copy.deepcopy(gaussian[lb:ub, lb:ub]))
#
#         ''' PREPARING WIND COMPONENTS '''
#
#         lb = (-1) * EYE_H2O[t]
#         ub = EYE_H2O[t]
#
#         lats = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lat)
#         lons = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lon)
#
#         lons_x, lats_y = np.meshgrid(lons, lats)
#
#         lon_sq = np.square((lons_x - mu))
#         lat_sq = np.square((lats_y - mu))
#
#         lon_by_2 = lon_sq / (2 * sigma * sigma)
#         lat_by_2 = lat_sq / (2 * sigma * sigma)
#
#         exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))
#
#         gaussian = 5 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val
#
#         uGauss = copy.deepcopy(gaussian)
#         vGauss = copy.deepcopy(gaussian)
#
#         # uGauss[int(gauss_size / 2):, :] = uGauss[int(gauss_size / 2):, :] * (-1)     # Represents Latitudes
#         # vGauss[:, 0: int(gauss_size / 2)] = vGauss[:, 0:int(gauss_size / 2)] * (-1)  # Represents Longitudes
#
#         uGauss, vGauss = circulatewind_4(uGauss, vGauss)
#         uGauss, vGauss = circulateEye(uGauss, vGauss)
#
#         lb = 50 - int(EYE_DIA[t] / 2)
#         ub = lb + EYE_DIA[t]
#
#         U[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = circularRain(
#             uGauss[lb:ub, lb:ub])
#         V[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = circularRain(
#             vGauss[lb:ub, lb:ub])
#
#         log(uGauss[lb:ub, lb:ub])
#
#         # package results for storage by the job gateway
#         for lon_idx in range(0, num_spatial_lon):
#             for lat_idx in range(0, num_spatial_lat):
#                 record = dict()
#                 record["timestamp"] = time_stamps[t]
#                 lon_label, lat_label = round(grid_lon[lat_idx, lon_idx], 2), round(grid_lat[lat_idx, lon_idx], 2)
#                 record["coordinate"] = [lon_label, lat_label]
#                 record["observation"] = [rain[lat_idx, lon_idx],
#                                          U[lat_idx, lon_idx],
#                                          V[lat_idx, lon_idx]]
#
#                 # record["data"] = dict()
#                 # record["data"]["rain"] = rain[lat_idx, lon_idx]
#                 # record["data"]["u"] = U[lat_idx, lon_idx]
#                 # record["data"]["v"] = V[lat_idx, lon_idx]
#
#                 if record["observation"] == [0, 0, 0]:
#                     continue  # don't bother storing data with all zeroes, PSM assumes all zeros if missing
#
#                 # record["TEST"] = False
#                 record_list.append(record)
#
#     log("Writing record_list to disk...")
#     with open("/home/cc/job_gateway/output_data/data.json", "w") as outfile:
#         outfile.write(json.dumps(record_list))
#     log("Written to disk! Asking job_gateway to upload...")
#
#     # trigger the job gateway to save the current job
#     command = ["/home/cc/job_gateway/venv/bin/python3",
#                "/home/cc/job_gateway/JobGateway.py",
#                "finish_job"]
#     try:
#         subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT)
#     except subprocess.CalledProcessError as cpe:
#         log("JobGateway returned exit code 1 on 'finish_job'")
#         with open("/home/cc/error_log.txt", "w") as errorlog:
#             errorlog.write(json.dumps(str(cpe)))
#         return  # could not save results for some reason?
#     log("JobGateway is all done! Results have been saved.")


def hurricane_parametrix(mu=0.0, sigma=1, rain_min=5, rain_max= 40, wind_severity=5):
    # trigger the job gateway to load the current job
    command = ["/home/cc/job_gateway/venv/bin/python3",
               "/home/cc/job_gateway/JobGateway.py",
               "fetch_job"]
    log("Calling JobGateway...")
    try:
        subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        log("JobGateway returned exit code 1 on 'fetch_job'")
        with open("/home/cc/error_log.txt", "w") as errorlog:
            errorlog.write(json.dumps(str(cpe)))
        return  # no job fetched
    log("JobGateway fetched")
    with open("/home/cc/job_gateway/context.json") as f:
        data = json.load(f)

    log(data)

    # job info, including sampling
    with open("/home/cc/job_gateway/job.json") as json_data:
        job_details = json.loads(json_data.read())
    job_variables = job_details["variables"]  # scaling_factor (used), evaporation_rate, transpiration_rate

    # load input parameters, if any are provided
    if job_variables["rain_min"]:
        rain_min = job_variables["rain_min"]
    if job_variables["rain_max"]:
        rain_min = job_variables["rain_max"]
    if job_variables["wind_severity"]:
        rain_min = job_variables["wind_severity"]

    record_list = []

    # Preparing Timestamps
    start_time = data['temporal']['begin']
    end_time = data['temporal']['end']
    time_step = 10800  # write a data output every 3 hours

    time_stamps = get_range(start_time, end_time, time_step)
    num_time = len(time_stamps)

    log(time_stamps)

    # Preparing timestamps
    lat_start = data['spatial']['top']
    lat_end = data['spatial']['bottom']
    lat_step = data['spatial']['x_resolution']

    lon_start = data['spatial']['left']
    lon_end = data['spatial']['right']
    lon_step = data['spatial']['y_resolution']

    lat_grids = get_range(lat_start, lat_end, -lat_step)
    lon_grids = get_range(lon_start, lon_end, lon_step)

    num_spatial_lat = len(lat_grids)
    num_spatial_lon = len(lon_grids)

    log(num_time, num_spatial_lat, num_spatial_lon)

    grid_lon, grid_lat = np.meshgrid(lon_grids, lat_grids)

    log(grid_lon.shape)
    log(grid_lat.shape)

    # Hurricane Path i.e. Eye Center Location <lat, lon>
    EYE_LAT = np.asarray([55, 50, 45, 40, 35, 34, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15])
    EYE_LON = np.asarray([70, 66, 62, 58, 54, 50, 46, 42, 38, 34, 30, 26, 22, 18, 14, 10])

    # Hurricane Eye Diameter(DIA)
    ct, bins, ignored = plt.hist(np.random.normal(0.0, 1.0, 1000), 16, normed=True)

    ct_min, ct_max = np.min(ct), np.max(ct)

    EYE_H2O = np.asarray(rain_min + ((ct - ct_min) / (ct_max - ct_min) * (rain_max - rain_min)), dtype='int')
    # EYE_H2O = np.asarray([10, 16, 18, 20, 22, 24, 22, 15, 14, 12, 10,  8,  6,  5,  5,  5])
    EYE_DIA = np.asarray(EYE_H2O / 2, dtype=int)

    FILE_NAMES = ['20160701_0', '20160701_3', '20160701_6', '20160701_9',
                  '20160701_12', '20160701_15', '20160701_18', '20160701_21',
                  '20160702_0', '20160702_3', '20160702_6', '20160702_9',
                  '20160702_12', '20160702_15', '20160702_18', '20160702_21']

    if SAVE_DISK:
        if not os.path.exists('./files/rain'):
            os.makedirs('./files/rain')

        if not os.path.exists('./files/lat'):
            os.makedirs('./files/lat')

        if not os.path.exists('./files/lng'):
            os.makedirs('./files/lng')

        if not os.path.exists('./files/U'):
            os.makedirs('./files/U')

        if not os.path.exists('./files/V'):
            os.makedirs('./files/V')

    gauss_size = 100

    for t in range(0, num_time):

        rain = np.zeros((num_spatial_lat, num_spatial_lon))
        U = np.zeros((num_spatial_lat, num_spatial_lon))
        V = np.zeros((num_spatial_lat, num_spatial_lon))

        # 6 * np.random.sample((num_spatial_lat, num_spatial_lon)) - 3  # Picking numbers between [-3, 3]

        ''' RAIN EXTRACTION '''

        lb = (-1) * EYE_H2O[t]
        ub = EYE_H2O[t]

        lats = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lat)
        lons = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lon)

        lons_x, lats_y = np.meshgrid(lons, lats)

        lon_sq = np.square((lons_x - mu))
        lat_sq = np.square((lats_y - mu))

        lon_by_2 = lon_sq / (2 * sigma * sigma)
        lat_by_2 = lat_sq / (2 * sigma * sigma)

        exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))

        gaussian = (rain_max * wind_severity) * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

        if VERBOSE:
            log(EYE_LAT[t], (EYE_LAT[t] + EYE_DIA[t]))
            log(EYE_LON[t], (EYE_LON[t] + EYE_DIA[t]))

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]
        rain[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = \
            circularRain(copy.deepcopy(gaussian[lb:ub, lb:ub]))

        ''' PREPARING WIND COMPONENTS '''

        lb = (-1) * EYE_H2O[t]
        ub = EYE_H2O[t]

        lats = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lat)
        lons = np.linspace(lb, ub, num=gauss_size)  # EYE_DIA[t])  # num_spatial_lon)

        lons_x, lats_y = np.meshgrid(lons, lats)

        lon_sq = np.square((lons_x - mu))
        lat_sq = np.square((lats_y - mu))

        lon_by_2 = lon_sq / (2 * sigma * sigma)
        lat_by_2 = lat_sq / (2 * sigma * sigma)

        exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))

        gaussian = wind_severity * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

        uGauss = copy.deepcopy(gaussian)
        vGauss = copy.deepcopy(gaussian)

        # uGauss[int(gauss_size / 2):, :] = uGauss[int(gauss_size / 2):, :] * (-1)     # Represents Latitudes
        # vGauss[:, 0: int(gauss_size / 2)] = vGauss[:, 0:int(gauss_size / 2)] * (-1)  # Represents Longitudes

        uGauss, vGauss = circulatewind_4(uGauss, vGauss)
        uGauss, vGauss = circulateEye(uGauss, vGauss)

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]

        U[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = circularRain(
            uGauss[lb:ub, lb:ub])
        V[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = circularRain(
            vGauss[lb:ub, lb:ub])

        log(uGauss[lb:ub, lb:ub])

        # package results for storage by the job gateway
        for lon_idx in range(0, num_spatial_lon):
            for lat_idx in range(0, num_spatial_lat):
                record = dict()
                record["timestamp"] = time_stamps[t]
                lon_label, lat_label = round(grid_lon[lat_idx, lon_idx], 2), round(grid_lat[lat_idx, lon_idx], 2)
                record["coordinate"] = [lon_label, lat_label]
                record["observation"] = [rain[lat_idx, lon_idx],
                                         U[lat_idx, lon_idx],
                                         V[lat_idx, lon_idx]]

                # record["data"] = dict()
                # record["data"]["rain"] = rain[lat_idx, lon_idx]
                # record["data"]["u"] = U[lat_idx, lon_idx]
                # record["data"]["v"] = V[lat_idx, lon_idx]

                if record["observation"] == [0, 0, 0]:
                    continue  # don't bother storing data with all zeroes, PSM assumes all zeros if missing

                # record["TEST"] = False
                record_list.append(record)

    log("Writing record_list to disk...")
    with open("/home/cc/job_gateway/output_data/data.json", "w") as outfile:
        outfile.write(json.dumps(record_list))
    log("Written to disk! Asking job_gateway to upload...")

    # trigger the job gateway to save the current job
    command = ["/home/cc/job_gateway/venv/bin/python3",
               "/home/cc/job_gateway/JobGateway.py",
               "finish_job"]
    try:
        subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        log("JobGateway returned exit code 1 on 'finish_job'")
        with open("/home/cc/error_log.txt", "w") as errorlog:
            errorlog.write(json.dumps(str(cpe)))
        return  # could not save results for some reason?
    log("JobGateway is all done! Results have been saved.")


def circulateEye(u, v):
    u2 = np.square(u)
    v2 = np.square(v)

    w = u2 + v2

    w = np.sqrt(w)

    idx = (w <= 0.1)

    u[idx] = 0
    v[idx] = 0

    return u, v


def circularRain(r):
    r[0, 0] = 0
    r[0, -1] = 0
    r[-1, 0] = 0
    r[-1, -1] = 0

    return r


def circulatewind_4(u, v):
    start_point = 0
    end_point = u.shape[0]
    mid_point = int(end_point / 2) + 1

    ENABLES = (1, 1, 1, 1)

    if ENABLES[0]:
        for r in range(start_point, mid_point):
            for c in range(start_point, mid_point):
                u[r, c] = u[r, c] if u[r, c] < 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] < 0 else v[r, c] * (-1)

    if ENABLES[1]:
        for r in range(start_point, mid_point):
            for c in range(mid_point, end_point):
                u[r, c] = u[r, c] if u[r, c] < 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] > 0 else v[r, c] * (-1)

    if ENABLES[2]:
        for r in range(mid_point, end_point):
            for c in range(mid_point, end_point):
                u[r, c] = u[r, c] if u[r, c] > 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] > 0 else v[r, c] * (-1)

    if ENABLES[3]:
        for r in range(mid_point, end_point):
            for c in range(start_point, mid_point):
                u[r, c] = u[r, c] if u[r, c] > 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] < 0 else v[r, c] * (-1)
    return u, v


def circulatewind_8(u, v):
    start_point = 0
    end_point = u.shape[0]
    mid_point = int(end_point / 2) + 1

    ENABLES = (1, 1, 1, 1, 1, 1, 1, 1)

    ''' WIND DIRECTION: 0 degree '''
    if ENABLES[0] == 1:
        for r in range(mid_point, end_point):
            for c in range(mid_point, r):
                u[r, c] = u[r, c] if u[r, c] > 0 else u[r, c] * (-1)
                v[r, c] = 0

    ''' WIND DIRECTION: 45 degree : u > 0, v > 0 '''
    if ENABLES[1] == 1:
        for r in range(mid_point, end_point):
            for c in range(r, end_point):
                u[r, c] = u[r, c] if u[r, c] > 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] > 0 else v[r, c] * (-1)

    ''' WIND DIRECTION: 90 degree '''
    if ENABLES[2] == 1:
        for r in range(start_point, mid_point):
            for c in range((end_point - r), end_point):
                v[r, c] = v[r, c] if v[r, c] > 0 else v[r, c] * (-1)
                u[r, c] = 0

    ''' WIND DIRECTION: 135 degree '''
    if ENABLES[3] == 1:
        for r in range(start_point, mid_point):
            for c in range(mid_point, (end_point - r)):
                u[r, c] = u[r, c] if u[r, c] < 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] > 0 else v[r, c] * (-1)

    ''' WIND DIRECTION: 180 degree '''
    if ENABLES[4] == 1:
        for r in range(start_point, mid_point):
            for c in range(r, mid_point):
                u[r, c] = u[r, c] if u[r, c] < 0 else u[r, c] * (-1)
                v[r, c] = 0

    ''' WIND DIRECTION: 225 degree '''
    if ENABLES[5] == 1:
        for r in range(start_point, mid_point):
            for c in range(start_point, r):
                u[r, c] = u[r, c] if u[r, c] < 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] < 0 else v[r, c] * (-1)

    ''' WIND DIRECTION: 270 degree '''
    if ENABLES[6] == 1:
        for c in range(start_point, mid_point):
            for r in range(mid_point, (end_point - c)):
                v[r, c] = v[r, c] if v[r, c] < 0 else v[r, c] * (-1)
                u[r, c] = 0

    ''' WIND DIRECTION: 315 degree '''
    if ENABLES[7] == 1:
        for c in range(start_point, mid_point):
            for r in range((end_point - c), end_point):
                u[r, c] = u[r, c] if u[r, c] > 0 else u[r, c] * (-1)
                v[r, c] = v[r, c] if v[r, c] < 0 else v[r, c] * (-1)

    return u, v


if __name__ == "__main__":
    try:
        hurricane_parametrix()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log("Encountered error:\nLine {0}\n{1}".format(exc_tb.tb_lineno, e))
