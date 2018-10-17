import urllib.request
import json
import time

lon_min = -87.64
lon_max = -80.02
lat_min = 24
lat_max = 31

res = 0.1
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}

results = dict()
curr_lon = lon_min
inc = 0
while curr_lon <= lon_max:
    curr_lat = lat_min
    if curr_lon not in results:
        results[curr_lon] = dict()
    while curr_lat <= lat_max:
        lon = curr_lon
        lat = curr_lat
        url = "https://api.onwater.io/api/v1/results/{0},{1}?access_token=fxTeXL-gp4zg4SKnB6T9". \
            format(lat, lon)
        time.sleep(4.01)  # don't exceed API limits
        try:
            request = urllib.request.Request(url, None, headers)  # The assembled request
            response = urllib.request.urlopen(request)
            data = response.read().decode("utf-8")  # The data u need
        except Exception as e:
            print(e)

        print(str(lon) + "," + str(lat))
        data = json.loads(data)
        results[curr_lon][curr_lat] = data["water"]
        curr_lat = round(curr_lat + res, 1)

    with open("/Users/hwbehren/Desktop/is_water.{0}.json".format(inc), "w") as outfile:
        outfile.write(json.dumps(results))
    inc = inc + 1
    curr_lon = round(curr_lon + res, 1)

print("Done!")
