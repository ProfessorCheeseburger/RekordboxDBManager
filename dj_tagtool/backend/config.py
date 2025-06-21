# dj_tagtool/backend/config.py

import json
import os

def load_config(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "categories": {},
        "rekordbox_db_path": "",
        "music_directory": "",
        "mytag_db_file": "",
        "use_rekordbox_xml": False,
        "tag_delimiter": ","
    }

def save_config(config, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
