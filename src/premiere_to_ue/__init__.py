"""Process editorial XML from Adobe Premiere for import into Unreal Engine."""

import importlib.metadata
import os
import pprint
import yaml

__version__ = importlib.metadata.version(__package__)

config = {}

with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as file:
    internal_config = yaml.safe_load(file)
    print("INFO: using internal config.yaml.")
    pprint.pprint(internal_config)
    config = internal_config

# optional local config, when found in current directory
if os.path.isfile("config.yaml"):
    with open("config.yaml", "r") as local_file:
        print("INFO: using additional local config.yaml.")
        local_config = yaml.safe_load(local_file)
        pprint.pprint(local_config)
        config = internal_config | local_config

print("INFO: combined config.yaml.")
pprint.pprint(config)
