import datetime
import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
if "\\" in os.getcwd():
    MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2185445645"
else:
    MOD_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2185445645"

LOC_DIR = MOD_PATH + r"\localisation"

path = os.path.abspath(os.path.join(os.getcwd()))  # debugging-tools
finalpath = os.path.join(os.path.dirname(path), "data", "Disaster.json")

data = os.path.join(path, "database.json")
provinces = os.path.join(path, "provinces.json")

DISASTER_PATH = os.path.join(MOD_PATH, "common", "disasters")

disasters_input = sorted(glob.glob(os.path.join(DISASTER_PATH, "*.txt")), key=lambda x: x.lower())
disaster_merged_txt = ""

dict_original = {}
dict_localisation = []
localized_names = {}


def start():
    """All shit"""
    merging_disasters(disasters_input)
    create_localisation_file(dict_localisation, LOC_DIR)
    json_parser(disaster_merged_txt)

    build()


def merging_disasters(disaster_in):
    """Merges all the disasters files in one file, divided by country"""
    global dict_localisation
    global disaster_merged_txt
    unique_list = []

    for disaster_file in disaster_in:
        with open(disaster_file, "r", encoding="utf-8") as reading_disaster_file:
            for line_disaster in reading_disaster_file:
                if line_disaster.strip().startswith("#") or len(line_disaster) < 2:
                    continue
                line_disaster = line_disaster.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
                if "." in line_disaster and "=" not in line_disaster and ":" not in line_disaster:
                    line_disaster = f'"{line_disaster.strip()}' + '"\n'
                disaster_merged_txt += line_disaster
                line_disaster = line_disaster.strip()
                if line_disaster.startswith("fee_") or line_disaster.startswith("name = ") or line_disaster.startswith("custom_tooltip = ") or line_disaster.startswith("tooltip = "):
                    if line_disaster.startswith("fee_"):
                        dict_localisation.append([line_disaster.split("=")[0].strip(), ""])
                    else:
                        dict_localisation.append([line_disaster.split("=")[1].strip(), ""])
        disaster_merged_txt += "\n}\n"

    for item in dict_localisation:
        if item[0].startswith(("modifier = ", "name =", "tooltip =", "custom_tooltip =")):
            item[0] = item[0].split("=")[1].strip()
        if item not in unique_list:
            unique_list.append(item)

    dict_localisation = unique_list

    print("Merged all events into one file")


