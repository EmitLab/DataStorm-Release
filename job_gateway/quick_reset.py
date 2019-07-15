import json
import os

if os.path.isfile("job.json"):
    os.remove("job.json")

if os.path.isfile("context.json"):
    os.remove("context.json")

instance_data = None
if os.path.isfile("instance.json"):
    with open("instance.json", "r") as json_data:
        instance_data = json.loads(json_data.read())

if instance_data is not None:
    instance_data["current_job"] = None
    with open("instance.json", "w") as outfile:
        outfile.write(json.dumps(instance_data))

print("reset complete")
