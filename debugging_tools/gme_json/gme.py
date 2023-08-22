import glob
import json
import os
import re
import time
from os.path import basename

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\GME.json"
provinces = parent + "\\provinces.json"
mod_path = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2469419235"
# eu4DIR = r'C:\Program Files\Epic Games\EuropaUniversalis4' # This is for EGS -- Vielor
localisation_dir = mod_path + r"\localisation"
monuments_path = mod_path + r"\common\great_projects"

data = parent + "\\database.txt"
monument_localisation = "monumentsLoc.txt"
tags = parent + "\\tags.txt"

monument_json = "monuments.json"
monuments_input = glob.glob(monuments_path + "\*.txt")
monument_output_b4_json = "monuments.txt"


def start():
    """all definitions"""
    merging_monuments(monuments_input)
    json_parser(monument_output_b4_json)
    create_localisation_file(monument_json, monument_localisation, localisation_dir)

    build(monument_json, finalpath)


def recursive_dict(dictionary):
    for key, value in list(dictionary.items()):
        if key in (
            "time",
            "build_trigger",
            "tier_0",
            "upgrade_time",
            "cost_to_upgrade",
            "on_upgraded",
            "build_cost",
            "move_days_per_unit_distance",
            "can_use_modifiers_trigger",
        ):
            del dictionary[key]
        else:
            if isinstance(value, dict):
                recursive_dict(value)
            elif isinstance(value, list):
                for ite in value:
                    if isinstance(ite, dict):
                        recursive_dict(ite)
            if (
                key.startswith("tier_")
                or key.startswith("has_owner")
                or key.startswith("culture")
                or key.startswith("religion")
                or key.startswith("province_is")
                or key.startswith("can")
                or key.startswith("has")
                or key.startswith("government")
                or key.startswith("is")
                or key.startswith("owne")
                or key
                in (
                    "area_modifier",
                    "conditional_modifier",
                    "country_modifiers",
                    "dynasty",
                    "modifier",
                    "province_modifiers",
                    "primary_culture",
                    "region_modifier",
                    "starting_tier",
                    "trigger",
                )
            ):
                if key == "can_upgrade_trigger":
                    new_key = "Monument Trigger"
                else:
                    new_key = key.replace("_", " ").title()
                dictionary[new_key] = dictionary.pop(key)
                if new_key.startswith("Religion") or new_key.startswith("Culture") or new_key == "Primary Culture":
                    if isinstance(value, str):
                        with open(data, "r+", encoding="utf_8") as data_mods:
                            for data_line in data_mods:
                                dat_a = data_line.split("\t")
                                if dat_a[0] == str(value):
                                    value = dat_a[1].strip()
                                    dictionary[new_key] = value
                                    continue
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            with open(data, "r+", encoding="utf_8") as data_mods:
                                for data_line in data_mods:
                                    dat_a = data_line.split("\t")
                                    if dat_a[0] == str(item):
                                        new_value = dat_a[1].strip()
                                        dictionary[new_key][i] = new_value
                                        continue
                elif new_key.startswith("Owne"):
                    if isinstance(value, list):
                        for i, item in enumerate(value):
                            with open(tags, "r+", encoding="utf_8") as tag_mods:
                                for tag_line in tag_mods:
                                    dat_a = tag_line.split("\t")
                                    if dat_a[0] == str(item):
                                        new_value = dat_a[1].strip()
                                        dictionary[new_key][i] = new_value
                                        continue
                    else:
                        with open(tags, "r+", encoding="utf8") as tags_loc:
                            for tagline in tags_loc:
                                tag_a = tagline.split("\t")
                                if tag_a[0] == value:
                                    country_localised = tag_a[1].strip()
                                    value = country_localised
                                    break
            elif key in ("tag", "Owned By"):
                new_key = "Country" if key == "tag" else "Owned By"
                dictionary[new_key] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        with open(tags, "r+", encoding="utf_8") as tag_mods:
                            for tag_line in tag_mods:
                                dat_a = tag_line.split("\t")
                                if dat_a[0] == str(item):
                                    new_value = dat_a[1].strip()
                                    dictionary[new_key][i] = new_value
                                    continue
                else:
                    with open(tags, "r+", encoding="utf8") as tags_loc:
                        for tagline in tags_loc:
                            tag_a = tagline.split("\t")
                            if tag_a[0] == value:
                                country_localised = tag_a[1].strip()
                                value = country_localised
                                break
            elif key == "start":
                new_key = "Province"
                dictionary[new_key] = dictionary.pop(key)
                with open(provinces, "r+", encoding="utf_8") as provinces_in:
                    province_lib = json.load(provinces_in)
                    for province_id, province_name in province_lib.items():
                        province_id_string = str(value)
                        if province_id_string == province_id:
                            value = str(value)
                            value = province_name
                            break
                dictionary[new_key] = value
            elif key.startswith("gme_"):
                with open(monument_localisation, "r+", encoding="utf_8") as monument_loc:
                    for monument_line in monument_loc:
                        monument_name_a = monument_line.split("\t")
                        if monument_name_a[0] == key:
                            new_key = monument_name_a[1].strip()
                            dictionary[new_key] = dictionary.pop(key)
                            break
            elif isinstance(key, str) and isinstance(value, float) or isinstance(value, str):
                with open(data, "r+", encoding="utf_8") as data_mods:
                    for data_line in data_mods:
                        dat_a = data_line.split("\t")
                        if dat_a[0] == key:
                            new_key = dat_a[1].strip()
                            dictionary[new_key] = dictionary.pop(key)
                            continue
                continue
            else:
                if key in ("OR", "NOT", "AND", "NOT"):
                    if isinstance(value, dict):
                        recursive_dict(value)
                    else:
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                recursive_dict(item)
                                continue
                            with open(data, "r+", encoding="utf_8") as data_mods:
                                for data_line in data_mods:
                                    dat_a = data_line.split("\t")
                                    if dat_a[0] == str(item):
                                        new_value = dat_a[1].strip()
                                        dictionary[key][i] = new_value
                                        continue
                else:
                    if isinstance(key, str) and isinstance(value, dict) and key not in ("Owner", "FROM", "else", "if", "limit"):
                        new_key = key.replace("_", " ").title()
                        dictionary[new_key] = dictionary.pop(key)
                    continue
    return dictionary