def build():
    """Final Build"""
    localized_datas = {}
    localized_provinces = {}
    mon_lib2 = {}

    with open(data, "r", encoding="utf-8") as file:
        localized_datas = json.load(file)
    with open(provinces, "r", encoding="utf-8") as file:
        localized_provinces = json.load(file)

    mon_lib2 = recurse_process_dict(dict_original, localized_datas, localized_provinces)

    with open(f"{os.path.dirname(finalpath)}\\Disaster.json", "w", encoding="utf-8") as output:
        json.dump(mon_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Successfully localised the file!")


def recurse_process_dict(dictionary, loc_datas, loc_provinces):
    """Recursively iterates through the dictionary to parse and localise it"""
    flag = False
    for key, value in list(dictionary.items()):
        if key == "progress":
            del dictionary[key]
        else:
            check_key_localisation = [
                key == "primary_culture"
                or key == "advisor"
                or key == "accepted_culture"
                or key == "custom_tooltip"
                or key == "disaster"
                or key == "has_country_modifier"
                or key == "has_idea_group"
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
            check_key_provinces = [key in {"owns_core_province", "owns", "province_id"}]
            check_key_flag = [
                key
                in {
                    "flag",
                    "clr_country_flag",
                    "clr_global_flag",
                    "clr_heir_flag",
                    "clr_province_flag",
                    "clr_ruler_flag",
                    "has_country_flag",
                    "has_global_flag",
                    "has_heir_flag",
                    "has_province_flag",
                    "has_ruler_flag",
                    "set_country_flag",
                    "set_global_flag",
                    "set_heir_flag",
                    "set_province_flag",
                    "set_ruler_flag",
                }
            ]

            if isinstance(value, (dict, list)) and ("can_start" in value):
                localized_name = localized_names.get(key)
                if localized_name is not None:
                    dictionary[localized_name] = value
                    del dictionary[key]
                    key = localized_name
            elif key in ("custom_trigger_tooltip", "variable_arithmetic_trigger"):
                if isinstance(value, list):
                    if any("custom_tooltip" in item or "tooltip" in item for item in value):
                        new_value = []
                        for item in value:
                            if key == "custom_trigger_tooltip":
                                new_value.append(localized_names.get(item.get("tooltip")))
                            else:
                                new_value.append(localized_names.get(item.get("custom_tooltip")))
                        if key == "custom_trigger_tooltip":
                            dictionary["Custom Trigger"] = new_value
                        else:
                            dictionary["Variable Arithmetic Trigger"] = new_value
                elif any(key in value for key in ("custom_tooltip", "tooltip")):
                    if key == "custom_trigger_tooltip":
                        dictionary["Custom Trigger"] = localized_names.get(value["tooltip"])
                    else:
                        dictionary["Variable Arithmetic Trigger"] = localized_names.get(value["custom_tooltip"])
                del dictionary[key]
                continue
            elif any(check_key_localisation):
                key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if not isinstance(value, (list, dict)) and (key == "custom_tooltip"):
                    localized_name = localized_names.get(value)
                    if localized_name is not None:
                        dictionary[key_new] = localized_name
                elif isinstance(value, dict):
                    continue
                elif isinstance(value, list):
                    for i, values in enumerate(value):
                        localized_data = loc_datas.get(values)
                        localized_name = localized_names.get(values)
                        if localized_data is not None:
                            dictionary[key_new][i] = localized_data
                        elif localized_name is not None:
                            dictionary[key_new][i] = localized_name
                else:
                    localized_data = loc_datas.get(value)
                    localized_name = localized_names.get(value)
                    if localized_data is not None:
                        dictionary[key_new] = localized_data
                    if localized_name is not None:
                        dictionary[key_new] = localized_name
            elif len(key) == 3 and key.isupper() and key not in ("NOT", "AND"):
                localized_data = loc_datas.get(key)
                if localized_data is not None:
                    dictionary[localized_data] = dictionary.pop(key)
            elif any(check_key_provinces):
                key_new = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        localized_province = loc_provinces.get(values)
                        if localized_province is not None:
                            dictionary[key_new][i] = localized_province
                elif isinstance(value, str):
                    dictionary[key_new] = value.replace("_", " ").title()
                else:
                    localized_province = loc_provinces.get(value)
                    if localized_province is not None:
                        dictionary[key_new] = localized_province
            elif any(check_key_flag):
                key_new = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        value_new = values.replace("_", " ").title()
                        dictionary[key_new][i] = value_new
                else:
                    value_new = value.replace("_", " ").title()
                    dictionary[key_new] = value_new
            if isinstance(value, dict):
                key_new = key.replace("_", " ").title()
                value_new = value
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                if isinstance(value, (list, dict)) and len(value) > 0:
                    recurse_process_dict(value, loc_datas, loc_provinces)
            elif isinstance(value, list):
                key_new = key.replace("_", " ").title()
                value_new = []
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                for ite in value:
                    if isinstance(ite, str):
                        if ite.startswith("disaster_fee"):
                            localized_name = localized_names.get(f"{ite}.T")
                            value_new.append(localized_name)
                        else:
                            value_new.append(ite.replace("_", " ").title())
                    elif isinstance(ite, (list, dict)) and len(ite) > 0:
                        value_new = value
                        dictionary[key_new] = value_new
                        recurse_process_dict(ite, loc_datas, loc_provinces)
                if len(value_new) > 0 and isinstance(ite, str):
                    dictionary[key_new] = value_new
            elif not any(check_key_localisation) and not any(check_key_flag):
                key_new = key.replace("_", " ").title()
                value_new = value
                if isinstance(value, str):
                    if len(value) == 3 and value not in ("NOT", "AND", "all") and not value[1:].isdigit():
                        flag = True
                        localized_data = loc_datas.get(value)
                        dictionary[key_new] = dictionary.pop(key)
                        dictionary[key_new] = localized_data
                    elif key in ("on_start", "on_end") or value.startswith("disaster_fee"):
                        localized_name = localized_names.get(f"{value_new}.T")
                        if value_new == "disaster_fee_vijayaba_kollaya.2":
                            localized_name = "Ending Event"
                        if localized_name is not None:
                            value_new = localized_name
                    else:
                        value_new = value.strip('"')
                        value_new = int(value) if value.isdigit() or (value.startswith("-") and value[1:].isdigit()) else value.replace("_", " ").title()
                if key in dictionary and not flag:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                flag = False

    return dictionary


def create_localisation_file(dict_localisation, LOC_DIR):
    """Fill the eventsLoc.txt with the localised values of the needed strings"""
    print("Started the creation of localisation")
    tolerance = 0.0125  # Adjust this tolerance value as needed
    unique_array = []
    filenames = fee_filter(LOC_DIR, "l_english.yml")

    key = ""

    for line in disaster_merged_txt.split("\n"):
        line = line.strip()
        if (
            line.startswith("title")
            or line.startswith("disaster_")
            or ("fee_" in line and "had_" not in line)
            or line.startswith("custom_tooltip")
            or line.startswith("trait")
            or line.startswith("has_country_modifier")
            or (line.startswith("name") and not line.startswith('name="'))
            or (line.startswith("tooltip") and "{" not in line)
            or (line.startswith("modifier=") and "{" not in line)
        ):
            if line.startswith("disaster_"):
                key = line.split("=")[0].split("disaster_")[1].strip().replace('"', "")
            elif "=" not in line:
                key = line.strip().replace('"', "") + ".T"
            elif "disaster_fee" in line:
                key = line.split("=")[1].split("#")[0].strip().replace('"', "") + ".T"
            else:
                key = line.split("=")[1].split("#")[0].strip().replace('"', "")

            dict_localisation.append([key, ""])

    for item in dict_localisation:
        if item[0] == "{" or "has_country_flag" in item[0]:
            del item
            continue
        if item not in unique_array:
            unique_array.append(item)

    dict_localisation = unique_array
    length = len(dict_localisation)

    for index, item in enumerate(dict_localisation, start=1):
        percentage = (index / length) * 100
        if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {current_time} - Progress: {percentage:.1f}%")
        key_to_localise = item[0]

        for filename in filenames:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        line_key, line_value = line.split(":", 1)
                        if line_key.strip() == key_to_localise.strip():
                            if line_value.startswith(("1", "0")):
                                line_value = line[1:]
                            localized_names[key_to_localise] = line_value.lstrip().strip().strip('"').replace('"', "").replace(",", "")
                            break

    print("Successfully populated the localisation file")


def fee_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(disaster_file):
    """let's parse it all"""
    global dict_original

    if "\\" in disaster_file:
        try:
            with open(disaster_file, "r", encoding="utf_8") as file:
                data_json = file.read()
            file_name = basename(disaster_file)
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {disaster_file}")
            return None
    else:
        data_json = disaster_file
        file_name = "disaster.txt"

    data_json = re.sub(r"#.*", "", data_json)  # Remove comments
    data_json = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data_json,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data_json = re.sub(r"[\t ]", "", data_json)  # Remove tabs and spaces

    if definitions := re.findall(r"(@\w+)=(.+)", data_json):  # replace @variables with value
        for definition in definitions:
            data_json = re.sub(r"^@.+", "", data_json, flags=re.MULTILINE)
            data_json = re.sub(definition[0], definition[1], data_json)

    data_json = re.sub(r"\n{2,}", "\n", data_json)  # Remove excessive new lines
    data_json = re.sub(r"\n", "", data_json, count=1)  # Remove the first new line
    data_json = re.sub(r"{(?=\w)", "{\n", data_json)  # reformat one-liners
    data_json = re.sub(r"(?<=\w)}", "\n}", data_json)  # reformat one-liners
    data_json = re.sub(r"^[\w-]+(?=[\=\n><])", r'"\g<0>"', data_json, flags=re.MULTILINE)  # Add quotes around keys
    data_json = re.sub(r"([^><])=", r"\1:", data_json)  # Replace = with : but not >= or <=
    data_json = re.sub(
        r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{},\n]+",
        r'"\g<0>"',
        data_json,
    )  # Add quotes around string _values
    data_json = re.sub(r':"yes"', ":true", data_json)  # Replace yes with true
    data_json = re.sub(r':"no"', ":false", data_json)  # Replace no with false
    data_json = re.sub(r"([<>]=?)(.+)", r':{"_value":\g<2>,"operand":"\g<1>"}', data_json)  # Handle < > >= <=
    data_json = re.sub(r"(?<![:{])\n(?!}|$)", ",", data_json)  # Add commas
    # data_json = re.sub(r"\s", "", data_json)  # remove all white space
    data_json = re.sub(r'{(("[trigger_a-zA-Z_]+")+)}', r"[\g<1>]", data_json)  # make lists
    data_json = re.sub(r'""', r'","', data_json)  # Add commas to lists
    data_json = re.sub(r'{("\w+"(,"\w+")*)}', r"[\g<1>]", data_json)
    data_json = re.sub(
        r"((\"hsv\")({\trigger_d\.\trigger_d{1,3}(,\trigger_d\.\trigger_d{1,3}){2}})),",
        r"{\g<2>:\g<3>},",
        data_json,
    )  # fix hsv objects
    data_json = re.sub(r":{([^}{:]*)}", r":[\1]", data_json)  # if there's no : between list elements need to replace {} with []
    data_json = re.sub(r"\[(\w+)\]", r'"\g<1>"', data_json)
    data_json = re.sub(r"\",:{", '":{', data_json)  # Fix user_empire_designs
    data_json = "{" + data_json + "}"

    try:
        json_data = json.loads(data_json, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print(f"Dumping intermediate code into file: {file_name}_{time.time():.0f}.intermediate")

        with open(f"./output/{file_name}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data_json)

        return None

    dict_original = json_data

    # with open(f"{file_name[:-4]}.json", "w", encoding="utf8") as file:
    #     json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Successfully created the json file")


def _handle_duplicates(ordered_pairs):
    trigger_d = {}
    for key, val in ordered_pairs:
        if key in trigger_d:
            if isinstance(trigger_d[key], list):
                trigger_d[key].append(val)
            else:
                trigger_d[key] = [trigger_d[key], val]
        else:
            trigger_d[key] = val
    return trigger_d


start()
