import datetime
import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2185445645"
VANILLA_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
LOC_DIR = MOD_PATH + r"\localisation"
LOC_DIR_VAN = VANILLA_PATH + r"\localisation"
EVENT_MOD_DIR = MOD_PATH + r"\common\event_modifiers"
EVENT_MOD_DIR_VAN = VANILLA_PATH + r"\common\event_modifiers"
# EVENT_MOD_DIR = MOD_PATH + r"\common\opinion_modifiers"
# EVENT_MOD_DIR_VAN = VANILLA_PATH + r"\common\opinion_modifiers"

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\FEE.json"

tags = parent + "\\tags.txt"
data = parent + "\\database.json"
provinces = parent + "\\provinces.json"

EVENTS_PATH = MOD_PATH + r"\events"

events_input = glob.glob(EVENTS_PATH + r"\*.txt")
modifiers_input = glob.glob(EVENT_MOD_DIR + r"\*.txt") + glob.glob(EVENT_MOD_DIR_VAN + r"\*.txt")

original_dict = {}
new_dict = {}
dict_modifiers = {}
dict_localisation = {}

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

localized_datas = {}
localized_provinces = {}

with open(data, "r", encoding="utf-8") as file:
    localized_datas = json.load(file)
with open(provinces, "r", encoding="utf-8") as file:
    localized_provinces = json.load(file)


def start():
    """All shit"""
    merging_events(events_input)
    merging_modifiers(modifiers_input)
    create_localisation_file(LOC_DIR)
    parse_correct_json()

    build(new_dict)


