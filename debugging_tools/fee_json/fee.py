import datetime
import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
mod_path = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2185445645"
vanilla_path = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
localisation_dir = mod_path + r"\localisation"
localisation_dir_vanilla = vanilla_path + r"\localisation"
event_modifiers_dir = mod_path + r"\common\event_modifiers"
event_modifiers_dir_vanilla = vanilla_path + r"\common\event_modifiers"

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\FEE.json"

tags = parent + "\\tags.txt"
data = parent + "\\database.txt"
provinces = parent + "\\provinces.json"

events_path = mod_path + r"\events"

event_json = "events.json"
event_modifiers_json = "eventModifiers.json"
event_localisation = "eventsLoc.txt"
events_input = glob.glob(events_path + r"\*.txt")
modifiers_input = glob.glob(event_modifiers_dir + r"\*.txt") + glob.glob(event_modifiers_dir_vanilla + r"\*.txt")
event_output_b4_json = "events.txt"

new_dict = {}
add_ruler_modifier = False
add_disaster_modifier = False
modifier_search = [
    "add_country_modifier",
    "add_disaster_modifier",
    "add_permanent_province_modifier",
    "add_province_modifier",
    "add_ruler_modifier",
]
extended_nested_search = modifier_search + [
    "country_event",
    "province_event",
]


def start():
    # merging_events(events_input)
    # create_localisation_file(event_localisation, localisation_dir, localisation_dir_vanilla)
    # merging_modifiers(modifiers_input)
    # json_parser(event_output_b4_json)

    # parse_correct_json()

    build(new_dict)


