import glob
import os
import re
from os.path import basename


def start():
    """Create the localisation folders and files for french/german/spanish"""
    mod_path = r"C:\Users\AlexI\OneDrive\Documenti\Paradox Interactive\Europa Universalis IV\mod"
    # mod = mod_path + r"\Ages-and-Splendor-Expaded"
    # mod = mod_path + r"\FlavourEventsExpanded"
    mod = mod_path + r"\Historical-Ideas-Expanded"
    # mod = mod_path + r"\Monuments-Expanded"
    mod = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1770950522"
    localisation_dir = mod + r"\localisation"
    filenames = glob.glob(localisation_dir + r"\*_l_english.yml")
    output_string = ["l_english", "l_french", "l_german", "l_spanish"]
    language_folders = {
        "l_english": "english",
        "l_french": "french",
        "l_german": "german",
        "l_spanish": "spanish"
    }

    # Create language folders if they don't exist
    for lang_folder in language_folders.values():
        folder_path = os.path.join(localisation_dir, lang_folder)
        if not os.path.exists(folder_path) and lang_folder != "english":
            os.makedirs(folder_path)

    for file in filenames:
        with open(file, "r", encoding="utf8") as f:
            data = f.read()
            data = data.replace('\ufeff', '')
            for current_lang, next_lang in zip(output_string, output_string[1:] + [output_string[0]]):  # noqa
                data = re.sub(current_lang + r":", next_lang + ":", data)
                final_folder = localisation_dir + rf"\{language_folders[next_lang]}"
                output_file = final_folder + \
                    fr"\{basename(file).split('l_english.yml')[0]}{next_lang}.yml"
                if next_lang != "l_english":
                    with open(output_file, "w", encoding="utf-8-sig", newline="\n") as out_file:
                        out_file.write(data)
                else:
                    break


start()