def build(final_dict):
    """Final Build"""
    mon_lib2 = {}

    mon_lib2 = recurse_process_dict(final_dict, dict_localisation, localized_datas, localized_provinces)

    with open(f"{os.path.dirname(finalpath)}\\FEE.json", "w", encoding="utf-8") as output:
        json.dump(mon_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Successfully localised the file!")


def merging_events(events_input):
    """Merges all the events files in one file, divided by country"""
    events_merged_txt = ""
    global dict_localisation
    global original_dict

    for event_file in events_input:
        if event_file[81:-4] == "_flavour_and_events_expanded_events" or event_file[81:-4].startswith("cato"):
            continue
        with open(event_file, "r", encoding="utf-8") as reading_event:
            events_merged_txt += event_file[81:-4]
            events_merged_txt += "={\n"
            for line_event in reading_event:
                if not line_event.strip().startswith(("#", "namespace=")):
                    if line_event.startswith("\t"):
                        line_event.replace("\t", "")
                    if ":" in line_event:
                        line_event = re.sub(r":", "_", line_event)
                    line_event = re.sub(r" = | =|= ", "=", line_event)
                    line_event = re.sub(r" { | {|{ ", "{", line_event)
                    line_event = re.sub(r" } | }|} ", "}", line_event)
                    line_event = re.sub(r"kill_heir={}", "kill_heir=yes", line_event)
                    line_event = re.sub(r"(\t )|( \t)", "\t\t", line_event)
                    line_event = re.sub(r"#.*", "", line_event)  # Remove comments
                    events_merged_txt += f"\t{line_event}"

                line = line_event.strip()
                if (
                    line.startswith("title")
                    or line.startswith("disaster_")
                    or line.startswith("custom_tooltip")
                    or line.startswith("has_country_modifier")
                    or (line.startswith("name") and not line.startswith(('name="', "namespace=")))
                    or (line.startswith("tooltip") and "{" not in line)
                    or (line.startswith("modifier=") and "{" not in line)
                ):
                    key = line.split("=")[1].split("#")[0].strip().replace('"', "")

                    dict_localisation[key] = ""

            events_merged_txt += "\n}\n"

    print("Merged all events into one file")

    original_dict = json_parser(events_merged_txt)

    # with open("Events.json", "w", encoding="utf8") as file:
    #     json.dump(original_dict, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Jsonised the event files")


def merging_modifiers(modifiers_input):
    """Merges all modifiers used in FEE's files into one json, localising and parsing them"""
    print("Started Merging Modifiers")

    modifiers_output = ""
    global dict_modifiers

    for modifiers_file in modifiers_input:
        with open(modifiers_file, "r", encoding="utf-8", errors="ignore") as reading_modifiers:
            for line_modifiers in reading_modifiers:
                if line_modifiers.strip().startswith("#") or len(line_modifiers) < 2 and line_modifiers != "}" or line_modifiers.strip().startswith("picture"):
                    continue
                modifiers_output += line_modifiers.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
        modifiers_output += "\n"

    print("Merged all modifiers into one file")

    dict_modifiers = json_parser(modifiers_output)

    print("Jsonised the Modifiers")

    for key in list(dict_modifiers):
        for key_second in list(dict_modifiers[key]):
            if key_second == 'religion':
                key_new = 'Modifier Removed If State Religion Changes'
            else:
                key_new = localized_datas.get(key_second) or key_second.replace("_", " ").title()
            dict_modifiers[key][key_new] = dict_modifiers[key].pop(key_second)

    # with open("EventModifiers.json", "w", encoding="utf-8") as file:
    #     json.dump(dict_modifiers, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Localised the modifiers")


def create_localisation_file(LOC_DIR):
    """Creates the Dict Localisation"""
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0125  # Adjust this tolerance value as needed

    filenames = fee_filter(LOC_DIR, "l_english.yml")
    # filenames.extend(fee_filter(LOC_DIR_VAN, "l_english.yml"))

    key = ""

    for key in list(dict_localisation):
        percentage = (index/len(dict_localisation)) * 100
        if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {current_time} - Progress: {percentage:.1f}%")
        index += 1

        if len(key) == 1:
            del dict_localisation[key]
            continue

        if key == 'bra_dispositio_achillea':
            dict_localisation[key] = "Dispositio Achillea"
        elif key == 'religious_zeal_at_conv':
            dict_localisation[key] = 'Religious Zeal'
        elif key == "is_usurper":
            dict_localisation[key] = 'Usurper'
        elif key == "edict_de_nantes":
            dict_localisation[key] = 'Edict de Nantes'
        elif key == 'supported_independence':
            dict_localisation[key] = "Supported our Independence"
        elif key == 'supported_independence':
            dict_localisation[key] = "Supported our Independence"
        elif key == 'counter_reformation':
            dict_localisation[key] = "Counter-Reformation"
        elif key == 'the_societas_jesu':
            dict_localisation[key] = "The Societas Jesu"
        elif key == 'opinion_left_empire':
            dict_localisation[key] = "Left the Holy Roman Empire"
        elif key == 'birth_of_a_new_city_adm':
            dict_localisation[key] = "Birth of a New City"
        elif key == 'opinion_eased_tension':
            dict_localisation[key] = "Eased Tension"
        elif key == 'opinion_export_good':
            dict_localisation[key] = "Increased Production Through Export"
        elif key == 'opinion_export_bad':
            dict_localisation[key] = "Economy Suffering due to Diverted Trade"
        elif key == 'che_conciliatory_views':
            dict_localisation[key] = "Conciliatory Views"
        elif key == 'opinion_betrayal':
            dict_localisation[key] = "Treacherous Ally"
        elif key == 'local_fortress':
            dict_localisation[key] = "Local Fortifications"
        elif key == 'influenza':
            dict_localisation[key] = "Influenza"
        elif key == 'opinion_improved_relations':
            dict_localisation[key] = "Improved Relations"
        elif key == 'border_friction_from_event':
            dict_localisation[key] = "Irritated over Claims"
        elif key == 'opinion_disappointed':
            dict_localisation[key] = "Disappointed"
        elif key == 'opinion_disgruntled':
            dict_localisation[key] = "Disgruntled"
        elif key == 'caught_spy':
            dict_localisation[key] = "Caught Spy"
        elif key == 'western_reforms':
            dict_localisation[key] = "Western Reforms"
        elif key == 'opinion_money_sent':
            dict_localisation[key] = "Sent us money in our time of need"
        elif key == 'christian_brotherhood':
            dict_localisation[key] = "Christian Brotherhood"
        elif key == 'fighting_famine':
            dict_localisation[key] = "Fighting Famine"
        elif key == 'contained_plague':
            dict_localisation[key] = "Contained Plague"
        elif key == 'severe_plague_local':
            dict_localisation[key] = "Severe Plague"
        elif key == 'cavalry_companions':
            dict_localisation[key] = "Cavalry Companions"
        elif key == 'military_reinforcement':
            dict_localisation[key] = "Military Reinforcement"
        elif key == 'mng_militry_incompetence':
            dict_localisation[key] = "Military Incompetence"

        for filename in filenames:
            if len(dict_localisation[key]) > 1:
                break
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    if ":" in line:
                        line_key, line_value = line.split(":", 1)
                        if line_value.startswith(("0", "1")):
                            line_value = line[1:]
                        if line_key.strip() == key:
                            if not key.startswith("enables_") and ":" in line_value:
                                # line_value = line_value.split(":")[1]
                                if line_value.startswith(("0", "1")):
                                    line_value = line_value[1:]
                            dict_localisation[key] = line_value.strip().replace('"', "").replace(",", "").title()
                            break

        if len(dict_localisation[key]) == 0:
            print(key)

    dict_localisation['ideagroups.1.T'] = 'New Traditions & Ambitions'

    dict_localisation['fee_portuguese_succession_crisis'] = "Portuguese Succession Crisis".title()
    dict_localisation['fee_decline_of_the_ottomans'] = "Decline of the Ottomans".title()
    dict_localisation['fee_division_of_the_habsburg_monarchy'] = "Division of the Habsburg Monarchy".title()
    dict_localisation['fee_partition_of_poland'] = "Partition of Poland?".title()
    dict_localisation['fee_pashtun_uprising'] = "Pashtun Uprising".title()
    dict_localisation['fee_zemene_mesafint'] = "Zemene Mesafint".title()
    dict_localisation['fee_crisis_of_the_mughal_empire'] = "Crisis of the Mughal Empire".title()
    dict_localisation['fee_italy_republican_matter'] = "Italian Republican Matter".title()
    dict_localisation['fee_netherlands_rampjaar'] = "Rampjaar".title()
    dict_localisation['fee_naples_conspiracy_barons_1'] = "First Conspirancy Of the Barons".title()
    dict_localisation['fee_naples_conspiracy_barons_2'] = "Second Conspirancy Of the Barons".title()

    # with open("FEELoc.json", "w", encoding="utf-8") as output:
    #     json.dump(reform_loc, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("Successfully populated the localisation file")


def recurse_process_dict(dictionary, loc_names, loc_datas, loc_provinces):
    """Recursively iterates through the dictionary to parse and localise it"""
    global add_ruler_modifier
    global add_disaster_modifier
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
            or key.endswith("estate")
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

        if key in ("ai_chance", "picture", "desc", 'hidden_effect') or (key == "name" and ".OPT" in value):
            del dictionary[key]
        else:
            if isinstance(value, dict) and ('.T' in key or '.OPT' in key or "Expires" in value):
                localized_name = loc_names.get(key) or key.replace("_", " ").title() + 'NOT_IN_LOC'
                dictionary[localized_name] = dictionary.pop(key)
                if 'Expires' in value and 'disaster' in value:
                    dictionary[localized_name]['Disaster'] = dictionary[localized_name].pop('disaster')
                    dictionary[localized_name]['Disaster'] = loc_names.get(dictionary[localized_name]['Disaster'])
                    continue
                key = localized_name

            elif any(key_localisation_check):
                key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if not isinstance(value, (list, dict)) and (key == "custom_tooltip"):
                    localized_name = loc_names.get(value) or value.replace("_", " ").title()
                elif isinstance(value, dict):  # qui non ci passa mai
                    print(key)
                elif isinstance(value, list):
                    for i, values in enumerate(value):
                        dictionary[key_new][i] = loc_datas.get(values) or loc_names.get(values) or loc_provinces.get(values) or values  # in this case it's likely ROOT, THIS, PREV etc.
                else:
                    dictionary[key_new] = loc_datas.get(value) or loc_names.get(value) or loc_provinces.get(value) or value  # in this case it's likely ROOT, THIS, PREV etc.

            elif len(key) == 3 and key.isupper() and key not in ("NOT", 'AND', 'ADM', 'DIP', 'MIL'):
                key_new = loc_datas.get(key) or key.replace("_", " ").title() + 'NOT_IN_LOC'
                dictionary[key_new] = dictionary.pop(key)

            elif any(key_provinces_check):
                key_new = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        dictionary[key_new][i] = loc_provinces.get(values) or values.replace("_", " ").title() + 'NOT_IN_LOC'
                else:
                    dictionary[key_new] = value.replace("_", " ").title() if isinstance(value, str) else loc_provinces.get(value)

            elif any(key_flag_check):
                key_new = key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if isinstance(value, list):
                    for i, values in enumerate(value):
                        dictionary[key_new][i] = values.replace("_", " ").title()
                else:
                    dictionary[key_new] = value.replace("_", " ").title()

            if isinstance(value, dict):
                if key == "change_religious_influence_equivalent_fee":
                    key_new = "Change Religious Influence"
                    dictionary[key_new] = dictionary.pop(key)
                else:
                    key_new = key.replace("_", " ").title()
                value_new = value
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                if isinstance(value, (list, dict)) and len(value) > 0:
                    recurse_process_dict(value, loc_names, loc_datas, loc_provinces)

            elif isinstance(value, list):
                key_new = key.replace("_", " ").title()
                value_new = value
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                for ite in value:
                    if isinstance(ite, (list, dict)) and len(ite) > 0:
                        recurse_process_dict(ite, loc_names, loc_datas, loc_provinces)

            elif not any(key_localisation_check) and not any(key_flag_check):
                key_new = key.replace("_", " ").title()
                value_new = value
                if isinstance(value, str):
                    if len(value) == 3 and value not in ("NOT", "AND") and not value[1:].isdigit():
                        flag = True
                        dictionary[key_new] = dictionary.pop(key)
                        dictionary[key_new] = loc_datas.get(value) or value.replace("_", " ").title()  # this is likely type = all or factor/modifier = X for mtth/randoms/etc
                    elif key == "id":
                        value_new = f"{value}.T"
                        value_new = loc_names.get(value_new) or value.replace("_", " ").title() + 'NOT_IN_LOC'
                    else:
                        value_new = value.strip('"')
                        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                            value_new = int(value)
                        else:
                            value_new = loc_names.get(value_new) or loc_datas.get(value_new) or value_new.replace("_", " ").title()
                if key in dictionary and not flag:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                flag = False

    return dictionary


def parse_correct_json():
    """Builds the corretc json"""
    global original_dict

    # Replace the old keys with the new keys
    for event_name, event_data in original_dict.items():
        # Check if the event name needs to be replaced
        if "disaster_" in event_name:
            event_name = event_name.split("disaster_")[1]
            if event_name in dict_localisation:
                event_name = f"Disaster: {dict_localisation[event_name]}"
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

    # with open("FEE.json", "w", encoding="utf-8") as output:
    #     json.dump(new_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Succesfully created the correct Json")


def process_event(event_data, event_title):
    """Processes nested list/dict events into singular one"""
    event_dict = {"desc": event_data.get("desc")}

    keys_to_check = [
        "is_triggered_only",
        "fire_only_once",
        "trigger",
        "mean_time_to_happen",
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
    """Processes nested list/dict options into singular one"""
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
        # elif key in {'add_opinion', 'reverse_add_opinion'}:
        #     who = ''
        #     if isinstance(value, list):
        #         for i, values in enumerate(value):
        #             new_key = values['modifier']
        #             option[new_key] = option.pop(key)
        #             who = localized_datas.get(option[new_key][i]['who']) or option[new_key][i]['who'].title()
        #             option[new_key][i] = dict_modifiers.get(new_key)
        #             option[new_key][i]['Country'] = who
        #     else:
        #         new_key = value['modifier']
        #         option[new_key] = option.pop(key)
        #         who = localized_datas.get(option[new_key]['who']) or option[new_key]['who'].title()
        #         option[new_key] = dict_modifiers.get(new_key)
        #         option[new_key]['Country'] = who
        elif isinstance(value, (list, dict)) and (isinstance(value, dict) and any(key_modifier in modifier_search for key_modifier in value.keys())):  # noqa
            processed_value = process_option(value)
            value = processed_value
            option_dict[key] = processed_value
        else:
            option_dict[key] = value

    return option_dict


def process_modifiers(modifier):
    """Processes nested list/dict modifiers into singular one"""
    global add_ruler_modifier
    global add_disaster_modifier
    global dict_modifiers
    result = {}

    for key_modifier, value_modifier in modifier.items():
        # Store the "duration" value if present
        value_duration = value_modifier.get("duration")

        if "name" in value_modifier:
            del value_modifier["name"]
        if "duration" in value_modifier:
            del value_modifier["duration"]

        # Search for the dictionary with the key matching the modifier
        if key_modifier in dict_modifiers:
            value_modifier.update(dict_modifiers[key_modifier])

        # Reinsert the "duration" key with its original value
        if value_duration is not None:
            if value_duration == "-1":
                if add_ruler_modifier:
                    value_modifier["Expires"] = "On Ruler's Death"
                elif add_disaster_modifier:
                    value_modifier["Expires"] = "On Disaster's End"
                else:
                    value_modifier["Expires"] = "Never"
            else:
                value_modifier["Expires"] = f"{value_duration} days"

        result[key_modifier] = value_modifier

    return result


def fee_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(event_o_b4_json):
    """let's parse it all"""

    data_json = event_o_b4_json
    if 'disaster_fee_crisis_of_the_mughal_empire' in data_json:
        filename = 'Events'
    else:
        filename = 'EventModifiers'

    data_json = re.sub(r"#.*", "", data_json)  # Remove comments
    data_json = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data_json,
        flags=re.MULTILINE,
    )  # Separate one line lists
    if 'disaster_fee_crisis_of_the_mughal_empire' in data_json:
        data_json = re.sub(r"[\t]", "", data_json)
        data_json = re.sub(r" \n", "\n", data_json)
        data_json = re.sub("}, },", "},},", data_json)
    else:
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
    if 'disaster_fee_crisis_of_the_mughal_empire' in data_json:
        data_json = re.sub(
            r"(?<=:)(?!-?(?:0|[1-9]\trigger_d*)(?:\.\trigger_d+)?(?:[eE][+-]?\trigger_d+)?)(?!\".*\")[^{\n]+",  # noqa
            r'"\g<0>"',
            data_json,
        )  # Add quotes around string _values
    else:
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
        print(f"ERROR: Unable to parse {filename}")
        print(f"Dumping intermediate code into file: {filename}_{time.time():.0f}.intermediate")

        with open(f"./output/{filename}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data_json)

        return None

    return json_data


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
