import random
import sys

# project_type = 'Harricane'
project_type = sys.argv[1]
response = dict()

if project_type == 'Harricane':
    response['project_type'] = project_type
    response['initial_wind_speed'] = random.randint(10, 50)
    response['temperature'] = random.randint(60, 100)
    response['humidity'] = random.randint(10, 90)

if project_type == 'HumanMobility':
    response['project_type'] = project_type
    response['flood_threshold'] = random.randint(20, 50)
    response['speed'] = random.randint(40, 100)

print response