def build(mon_json, finalpath):
    """Final build"""
    with open(mon_json, "r+", encoding="utf_8") as monuments_in:
        mon_lib = json.load(monuments_in)
        mon_lib2 = {}

        mon_lib2 = recursive_dict(mon_lib)

        with open(f"{os.path.dirname(finalpath)}\\GME.json", "w", encoding="utf-8") as output:
            json.dump(mon_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


def merging_monuments(monuments_input):
    """merge all Monuments into trigger_a single file"""
    with open("monuments.txt", "w", encoding="utf-8") as monument_output:
        for monument_file in monuments_input:
            with open(monument_file, "r", encoding="utf-8") as reading_mon:
                monument_output.write(monument_file[100:-4])
                monument_output.write(" = {\n")
                for line_mon in reading_mon:
                    monument_output.write("\t")
                    monument_output.write(line_mon)

                monument_output.write("\n}\n")
    print("Merged all monuments into one file")


def create_localisation_file(monument_json, monument_localisation, localisation_dir):
    """time to do the unification of the yml"""
    with open(monument_json, "r+", encoding="utf_8") as loc_out:
        loc_lib = json.load(loc_out)
        array = []

        filenames = gme_filter(localisation_dir, "yml")
        filenames.extend(gme_filter(localisation_dir, "english.yml"))

        for m_loc in loc_lib:
            for trigger_m in loc_lib[m_loc]:
                array.append([trigger_m, ""])
                for file in filenames:
                    with open(file, "r+", encoding="utf_8") as loc_out:
                        for line in loc_out:
                            line = line.strip()
                            if line.find(":") != -1:
                                line2 = line.split(":", 1)
                                if line2[0].casefold() == array[-1][0].casefold():
                                    array[-1][1] = line2[1].split('"', 1)[1][:-1]
                                    break
                    if array[-1][1] != "":
                        break
                # if array[-1][1] == '':
                #    print(array[-1])

    with open(monument_localisation, "w", encoding="utf_8") as output:
        for i in array:
            output.write(i[0] + "\t" + i[1])
            output.write("\n")

    print("Successfully populated the localisation file")


def gme_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(monument_o_b4_json):
    """let's parse it all"""
    try:
        file = open(monument_o_b4_json, "r", encoding="utf_8")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {monument_o_b4_json}")
        return None

    file_name = basename(monument_o_b4_json)

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"date=1.01.01", "", data)
    data = re.sub(r"time={months=120} ", "", data)
    data = re.sub(r"build_cost=1000", "", data)
    data = re.sub(r"type=monument", "", data)
    data = re.sub(r"can_be_moved=no", "", data)
    data = re.sub(r"on_built={}", "", data)
    data = re.sub(r"on_destroyed={}", "", data)
    data = re.sub(r"build_trigger={}", "", data)
    data = re.sub(r"keep_trigger={}", "", data)

    if definitions := re.findall(r"(@\w+)=(.+)", data):  # replace @variables with value
        for definition in definitions:
            data = re.sub(r"^@.+", "", data, flags=re.MULTILINE)
            data = re.sub(definition[0], definition[1], data)

    data = re.sub(r"\n{2,}", "\n", data)  # Remove excessive new lines
    data = re.sub(r"\n", "", data, count=1)  # Remove the first new line
    data = re.sub(r"{(?=\w)", "{\n", data)  # reformat one-liners
    data = re.sub(r"(?<=\w)}", "\n}", data)  # reformat one-liners
    data = re.sub(r"^[\w-]+(?=[\=\n><])", r'"\g<0>"', data, flags=re.MULTILINE)  # Add quotes around keys
    data = re.sub(r"([^><])=", r"\1:", data)  # Replace = with : but not >= or <=
    data = re.sub(
        r"(?<=:)(?!-?(?:0|[1-9]\trigger_d*)(?:\.\trigger_d+)?(?:[eE][+-]?\trigger_d+)?)(?!\".*\")[^{\n]+",
        r'"\g<0>"',
        data,
    )  # Add quotes around string _values
    data = re.sub(r':"yes"', ":true", data)  # Replace yes with true
    data = re.sub(r':"no"', ":false", data)  # Replace no with false
    data = re.sub(r"([<>]=?)(.+)", r':{"_value":\g<2>,"operand":"\g<1>"}', data)  # Handle < > >= <=
    data = re.sub(r"(?<![:{])\n(?!}|$)", ",", data)  # Add commas
    data = re.sub(r"\s", "", data)  # remove all white space
    data = re.sub(r'{(("[trigger_a-zA-Z_]+")+)}', r"[\g<1>]", data)  # make lists
    data = re.sub(r'""', r'","', data)  # Add commas to lists
    data = re.sub(r'{("\w+"(,"\w+")*)}', r"[\g<1>]", data)
    data = re.sub(
        r"((\"hsv\")({\trigger_d\.\trigger_d{1,3}(,\trigger_d\.\trigger_d{1,3}){2}})),",
        r"{\g<2>:\g<3>},",
        data,
    )  # fix hsv objects
    data = re.sub(r":{([^}{:]*)}", r":[\1]", data)  # if there's no : between list elements need to replace {} with []
    data = re.sub(r"\[(\w+)\]", r'"\g<1>"', data)
    data = re.sub(r"\",:{", '":{', data)  # Fix user_empire_designs
    data = "{" + data + "}"

    file_name = basename(monument_o_b4_json)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open(f"./output/{file_name}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data)

        return None

    with open(f"{file_name[:-4]}.json", "w", encoding="utf_8") as file:
        json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Successfully created the json file")


def _handle_duplicates(ordered_pairs):
    trigger_d = {}
    for k, v in ordered_pairs:
        if k in trigger_d:
            if isinstance(trigger_d[k], list):
                trigger_d[k].append(v)
            else:
                trigger_d[k] = [trigger_d[k], v]
        else:
            trigger_d[k] = v
    return trigger_d


start()
