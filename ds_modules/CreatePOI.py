import json
import sys


def main():

    hurricane_path = "/home/cc/job_gateway/input_data/hurricane/dsfr.json"
    flood_path = "/home/cc/job_gateway/input_data/flood/dsfr.json"
    map_path = "/home/cc/streets_highway_river.wkt"

    # hurricane_path = "../job_gateway/input_data/hurricane/dsfr.json"
    # flood_path = "../job_gateway/input_data/flood/dsfr.json"
    # map_path = "streets_highway_river.wkt"

    hurricane_nodes = set()
    with open(hurricane_path) as f:
        hurricane_content = json.loads(f.read())

    for each_line in hurricane_content:
        coordinate = each_line["coordinate"]
        observation = each_line["observation"]
        if sum(observation) > 0:
            hurricane_nodes.add(str(coordinate[0]) + "," + str(coordinate[1]))

    flood_nodes = set()
    with open(flood_path) as f:
        flood_content = json.loads(f.read())

    for each_line in flood_content:
        coordinate = each_line["coordinate"]
        observation = each_line["observation"]
        if sum(observation) >= 35:
            hurricane_nodes.add(str(coordinate[0]) + "," + str(coordinate[1]))

    with open(map_path) as f:
        map_content = f.readlines()

    map_nodes = set()
    x_max = float(0)
    x_min = float("inf")
    y_max = float(0)
    y_min = float("inf")

    for each in map_content:
        # print(each.replace("\n", "").replace("LINESTRING (", "").replace(")", ""))
        map_line = each.replace("\n", "").replace("LINESTRING (", "").replace(")", "")
        tmp_nodes = map_line.split(",")

        for each_node in tmp_nodes:
            map_nodes.add(each_node.strip())
            tmp_nodes_x = float(each_node.strip().split(" ")[0])
            tmp_nodes_y = float(each_node.strip().split(" ")[1])

            if tmp_nodes_x < x_min:
                x_min = tmp_nodes_x

            if tmp_nodes_y < y_min:
                y_min = tmp_nodes_y

            if tmp_nodes_x > x_max:
                x_max = tmp_nodes_x

            if tmp_nodes_y > y_max:
                y_max = tmp_nodes_y

    # Loop each node to see if it is affected by hurricane and flood
    node_prob = []
    for each_node in map_nodes:
        real_x = round((float(each_node.strip().split(" ")[0]) - x_min) / (x_max - x_min) * 7.62 - 87.64, 2)
        real_y = round((float(each_node.strip().split(" ")[1]) - y_min)/(y_max - y_min)*7 + 24, 2)

        tmp_node = str(real_x) + "," + str(real_y)
        if tmp_node in hurricane_nodes or tmp_node in flood_nodes:
            node_prob.append(each_node.replace(" ", "-") + ":" + str(0))
        else:
            node_prob.append(each_node.replace(" ", "-") + ":" + str(0.01))

    # print(node_prob)
    poi_file = open("/home/cc/DataStorm/data/POIs/output0.txt", "w")
    poi_file.writelines(["%s\n" % item for item in node_prob])


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)

    except Exception as e:
        print(e)
