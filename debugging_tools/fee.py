import datetime
import glob
import json
import os
import re
import time
from os.path import basename

from natsort import natsorted

# all definitions
if "\\" in os.getcwd():
    MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2185445645"
    VANILLA_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
else:
    MOD_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2185445645"
    VANILLA_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Europa Universalis IV"

LOC_DIR = os.path.join(MOD_PATH, "localisation")
EVENT_MOD_DIR = os.path.join(MOD_PATH, "common", "event_modifiers")
EVENT_MOD_DIR_VAN = os.path.join(VANILLA_PATH, "common", "event_modifiers")

path = os.path.abspath(os.path.join(os.getcwd()))  # debugging-tools
finalpath = os.path.join(os.path.dirname(path), "data", "FEE.json")

data = os.path.join(path, "database.json")
provinces = os.path.join(path, "provinces.json")

EVENTS_PATH = os.path.join(MOD_PATH, "events")

events_input = sorted(glob.glob(os.path.join(EVENTS_PATH, "*.txt")), key=lambda x: x.lower())
modifiers_input = glob.glob(os.path.join(EVENT_MOD_DIR, "*.txt"))
modifiers_input += glob.glob(os.path.join(EVENT_MOD_DIR_VAN, "*.txt"))

dict_original = {}
dict_new = {}
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

tag_provinces_checks = [
    "NOT",
    "AND",
    "ADM",
    "DIP",
    "MIL",
    "tag",
    "who",
    "key",
    "age",
    "adm",
    "dip",
    "mil",
    "mod",
    "win",
    "else",
    "Root",
    "From",
    "Prev",
    "ROOT",
    "FROM",
    "PREV",
    "Meme",
    "area",
    "owns",
]
key_flag_check = [
    "flag",
    "clr_country_flag",
    "clr_global_flag",
    "clr_heir_flag",
    "clr_province_flag",
    "clr_ruler_flag",
    "has_country_flag",
    "has_global_flag",
    "has_consort_flag",
    "has_heir_flag",
    "has_province_flag",
    "has_ruler_flag",
    "set_country_flag",
    "set_global_flag",
    "set_heir_flag",
    "set_province_flag",
    "set_ruler_flag",
]
key_provinces_check = ["owns_core_province", "owns", "province_id"]
key_localisation_check = [
    "id",
    "key",
    "modifier",
    "custom_tooltip",
    "tooltip",
    "disaster",
    "has_disaster",
    "has_country_modifier",
    "has_province_modifier",
    "has_ruler_modifier",
    "remove_country_modifier",
    "remove_province_modifier",
]
key_database = [
    "trait",
    "advisor",
    "remove_advisor",
    "kill_advisor",
    "full_idea_group",
    "has_idea_group",
    "has_idea",
    "who",
    "exists",
    "type",
    "general_with_name",
    "has_ruler",
    "is_claim",
    "is_core",
    "is_permanent_claim",
    "add_claim",
    "add_core",
    "add_permanent_claim",
    "country_or_non_sovereign_subject_holds",
    "join_all_offensive_wars_of",
    "join_all_defensive_wars_of",
    "casus_belli",
    "units_in_province",
    "target",
    "discover_country",
    "has_discovered",
    "add_reform_center",
    "is_religion_enabled",
    "ruler_religion",
    "has_institution",
    "break_union",
    "cede_province",
    "white_peace",
    "inherit",
    "vassalize",
    "release",
    "alliance_with",
    "has_subject_of_type",
    "is_subject_of",
    "is_subject_of_type",
    "is_capital_of",
    "is_enemy",
    "marriage_with",
    "overlord_of",
    "vassal_of",
    "controlled_by",
    "owned_by",
    "sieged_by",
    "is_neighbor_of",
    "country",
    "switch_tag",
    "tag",
    "was_tag",
    "current_age",
    "in_league",
    "separatist_target",
]
key_database_start = [
    "area",
    "continent",
    "religion",
    "culture",
    "attacker",
    "defender",
    "create_",
    "change_",
    "historical",
    "is_institution",
]
key_database_ends = [
    "estate",
    "region",
    "friend",
    "rival",
    "culture",
    "trade_goods",
    "building",
    "war_with",
    "truce_with",
    "union_with",
    "_personality",
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

    build(dict_new)


def merging_events(events_input):
    """Merges all the events files in one file, divided by country"""
    events_merged_txt = ""
    global dict_localisation
    global dict_original

    for event_file in events_input:
        event_file_name = basename(event_file)
        if event_file_name[:-4] == "_flavour_and_events_expanded_events" or event_file_name.startswith("cato"):
            continue
        with open(event_file, "r", encoding="utf-8") as reading_event:
            events_merged_txt += event_file_name[:-4]
            events_merged_txt += "={\n"
            for line_event in reading_event:
                if line_event.isspace():
                    continue

                if not line_event.strip().startswith(("#", "namespace", "namespace=")):
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
                    or (line.startswith("name") and not line.startswith(('name="', "namespace=", "namespace")))
                    or (line.startswith("tooltip") and "{" not in line)
                    or (line.startswith("modifier=") and "{" not in line)
                ):
                    key = line.split("=")[1].split("#")[0].strip().replace('"', "")

                    dict_localisation[key] = ""

            events_merged_txt += "\n}\n"

    print("Merged all events into one file")

    # with open("Events.tx", "w", encoding="utf8") as file:
    #     file.write(events_merged_txt)

    dict_original = json_parser(events_merged_txt) or {}

    # with open("Events.json", "w", encoding="utf8") as file:
    #     json.dump(dict_original, file, indent="\t", separators=(",", ": "), ensure_ascii=False)

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

    dict_modifiers = json_parser(modifiers_output) or {}

    print("Jsonised the Modifiers")

    for key in list(dict_modifiers):
        for key_second in list(dict_modifiers[key]):
            if key_second == "religion":
                key_new = "Modifier Removed If State Religion Changes"
            else:
                key_new = localized_datas.get(key_second) or key_second.replace("_", " ").title()
            dict_modifiers[key][key_new] = dict_modifiers[key].pop(key_second)

    # with open("EventModifiers.json", "w", encoding="utf-8") as file:
    #     json.dump(dict_modifiers, file, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("Localised the modifiers")


