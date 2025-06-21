# dj_tagtool/backend/processing.py

import os
import xml.etree.ElementTree as ET

from dj_tagtool.backend.parsing import extract_file_paths_from_xml, get_file_paths_from_directory, process_comments
from dj_tagtool.backend.metadata import update_metadata_flac, update_metadata_mp3, update_track_in_xml

def update_xml(config):
    categories = config["categories"]
    delimiter = config["tag_delimiter"]
    mytag_db_file = config["mytag_db_file"]
    rekordbox_db_path = config["rekordbox_db_path"]
    use_xml = config["use_rekordbox_xml"]

    if use_xml:
        file_paths = extract_file_paths_from_xml(rekordbox_db_path)
    else:
        file_paths = get_file_paths_from_directory(config["music_directory"])

    if os.path.exists(mytag_db_file):
        tree = ET.parse(mytag_db_file)
        root = tree.getroot()
    else:
        root = ET.Element("MusicTags")
        tree = ET.ElementTree(root)

    for path in file_paths:
        if not os.path.exists(path):
            continue
        comments = []
        if path.lower().endswith('.flac'):
            from mutagen.flac import FLAC
            audio = FLAC(path)
            comments = audio.get("comment", [])
        elif path.lower().endswith('.mp3'):
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3
            audio = MP3(path, ID3=ID3)
            comments = [frame.text for frame in audio.tags.getall("COMM")]

        flat_comments = [c for comment in comments for c in (comment if isinstance(comment, list) else [comment])]
        cat_tags = process_comments(flat_comments, categories)

        song_elem = next((s for s in root.findall("Song") if s.find("FilePath").text == path), None)
        if not song_elem:
            song_elem = ET.SubElement(root, "Song")
            ET.SubElement(song_elem, "FilePath").text = path

        for cat, info in categories.items():
            cat_elem = song_elem.find(cat) or ET.SubElement(song_elem, cat)
            existing = {t.text for t in cat_elem.findall("Tag")}
            for tag in cat_tags.get(cat, []):
                if tag not in existing:
                    ET.SubElement(cat_elem, "Tag").text = tag

        if path.lower().endswith('.flac'):
            update_metadata_flac(path, cat_tags, categories, delimiter)
        elif path.lower().endswith('.mp3'):
            update_metadata_mp3(path, cat_tags, categories, delimiter)

        if use_xml:
            update_track_in_xml(rekordbox_db_path, path, cat_tags, categories, delimiter)

    ET.indent(tree, '  ')
    tree.write(mytag_db_file, encoding="utf-8", xml_declaration=True)

def run_conversion(config_dict):
    update_xml(config_dict)
    return f"Conversion completed. Output saved to: {config_dict['mytag_db_file']}"
