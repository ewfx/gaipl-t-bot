import os
import yaml
from pathlib import Path

def load_config_details(file):
    try:
        with open(file, 'r', encoding = "utf-8") as read_data:
            config_data = yaml.safe_load(read_data)
            return config_data
    except yaml.YAMLError as exc:
        return str(exc)

def correct_path():
    possible_paths = [Path(os.path.join(os.getcwd(), "config.yml")), Path(os.path.join(os.getcwd(), "config", "config.yml"))]  
    for paath in possible_paths:
        if os.path.exists(paath):
            return paath
    return None


load_config_data = load_config_details(correct_path())