def create_localisation_file(LOC_DIR):
    """Creates the Dict Localisation"""
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0125  # Adjust this tolerance value as needed

    filenames = glob.glob(os.path.join(LOC_DIR, "*l_english.yml"))

    key = ""

    for key in list(dict_localisation):
        percentage = (index / len(dict_localisation)) * 100
        if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {current_time} - Progress: {percentage:.1f}%")
        index += 1

        if len(key) == 1:
            del dict_localisation[key]
            continue

        if key == "BYZ_enemy_fortifications":
            dict_localisation[key] = "Enemy Blockade Capabilities"
        elif key == "birth_of_a_new_city_adm":
            dict_localisation[key] = "Birth of a New City"
        elif key == "border_friction_from_event":
            dict_localisation[key] = "Irritated over Claims"
        elif key == "bra_dispositio_achillea":
            dict_localisation[key] = "Dispositio Achillea"
        elif key == "caught_spy":
            dict_localisation[key] = "Caught Spy"
        elif key == "cavalry_companions":
            dict_localisation[key] = "Cavalry Companions"
        elif key == "che_conciliatory_views":
            dict_localisation[key] = "Conciliatory Views"
        elif key == "christian_brotherhood":
            dict_localisation[key] = "Christian Brotherhood"
        elif key == "company_mint":
            dict_localisation[key] = "Company Mint"
        elif key == "contained_plague":
            dict_localisation[key] = "Contained Plague"
        elif key == "counter_reformation":
            dict_localisation[key] = "Counter-Reformation"
        elif key == "developing_company_settlement":
            dict_localisation[key] = "Thriving Settlement"
        elif key in ["earthquake", "pal_stay_united"]:
            dict_localisation[key] = "Earthquake"
        elif key == "economic_urbanization_modifier":
            dict_localisation[key] = "Urbanization"
        elif key == "edict_de_nantes":
            dict_localisation[key] = "Edict de Nantes"
        elif key == "fighting_famine":
            dict_localisation[key] = "Fighting Famine"
        elif key == "gen_trade_access_denied":
            dict_localisation[key] = "Denied exclusive trade privileges through the Bosphorus"
        elif key == "gen_trade_given":
            dict_localisation[key] = "Granted exclusive trade privileges through the Bosphorus"
        elif key == "hau_refused_to_help":
            dict_localisation[key] = "Refused to aid us"
        elif key == "home_of_consort":
            dict_localisation[key] = "Home of Consort"
        elif key == "impoverished_artisans":
            dict_localisation[key] = "Impoverished Craftsmen"
        elif key == "influenza":
            dict_localisation[key] = "Influenza"
        elif key == "is_usurper":
            dict_localisation[key] = "Usurper"
        elif key == "local_fortress":
            dict_localisation[key] = "Local Fortifications"
        elif key == "major_slave_market":
            dict_localisation[key] = "Major Slave Market"
        elif key == "military_reinforcement":
            dict_localisation[key] = "Military Reinforcement"
        elif key == "mng_militry_incompetence":
            dict_localisation[key] = "Military Incompetence"
        elif key == "monopoly_enforced":
            dict_localisation[key] = "Monopoly Enforced"
        elif key == "opinion_betrayal":
            dict_localisation[key] = "Treacherous Ally"
        elif key == "opinion_disappointed":
            dict_localisation[key] = "Disappointed"
        elif key == "opinion_disgruntled":
            dict_localisation[key] = "Disgruntled"
        elif key == "opinion_eased_tension":
            dict_localisation[key] = "Eased Tension"
        elif key == "opinion_export_bad":
            dict_localisation[key] = "Economy Suffering due to Diverted Trade"
        elif key == "opinion_export_good":
            dict_localisation[key] = "Increased Production Through Export"
        elif key == "opinion_improved_relations":
            dict_localisation[key] = "Improved Relations"
        elif key == "opinion_left_empire":
            dict_localisation[key] = "Left the Holy Roman Empire"
        elif key == "opinion_money_sent":
            dict_localisation[key] = "Sent us money in our time of need"
        elif key == "opinion_rejected_papal_demand_advisor":
            dict_localisation[key] = "Hosting a Heretic"
        elif key == "opinion_sent_help":
            dict_localisation[key] = "Sent Help"
        elif key == "opinion_supported_war":
            dict_localisation[key] = "Supported our War"
        elif key == "opinion_supported_war_enemy":
            dict_localisation[key] = "Supported our Enemy"
        elif key == "raided_by_cavalry":
            dict_localisation[key] = "Raided by Cavalry"
        elif key == "regimental_town":
            dict_localisation[key] = "Regimental City"
        elif key == "religious_zeal_at_conv":
            dict_localisation[key] = "Religious Zeal"
        elif key == "roman_garisson":
            dict_localisation[key] = "Reinforced Roman Garrison"
        elif key == "severe_plague_local":
            dict_localisation[key] = "Severe Plague"
        elif key == "supported_independence":
            dict_localisation[key] = "Supported our Independence"
        elif key == "the_societas_jesu":
            dict_localisation[key] = "The Societas Jesu"
        elif key == "urbanites_chastised":
            dict_localisation[key] = "Over-Exploited Cities"
        elif key == "western_reforms":
            dict_localisation[key] = "Western Reforms"

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
                            line_value = line_value.replace("§M", "").replace("§G", "").replace("§Y", "").replace("§R", "").replace("§!", "")
                            dict_localisation[key] = line_value.strip().replace('"', "").replace(",", "").title()
                            break

        if len(dict_localisation[key]) == 0:
            print(key)

    dict_localisation["ideagroups.1.T"] = "New Traditions & Ambitions"
    dict_localisation["centralization_modifier"] = "Increased Centralization"

    dict_localisation["fee_portuguese_succession_crisis"] = "Portuguese Succession Crisis".title()
    dict_localisation["fee_decline_of_the_ottomans"] = "Decline of the Ottomans".title()
    dict_localisation["fee_division_of_the_habsburg_monarchy"] = "Division of the Habsburg Monarchy".title()
    dict_localisation["fee_partition_of_poland"] = "Partition of Poland?".title()
    dict_localisation["fee_pashtun_uprising"] = "Pashtun Uprising".title()
    dict_localisation["fee_zemene_mesafint"] = "Zemene Mesafint".title()
    dict_localisation["fee_crisis_of_the_mughal_empire"] = "Crisis of the Mughal Empire".title()
    dict_localisation["fee_italy_republican_matter"] = "Italian Republican Matter".title()
    dict_localisation["fee_netherlands_rampjaar"] = "Rampjaar".title()
    dict_localisation["fee_naples_conspiracy_barons_1"] = "First Conspirancy Of the Barons".title()
    dict_localisation["fee_naples_conspiracy_barons_2"] = "Second Conspirancy Of the Barons".title()
    dict_localisation["fee_vijayaba_kollaya"] = "Vijayaba Kollaya".title()

    # with open("FEELoc.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_localisation, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("Successfully populated the localisation file")


