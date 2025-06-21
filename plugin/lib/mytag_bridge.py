# mytag_bridge.py
from pyrekordbox import library
import os

lib = library.get()

def _get_track(filepath):
    filepath = filepath.lower().replace("\\", "/")
    for t in lib.tracks:
        if t.location and os.path.normpath(t.location).lower() == filepath:
            return t
    return None

def get_tags_for_file(filepath):
    track = _get_track(filepath)
    return track.my_tags if track else []

def add_tag_to_file(filepath, tag):
    track = _get_track(filepath)
    if track and tag not in track.my_tags:
        track.my_tags.append(tag)
        track.save()
        return True
    return False

def remove_tag_from_file(filepath, tag):
    track = _get_track(filepath)
    if track and tag in track.my_tags:
        track.my_tags.remove(tag)
        track.save()
        return True
    return False

def set_tags_for_file(filepath, tags):
    track = _get_track(filepath)
    if track:
        track.my_tags = tags
        track.save()
        return True
    return False