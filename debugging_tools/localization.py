import glob
import os
import re
from os.path import basename


def start():
    """Create the localisation folders and files for various mods and languages"""
    mod_path = r"C:\Users\AlexI\OneDrive\Documenti\Paradox Interactive\Europa Universalis IV\mod"

    mod_paths = [
        os.path.join(mod_path, "Ages-and-Splendor-Expaded"),
        os.path.join(mod_path, "FlavourEventsExpanded"),
        os.path.join(mod_path, "Historical-Ideas-Expanded"),
        os.path.join(mod_path, "Governments Expanded"),
        os.path.join(mod_path, "Monuments-Expanded"),
        # Add more mod paths as needed
    ]

    languages = {
        "l_english": "english",
        "l_french": "french",
        "l_german": "german",
        "l_spanish": "spanish",
    }

    for mod_path in mod_paths:
        print(f"Processing {os.path.basename(mod_path)}")
        process_mod(mod_path, languages)


def process_mod(mod_path, languages):
    """Process a single mod and create localized files for specified languages"""
    localisation_dir = os.path.join(mod_path, "localisation")
    filenames = glob.glob(os.path.join(localisation_dir, "*_l_english.yml"))

    for lang_folder in languages.values():
        folder_path = os.path.join(localisation_dir, lang_folder)
        if not os.path.exists(folder_path) and lang_folder != "english":
            os.makedirs(folder_path)

    lang_list = list(languages)  # Convert dictionary keys to a list
    for file in filenames:
        with open(file, "r", encoding="utf8") as f:
            data = f.read()
            data = data.replace("\ufeff", "")
            for current_lang, next_lang in zip(lang_list, lang_list[1:] + [lang_list[0]]):
                data = re.sub(f"{current_lang}:", f"{next_lang}:", data)
                final_folder = os.path.join(localisation_dir, languages[next_lang])
                output_file = os.path.join(final_folder, f"{basename(file).split('l_english.yml')[0]}{next_lang}.yml")
                if next_lang != "l_english":
                    with open(output_file, "w", encoding="utf-8-sig", newline="\n") as out_file:
                        out_file.write(data)
                else:
                    break


# Run the script
start()