def build(final_dict):
    """Final Build"""
    recurse_process_dict(final_dict, dict_localisation, localized_datas, localized_provinces)

    with open(f"{os.path.dirname(finalpath)}\\FEE.json", "w", encoding="utf-8") as output:
        json.dump(final_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("Successfully localised the file!")


def recurse_process_dict(dictionary, loc_names, loc_datas, loc_provinces):
    """Recursively iterates through the dictionary to parse and localise it"""
    global add_ruler_modifier
    global add_disaster_modifier
    skip = False
    for key, value in list(dictionary.items()):
        if key in ("ai_chance", "picture", "desc", "hidden_effect") or (key == "name" and ".OPT" in value):
            del dictionary[key]
            continue
        else:
            skip = False
            if isinstance(value, dict):
                value_new = value
                if ".T" in key or ".OPT" in key or "Expires" in value:
                    key_new = loc_names.get(key)
                    if "Expires" in value:
                        skip = True
                elif key == "change_religious_influence_equivalent_fee":
                    key_new = "Change Religious Influence"
                elif key == "add_stability_or_adm_power_per_stab" or key in ("add_prestige_or_monarch_power", "add_innovativeness_or_monarch_power"):
                    key_new = "Add Stability Or Adm Power" if key == "add_stability_or_adm_power_per_stab" else key.replace("_", " ").title()
                    value_new = int(dictionary[key]["amount"])
                    skip = True
                elif key == "kill_leader":
                    key_new = "Kill Leader"
                    value_new = dictionary[key]["type"]
                    skip = True
                elif key in ("is_or_was_tag", "is_expanded_mod_active"):
                    key_new = key.replace("_", " ").title()
                    value_new = loc_datas.get(dictionary[key]["tag"]) if key == "is_or_was_tag" else loc_datas.get(dictionary[key]["mod"])
                    skip = True
                elif (len(key) == 3 or len(key) == 4) and key not in tag_provinces_checks:
                    key_new = loc_datas.get(key) if key.isalpha() else loc_provinces.get(key)
                elif key in ("country_event", "province_event"):
                    key_new = "Event"
                else:
                    key_new = key.replace("_", " ").title()

                temp = dictionary.pop(key)
                dictionary[key_new] = temp
                dictionary[key_new] = value_new

                if isinstance(value, (list, dict)) and len(value) > 0 and skip is False:
                    recurse_process_dict(value, loc_names, loc_datas, loc_provinces)

            elif isinstance(value, list):
                if (len(key) == 3 or len(key) == 4) and key not in tag_provinces_checks:
                    key_new = loc_datas.get(key) if key.isalpha() else loc_provinces.get(key)
                else:
                    key_new = "Country" if key == "tag" else key.replace("_", " ").title()

                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value

                for i, ite in enumerate(value):
                    if isinstance(ite, dict):
                        recurse_process_dict(ite, loc_names, loc_datas, loc_provinces)
                    elif isinstance(ite, list):
                        # it usually never passes here, since a lit of list are really uncommon
                        print(key, value, ite)
                    else:
                        if key in key_flag_check:
                            value_new = ite.replace("_", " ").title()
                        elif key in key_provinces_check:
                            value_new = loc_provinces.get(ite)
                        elif key in key_database or any(key.startswith(k) for k in key_database_start) or any(key.endswith(k) for k in key_database_ends):
                            value_new = loc_datas.get(ite) if ite != "all" else ite.replace("_", " ").title()
                        elif key in key_localisation_check:
                            value_new = True
                            if key in ("custom_tooltip", "tooltip"):
                                skip = True
                                key_new_tt = loc_names.get(ite) or ite.replace("_", " ").title()
                                del dictionary[key_new][i]
                                dictionary[key_new].append(key_new_tt)
                            if key in ("id", "key"):
                                value_new = loc_names.get(f"{ite}.T") if key == "id" else loc_names.get(ite)
                        else:
                            value_new = ite if isinstance(ite, bool) else ite.replace("_", " ").title()

                        if skip is False:
                            dictionary[key_new][i] = value_new

            else:  # key are always string
                if isinstance(value, str) and is_numeric_string(value):  # forcing all the "numbers" to float/int
                    if "." in value or "e" in value.lower():
                        value = float(value)
                    else:
                        value = int(value)
                    dictionary[key] = value

                if isinstance(value, (bool, int, float)):
                    if key.startswith("fee_add_estate") or key.startswith("fee_reduce_estate"):
                        key_new = key.replace("fee_", "").replace("_", " ").title()
                    else:
                        key_new = key.replace("_", " ").title()

                    dictionary[key_new] = dictionary.pop(key)
                else:  # value are strings
                    if key in key_database or any(key.startswith(k) for k in key_database_start) or any(key.endswith(k) for k in key_database_ends):
                        key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                        value_new = loc_datas.get(value) if value != "all" else value.replace("_", " ").title()
                    elif key in key_flag_check or key in key_provinces_check:
                        key_new = key.replace("_", " ").title()
                        value_new = loc_provinces.get(value) if key in key_provinces_check else value.replace("_", " ").title()
                    elif key in key_localisation_check:
                        key_new = key.replace("_", " ").title()
                        value_new = value
                        if key in ("custom_tooltip", "tooltip"):
                            key_new = loc_names.get(value) or value.replace("_", " ").title()
                            value_new = True
                        elif key == "id":
                            value_new = loc_names.get(f"{value}.T")
                        else:
                            value_new = loc_names.get(value)
                    else:
                        key_new = key.replace("_", " ").title()
                        value_new = value

                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new

            continue

    return dictionary


def parse_correct_json():
    """Builds the corretc json"""
    global dict_original

    # Replace the old keys with the new keys
    for event_name, event_data in list(dict_original.items()):
        if "country_event" in dict_original[event_name] and "province_event" in dict_original[event_name]:
            country_events = dict_original[event_name]["country_event"]
            province_events = dict_original[event_name]["province_event"]

            # Ensure country_events and province_events are lists
            country_events = [country_events] if isinstance(country_events, dict) else country_events
            province_events = [province_events] if isinstance(province_events, dict) else province_events

            combined_events = natsorted(country_events + province_events, key=lambda x: list(x.values())[0])

            del dict_original[event_name]["country_event"]
            del dict_original[event_name]["province_event"]
            dict_original[event_name]["combined_event"] = combined_events
        # Check if the event name needs to be replaced
        if "disaster_" in event_name:
            event_name = event_name.split("disaster_")[1]
            if event_name in dict_localisation:
                event_name = f"Disaster: {dict_localisation[event_name]}"
            if event_name == "fee_naples_conspiracy_barons":
                event_name = "Disaster: Conspiracy of the Barons"
        else:
            if len(dict_original[event_name]) == 0:
                continue
            event_name = event_name.split("FEE_")[1].split("_Events")[0].replace("_", " ").title()

        dict_new[event_name] = {}
        for event_type in {"country_event", "province_event", "combined_event"}:
            if event_type in event_data:
                events = event_data[event_type]
                if isinstance(events, list):
                    for event in events:
                        if "hidden" in event and event["hidden"]:
                            continue
                        dict_new[event_name].update(process_event(event, event["title"]))
                else:
                    if "hidden" in events and events["hidden"]:
                        continue
                    dict_new[event_name].update(process_event(events, events["title"]))

    # with open("FEE.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_new, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

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
        elif isinstance(value, dict):
            processed_value = process_option(value)
            value = processed_value
            option_dict[key] = processed_value
        elif isinstance(value, list) and len(value) > 0 and any(isinstance(i, dict) for i in value):
            processed_list = [process_option(item) for item in value]
            option_dict[key] = processed_list
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
                    if 'desc' in value_modifier and value_modifier['desc'] == 'fee_diseases_until_end_of_plague':
                        value_modifier["Expires"] = "On Plague's End"
                        del value_modifier["desc"]
                    else:
                        value_modifier["Expires"] = "Never"
            else:
                value_modifier["Expires"] = f"{value_duration} days"

        if "disaster" in value_modifier:
            value_modifier["Disaster"] = value_modifier.pop("disaster")
            value_modifier["Disaster"] = dict_localisation.get(value_modifier["Disaster"])

        result[key_modifier] = value_modifier

    return result


def json_parser(event_o_b4_json):
    """let's parse it all"""

    data_json = event_o_b4_json
    if "disaster_fee_crisis_of_the_mughal_empire" in data_json:
        filename = "Events"
    else:
        filename = "EventModifiers"

    data_json = re.sub(r"#.*", "", data_json)  # Remove comments
    data_json = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-trigger_a-zA-Z])+(\s)(?=[0-9\.\-trigger_a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data_json,
        flags=re.MULTILINE,
    )  # Separate one line lists
    if "disaster_fee_crisis_of_the_mughal_empire" in data_json:
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
    if "disaster_fee_crisis_of_the_mughal_empire" in data_json:
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


def is_numeric_string(s):
    return re.match(r"^[-+]?\d*\.?\d+$", s) is not None


start()
