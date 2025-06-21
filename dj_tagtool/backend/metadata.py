# dj_tagtool/backend/metadata.py

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TXXX
from mutagen.easyid3 import EasyID3
import xml.etree.ElementTree as ET
import os

def update_metadata_flac(path, tags, categories, delimiter):
    audio = FLAC(path)
    for cat, info in categories.items():
        key = info.get('flac_metadata_field', '').upper().replace(" ", "")
        if tags.get(cat):
            audio[key] = delimiter.join(tags[cat])
    audio.save()

def update_metadata_mp3(path, tags, categories, delimiter):
    audio = MP3(path, ID3=ID3)
    for cat, info in categories.items():
        field = info.get('mp3_metadata_field', '').lower()
        tag_str = delimiter.join(tags.get(cat, []))
        if not tag_str:
            continue
        if field in EasyID3.valid_keys:
            e_audio = MP3(path, ID3=EasyID3)
            e_audio[field] = tag_str
            e_audio.save()
        else:
            audio.tags.add(TXXX(encoding=3, desc=field, text=tag_str))
    audio.save()

def update_track_in_xml(db_path, file_path, tags, categories, delimiter):
    tree = ET.parse(db_path)
    root = tree.getroot()
    for track in root.iter("TRACK"):
        location = track.get("Location")
        if location and location == f"file://localhost/{file_path.replace(' ', '%20')}":
            for cat, info in categories.items():
                field = info.get("rekordbox_field")
                if field and tags.get(cat):
                    track.set(field, delimiter.join(tags[cat]))
            break
    ET.indent(tree, '  ')
    tree.write(db_path, encoding="utf-8", xml_declaration=True)
