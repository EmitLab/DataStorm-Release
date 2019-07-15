import json
import sys

# create an spatiotemporal index scaffolding for the current context
with open("/home/cc/job_gateway/context.json") as json_data:
    context = json.loads(json_data.read())

with open("/home/cc/job_gateway/job.json") as json_data:
    job = json.loads(json_data.read())

with open('/home/cc/DataStorm/default_template.txt', 'r') as content_file:
    content = content_file.read()

content = content.replace("$$TIME$$", context["temporal"]["window_size"])
content = content.replace("$$GRANULARITY$$", "10800")
content = content.replace("$$SPEED_LOWER$$", job["variables"]["speed_lower"])
content = content.replace("$$SPEED_UPPER$$", job["variables"]["speed_upper"])

text_file = open("/home/cc/DataStorm/default_settings.txt", "w")
text_file.write(content)
text_file.close()

sys.exit(0)
