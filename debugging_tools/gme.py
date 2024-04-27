import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
if "\\" in os.getcwd():
    MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2469419235"
else:
    MOD_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2469419235"

LOC_DIR = os.path.join(MOD_PATH, "localisation")
MON_DIR = os.path.join(MOD_PATH, "common", "great_projects")

path = os.path.abspath(os.path.join(os.getcwd()))  # debugging-tools
finalpath = os.path.join(os.path.dirname(path), "data", "GME.json")

data = os.path.join(path, "database.json")
provinces = os.path.join(path, "provinces.json")

MON_INPUT = sorted(glob.glob(os.path.join(MON_DIR, "*.txt")), key=lambda x: x.lower())

dict_original = {}
dict_localisation = {}


def start():
    """calls"""
    merging_monuments(MON_INPUT)
    create_localisation_file(LOC_DIR)

    build(dict_original)


def merging_monuments(MON_INPUT):
    """merge all Monuments into trigger_a single file"""
    monument_merged_tx = ""

    for monument_file in MON_INPUT:
        with open(monument_file, "r", encoding="utf-8") as reading_mon:
            monument_merged_tx += monument_file[100:-4]
            monument_merged_tx += " = {\n"
            for line_mon in reading_mon:
                if line_mon.startswith("#"):
                    continue
                monument_merged_tx += "\t"
                monument_merged_tx += line_mon

            monument_merged_tx += "\n}\n"

    print("Merged all monuments into one file")

    json_parser(monument_merged_tx)


def create_localisation_file(directory_localisation):
    """time to do the unification of the yml"""
    print("Started the creation of localisation")
    filenames = gme_filter(directory_localisation, "yml")

    for key in dict_original:
        for key_sub in dict_original[key]:
            dict_localisation[key_sub] = ""

            for filename in filenames:
                if len(dict_localisation[key_sub]) > 1:
                    break
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        if ":" in line:
                            line_key_sub, line_value = line.split(":", 1)
                            if line_value.startswith(("0", "1")):
                                line_value = line[1:]
                            if line_key_sub.strip() == key_sub:
                                dict_localisation[key_sub] = line_value.strip().replace('"', "").replace(",", "").title()
                                break

    dict_localisation["GME_OWNS_ALL_PROVINCES_IN_COROMANDEL_TT"] = "Owns all Provinces in the Coromandel Trade Node"
    dict_localisation["GME_BAHMANI_TOMBS_TT"] = "Either is or was Ahmednagar, Bahamnis, Berar, Bijapur, Golkonda or has their dynasties."

    print("Successfully populated the localisation file")


def build(dictionary):
    """Final build"""
    localized_datas = {}
    dict_final = {}
    localized_provinces = {}

    with open(data, "r", encoding="utf-8") as file:
        localized_datas = json.load(file)
    with open(provinces, "r", encoding="utf-8") as file:
        localized_provinces = json.load(file)

    dict_final = recursive_dict(dictionary, dict_localisation, localized_datas, localized_provinces)

    with open(f"{os.path.dirname(finalpath)}\\GME.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Successfully created the final file")


def recursive_dict(dictionary, loc_names, loc_datas, loc_provinces):

    for key, value in list(dictionary.items()):
        if key in (
            "time",
            "can_use_modifiers_trigger",
            "build_trigger",
            "tier_0",
            "upgrade_time",
            "cost_to_upgrade",
            "on_upgraded",
        ):
            del dictionary[key]
        else:
            key_localisation_check = [
                key == "primary_culture"
                or key.startswith("tier_")
                or key == "add_building"
                or key == "add_ruler_personality"
                or key == "advisor"
                or key == "accepted_culture"
                or key == "change_culture"
                or key == "change_trade_goods"
                or key == "custom_tooltip"
                or key == "disaster"
                or key == "has_building"
                or key == "has_country_modifier"
                or key == "has_idea_group"
                or key == "remove_building"
                or key == "remove_country_modifier"
                or key == "ruler_has_personality"
                or key == "tag"
                or key == "trade_goods"
                or key == "trait"
                or key == "was_tag"
                or key.startswith("area")
                or key.startswith("continent")
                or key.startswith("culture")
                or key.startswith("owned_by")
                or key.startswith("region")
                or key.startswith("religion")
                or key.startswith("superregion")
            ]

            if isinstance(value, dict):
                if key.replace("_", " ").title().startswith(("Province Is Or Accepts Religion", "Province Is Owner Culture")):
                    key_new = key.replace("_", " ").title()
                    if key.endswith("religion_group"):
                        value_new = loc_datas.get(dictionary[key]["religion_group"])
                    elif key.endswith("religion"):
                        value_new = loc_datas.get(dictionary[key]["religion"])
                    else:
                        value_new = loc_datas.get(dictionary[key]["culture_group"])
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                    continue
                elif key.replace("_", " ").title() == "Custom Trigger Tooltip":
                    key_new = loc_names.get(dictionary[key]["tooltip"])
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = "True"
                    continue

                if key == "can_upgrade_trigger":
                    key_new = "Monument Trigger"
                elif key.startswith("gme_"):
                    key_new = loc_names.get(key)
                else:
                    key_new = key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value

                key = key_new
                recursive_dict(value, loc_names, loc_datas, loc_provinces)
            elif isinstance(value, list):
                if any(key_localisation_check) and key not in ("area_modifier", "region_modifier"):
                    if key in ["tag", "owned_by", "primary_culture"] or key.startswith(("culture", "religion")):
                        key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                        if key in dictionary:
                            dictionary[key_new] = dictionary.pop(key)
                        for i, values in enumerate(value):
                            localized_data = loc_datas.get(values)
                            localized_name = loc_names.get(values)
                            dictionary[key_new][i] = localized_data if localized_data is not None else localized_name
                else:
                    key_new = "Monument Trigger" if key == "can_upgrade_trigger" else key.replace("_", " ").title()
                    dictionary[key_new] = dictionary.pop(key)
                    key = key_new
                    if len(value) != 0 and isinstance(value, dict):
                        recursive_dict(value, loc_names, loc_datas, loc_provinces)
                    elif isinstance(value, list):
                        for values in value:
                            if isinstance(values, dict):
                                recursive_dict(values, loc_names, loc_datas, loc_provinces)
            elif isinstance(key, str):
                if key == "start":
                    key_new = "Province"
                elif isinstance(value, bool) or key == "starting_tier" or any(key_localisation_check):
                    key_new = key.replace("_", " ").title()
                else:
                    key_new = loc_datas.get(key)
                value_new = loc_provinces.get(value) if key == "start" else loc_datas.get(value)
                if key_new is None:
                    key_new = key
                if value_new is None:
                    value_new = value
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value_new
                key = key_new
                value = value_new

    return dictionary


def gme_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(mon_file):
    """let's parse it all"""
    global dict_original

    if "\\" in mon_file:
        try:
            with open(mon_file, "r", encoding="utf8") as file:
                data = file.read()
            file_name = basename(mon_file)
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {mon_file}")
            return None
    else:
        data = mon_file
        file_name = "monFile.txt"

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
    data = re.sub(r"build_cost=0", "", data)
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

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open(f"./output/{file_name}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data)

        return None

    dict_original = json_data

    # with open(f"{file_name[:-4]}.json", "w", encoding="utf8") as file:
    #     json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Created the initial json file")


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
