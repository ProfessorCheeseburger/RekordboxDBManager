# dj_tagtool/gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import sys
import json
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from PIL import Image, ImageTk
import io

from dj_tagtool.backend.processing import run_conversion
from dj_tagtool.backend.config import load_config, save_config

class MusicTagsApp:
        
    def __init__(self, root):
        self.root = root
        self.root.title("MyTag Extractor and Converter")
        self.root.geometry("600x250")
        self.config_file = 'config.json'
        
        def resource_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', relative_path)
        
        icon_path = resource_path('assets/rekordbox.ico')
        self.root.iconbitmap(icon_path)
        
        self.load_config()
        self.create_widgets()
       
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', relative_path)
        
    def load_config(self):
        """Load the configuration from the JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "use_rekordbox_xml": False,
                "rekordbox_db_path": "/path/to/exported/rekordbox.xml",
                "music_directory": "/path/to/your/music/directory",
                "mytag_db_file": "MyTags.xml",
                "tag_delimiter": " / "
            }
            self.add_default_categories()

    def save_config(self):
        save_config(self.config, self.config_file)
    
    def add_default_categories(self):
        """Add the default categories if none exist."""
        default_categories = {
            "Genre": {
                "tags": ["House", "Trap", "Dubstep", "Disco", "Drum and Bass"],
                "rekordbox_field": "Genre",
                "mp3_metadata_field": "GENRE",
                "flac_metadata_field": "GENRE"
            },
            "Components": {
                "tags": ["Synth", "Piano", "Kick", "Hi Hat"],
                "rekordbox_field": "Composer",
                "mp3_metadata_field": "COMPOSER",
                "flac_metadata_field": "COMPOSER"
            },
            "Situation": {
                "tags": ["Warm Up", "Building", "Peak Time", "After Hours", "Lounge", "House Party"],
                "rekordbox_field": "Label",
                "mp3_metadata_field": "LABEL",
                "flac_metadata_field": "LABEL"
            },
            "Mood": {
                "tags": ["Happy", "Melancholy", "Emotional", "Hype", "Angry"],
                "rekordbox_field": "Comments",
                "mp3_metadata_field": "COMMENT",
                "flac_metadata_field": "COMMENT"
            }
        }
    
        self.config["categories"] = default_categories
        self.save_config()    
    
    def create_widgets(self):
        """Create the GUI widgets."""
        self.create_file_selectors()
        self.create_buttons()

    def create_file_selectors(self):
        """Create the file selectors for Rekordbox XML, music directory, and output XML."""
        
        # Rekordbox XML Path
        self.rekordbox_label = tk.Label(self.root, text="Rekordbox XML Path:")
        self.rekordbox_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.rekordbox_path = tk.Entry(self.root, width=50)
        self.rekordbox_path.insert(0, self.config.get("rekordbox_db_path", ""))
        self.rekordbox_path.grid(row=0, column=1, padx=10, pady=5)
        self.rekordbox_path.bind("<KeyRelease>", self.on_file_path_change)

        self.rekordbox_browse = tk.Button(self.root, text="Browse", command=self.browse_rekordbox)
        self.rekordbox_browse.grid(row=0, column=2, padx=10, pady=5)

        # Music Directory Path
        self.music_dir_label = tk.Label(self.root, text="Music Directory Path:")
        self.music_dir_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.music_dir_path = tk.Entry(self.root, width=50)
        self.music_dir_path.insert(0, self.config.get("music_directory", ""))
        self.music_dir_path.grid(row=1, column=1, padx=10, pady=5)
        self.music_dir_path.bind("<KeyRelease>", self.on_file_path_change)

        self.music_dir_browse = tk.Button(self.root, text="Browse", command=self.browse_music_dir)
        self.music_dir_browse.grid(row=1, column=2, padx=10, pady=5)

        # Output XML Path
        self.output_xml_label = tk.Label(self.root, text="MyTags Database XML Path:")
        self.output_xml_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.output_xml_path = tk.Entry(self.root, width=50)
        self.output_xml_path.insert(0, self.config.get("mytag_db_file", ""))
        self.output_xml_path.grid(row=2, column=1, padx=10, pady=5)
        self.output_xml_path.bind("<KeyRelease>", self.on_file_path_change)

        self.output_xml_browse = tk.Button(self.root, text="Browse", command=self.browse_output_xml)
        self.output_xml_browse.grid(row=2, column=2, padx=10, pady=5)
        
        # Tag Delimiter
        self.tag_delimiter_label = tk.Label(self.root, text="Tag Delimiter:")
        self.tag_delimiter_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.tag_delimiter = tk.Entry(self.root, width=5)
        self.tag_delimiter.insert(0, self.config.get("tag_delimiter", ""))
        self.tag_delimiter.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        self.tag_delimiter.bind("<KeyRelease>", self.on_file_path_change)

        # Use Rekordbox XML Checkbox
        self.use_rekordbox_var = tk.BooleanVar(value=self.config.get("use_rekordbox_xml", False))
        self.use_rekordbox_checkbox = tk.Checkbutton(self.root, text="Use Rekordbox XML", variable=self.use_rekordbox_var, command=self.on_use_rekordbox_change)
        self.use_rekordbox_checkbox.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    def on_file_path_change(self, event):
        """Update the corresponding value in config when a file path is modified."""
        self.config["rekordbox_db_path"] = self.rekordbox_path.get()
        self.config["music_directory"] = self.music_dir_path.get()
        self.config["mytag_db_file"] = self.output_xml_path.get()
        self.config["tag_delimiter"] = self.tag_delimiter.get()
        self.save_config()

    def on_use_rekordbox_change(self):
        """Update the 'use_rekordbox_xml' value in the config when the checkbox is toggled."""
        self.config["use_rekordbox_xml"] = self.use_rekordbox_var.get()
        self.save_config()

    def create_buttons(self):
        """Create the 'MyTags' and 'Run Script' buttons side by side."""
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        # MyTags Button
        self.mytags_button = tk.Button(button_frame, text="MyTags", command=self.open_mytags_window)
        self.mytags_button.grid(row=0, column=0, padx=10, pady=5)

        # Run Script Button
        self.run_button = tk.Button(button_frame, text="Run Script", command=self.run_script)
        self.run_button.grid(row=0, column=1, padx=10, pady=5)
        
        # Tagger Button
        self.tagger_button = tk.Button(button_frame, text="Tagger", command=self.open_tagger_window)
        self.tagger_button.grid(row=0, column=2, padx=10, pady=5)
        
    def browse_rekordbox(self):
        """Browse for the Rekordbox XML file."""
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.rekordbox_path.delete(0, tk.END)
            self.rekordbox_path.insert(0, file_path)
            self.on_file_path_change(None)  # Trigger config update

    def browse_music_dir(self):
        """Browse for the music directory."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.music_dir_path.delete(0, tk.END)
            self.music_dir_path.insert(0, dir_path)
            self.on_file_path_change(None)  # Trigger config update

    def browse_output_xml(self):
        """Browse for the output XML file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if file_path:
            self.output_xml_path.delete(0, tk.END)
            self.output_xml_path.insert(0, file_path)
            self.on_file_path_change(None)  # Trigger config update
            
    def open_tagger_window(self):
        tagger = tk.Toplevel(self.root)
        tagger.title("Tagger")
        tagger.geometry("1000x600")

        paned_window = tk.PanedWindow(tagger, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Left Pane: File Browser ---
        left_frame = tk.Frame(paned_window, width=250)
        paned_window.add(left_frame)

        file_tree = ttk.Treeview(left_frame)
        file_tree.pack(fill=tk.BOTH, expand=True)

        yscrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=file_tree.yview)
        file_tree.configure(yscrollcommand=yscrollbar.set)
        yscrollbar.pack(side="right", fill="y")

        def populate_tree(path, parent=""):
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                node = file_tree.insert(parent, "end", text=item, open=False)
                if os.path.isdir(abs_path):
                    populate_tree(abs_path, node)

        music_dir = self.config.get("music_directory", os.getcwd())
        populate_tree(music_dir)

        # --- Middle Pane: Metadata Viewer ---
        middle_frame = tk.Frame(paned_window, width=350)
        paned_window.add(middle_frame)

        album_art_label = tk.Label(middle_frame, text="No Image")
        album_art_label.pack(pady=10)

        metadata_entries = {}

        def show_metadata(file_path):
            for widget in middle_frame.winfo_children():
                if widget != album_art_label:
                    widget.destroy()

            metadata_entries.clear()

            # Load metadata
            if file_path.endswith(".mp3"):
                audio = EasyID3(file_path)
            elif file_path.endswith(".flac"):
                audio = FLAC(file_path)
            else:
                return

            # Album Art
            if file_path.endswith(".mp3"):
                from mutagen.id3 import ID3
                id3 = ID3(file_path)
                apics = id3.getall("APIC")
                if apics:
                    art = apics[0].data
                    img = Image.open(io.BytesIO(art)).resize((150, 150))
                    img = ImageTk.PhotoImage(img)
                    album_art_label.config(image=img)
                    album_art_label.image = img
                else:
                    album_art_label.config(image="", text="No Album Art")
            else:
                album_art_label.config(image="", text="No Album Art")

            for i, (k, v) in enumerate(audio.items()):
                label = tk.Label(middle_frame, text=k)
                label.pack(anchor="w")
                entry = tk.Entry(middle_frame, width=40)
                entry.insert(0, ", ".join(v))
                entry.pack(anchor="w")
                metadata_entries[k] = entry

            def save_metadata():
                for key, entry in metadata_entries.items():
                    try:
                        audio[key] = entry.get()
                    except Exception:
                        continue
                audio.save()
                messagebox.showinfo("Saved", "Metadata updated.")

            tk.Button(middle_frame, text="Save Metadata", command=save_metadata).pack(pady=10)

        # --- Right Pane: Tags ---
        right_frame = tk.Frame(paned_window, width=400)
        paned_window.add(right_frame)

        category_checkboxes = {}

        def show_tags(file_path):
            if not file_path.lower().endswith((".mp3", ".flac")):
                return

            if file_path.endswith(".mp3"):
                audio = EasyID3(file_path)
                is_mp3 = True
            elif file_path.endswith(".flac"):
                audio = FLAC(file_path)
                is_mp3 = False
            else:
                return

            for widget in right_frame.winfo_children():
                widget.destroy()

            def update_tags():
                for cat, data in category_checkboxes.items():
                    field = self.config["categories"][cat][
                        "mp3_metadata_field" if is_mp3 else "flac_metadata_field"
                    ]
                    checked_tags = [tag for tag, var in data.items() if var.get()]
                    if checked_tags:
                        audio[field] = self.config["tag_delimiter"].join(checked_tags)
                    elif field in audio:
                        del audio[field]
                audio.save()
                messagebox.showinfo("Updated", "Tags updated.")

            for category, data in self.config.get("categories", {}).items():
                category_label = ttk.Label(right_frame, text=category, font=("Helvetica", 12, "bold"))
                category_label.pack(anchor="w", pady=(10, 0))

                # Get the metadata field name from the config
                metadata_field = None
                if isinstance(audio, EasyID3):
                    metadata_field = data.get("mp3_metadata_field", "").lower()
                else:
                    metadata_field = data.get("flac_metadata_field", "").lower()

                # Get current tags from the audio file (if present)
                current_tags = []
                if metadata_field:
                    raw_value = audio.get(metadata_field, [""])[0] if metadata_field in audio else ""
                    current_tags = [tag.strip() for tag in raw_value.split(self.config.get("tag_delimiter", " / "))]

                for tag in data.get("tags", []):
                    var = tk.BooleanVar(value=tag in current_tags)

                    cb = ttk.Checkbutton(right_frame, text=tag, variable=var)
                    cb.var = var  # Store variable for later access if needed
                    cb.pack(anchor="w", padx=10)

                    # Add callback to update tag in metadata when toggled
                    def on_check(tag=tag, category=category, var=var):
                        # Re-fetch field
                        field = data.get("mp3_metadata_field" if isinstance(audio, EasyID3) else "flac_metadata_field", "").lower()
                        current = audio.get(field, [""])[0] if field in audio else ""
                        tags = [t.strip() for t in current.split(self.config.get("tag_delimiter", " / ")) if t.strip()]
                        if var.get() and tag not in tags:
                            tags.append(tag)
                        elif not var.get() and tag in tags:
                            tags.remove(tag)
                        audio[field] = self.config.get("tag_delimiter", " / ").join(tags)
                        audio.save()

                    cb.config(command=on_check)

            tk.Button(right_frame, text="Save Tags", command=update_tags).pack(pady=10)

        # --- Tree File Select Event ---
        def on_select(event):
            item = file_tree.selection()
            if not item:
                return
            path = music_dir
            for node in file_tree.selection():
                path_parts = []
                while node:
                    path_parts.insert(0, file_tree.item(node, "text"))
                    node = file_tree.parent(node)
                path = os.path.join(music_dir, *path_parts)

            if os.path.isfile(path) and path.lower().endswith((".mp3", ".flac")):
                show_metadata(path)
                show_tags(path)

        file_tree.bind("<<TreeviewSelect>>", on_select)

    def open_mytags_window(self):
        """Open the MyTags window to modify categories."""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("MyTags")
        prefs_window.geometry("600x400")

        notebook = ttk.Notebook(prefs_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Add default categories if none exist
        if not self.config["categories"]:
            self.add_default_categories()

        # Create tabs for each category
        for category in list(self.config["categories"].keys()):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=category)

            self.create_category_tab(tab, category)

        prefs_window.mainloop()

    def create_category_tab(self, parent, category):
        # Create the input fields for a specific category.
        category_info = self.config["categories"].get(category, {})

        # Category Name
        tk.Label(parent, text="Category:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        category_name_entry = tk.Entry(parent, width=30)
        category_name_entry.insert(0, category)
        category_name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Tags
        tk.Label(parent, text="Tags (comma separated):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tags_entry = tk.Entry(parent, width=30)
        tags_entry.insert(0, ", ".join(category_info.get("tags", [])))
        tags_entry.grid(row=1, column=1, padx=10, pady=5)

        # Rekordbox Field
        rekordbox_field_options = ["Name", "Artist", "Composer", "Album", "Grouping", "Genre", "Comments", "Remixer", "Label", "Mix", "Lyricist"]
        tk.Label(parent, text="Rekordbox Field:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        rekordbox_field_combobox = ttk.Combobox(parent, values=rekordbox_field_options, width=30)
        rekordbox_field_combobox.set(category_info.get("rekordbox_field", ""))
        rekordbox_field_combobox.grid(row=2, column=1, padx=10, pady=5)

        # MP3 Metadata Field
        mp3_metadata_field_options = [
            "album", "bpm", "comments", "compilation", "composer", "copyright", "encodedby", "lyricist",
            "length", "media", "mood", "grouping", "title", "version", "artist", "publisher", "albumartist",
            "conductor", "arranger", "discnumber", "organization", "tracknumber", "author", "albumartistsort",
            "albumsort", "composersort", "artistsort", "titlesort", "isrc", "discsubtitle", "language",
            "genre", "date", "originaldate", "performer", "website", "releasecountry", "asin", "barcode",
            "catalognumber", "custom"  # <-- added 'custom' option
        ]

        tk.Label(parent, text="MP3 Metadata Field:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        mp3_metadata_field_combobox = ttk.Combobox(parent, values=mp3_metadata_field_options, width=30)
        mp3_metadata_field_combobox.set(category_info.get("mp3_metadata_field", ""))
        mp3_metadata_field_combobox.grid(row=3, column=1, padx=10, pady=5)

        # MP3 Custom Entry (initially hidden)
        mp3_custom_entry = tk.Entry(parent, width=30)
        mp3_custom_entry.grid(row=4, column=1, padx=10, pady=5)
        mp3_custom_entry.grid_remove()

        # FLAC Metadata Field
        flac_metadata_field_options = [
            "Artist", "Album", "Album Artist", "Genre", "Composer", "Label", "Comment", "Band", "Mix Artist",
            "Lyricist", "Author", "Conductor", "Copyright", "License", "custom"  # <-- added 'custom'
        ]
        tk.Label(parent, text="FLAC Metadata Field:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        flac_metadata_field_combobox = ttk.Combobox(parent, values=flac_metadata_field_options, width=30)
        flac_metadata_field_combobox.set(category_info.get("flac_metadata_field", ""))
        flac_metadata_field_combobox.grid(row=5, column=1, padx=10, pady=5)

        # FLAC Custom Entry (initially hidden)
        flac_custom_entry = tk.Entry(parent, width=30)
        flac_custom_entry.grid(row=6, column=1, padx=10, pady=5)
        flac_custom_entry.grid_remove()

        # Dropdown handlers
        def on_mp3_field_change(event=None):
            if mp3_metadata_field_combobox.get() == "custom":
                mp3_custom_entry.grid()
                mp3_custom_entry.insert(0, category_info.get("mp3_metadata_field", ""))
            else:
                mp3_custom_entry.grid_remove()

        def on_flac_field_change(event=None):
            if flac_metadata_field_combobox.get() == "custom":
                flac_custom_entry.grid()
                flac_custom_entry.insert(0, category_info.get("flac_metadata_field", ""))
            else:
                flac_custom_entry.grid_remove()

        mp3_metadata_field_combobox.bind("<<ComboboxSelected>>", on_mp3_field_change)
        flac_metadata_field_combobox.bind("<<ComboboxSelected>>", on_flac_field_change)

        # Initial trigger
        on_mp3_field_change()
        on_flac_field_change()

        # Save Button
        def save_category():
            mp3_field = mp3_metadata_field_combobox.get()
            flac_field = flac_metadata_field_combobox.get()

            if mp3_field == "custom":
                mp3_field = mp3_custom_entry.get().strip()

            if flac_field == "custom":
                flac_field = flac_custom_entry.get().strip()

            self.config["categories"][category_name_entry.get()] = {
                "tags": [tag.strip() for tag in tags_entry.get().split(",")],
                "rekordbox_field": rekordbox_field_combobox.get(),
                "mp3_metadata_field": mp3_field,
                "flac_metadata_field": flac_field
            }
            self.save_config()

            notebook.tab(notebook.index(parent), text=category_name_entry.get())

        save_button = tk.Button(parent, text="Save", command=save_category)
        save_button.grid(row=7, column=0, columnspan=2, pady=10)

    def run_script(self):
        self.update_config()
        def thread_func():
            try:
                self.root.title("Running... Please Wait")
                result = run_conversion(self.config)
                self.root.title("MyTag Extractor and Converter")
                self.show_popup(result)
            except Exception as e:
                self.show_popup(f"Error: {str(e)}")
        threading.Thread(target=thread_func).start()

    def show_popup(self, message):
        self.root.after(0, lambda: messagebox.showinfo("Script Output", message))
