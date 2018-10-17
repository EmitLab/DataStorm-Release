import asyncio
import json
import os
import sys

import websockets

# Note: Make sure that atleast visualization_config.json is in same folder as this main.py script
# 
# FOR LOCAL MACHINE:
# run this on local machine: python main.py 127.0.0.1 3000 MODEL
#      (if running locally): http://localhost:8080/DVProj/
# ------------------------------------------------------------------------------------------------
# FOR SERVER:
#             Run on  SERVER: python3 main.py 192.168.0.250 3000 hurricane
# After running, open browser and access link(if running on SERVER):
# http://localhost:8080/DVProj/?ip=129.114.111.8&port=3000

SOCKETS = set()
NOTIFIER_FOLDER = "/home/cc/viz-actor/"
VISUALIZATION_CONFIG = [
    {
        'model_type': "hurricane",
        'visual_type': "square_map",
        'options': {
            'name': "rain",
            'colors': ["#008000"],
            'max': 20,
            'min': 0.001,
            'opacity': 0.4,
            'sizes': [0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
            'size': 0.1,
            'values': {"value": 0}
        }
    },
    {
        'model_type': "flood",
        'visual_type': "heat_map",
        'options': {
            'name': "flood",
            'colors': ["#000DBF", "#1A00C3", "#4400C7", "#6F00CB", "#9C00CF", "#CB00D4", "#D800B4", "#DC008A",
                       "#E0005F", "#E50031"],
            'max': 180,
            'min': .1,
            'opacity': 0.4,
            'size': 0.1,
            'values': {"value": 0}
        }
    },
    {
        'model_type': "hurricane",
        'visual_type': "vector",
        'options': {
            'name': "wind",
            'min': 0.001,
            'size': 0.1,
            'sizes': [0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
            'values': {"value": 0, "u": 1, "v": 2}
        }
    },
    {
        'model_type': "human_mobility",
        'visual_type': "circle_map",
        'options': {
            'name': "human_mobility",
            'color': "#8B0000",
            'min': 0.1,
            'values': {"value": 0}
        }
    }
]

# DEFAULT_CONFIG = {}
'''
DEFAULT_CONFIG = {
    'date': {
        'begin': 'Jul 01 2018 00:00:00',
        'end': 'Jul 03 2018 00:00:00',
        'increment_hours': 0
    },
    'filters': {
        'flood': True,
        'network': True,
        'rain': True,
        'wind': True
    }
}
'''


async def set_config(socket, config):
    try:
        print('Sending user config...')

        prev_flag = 0
        flag_dict = {socket: prev_flag}
        count = 1
        while count < 16:
            files = [f for f in os.listdir(NOTIFIER_FOLDER + ".") if os.path.isfile(f) and
                     f.endswith('viz_config.json')]
            model_config_files_flag = len(files)
            if model_config_files_flag == 1:
                config = json.load(open(NOTIFIER_FOLDER + "hurricane_viz_config.json"))
            elif model_config_files_flag == 2:
                config = json.load(open(NOTIFIER_FOLDER + "flood_viz_config.json"))
            elif model_config_files_flag == 3:
                config = json.load(open(NOTIFIER_FOLDER + "human_mobility_viz_config.json"))
            else:
                config = json.load(open(NOTIFIER_FOLDER + "visualization_config.json"))

            # reset counter for new visualization
            if prev_flag != model_config_files_flag:
                count = 1

            if config['date']['increment_hours'] < 24:
                config['date']['increment_hours'] = count * 3

            await socket.send(json.dumps({'type': 'set_config', 'content': config, 'counter': count}))
            count += 1
            prev_flag = model_config_files_flag

            await asyncio.sleep(5)

    finally:
        SOCKETS.remove(socket)


async def set_visualization_config(socket, config):
    print('Sending visualization config...')
    count = 1
    # while count<5:
    await socket.send(json.dumps({'type': 'set_visualization_config', 'content': config, 'count': count}))


async def connect(socket, path):
    SOCKETS.add(socket)
    DEFAULT_CONFIG = {}
    # DEFAULT_CONFIG = json.load(open("visualization_config.json"))
    try:
        if model_type == 'hurricane':
            DEFAULT_CONFIG['filters']['network'] = False
            DEFAULT_CONFIG['filters']['flood'] = False
        elif model_type == 'flood':
            DEFAULT_CONFIG['filters']['network'] = False

        await set_visualization_config(socket, VISUALIZATION_CONFIG)
        await set_config(socket, DEFAULT_CONFIG)

        """
        async for message in socket:
            data = json.loads(message)
            if data['type'] == 'response':
                await socket.send(json.dumps({'type': '', 'content': ''}))
        """
    finally:
        # sys.exit(0)
        SOCKETS.remove(socket)


ip = '127.0.0.1'
port = 3000
model_type = None
print(sys.argv)
if len(sys.argv) > 1:
    ip = str(sys.argv[1])
if len(sys.argv) > 2:
    port = int(sys.argv[2])
if len(sys.argv) > 3:
    model_type = str(sys.argv[3])

asyncio.get_event_loop().run_until_complete(websockets.serve(connect, ip, port))
asyncio.get_event_loop().run_forever()
