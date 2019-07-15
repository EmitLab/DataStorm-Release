from scipy.stats import truncnorm
import matplotlib.pyplot as plt

import numpy as np
import json
import os
import copy

VERBOSE = False
SAVE_DISK = False


def get_range(start, end, step):
    return np.arange(start, end, step)


def test_eye(mu=0.0, sigma=1):
    lats = np.linspace(-10, 10, num=10)  # num_spatial_lat)
    lons = np.linspace(-10, 10, num=10)  # num_spatial_lon)

    lons_x, lats_y = np.meshgrid(lons, lats)

    lon_sq = np.square((lons_x - mu))
    lat_sq = np.square((lats_y - mu))

    print(lon_sq[0:5, 0:5])
    print(lat_sq[0:5, 0:5])

    lon_by_2 = lon_sq / (2 * sigma * sigma)
    lat_by_2 = lat_sq / (2 * sigma * sigma)

    exp_val = np.exp((-1) * (lon_by_2 + lat_by_2))

    gaussian = 100 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

    np.savetxt('gaussian.csv', gaussian, fmt='%f', delimiter=',')


def main(mu=0.0, sigma=1):
    with open("context.json") as f:
        data = json.load(f)

    print(data)

    record_list = []

    # Preparing Timestamps
    start_time = data['temporal']['begin']
    end_time = data['temporal']['end']
    time_step = data['temporal']['window_size']

    time_stamps = get_range(start_time, end_time, time_step)
    num_time = len(time_stamps)

    print(time_stamps)

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

    print(num_time, num_spatial_lat, num_spatial_lon)

    grid_lon, grid_lat = np.meshgrid(lon_grids, lat_grids)

    # print(grid_lat[0:5, 0:5])
    # print(grid_lon[0:5, 0:5])

    print(grid_lon.shape)
    print(grid_lat.shape)

    # Hurricane Eye Diameter(DIA), Eye Center Location <lat, lon>

    EYE_H2O = np.asarray([10, 16, 18, 20, 22, 24, 22, 15, 14, 12, 10,  8,  6,  5,  5,  5])
    EYE_DIA = np.asarray(EYE_H2O / 2, dtype=int)
    EYE_LAT = np.asarray([55, 50, 45, 40, 35, 34, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15])
    EYE_LON = np.asarray([70, 66, 62, 58, 54, 50, 46, 42, 38, 34, 30, 26, 22, 18, 14, 10])

    FILE_NAMES = [ '20160701_0',  '20160701_3',  '20160701_6',  '20160701_9',
                  '20160701_12', '20160701_15', '20160701_18', '20160701_21',
                   '20160702_0',  '20160702_3',  '20160702_6',  '20160702_9',
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

        gaussian = 100 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

        if VERBOSE:
            print(EYE_LAT[t], (EYE_LAT[t] + EYE_DIA[t]))
            print(EYE_LON[t], (EYE_LON[t] + EYE_DIA[t]))

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]
        rain[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = gaussian[lb:ub, lb:ub]

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

        gaussian = 5 * (1 / np.sqrt(np.square(2 * np.pi))) * exp_val

        UGauss = copy.deepcopy(gaussian)
        VGauss = copy.deepcopy(gaussian)

        UGauss[:, 0: int(gauss_size / 2)] = UGauss[:, 0:int(gauss_size / 2)] * (-1)
        VGauss[int(gauss_size / 2):, :] = VGauss[int(gauss_size / 2):, :] * (-1)

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]

        U[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = VGauss[lb:ub, lb:ub]
        V[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = UGauss[lb:ub, lb:ub]

        if t == 0:
            print(int(UGauss.shape[1] / 2))
            print(UGauss[lb:ub, lb:ub])
            print(VGauss[lb:ub, lb:ub])

        if SAVE_DISK:
            np.savetxt('./files/rain/' + FILE_NAMES[t] + '.rain.csv', rain, fmt='%f', delimiter=',')
            np.savetxt('./files/lat/' + FILE_NAMES[t] + '.lat.csv', grid_lat, fmt='%f', delimiter=',')
            np.savetxt('./files/lng/' + FILE_NAMES[t] + '.lng.csv', grid_lon, fmt='%f', delimiter=',')
            np.savetxt('./files/U/' + FILE_NAMES[t] + '.u.csv', U, fmt='%f', delimiter=',')
            np.savetxt('./files/V/' + FILE_NAMES[t] + '.v.csv', V, fmt='%f', delimiter=',')

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

                record["data"] = dict()
                record["data"]["rain"] = rain[lat_idx, lon_idx]
                record["data"]["u"] = U[lat_idx, lon_idx]
                record["data"]["v"] = V[lat_idx, lon_idx]

                record["TEST"] = False
                record_list.append(record)


def hurricane_parametrix(mu=0.0, sigma=1, rain_min=5, rain_max= 40, wind_severity=5):
    with open("context.json") as f:
        data = json.load(f)

    print(data)

    record_list = []

    # Preparing Timestamps
    start_time = data['temporal']['begin']
    end_time = data['temporal']['end']
    time_step = data['temporal']['window_size']

    time_stamps = get_range(start_time, end_time, time_step)
    num_time = len(time_stamps)

    print(time_stamps)

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

    print(num_time, num_spatial_lat, num_spatial_lon)

    grid_lon, grid_lat = np.meshgrid(lon_grids, lat_grids)

    # print(grid_lat[0:5, 0:5])
    # print(grid_lon[0:5, 0:5])

    print(grid_lon.shape)
    print(grid_lat.shape)

    # Hurricane Path i.e. Eye Center Location <lat, lon>
    EYE_LAT = np.asarray([55, 50, 45, 40, 35, 34, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15])
    EYE_LON = np.asarray([70, 66, 62, 58, 54, 50, 46, 42, 38, 34, 30, 26, 22, 18, 14, 10])

    # Hurricane Eye Diameter(DIA)
    ct, bins, ignored = plt.hist(np.random.normal(0.0, 1.0, 1000), 16, normed=True)
    print(ct)

    ct_min, ct_max = np.min(ct), np.max(ct)

    EYE_H2O = np.asarray(rain_min + ((ct - ct_min) / (ct_max - ct_min) * (rain_max - rain_min)), dtype='int')
    # EYE_H2O = np.asarray([10, 16, 18, 20, 22, 24, 22, 15, 14, 12, 10,  8,  6,  5,  5,  5])
    EYE_DIA = np.asarray(EYE_H2O / 2, dtype=int)


    FILE_NAMES = [ '20160701_0',  '20160701_3',  '20160701_6',  '20160701_9',
                  '20160701_12', '20160701_15', '20160701_18', '20160701_21',
                   '20160702_0',  '20160702_3',  '20160702_6',  '20160702_9',
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
            print(EYE_LAT[t], (EYE_LAT[t] + EYE_DIA[t]))
            print(EYE_LON[t], (EYE_LON[t] + EYE_DIA[t]))

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]
        rain[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = gaussian[lb:ub, lb:ub]

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

        UGauss = copy.deepcopy(gaussian)
        VGauss = copy.deepcopy(gaussian)

        UGauss[:, 0: int(gauss_size / 2)] = UGauss[:, 0:int(gauss_size / 2)] * (-1)
        VGauss[int(gauss_size / 2):, :] = VGauss[int(gauss_size / 2):, :] * (-1)

        lb = 50 - int(EYE_DIA[t] / 2)
        ub = lb + EYE_DIA[t]

        U[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = VGauss[lb:ub, lb:ub]
        V[EYE_LAT[t]:(EYE_LAT[t] + EYE_DIA[t]), EYE_LON[t]:(EYE_LON[t] + EYE_DIA[t])] = UGauss[lb:ub, lb:ub]

        if t == 0:
            print(int(UGauss.shape[1] / 2))
            print(UGauss[lb:ub, lb:ub])
            print(VGauss[lb:ub, lb:ub])

        if SAVE_DISK:
            np.savetxt('./files/rain/' + FILE_NAMES[t] + '.rain.csv', rain, fmt='%f', delimiter=',')
            np.savetxt('./files/lat/' + FILE_NAMES[t] + '.lat.csv', grid_lat, fmt='%f', delimiter=',')
            np.savetxt('./files/lng/' + FILE_NAMES[t] + '.lng.csv', grid_lon, fmt='%f', delimiter=',')
            np.savetxt('./files/U/' + FILE_NAMES[t] + '.u.csv', U, fmt='%f', delimiter=',')
            np.savetxt('./files/V/' + FILE_NAMES[t] + '.v.csv', V, fmt='%f', delimiter=',')

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

                record["data"] = dict()
                record["data"]["rain"] = rain[lat_idx, lon_idx]
                record["data"]["u"] = U[lat_idx, lon_idx]
                record["data"]["v"] = V[lat_idx, lon_idx]

                record["TEST"] = False
                record_list.append(record)

                # if np.sum(record['observation']) > 0.0:
                #     print(record)


if __name__ == "__main__":
    try:
        # main()
        hurricane_parametrix(mu=0.0, sigma=1, rain_min=5, rain_max=40, wind_severity=5)
    except Exception as e:
        print(e)
