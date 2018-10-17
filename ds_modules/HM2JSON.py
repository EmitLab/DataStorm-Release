import csv
import json
import sys


def main():

    location_path = "/home/cc/DataStorm/reports/default_scenario_LocationSnapshotReport.txt"

    with open("/home/cc/job_gateway/context.json") as json_data:
        context = json.loads(json_data.read())

    time_begin = context["temporal"]["begin"]

    with open(location_path) as f:
        reader = csv.reader(f)
        data = [r for r in reader]

    timestamp = 0
    results = []
    for i in range(len(data)):

        if '[' in data[i][0]:
            timestamp = time_begin + int(data[i][0].replace("[", "").replace("]", ""))
            continue

        coords = data[i][0].split(" ")
        doc = dict()
        doc["observation"] = [1]
        doc["coordinate"] = [float(coords[1]), float(coords[2])]
        doc["timestamp"] = timestamp

        results.append(doc)

    # thefile = open('location.txt', 'w')
    # thefile.writelines(["%s\n" % item for item in results])
    with open("/home/cc/job_gateway/output_data/data.json", "w") as outfile:
        outfile.write(json.dumps(results))


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)

    except Exception as e:
        print(e)