def parse_correct_json():
    # Read the new keys from the text file
    with open("eventsLoc.txt", "r", encoding="utf-8") as f:
        new_keys = {}
        for line in f:
            items = line.strip().split("\t")
            if len(items) == 2:
                old_key, new_key = items
            elif len(items) == 1:
                old_key, new_key = items[0], ""
            else:
                continue
            new_keys[old_key] = new_key

    #  Load the original dictionary from the JSON file
    with open(event_json, "r+", encoding="utf8") as events_in:
        original_dict = json.load(events_in)

    # Replace the old keys with the new keys
    for event_name, event_data in original_dict.items():
        # Check if the event name needs to be replaced
        if "disaster_" in event_name:
            event_name = event_name.split("disaster_")[1]
            if event_name in new_keys:
                event_name = f"Disaster: {new_keys[event_name]}"
        else:
            event_name = event_name.split("FEE_")[1].split("_Events")[0].replace("_", " ").title()

        new_dict[event_name] = {}
        for event_type in {"country_event", "province_event"}:
            if event_type in event_data:
                events = event_data[event_type]
                if isinstance(events, list):
                    for event in events:
                        new_dict[event_name].update(process_event(event, event["title"]))
                else:
                    new_dict[event_name].update(process_event(events, events["title"]))

    with open("FEE.json", "w", encoding="utf-8") as output:
        json.dump(new_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Succesfully created the correct Json")


def process_event(event_data, event_title):
    event_dict = {"desc": event_data.get("desc")}

    keys_to_check = [
        "is_triggered_only",
        "fire_only_once",
        "trigger",
        "mean_time_to_happen",
        "immediate",
    ]

    for key in keys_to_check:
        if key in event_data:
            event_dict[key] = event_data[key]
    if "option" in event_data:
        options = event_data["option"]
        if isinstance(options, list):
            for option in options:
                event_dict[option["name"]] = process_option(option)
        else:
            event_dict[options["name"]] = process_option(options)
    if "after" in event_data:
        event_dict["after"] = event_data["after"]

    return {event_title: event_dict}


def process_option(option):
    global add_ruler_modifier
    global add_disaster_modifier

    option_dict = {}
    if "name" in option:
        option_dict = {"name": option["name"]}
    for key, value in option.items():
        if key in {"name", "ai_chance"}:
            continue

        if key in modifier_search:
            if key == "add_disaster_modifier":
                add_disaster_modifier = True
            elif key == "add_ruler_modifier":
                add_ruler_modifier = True
            if isinstance(value, list):
                processed_modifiers = {modifier["name"]: dict(modifier) for modifier in value}
                processed_modifiers = process_modifiers(processed_modifiers)
                option_dict.update(processed_modifiers)
            else:
                processed_modifier = process_modifiers({value["name"]: dict(value)})
                option_dict.update(processed_modifier)
            add_ruler_modifier = False
            add_disaster_modifier = False
        elif isinstance(value, (list, dict)) and (isinstance(value, dict) and any(key_modifier in modifier_search for key_modifier in value.keys())):  # noqa
            processed_value = process_option(value)
            value = processed_value
            option_dict[key] = processed_value
        else:
            option_dict[key] = value

    return option_dict


def process_modifiers(modifier):
    global add_ruler_modifier
    global add_disaster_modifier
    result = {}

    for modifier_key, modifier_data in modifier.items():
        # Store the "duration" value if present
        duration_value = modifier_data.get("duration")

        if "name" in modifier_data:
            del modifier_data["name"]
        if "duration" in modifier_data:
            del modifier_data["duration"]

        with open(event_modifiers_json, "r", encoding="utf-8") as mod_file:
            mod_dict = json.load(mod_file)

        # Search for the dictionary with the key matching the modifier
        if modifier_key in mod_dict:
            modifier_data.update(mod_dict[modifier_key])

        # Reinsert the "duration" key with its original value
        if duration_value is not None:
            if duration_value == "-1":
                if add_ruler_modifier:
                    modifier_data["Expires"] = "On Ruler's Death"
                elif add_disaster_modifier:
                    modifier_data["Expires"] = "On Disaster's End"
                else:
                    modifier_data["Expires"] = "Never"
            else:
                modifier_data["Expires"] = f"{duration_value} days"

        result[modifier_key] = modifier_data

    return result


def build(new_dict):
    localized_names = {}
    localized_datas = {}
    localized_provinces = {}
    with open(event_localisation, "r", encoding="utf-8") as file:
        for line in file:
            if len(line.strip().split("\t")) == 2:
                key, localized_name = line.strip().split("\t")
                localized_names[key] = localized_name
    with open(data, "r", encoding="utf-8") as file:
        for line in file:
            if len(line.strip().split("\t")) == 2:
                key, localized_data = line.strip().split("\t")
                localized_datas[key] = localized_data
    with open(provinces, "r", encoding="utf-8") as file:
        localized_provinces = json.load(file)

    with open("FEE.json", "r", encoding="utf-8") as f:
        new_dict = json.load(f)
    mon_lib2 = {}

    mon_lib2 = recurse_process_dict(new_dict, localized_names, localized_datas, localized_provinces)

    with open("FEE_Test.json", "w", encoding="utf-8") as output:
        json.dump(mon_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    # with open(f"{os.path.dirname(finalpath)}\\FEE.json", "w", encoding="utf-8") as output:
    #     json.dump(mon_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False) #, sort_keys=True)

    print("Successfully localised the file!")


def recurse_process_dict(dictionary, loc_names, loc_datas, loc_provinces):
    global add_ruler_modifier
    global add_disaster_modifier
    check_province = False
    flag = False
    for key, value in list(dictionary.items()):
        key_localisation_check = [
            key == "primary_culture"
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
        key_provinces_check = [key in {"owns_core_province", "owns", "province_id"}]
        key_flag_check = [
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

        if key in {"ai_chance", "picture", "desc"} or (key == "name" and ".OPT" in value):
            del dictionary[key]
        else:
            check_province = key != "random_list"
            if isinstance(value, (dict, list)) and (".T" in key or ".OPT" in key or "Expires" in value):
                localized_name = loc_names.get(key)
                if localized_name is not None:
                    dictionary[localized_name] = value
                    del dictionary[key]
                    key = localized_name
            elif any(key_localisation_check):
                new_key = "Country" if key == "tag" else key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                if not isinstance(value, (list, dict)) and (key == "custom_tooltip"):
                    localized_name = loc_names.get(value)
                    if localized_name is not None:
                        dictionary[new_key] = localized_name
                elif isinstance(value, dict):
                    continue
                elif isinstance(value, list):
                    for i, values in enumerate(value):
                        localized_data = loc_datas.get(values)
                        localized_name = loc_names.get(values)
                        if localized_data is not None:
                            dictionary[new_key][i] = localized_data
                        elif localized_name is not None:
                            dictionary[new_key][i] = localized_name
                else:
                    localized_data = loc_datas.get(value)
                    localized_name = loc_names.get(value)
                    if localized_data is not None:
                        dictionary[new_key] = localized_data
                    if localized_name is not None:
                        dictionary[new_key] = localized_name
            elif len(key) == 3 and key != "NOT" and key.isupper() and key != "AND":
                localized_data = loc_datas.get(key)
                if localized_data is not None:
                    dictionary[localized_data] = dictionary.pop(key)
            elif any(key_provinces_check):
                new_key = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        localized_province = loc_provinces.get(values)
                        if localized_province is not None:
                            dictionary[new_key][i] = localized_province
                elif isinstance(value, str):
                    dictionary[new_key] = value.replace("_", " ").title()
                else:
                    localized_province = loc_provinces.get(value)
                    if localized_province is not None:
                        dictionary[new_key] = localized_province
            elif any(key_flag_check):
                new_key = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        new_value = values.replace("_", " ").title()
                        dictionary[new_key][i] = new_value
                else:
                    new_value = value.replace("_", " ").title()
                    dictionary[new_key] = new_value
            if isinstance(value, dict):
                if key == "change_religious_influence_equivalent_fee":
                    new_key = "Change Religious Influence"
                    dictionary[new_key] = dictionary.pop(key)
                else:
                    new_key = key.replace("_", " ").title()
                new_value = value
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                    dictionary[new_key] = new_value
                if isinstance(value, (list, dict)) and len(value) > 0:
                    recurse_process_dict(value, loc_names, loc_datas, loc_provinces)
            elif isinstance(value, list):
                new_key = key.replace("_", " ").title()
                new_value = value
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                    dictionary[new_key] = new_value
                for ite in value:
                    if isinstance(ite, (list, dict)) and len(ite) > 0:
                        recurse_process_dict(ite, loc_names, loc_datas, loc_provinces)
            elif not any(key_localisation_check) and not any(key_flag_check):
                new_key = key.replace("_", " ").title()
                new_value = value
                if isinstance(value, str):
                    if len(value) == 3 and value != "NOT" and value != "AND" and not value[1:].isdigit():
                        flag = True
                        localized_name = loc_datas.get(value)
                        dictionary[new_key] = dictionary.pop(key)
                        dictionary[new_key] = localized_name
                    elif key == "id":
                        new_value = f"{value}.T"
                        loc_names = loc_names.get(new_value)
                        if loc_names is not None:
                            new_value = loc_names
                    else:
                        new_value = value.strip('"')
                        new_value = int(value) if value.isdigit() or (value.startswith("-") and value[1:].isdigit()) else value.replace("_", " ").title()
                if key in dictionary and not flag:
                    dictionary[new_key] = dictionary.pop(key)
                    dictionary[new_key] = new_value
                flag = False

    return dictionary


def merging_events(events_input):
    print("Started the Merge of all files")
    with open("events.txt", "w", encoding="utf-8") as event_output:
        for event_file in events_input:
            if event_file[81:-4] == "_flavour_and_events_expanded_events" or event_file[81:-4].startswith("cato"):
                continue
            with open(event_file, "r", encoding="utf-8") as reading_event:
                event_output.write(event_file[81:-4])
                event_output.write("={\n")
                for line_event in reading_event:
                    if not line_event.strip().startswith("namespace") and not line_event.strip().startswith("#"):
                        if line_event.startswith("\t"):
                            line_event.replace("\t", "")
                        if ":" in line_event:
                            line_event = line_event.replace(":", "_")
                        line_event = re.sub(r" = | =|= ", "=", line_event)
                        line_event = re.sub(r" { | {|{ ", "{", line_event)
                        line_event = re.sub(r" } | }|} ", "}", line_event)
                        line_event = re.sub(r"kill_heir={}", "kill_heir=yes", line_event)
                        line_event = re.sub(r"(\t )|( \t)", "\t\t", line_event)
                        event_output.write(f"\t{line_event}")

                event_output.write("\n}\n")

    print("Merged all events into one file")


def merging_modifiers(modifiers_input):
    print("Started Merging Modifiers")
    modifiers_output = ""
    modifiers_to_update = []
    for modifiers_file in modifiers_input:
        with open(modifiers_file, "r", encoding="utf-8") as reading_modifiers:
            for line_modifiers in reading_modifiers:
                if line_modifiers.strip().startswith("#") or len(line_modifiers) < 2 and line_modifiers != "}" or line_modifiers.strip().startswith("picture"):
                    continue
                else:
                    modifiers_output += line_modifiers.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
        modifiers_output += "\n"

    with open("eventModifiers.txt", "w", encoding="utf-8") as file:
        file.write(modifiers_output)

    print("Merged all modifiers into one file")
    second_json_parser(modifiers_output)
    print("Jsonised the Modifiers")
    with open(event_modifiers_json, "r+", encoding="utf-8") as event_modif_file:
        event_mod_dict = json.load(event_modif_file)
        for key, value in event_mod_dict.items():
            if isinstance(value, dict):
                for modifier, number in value.items():
                    with open(data, "r+", encoding="utf_8") as data_mods:
                        for data_line in data_mods:
                            dat_a = data_line.split("\t")
                            if dat_a[0] == str(modifier):
                                new_value = dat_a[1].strip()
                                modifiers_to_update.append((key, modifier, new_value))
                                break

    # Update the event_mod_dict after iteration
    for key, modifier, new_value in modifiers_to_update:
        number = event_mod_dict[key][modifier]
        del event_mod_dict[key][modifier]
        event_mod_dict[key][new_value] = number

    with open(event_modifiers_json, "w", encoding="utf-8") as file:
        json.dump(event_mod_dict, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Localised the modifiers")


def create_localisation_file(event_localisation, localisation_dir, localisation_dir_vanilla):
    print("Started the creation of localisation")
    tolerance = 0.0125  # Adjust this tolerance value as needed
    array = []
    unique_array = []
    filenames = fee_filter(localisation_dir, "yml")
    filenames.extend(fee_filter(localisation_dir, "l_english.yml"))
    filenames.extend(fee_filter(localisation_dir_vanilla, "l_english.yml"))

    key = ""

    with open(event_output_b4_json, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if (
                line.startswith("title")
                or line.startswith("disaster_")
                or line.startswith("custom_tooltip")
                or line.startswith("trait")
                or line.startswith("has_country_modifier")
                or (line.startswith("name") and not line.startswith('name="'))
                or (line.startswith("tooltip") and "{" not in line)
                or (line.startswith("modifier=") and "{" not in line)
            ):
                if line.startswith("disaster_"):
                    key = line.split("=")[0].split("disaster_")[1].strip().replace('"', "")
                else:
                    key = line.split("=")[1].split("#")[0].strip().replace('"', "")

                array.append([key, ""])

    for item in array:
        if item not in unique_array:
            unique_array.append(item)

    length = len(unique_array)

    for index, item in enumerate(unique_array, start=1):
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
                            item[1] = line_value.lstrip().strip().strip('"').replace("0", "").replace("1", "").replace('"', "").replace(",", "")
                            break

    with open(event_localisation, "w", encoding="utf-8") as output:
        for key, value in unique_array:
            output.write(f"{key}\t{value}\n")

    print("Successfully populated the localisation file")


def fee_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(event_o_b4_json):
    """let's parse it all"""
    try:
        with open(event_o_b4_json, "r", encoding="utf8") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {event_o_b4_json}")
        return None

    file_name = basename(event_o_b4_json)

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t]", "", data)
    data = re.sub(r" \n", "\n", data)
    data = re.sub("}, },", "},},", data)

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
        r"(?<=:)(?!-?(?:0|[1-9]\trigger_d*)(?:\.\trigger_d+)?(?:[eE][+-]?\trigger_d+)?)(?!\".*\")[^{\n]+",  # noqa
        r'"\g<0>"',
        data,
    )  # Add quotes around string _values
    data = re.sub(r':"yes"', ":true", data)  # Replace yes with true
    data = re.sub(r':"no"', ":false", data)  # Replace no with false
    data = re.sub(r"([<>]=?)(.+)", r':{"_value":\g<2>,"operand":"\g<1>"}', data)  # Handle < > >= <=
    data = re.sub(r"(?<![:{])\n(?!}|$)", ",", data)  # Add commas
    # data = re.sub(r"\s", "", data)  # remove all white space
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
        print(f"Dumping intermediate code into file: {file_name}_{time.time():.0f}.intermediate")

        with open(f"./output/{file_name}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data)

        return None

    with open(f"{file_name[:-4]}.json", "w", encoding="utf8") as file:
        json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Successfully created the json file")


def second_json_parser(event_o_b4_json):
    """let's parse it all"""

    data = event_o_b4_json
    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces

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
        r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{},\n]+",
        r'"\g<0>"',
        data,
    )  # Add quotes around string _values
    data = re.sub(r':"yes"', ":true", data)  # Replace yes with true
    data = re.sub(r':"no"', ":false", data)  # Replace no with false
    data = re.sub(r"([<>]=?)(.+)", r':{"_value":\g<2>,"operand":"\g<1>"}', data)  # Handle < > >= <=
    data = re.sub(r"(?<![:{])\n(?!}|$)", ",", data)  # Add commas
    # data = re.sub(r"\s", "", data)  # remove all white space
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
        print("ERROR: Unable to parse eventModifiers")
        print(f"Dumping intermediate code into file: eventModifiers_{time.time():.0f}.intermediate")

        with open(f"./output/eventModifiers_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data)

        return None

    with open("eventModifiers" + ".json", "w", encoding="utf8") as file:
        json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
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
