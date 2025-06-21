# dj_tagtool/backend/parsing.py

import os
import re
import xml.etree.ElementTree as ET

def extract_file_paths_from_xml(rekordbox_db_path):
    tree = ET.parse(rekordbox_db_path)
    root = tree.getroot()
    file_paths = []
    for track in root.iter("TRACK"):
        location = track.get("Location")
        if location:
            file_paths.append(location.replace("file://localhost/", "").replace("%20", " "))
    return file_paths

def get_file_paths_from_directory(music_directory):
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(music_directory)
        for file in files if file.lower().endswith(('.flac', '.mp3'))
    ]

def process_comments(comments, categories):
    pattern = re.compile(r'/\*(.*?)\*/', re.DOTALL)
    categorized = {k: [] for k in categories}
    categorized['No Category'] = []
    for comment in comments:
        matches = pattern.findall(comment)
        for match in matches:
            tags = [tag.strip() for tag in match.split(" / ")]
            for tag in tags:
                assigned = False
                for cat, info in categories.items():
                    if tag in info['tags']:
                        categorized[cat].append(tag)
                        assigned = True
                        break
                if not assigned:
                    categorized['No Category'].append(tag)
    return categorized
