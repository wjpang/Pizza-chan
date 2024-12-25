import glob
import json
import os
import re
import time
from os.path import basename

from natsort import natsorted

# all definitions
if "\\" in os.getcwd():
    FEE_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2185445645"
    GEE_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1596815683"
    GME_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2469419235"
    HIE_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2804377099"
    VAN_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
    # eu4_dir = r'C:\Program Files\Epic Games\EuropaUniversalis4'  # This is for EGS
else:
    FEE_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2185445645"
    GEE_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/1596815683"
    GME_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2469419235"
    HIE_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/236850/2804377099"
    VAN_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Europa Universalis IV"

EVENTS_DIR_FEE = os.path.join(FEE_PATH, "events")
MODIFS_DIR_FEE = os.path.join(FEE_PATH, "common", "event_modifiers")
MODIFS_DIR_VAN = os.path.join(VAN_PATH, "common", "event_modifiers")
DISASTER_PATH = os.path.join(FEE_PATH, "common", "disasters")
EVENTS_PATH = os.path.join(FEE_PATH, "events")

path = os.path.abspath(os.path.join(os.getcwd()))  # debugging-tools

mod = ""

dict_original = {}
dict_new = {}
dict_final = {}
dict_modifiers = {}
dict_reform = {}
dict_localisation = {}

check_multiple_custom_tooltip = [
    "HIE_SPA_AND_FUERO_JUZGO_TT",
    "HIE_SPA_ARA_UNION_OF_CROWNS_ITALY_TT",
    "HIE_SPA_ARA_UNION_OF_CROWNS_IBERIA_TT",
    "HIE_PARLIAMENT_SEAT_DEV_GOVERNING_COST_TT",
    "HIE_COWRIE_TRADE_TT",
    "HIE_RAJPUT_CLAN_SYSTEM_TT",
]
key_database = [
    "accepted_culture", "add_building", "add_claim", "add_core",
    "add_permanent_claim", "add_reform_center", "add_ruler_personality",
    "adm_tech", "advisor",  "alliance_with", "break_union", "casus_belli",
    "cede_province", "change_culture", "change_trade_goods", "controlled_by",
    "country", "country_or_non_sovereign_subjec", "current_age",
    "custom_tooltip", "dip_tech", "disaster", "discover_country", "exists",
    "full_idea_group", "general_with_name", "government", "has_building",
    "has_discovered", "has_dlc", "has_idea", "has_idea_group", "has_institution",
    "has_leader", "has_reform", "has_ruler", "has_subject_of_type", "in_league",
    "inherit", "is_capital_of", "is_claim", "is_core", "is_enemy",
    "is_neighbor_of", "is_permanent_claim", "is_religion_enabled",
    "is_subject_of", "is_subject_of_type", "join_all_defensive_wars_of",
    "join_all_offensive_wars_of", "kill_advisor", "marriage_with", "mil_tech",
    "overlord_of", "owned_by", "primary_culture", "release", "remove_advisor",
    "remove_building", "ruler_has_personality", "ruler_religion",
    "separatist_target", "sieged_by", "switch_tag", "tag", "target",
    "trade_goods", "trait", "type", "units_in_province", "vassal_of",
    "vassalize", "was_tag", "white_peace", "who", "crown_land_share",
    "province_id", "has_terrain", "culture_group", "have_had_reform",
    "technology_group",
]
key_database_start = [
    "attacker", "change_", "continent", "create_", "defender",
    "historical", "is_institution", "owned_by", "religion", "tier_",
]
key_database_ends = [
    "estate", "region", "friend", "rival", "culture", "trade_goods", "building",
    "war_with", "truce_with", "union_with", "_personality", "area", "disaster",
    "province_modifier", "ruler_modifier", "country_modifier", "estate_privilege",
    "_rebels", "reform_center", "government_reform"
]
key_flag_check = [
    "flag", "clr_country_flag", "clr_global_flag", "clr_heir_flag",
    "clr_province_flag", "clr_ruler_flag", "has_country_flag", "has_global_flag",
    "has_consort_flag", "has_heir_flag", "has_province_flag", "has_ruler_flag",
    "set_country_flag", "set_global_flag", "set_heir_flag", "set_province_flag",
    "set_ruler_flag",
]
key_localisation_check = [
    "id", "key", "modifier", "custom_tooltip", "tooltip", "disaster", "end_disaster",
    "has_disaster", "has_country_modifier", "has_province_modifier",
    "has_ruler_modifier", "remove_country_modifier", "remove_province_modifier",
]
tag_provinces_checks = [
    "ADM", "adm", "age", "AND", "area", "DIP", "dip", "else", "From", "FROM",
    "key", "Meme", "MIL", "mil", "mod", "NOT", "owns", "Prev", "PREV", "Root",
    "ROOT", "tag", "who", "win",
]
key_database_ends_map = [
    "area", "region", "superregion",
]
key_database_unit = [
    "artillery", "infantry", "cavalry", "galley", "lightship", "heavy_ship",
    "large_cast_bronze_mortar",
]

add_ruler_modifier = False
add_disaster_modifier = False

modifier_search = [
    "add_country_modifier", "add_disaster_modifier",
    "add_permanent_province_modifier", "add_province_modifier", "add_ruler_modifier",
]
extended_nested_search = modifier_search + ["country_event", "province_event", ]

with open(os.path.join(path, "database.json"), "r", encoding="utf-8") as file:
    localized_datas = json.load(file)


def start():
    """All the shit"""
    create_localisation()

    FEE()
    GEE()
    GME()
    HIE()


def create_localisation():
    """Creates the Dict Localisation"""

    localisation_files = glob.glob(os.path.join(os.path.join(FEE_PATH, "localisation"), "*l_english.yml"))
    localisation_files += glob.glob(os.path.join(os.path.join(GEE_PATH, "localisation"), "*l_english.yml"))
    localisation_files += glob.glob(os.path.join(os.path.join(GME_PATH, "localisation"), "*l_english.yml"))
    localisation_files += glob.glob(os.path.join(os.path.join(HIE_PATH, "localisation"), "*l_english.yml"))
    localisation_files += glob.glob(os.path.join(os.path.join(VAN_PATH, "localisation"), "*l_english.yml"))

    for file in localisation_files:
        with open(file, "r", encoding="utf-8-sig") as f:
            loc = f.readlines()
        for line in loc:
            line = line.strip()
            if line.startswith("#") or line == "" or line == "l_english:":
                continue
            line = line.split(":", 1)
            line[1] = line[1].replace('"', "").strip().replace("§!", "").replace("§R", "").replace("§Y", "").replace("§G", "").replace("§M", "")
            if line[1] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                line[1] = ""
            if line[1] != "" and line[1][0] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"} and line[1][1] == " ":  # Remove numbers at the beginning of the string
                line[1] = line[1][2:]
            if line[1].startswith("\\n"):
                line[1] = line[1][2:]
            elif line[1].endswith("\\n"):
                line[1] = line[1][:-2]
            dict_localisation[line[0]] = line[1].title()

    dict_localisation["fee_crisis_of_the_mughal_empire"] = "Crisis of the Mughal Empire".title()
    dict_localisation["fee_decline_of_the_bahmani_sultanate"] = "Decline of the Bahmani Sultanate".title()
    dict_localisation["fee_decline_of_the_ottomans"] = "Decline of the Ottomans".title()
    dict_localisation["fee_decline_of_vijayanagar"] = "Decline of Vijayanagar".title()
    dict_localisation["fee_division_of_the_habsburg_monarchy"] = "Division of the Habsburg Monarchy".title()
    dict_localisation["fee_italy_republican_matter"] = "Italian Republican Matter".title()
    dict_localisation["fee_naples_conspiracy_barons_1"] = "First Conspirancy Of the Barons".title()
    dict_localisation["fee_naples_conspiracy_barons_2"] = "Second Conspirancy Of the Barons".title()
    dict_localisation["fee_netherlands_rampjaar"] = "Rampjaar".title()
    dict_localisation["fee_partition_of_poland"] = "Partition of Poland?".title()
    dict_localisation["fee_pashtun_uprising"] = "Pashtun Uprising".title()
    dict_localisation["fee_portuguese_succession_crisis"] = "Portuguese Succession Crisis".title()
    dict_localisation["fee_vijayaba_kollaya"] = "Vijayaba Kollaya".title()
    dict_localisation["fee_zemene_mesafint"] = "Zemene Mesafint".title()
    dict_localisation["pal_stay_united"] = "Stay United".title()

    dict_localisation["feudalism_vs_autocracy"] = "Feudalism Vs Autocracy"

    dict_localisation["start"] = "Traditions"
    dict_localisation["bonus"] = "Ambition"

    print("Successfully populated the localisation file")


def FEE():
    print("\nStarted Working on FEE")
    global mod
    mod = "FEE"

    print("\tStarting work on Disasters")

    disaster_merged_txt = ""
    for disaster_file in sorted(glob.glob(os.path.join(DISASTER_PATH, "*.txt")), key=lambda x: x.lower()):
        with open(disaster_file, "r", encoding="utf-8") as reading_disaster_file:
            for line_disaster in reading_disaster_file:
                if line_disaster.strip().startswith("#") or len(line_disaster) < 1:
                    continue
                line_disaster = line_disaster.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}") + "\n"
                if "." in line_disaster and "=" not in line_disaster and ":" not in line_disaster:
                    line_disaster = f'"{line_disaster}' + '"\n'
                disaster_merged_txt += line_disaster

    dict_new = JsonParser(disaster_merged_txt)

    build(dict_new)

    print("\tCreated the Disaster json\n")

    print("\tStarting work on Events")
    global dict_original
    global dict_modifiers

    events_merged_txt = ""
    for event_file in sorted(glob.glob(os.path.join(EVENTS_PATH, "*.txt")), key=lambda x: x.lower()):
        event_file_name = basename(event_file)
        if event_file_name[:-4] == "_flavour_and_events_expanded_events" or event_file_name.startswith("cato"):
            continue
        with open(event_file, "r", encoding="utf-8") as reading_event:
            events_merged_txt += event_file_name[:-4]
            events_merged_txt += "={\n"
            for line_event in reading_event:
                if line_event.isspace():
                    continue
                if 'birth_date' in line_event or "started_in" in line_event:
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

            events_merged_txt += "\n}\n"

    print("\tMerged all events into one file")

    dict_original = JsonParser(events_merged_txt) or {}

    print("\tStarted Merging Modifiers")

    modifiers_output = ""
    modifiers_input = glob.glob(os.path.join(MODIFS_DIR_FEE, "*.txt"))
    modifiers_input += glob.glob(os.path.join(MODIFS_DIR_VAN, "*.txt"))

    for modifiers_file in modifiers_input:
        with open(modifiers_file, "r", encoding="utf-8", errors="ignore") as reading_modifiers:
            for line_modifiers in reading_modifiers:
                if line_modifiers.strip().startswith("#") or len(line_modifiers) < 2 and line_modifiers != "}" or line_modifiers.strip().startswith("picture"):
                    continue
                modifiers_output += line_modifiers.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
        modifiers_output += "\n"

    dict_modifiers = JsonParser(modifiers_output) or {}

    for key in list(dict_modifiers):
        for key_second in list(dict_modifiers[key]):
            if key_second == "religion":
                key_new = "Modifier Removed If State Religion Changes"
            else:
                key_new = localized_datas.get(key_second) or key_second.replace("_", " ").title()
            dict_modifiers[key][key_new] = dict_modifiers[key].pop(key_second)
            if isinstance(dict_modifiers[key][key_new], list):
                print(key)

    print("\tLocalised the modifiers")

    dict_new = parse_correct_json(dict_original)

    build(dict_new)


def GEE():
    print("\nStarted Working on GEE")
    global mod
    mod = "GEE"
    reforms_merged_txt = ""

    dict_original = JsonParser(os.path.join(GEE_PATH, "common", "governments", "zzz_00_governments.txt")) or {}

    for reform_file in glob.glob(os.path.join(GEE_PATH, "common", "government_reforms", "*.txt")):
        if reform_file.endswith("modified_by_GE.txt"):
            continue
        with open(reform_file, "r", encoding="utf-8") as reading_reforms:
            for line_reform in reading_reforms:
                if line_reform.strip().startswith("#") or len(line_reform) < 2 and line_reform != "}" or line_reform.strip().startswith("picture"):
                    continue
                line_reform = line_reform.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
                if 'albergo_nobili_mechanic' in reforms_merged_txt:
                    if ":" in line_reform:
                        line_reform = re.sub(r":", "_", line_reform)
                reforms_merged_txt += line_reform
                line_reform = line_reform.strip()
                if (
                    "{" not in line_reform
                    and line_reform.startswith("modifier = ")
                    or line_reform.startswith("name = ")
                    or (line_reform.endswith("yes") and line_reform.startswith("enables_") and not line_reform.endswith("idea_group = yes"))
                    or line_reform.endswith("_mechanic")
                ) and not line_reform.startswith("gui"):
                    if '"' in line_reform:
                        line_reform = line_reform.replace('"', '')
                    if (
                        line_reform.startswith("name = ") or
                        line_reform.startswith("cooldown_token = ") or
                        line_reform.startswith("mechanic_type = ")
                    ):
                        line_reform = line_reform.split("=")[1].strip()
        reforms_merged_txt += "\n"

    print("\tMerged all Government Reforms into one file")

    dict_reform = JsonParser(reforms_merged_txt) or {}

    for key, value in dict_original.items():
        if key in "pre_dharma_mapping":
            continue
        dict_new[key] = {}
        for reform_key, reform_value in value.items():
            if reform_key != "reform_levels":
                continue
            for list_name, list_reform in reform_value.items():
                dict_new[key][list_name] = {}
                for reform, reforms in list_reform.items():
                    for singular_reform in reforms:
                        if singular_reform not in dict_reform:
                            continue
                        dict_new[key][list_name][singular_reform] = dict_reform[singular_reform]
                        continue
                    continue
                continue
            break

    print("\tSuccessfully fixed the Reform json")

    build(dict_new)

    print("\tCreated the GE-Reform json")


def GME():
    print("\nStarted Working on GME")
    global mod
    mod = "GME"

    monument_merged_tx = ""

    MON_DIR = os.path.join(GME_PATH, "common", "great_projects")
    MON_INPUT = glob.glob(os.path.join(MON_DIR, "*.txt"))

    for monument_file in MON_INPUT:
        with open(monument_file, "r", encoding="utf-8") as reading_mon:
            if "\\" in monument_file:
                monument_merged_tx += monument_file[100:-4]
            else:
                monument_merged_tx += monument_file[138:-4]
            monument_merged_tx += " = {\n"
            for line_mon in reading_mon:
                if line_mon.startswith("#"):
                    continue
                monument_merged_tx += "\t"
                monument_merged_tx += line_mon

            monument_merged_tx += "\n}\n"

    print("\tMerged all monuments into one file")

    dict_new = JsonParser(monument_merged_tx)

    build(dict_new)

    print("\tCreated the GME json")


def HIE():
    print("\nStarted Working on HIE")
    global mod
    mod = "HIE"

    dict_new = JsonParser(os.path.join(HIE_PATH, "common", "ideas", "000_HIE_country_ideas.txt"))

    build(dict_new)

    print("\tCreated the HIE json")


def build(dictionary):
    dict_localisation.update(localized_datas)

    dict_final = recurse_process_dict(dictionary, dict_localisation)

    if mod == "FEE":
        if 'Advisor' in dict_final:
            path_final = os.path.join(os.path.dirname(path), "data", "FEE.json")
        else:
            path_final = os.path.join(os.path.dirname(path), "data", "Disaster.json")
    elif mod == "HIE":
        dict_final = dict(sorted(dict_final.items()))
        path_final = os.path.join(os.path.dirname(path), "data", "HIE.json")
    elif mod == "GME":
        path_final = os.path.join(os.path.dirname(path), "data", "GME.json")
    elif mod == "GEE":
        path_final = os.path.join(os.path.dirname(path), "data", "GE.json")

    with open(path_final, "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)


def recurse_process_dict(dictionary, loc_names):
    """Recursively iterates through the dictionary to parse and localise it"""
    skip = False

    for key, value in list(dictionary.items()):
        if mod == "HIE":
            if key in ("trigger", "removed_effect", "free"):
                del dictionary[key]
                continue
        elif mod == "GME":
            if key in (
                "time", "can_use_modifiers_trigger",
                "build_trigger", "tier_0",
                "upgrade_time", "cost_to_upgrade",
                "on_upgraded", "on_built", "on_destroyed",
                "keep_trigger", "type", "can_be_moved", "build_cost"
            ):
                del dictionary[key]
                continue
        elif mod == "FEE":
            if key in (
                "ai_chance", "picture", "desc", "hidden_effect", "progress",
                "while", "goto",
            ) or (key == "name" and ".OPT" in value):
                del dictionary[key]
                continue
        elif mod == "GEE":
            if key in (
                "icon", "legacy_equivalent", "allow_normal_conversion",
                "valid_for_nation_designer", "nation_designer_trigger",
                "nation_designer_cost", "ai", "hidden_effect", "effect",
                "removed_effect",
            ):
                del dictionary[key]
                continue
        if key == "custom_tooltip" and isinstance(value, str) and len(value) < 3:
            del dictionary[key]
            continue

        skip = False

        if isinstance(value, dict):
            value_new = value
            # This should handle all of HIE
            if key.isalpha() and key.upper() in (
                'ADM', 'DIP', 'MIL',
                'OR', 'NOT', 'AND', "IF", "ELSE", "WHILE"
            ):
                key_new = key.replace("_", " ").title()
            elif key.startswith("HIE_") or key.startswith("hie") or key in ("start", "bonus", "MFA_byzantine_claimants"):
                key_new = key.replace("_ideas", "")
                key_new = key_new.replace("HIE_", "")
                key_new = loc_names.get(key_new)
                dictionary[key_new] = dictionary.pop(key)
                value_new = recurse_process_dict(value, loc_names)
                value_new = dictionary[key_new]
                continue
            elif key == "effect" and any(k in value for k in ("country_event", "unlock_estate", "custom_tooltip", "add_country_modifier", "remove_temporary_colonist")):
                key_new = key.replace("_", " ").title()
                if "country_event" in value:
                    del dictionary[key]
                    continue

                if "unlock_estate" in value:
                    dictionary["Effect"] = {}
                    dictionary["Effect"]["Enable Estate"] = loc_names.get(dictionary[key]["unlock_estate"]["estate"])
                    del dictionary[key]
                    continue
                if "custom_tooltip" in value or "add_country_modifier" in value:
                    dictionary["Effect"] = {}
                    del dictionary[key]
                    value_new = True
                    if "custom_tooltip" in value:
                        if any(key in value["custom_tooltip"] for key in check_multiple_custom_tooltip):
                            transform_multiple_entry(dictionary["Effect"], value)
                            continue
                        result = transform_singular_entry(key, value["custom_tooltip"])
                        key_new, value_new = result if result is not None else (key, value["custom_tooltip"])
                    else:
                        if "hie_ita_gpv_fanti_da_mar_modifier" in value["add_country_modifier"]["name"] or \
                                "hie_mer_the_legion_mewar_modifier" in value["add_country_modifier"]["name"]:
                            transform_multiple_entry(dictionary["Effect"], value)
                            continue
                        result = transform_singular_entry(key, value["add_country_modifier"])
                        key_new, value_new = result if result is not None else (key, value["add_country_modifier"])
                    dictionary["Effect"][key_new] = value_new
                else:
                    del dictionary[key]
                continue
            # from now on it's the rest
            elif key == "can_upgrade_trigger" or "starting_tier" in value or any(k.startswith("gme_") for k in value) or key.startswith("tier_") or key in ("province_modifiers", "area_modifier", "region_modifier", "country_modifiers", "conditional_modifier"):
                if "starting_tier" in value:
                    key_new = loc_names.get(key).title()
                elif key == "can_upgrade_trigger":
                    key_new = "Monument Trigger"
                else:
                    key_new = key.replace("_", " ").title()

                dictionary[key_new] = dictionary.pop(key)
                value_new = recurse_process_dict(value, loc_names)
                value_new = dictionary[key_new]
                continue

            # This should handle GE's tiers
            elif key in ("monarchy", "republic", "tribal", "native", "theocracy"):
                key_new = key.replace("_", " ").title()
                value = localise_reform_tiers(value, loc_names)
                if len(value) < 1:
                    skip = True
            elif 'icon' in value or key.endswith('_reform') or key.endswith('_reform_GE'):
                if key in ('tur_reform_eyalets', 'tur_reform_beylerbeys'):
                    del dictionary[key]
                    continue
                key_new = loc_names.get(key)
                if key_new is None:
                    print(key)
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = recurse_process_dict(value, loc_names)
                continue

            elif key == "random_list":
                key_new = key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
                for key_random, value_random in value.items():
                    if isinstance(value_random, dict):
                        value_random_new = recurse_process_dict(value_random, loc_names)
                        dictionary[key_new][key_random] = value_random_new
                    elif isinstance(value_random, list):
                        value_random_new = []
                        for item in value_random:
                            value_random_new.append(recurse_process_dict(item, loc_names))
                        dictionary[key_new][key_random] = value_random_new

                dictionary[key_new][key_random] = value_random
                continue
            elif key.startswith("province_is"):
                key_new = key.replace("_", " ").title()
                if key.endswith("religion_group"):
                    value_new = loc_names.get(dictionary[key]["religion_group"])
                elif key.endswith("religion"):
                    value_new = loc_names.get(dictionary[key]["religion"])
                else:
                    value_new = loc_names.get(dictionary[key]["culture_group"])
                skip = True
            elif key in ("custom_trigger_tooltip", "variable_arithmetic_trigger"):
                if key in "variable_arithmetic_trigger":
                    key_new = loc_names.get(dictionary[key]["custom_tooltip"]).replace("§R", "").replace("§Y", "").replace("§G", "").replace("§!", "").replace("£", "")
                else:
                    key_new = loc_names.get(dictionary[key]["tooltip"]).replace("§R", "").replace("§Y", "").replace("§G", "").replace("§!", "").replace("£", "")
                value_new = True
                skip = True
            elif key == "provincial_institution_progress":
                key_new = dictionary[key]["which"].title()
                value_new = dictionary[key]["value"]
                skip = True
            elif ".T" in key or ".OPT" in key or "Expires" in value or "on_monthly" in value:
                key_new = loc_names.get(key) or key.replace("_", " ").title()
                key_new = key_new.replace(",", "").title()
                if "Expires" in value:
                    skip = True
            elif key in ("is_or_was_tag", "is_expanded_mod_active"):
                key_new = key.replace("_", " ").title()
                if key == "is_or_was_tag":
                    value_new = loc_names.get(dictionary[key]["tag"])
                else:
                    value_new = loc_names.get(dictionary[key]["mod"])
                skip = True
            elif key == "employed_advisor":
                key_new = f"Employed {loc_names.get(value['category'])} Advisor"
                del value["category"]
                if "name" not in value:
                    skip = True
                    value_new = True
            elif key.endswith("or_monarch_power") or key.endswith("or_mil_power") or key.endswith("adm_power_per_stab") or key == "add_legitimacy_equivalent":
                if key == "add_stability_or_adm_power_per_stab":
                    key_new = "Add Convertible Stability"
                else:
                    key_new = "Add Convertible " + f"{key.replace('add_', '').replace('or_monarch_power', '').replace('or_mil_power', '').replace('equivalent', '').replace('_', '').title()}"
                value_new = int(dictionary[key]["amount"])
                skip = True
            elif key == "kill_leader":
                key_new = "Kill Leader"
                value_new = dictionary[key]["type"]
                skip = True
            elif (len(key) == 2 or len(key) == 3 or len(key) == 4) and key not in tag_provinces_checks and not any(".T" in k for k in value):
                key_new = loc_names.get(key) if key.isalpha() else loc_names.get(f"PROV{key}")
            elif key == "change_religious_influence_equivalent_fee":
                if "add" in dictionary[key]:
                    key_new = "Add Religious Influence"
                    value_new = dictionary[key]["add"]
                else:
                    key_new = "Remove Religious Influence"
                    value_new = dictionary[key]["remove"]
                skip = True
            elif key in ("country_event", "province_event"):
                key_new = "Event"
            elif any(key.endswith(k) for k in key_database_ends_map) or key == "basque_country":
                if "type" in value:
                    key_new = f"All Provinces in {loc_names.get(key)}"
                    del value["type"]
                    if ("owned_by" in value or "country_or_non_sovereign_subject_holds" in value) and len(value) == 1:
                        if "owned_by" in value:
                            key_new = f"{key_new} Owned by"
                            value_new = f"{loc_names.get(value['owned_by'])}"
                            del value["owned_by"]
                        else:
                            key_new = f"{key_new} Owned by"
                            value_new = f"{loc_names.get(value['country_or_non_sovereign_subject_holds'])} or its Non-Tributary Subjects"
                            del value["country_or_non_sovereign_subject_holds"]
                        skip = True
                else:
                    key_new = loc_names.get(key)
            elif key == "unlock_estate_privilege":
                key_new = key.replace("_", " ").title()
                value_new = loc_names.get(value["estate_privilege"])
                skip = True
            elif "estate" in key:
                if value["estate"] == "all":
                    if "change" in key or "add" in key:
                        key_new = f'{key.replace("_", " ").title().replace(" Estate", "")} To All Estates'
                    else:
                        key_new = key.replace("_", " ").title().replace("Estate", "All Estates")
                else:
                    key_new = f"{key.replace('_', ' ').title()}".replace("Estate", f"{loc_names.get(value['estate'])} Estate")
                if "loyalty" in value:
                    if "modifier" in key:
                        key_new = key_new.replace("Add", f"Add {value['loyalty']}").replace("Modifier", "For")
                        value_new = f"{value['duration']} Days"
                    else:
                        value_new = value["loyalty"]
                elif "influence" in value:
                    if "modifier" in key:
                        key_new = key_new.replace("Add", f"Add {value['influence']}").replace("Modifier", "For")
                        value_new = f"{value['duration']} Days"
                    else:
                        value_new = value["influence"]
                elif "share" in value:
                    value_new = value["share"]
                else:
                    value_new = True
                skip = True
            elif key == "spawn_rebels":
                key_new = key.replace("_", " ").title().replace("Rebels", f"{loc_names.get(value['type'])} of Size")
                if "leader" in value:
                    key_new = key_new.replace("of Size", f"Lead by {value['leader']} of Size")
                if "leader_dynasty" in value:
                    key_new = key_new.replace("of Size", f"of the {value['leader_dynasty']} Dynasty")
                key_new = key_new.replace(" of Size", "")
                value_new = f"Size {value['size']}"
                skip = True
            elif key == "add_institution_embracement":
                key_new = key.replace("_", " ").title().replace("Institution", f"{loc_names.get(value['which'])}")
                value_new = int(f"{value['value']}")
                skip = True
            elif key.startswith("event_target"):
                key_new = key.lower().replace("event_target_", "").replace("fee_", "").replace("_", " ").title()
            else:
                key_new = key.replace("_", " ").title()

            dictionary[key_new] = dictionary.pop(key)
            dictionary[key_new] = value_new if skip else recurse_process_dict(value, loc_names)

        elif isinstance(value, list):
            value_new = value
            if key in ("province_modifiers", "area_modifier", "region_modifier", "country_modifiers", "conditional_modifier", "can_upgrade_trigger"):
                key_new = "Monument Trigger" if key == "can_upgrade_trigger" else key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
            elif key in ("custom_trigger_tooltip", "variable_arithmetic_trigger"):
                if any("custom_tooltip" in item or "tooltip" in item for item in value):
                    value_new = []
                    for item in value:
                        if key == "custom_trigger_tooltip":
                            value_new.append(loc_names.get(item.get("tooltip")).replace("§R", "").replace("§Y", "").replace("§G", ""))
                        else:
                            value_new.append(loc_names.get(item.get("custom_tooltip")).replace("§R", "").replace("§Y", "").replace("§G", ""))
                        if '\\n' in value_new:
                            print(value_new)
                    if key == "custom_trigger_tooltip":
                        dictionary["Custom Trigger"] = value_new
                    else:
                        dictionary["Variable Arithmetic Trigger"] = value_new
                    del dictionary[key]
                continue
            elif key in key_database_unit:
                key_new = f"Create {len(value)} {loc_names.get(key) or key.replace('_', ' ').title()} For"
                value_new = loc_names.get(value[0])
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value_new
                continue
            elif (
                key in key_database or any(key.startswith(k) for k in key_database_start) or any(key.endswith(k) for k in key_database_ends)
            ) or any(
                isinstance(item, str) and item.startswith('disaster_fee') for item in value
            ) or key.startswith("owns") or key in key_flag_check:
                key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
                for i, values in enumerate(value):
                    if isinstance(values, dict):
                        dictionary[key_new][i] = recurse_process_dict(values, loc_names)
                    else:
                        if isinstance(values, int):
                            dictionary[key_new][i] = loc_names.get(f"PROV{values}")
                        elif values.startswith('disaster_fee'):
                            dictionary[key_new][i] = loc_names.get(f"{values.replace(',','')}.T").title()
                        elif key.endswith("building"):
                            dictionary[key_new][i] = loc_names.get(f"building_{values}")
                        elif key == "has_dlc":
                            dictionary[key_new][i] = values.replace("_", " ").title()
                        elif key in key_flag_check:
                            dictionary[key_new][i] = values.replace("_", " ").title().replace("Fee ", "")
                        else:
                            dictionary[key_new][i] = loc_names.get(values)
                continue
            elif key in ("government_abilities", "factions"):
                key_new = key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
                for i, values in enumerate(value):
                    dictionary[key_new][i] = loc_names.get(values) or values.replace("_", " ").title()
                continue
            else:
                key_new = key.replace("_", " ").title()
                dictionary[key_new] = dictionary.pop(key)
                key = key_new

            if len(value) != 0 and isinstance(value, dict):
                recurse_process_dict(value, loc_names)
            elif isinstance(value, list):
                for values in value:
                    if isinstance(values, dict):
                        recurse_process_dict(values, loc_names)

            continue

        else:  # value are always strings or numbers
            if isinstance(value, str) and is_numeric_string(value):  # forcing all the "numbers" to float/int
                if "." in value or "e" in value.lower():
                    value = float(value)
                else:
                    value = int(value)
                dictionary[key] = value

            value_new = value

            if key == "start":
                key_new = "Province"
                value_new = loc_names.get(f"PROV{value}")
            elif not key.endswith("idea_group") and (key.startswith("enables_") or key.startswith("enable_")):
                key_new = key.replace("_", " ").title()
                value_new = loc_names.get(f"mechanic_{key}_yes")
                if value_new is not None:
                    if ':' in value_new:
                        value_new = value_new.split(':')[1].strip()
                else:
                    value_new = key.replace("_", "").title()
            elif key == "starting_tier" or key in key_database or any(key.startswith(k) for k in key_database_start) or any(key.endswith(k) for k in key_database_ends):
                key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                if not isinstance(value, (bool, int, float)) and value != "all":
                    if key == "custom_tooltip":
                        key_new = loc_names.get(value) or value
                        key_new = key_new
                        value_new = True
                    elif key in ("has_dlc", "has_leader"):
                        value_new = value.replace("_", " ").title()
                    elif key.endswith("building"):
                        value_new = loc_names.get(f"building_{value}")
                    else:
                        value_new = loc_names.get(value)
            elif key == "tag":
                key_new = "Country"
            else:
                key_new = key.replace("_", " ").title()
                if isinstance(value, str):
                    if key in key_flag_check:
                        value_new = value.replace("_", " ").title().replace("Fee ", "")
                    elif key in key_localisation_check:
                        key_new = key.replace("_", " ").title()
                        value_new = value
                        if key in ("custom_tooltip", "tooltip"):
                            if len(dictionary[key]) < 2:
                                del dictionary[key]
                                continue
                            elif '_' in value and loc_names.get(value) is not None:
                                key_new = loc_names.get(value)
                                if '\\n' in key_new:
                                    tt_list = key_new.split("\\n")
                                    del dictionary[key]
                                    dictionary["Custom Tooltip"] = []
                                    for tt_split in tt_list:
                                        if len(tt_split) > 2:
                                            dictionary["Custom Tooltip"].append(tt_split)
                                    continue
                            else:
                                key_new = value.replace("_", " ").title()
                            value_new = True
                        elif key == "id":
                            value_new = loc_names.get(f"{value}.T")
                        else:
                            value_new = loc_names.get(value)
                    elif key == "save_event_target_as":
                        key_new = key.replace("_", " ").title()
                        value_new = value.lower().replace("event_target_", "").replace("fee_", "").replace("_", " ").title()
                    elif value.startswith('disaster_fee_') or value.startswith("FEE_"):
                        key_new = key.replace("_", " ").title()
                        value_new = loc_names.get(f"{value}.T")
                    elif key == "remove_advisor_by_category":
                        key_new = f"Fire {loc_names.get(value)} Adivsor"
                        value_new = True
                    else:
                        value_new = loc_names.get(value) or value
                else:
                    if key.upper() in ("ADM", "DIP", "MIL"):
                        key_new = loc_names.get(key)
                    else:
                        key_new = loc_names.get(key) or key.replace("_", " ").title()

            if key_new is None:
                key_new = key

            dictionary[key_new] = dictionary.pop(key)
            dictionary[key_new] = value_new

    return dictionary


def localise_reform_tiers(dictionary, loc_names):
    """localises the reform file's tiers"""
    counter = len(dictionary)
    for key, value in list(dictionary.items()):
        if counter == 4 and key == "Parliamentary Vs Presidential":
            key = "guiding_principle_of_administration"
        elif counter == 3 and key == "Regionalism":
            key = "electorate"
        elif counter == 2 and key == "State Economics":
            key = "office_selection"
        elif counter == 1 and key == "Consolidation Of Power":
            key = "question_of_dictatorship"
        elif counter == 1 and key == "Modernization":
            key = "tribal_reformation"
        elif counter == 4 and key == "agricultural_revolution":
            key = "story_tradition"
        elif counter == 3 and key == "legal_basis":
            key = "agricultural_revolution"
        elif counter == 2 and key == "national_identity":
            key = "legal_basis"
        elif counter == 1 and key == "Tribe Organization":
            key = "national_identity"
        elif counter == 6 and key == "Education Of The State":
            key = "economical_matters"
        elif counter == 5 and key == "Religious Doctrine":
            key = "divine_cause"
        elif counter == 4 and key == "Sacred War Organization":
            key = "separation_of_power_theocracy"
        elif counter == 3 and key == "Religious Enforcement":
            key = "nature_of_faith"
        elif counter == 2 and key == "Secularization?":
            key = "culture_within_the_state"
        elif counter == 1 and key == "Clergy In Administration":
            key = "faith_and_the_world"

        new_key = loc_names.get(key)

        if new_key.title() == "Military Doctrines And Organization":
            if "Feudalism Vs Autocracy" in dictionary:
                new_key = "Royal Military Organization"
            elif "Republican Virtues" in dictionary:
                new_key = "People's War Organization"
            elif "Religious Doctrine" in dictionary:
                new_key = "Sacred War Organization"
        elif new_key.title() == "Economical Matters":
            if "Feudalism Vs Autocracy" in dictionary:
                new_key = "Crown Economics"
            elif "Republican Virtues" in dictionary:
                new_key = "State Economics"
            elif "Religious Doctrine" in dictionary:
                new_key = "Divine Economics"
        elif new_key.title() == "Separation Of Power":
            if "Feudalism Vs Autocracy" in dictionary:
                new_key = "Separation Of Powers"
            elif "Republican Virtues" in dictionary:
                new_key = "Parliamentary vs Presidential"
            elif "Religious Doctrine" in dictionary:
                new_key = "Religious Separation"

        dictionary[new_key.title()] = dictionary.pop(key)

        counter = counter - 1

        if counter == 0:
            break

    return dictionary


def transform_multiple_entry(dictionary, value):
    if "add_country_modifier" in value:
        if "hie_ita_gpv_fanti_da_mar_modifier" in value["add_country_modifier"]["name"]:
            modifiers = {
                "Marines' Fire Damage": 0.10,
                "Marines' Shock Damage": 0.10,
                "Marines' Shock Damage Received": -0.10
            }
            dictionary.update(modifiers)
            return
        elif "hie_mer_the_legion_mewar_modifier" in value["add_country_modifier"]["name"]:
            modifiers = {
                "Rajput's Recover Morale Speed": 0.10,
                "Rajput's Regiment Manpower Usage": -0.10
            }
            dictionary.update(modifiers)
            return
    elif "HIE_SPA_AND_FUERO_JUZGO_TT" in value.get("custom_tooltip", ""):
        modifiers = {
            "Culture Group Provinces' Local Unrest": -2,
            "Culture Group Provinces' Local Tax": 0.15
        }
        dictionary.update(modifiers)
        return
    elif "HIE_SPA_ARA_UNION_OF_CROWNS_ITALY_TT" in value.get("custom_tooltip", "") or \
            "HIE_SPA_ARA_UNION_OF_CROWNS_IBERIA_TT" in value.get("custom_tooltip", ""):
        modifiers = {
            "Italian Provinces' Local Unrest": -2,
            "Italian Provinces' Defensiveness": 0.10,
            "Iberian Provinces' Local Unrest": -2,
            "Iberian Provinces' Local Autonomy": -0.025
        }
        dictionary.update(modifiers)
        return
    elif "HIE_PARLIAMENT_SEAT_DEV_GOVERNING_COST_TT" in value.get("custom_tooltip", ""):
        modifiers = {
            "Parliament Seat' Local Development Cost": -0.10,
            "Parliament Seat' Governing Cost Modifier": -0.15
        }
        dictionary.update(modifiers)
        return
    elif "HIE_COWRIE_TRADE_TT" in value.get("custom_tooltip", ""):
        modifiers = {
            "Western India Ocean Super Region' Trade Power": 0.15,
            "Western India Ocean Super Region' Trade Value": 0.15
        }
        dictionary.update(modifiers)
        return
    elif "HIE_RAJPUT_CLAN_SYSTEM_TT" in value.get("custom_tooltip", ""):
        modifiers = {
            "Rajput Provinces' Local Regiment Cost": -0.15,
            "Rajput Provinces' Local Recruitment Time": -0.15
        }
        dictionary.update(modifiers)
        return


def transform_singular_entry(key, value):
    if "duration" in value:
        if "hie_ven_fanti_mar_modifier" in value["name"]:
            return "Marines' Shock Damage", 0.10
        elif "hie_hol_soldaten_ter_zee_modifier" in value["name"]:
            return "Marines' Infantry Combat Ability", 0.10
        elif "hie_pga_braccio_montone_modifier" in value["name"]:
            return "Mercenaries' Shock Damage", 0.10
        elif "hie_grk_rajput_heritage_modifier" in value["name"]:
            return "Rajput's Regiment Manpower Usage", -0.15

    elif "admirals_give_army_professionalism_tt" in value:
        return "Army Professionalism gained from recruiting Admirals", 0.5
    elif "HIE_CORRUPTION_HIRING_GENERALS_TT" in value:
        return "Corruption lose when hiring a general", -0.1

    elif "HIE_RAG_ABOLITION_SLAVERY_TT" in value:
        return "This will result in the Abolition of Slavery", True

    elif "HIE_ATTRITION_IN_HILLS_HIGHLANDS_MOUNTAINS_TT" in value:
        return "Highlands, Hills and Mountains' Hostile Attrition", 3

    elif "HIE_DEV_COST_REDUCTION_IN_ARCTIC_TT" in value:
        return "Arctic Provinces's Development Cost", -0.30
    elif "HIE_DEV_COST_REDUCTION_IN_ARID_TT" in value:
        return "Arid Provinces's Development Cost", -0.15
    elif "HIE_DEV_COST_REDUCTION_IN_DRYLANDS_TT" in value:
        return "Drylands Provinces's Development Cost", -0.15
    elif "HIE_DEV_COST_REDUCTION_IN_DESERT_TT" in value:
        return "Desert Provinces's Development Cost", -0.15
    elif "HIE_DEV_COST_REDUCTION_IN_HILLS_HIGHLANDS_MOUNTAINS_TT" in value:
        return "Highlands, Hills and Mountains' Development Cost", -0.20
    elif "HIE_DEV_COST_REDUCTION_IN_JUNGLE_TT" in value:
        return "Jungle Provinces's Development Cost", -0.15
    elif "HIE_DEV_COST_REDUCTION_IN_JUNGLE_STRONG_TT" in value:
        return "Jungle Provinces's Development Cost", -0.25
    elif "HIE_DEV_COST_REDUCTION_IN_METAL_PROVS_TT" in value:
        return "Metal Provinces' Development Cost", -0.15
    elif "HIE_DEV_COST_REDUCTION_IN_STEPPE_TT" in value:
        return "Steppe Provinces's Development Cost", -0.25
    elif "HIE_DEV_COST_REDUCTION_IN_TROPIC_TT" in value:
        return "Tropical Provinces's Development Cost", -0.10

    elif "HIE_GOODS_PRODUCED_IN_LIVESTOCK_PROVS_UPDATE_TT" in value:
        return "Livestock Provinces' Goods Produced", 0.5
    elif "HIE_GOODS_PRODUCED_IN_METAL_PROVS_TT" in value:
        return "Metal Provinces' Goods Produced Modifier", 0.10
    elif "HIE_GOODS_PRODUCED_IN_SILK_PROVS_UPDATE_TT" in value:
        return "Silk Provinces' Goods Produced", 1

    elif "HIE_GOV_COST_REDUCTION_IN_PRUSSIAN_PROVINCES_TT" in value:
        return "Prussian Provinces' Governing Cost", -0.15
    elif "HIE_ITA_SAR_STATUTE_SABAUDIAE_TT" in value:
        return "Latin Provinces' Governing Cost", -0.15
    elif "HIE_GOV_COST_REDUCTION_IN_PRIMARY_CULTURE_PROVINCES_TT" in value:
        return "Primary Culture's Governing Cost", -0.10

    elif "HIE_SPA_BAS_REVITALIZE_CANTABRIAN_SHIPYARDS_TT" in value:
        return "Iberian Naval Supplies Provinces' Trade Goods", 0.50
    elif "HIE_SPA_GAL_ASIENTO_SYSTEM_TT" in value:
        return "Colonial Subjects' Trade Goods Modifier", 0.10

    elif "HIE_SPA_GAL_MODERNIZED_CAMINO_REAL_TT" in value:
        return "Expanded Infrastructure Provinces' Local Tax", 0.15

    elif "HIE_TUS_THORNTON_EXPEDITION_TT" in value:
        return "Colonial Colombia's Local Settler Increase", 25
    elif "HIE_MEXICAN_COLONIAL_GROWTH_TT" in value:
        return "Colonial Mexico's Local Settler Increase", 20

    elif "HIE_ITA_CULLA_RINASCIMENTO_TT" in value:
        return "Italy Provinces' Construction Cost", -0.10
    elif "HIE_BUILD_COST_REDUCTION_IN_JUNGLE_TT" in value:
        return "Jungle Provinces' Construction Cost", -0.10

    elif "HIE_ITA_MFV_STELLA_FORTE_TT" in value:
        return "Chance of Lux Stella on new heirs", 0.02

    elif "HIE_EIC_E_I_C_RESIDENCY_TT" in value:
        return "Vassal Acceptance when independent", 15

    elif "HIE_ITA_CRU_DIO_LO_VUOLE_TT" in value:
        return "Years of Manpower recovered in Religious War won", 1

    elif "HIE_ENEMY_MOVEMENT_SPEED_IN_OWNED_PROVS_TT" in value:
        return "Provinces's Hostile Movement Speed ", -0.25

    elif "HIE_NAG_DEOGARH_FORT_TT" in value:
        return "Capital's Fort Level", 1
    elif "HIE_MEW_ALWAR_TT" in value:
        return "Capital's Goods Produced", 2

    elif "HIE_GWA_LAND_OF_THE_ANCIENTS_TT" in value:
        return "Gird's Area Development Cost", -0.15

    elif "HIE_TRADE_VALUE_IN_HILL_UPDATE_TT" in value:
        return "Hill Provinces' Trade Value", 0.15
    elif "HIE_TRADE_POWER_IN_HIGHLANDS_HILLS_MOUNTAINS_UPDATE_TT" in value:
        return "Highlands, Hills and Mountains' Trade Power", 0.15

    elif "enable_baseline_invite_scholar_tt" in value:
        return "Grants Permament residence of a Scholar", True


def parse_correct_json(dictionary_to_fix):
    """Builds the corretc json"""
    dict_corrected = {}

    # Replace the old keys with the new keys
    for event_name, event_data in list(dictionary_to_fix.items()):
        if "country_event" in dictionary_to_fix[event_name] and "province_event" in dictionary_to_fix[event_name]:
            country_events = dictionary_to_fix[event_name]["country_event"]
            province_events = dictionary_to_fix[event_name]["province_event"]

            # Ensure country_events and province_events are lists
            country_events = [country_events] if isinstance(country_events, dict) else country_events
            province_events = [province_events] if isinstance(province_events, dict) else province_events

            combined_events = natsorted(country_events + province_events, key=lambda x: list(x.values())[0])

            del dictionary_to_fix[event_name]["country_event"]
            del dictionary_to_fix[event_name]["province_event"]
            dictionary_to_fix[event_name]["combined_event"] = combined_events
        # Check if the event name needs to be replaced
        if "disaster_" in event_name:
            event_name = event_name.split("disaster_")[1]
            if event_name in dict_localisation:
                event_name = f"Disaster: {dict_localisation[event_name]}"
            if event_name == "fee_naples_conspiracy_barons":
                event_name = "Disaster: Conspiracy of the Barons"
        else:
            if len(dictionary_to_fix[event_name]) == 0:
                continue
            event_name = event_name.split("FEE_")[1].split("_Events")[0].replace("_", " ").title()

        dict_corrected[event_name] = {}
        for event_type in {"country_event", "province_event", "combined_event"}:
            if event_type in event_data:
                events = event_data[event_type]
                if isinstance(events, list):
                    for event in events:
                        if "hidden" in event and event["hidden"]:
                            continue
                        dict_corrected[event_name].update(process_event(event, event["title"]))
                else:
                    if "hidden" in events and events["hidden"]:
                        continue
                    dict_corrected[event_name].update(process_event(events, events["title"]))

    # with open("FEE.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_corrected, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("\tSuccesfully created the correct Json")

    return dict_corrected


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
            if value_duration == -1:
                if add_ruler_modifier:
                    value_modifier["Expires"] = "On Ruler's Death"
                elif add_disaster_modifier:
                    value_modifier["Expires"] = "On Disaster's End"
                else:
                    if 'desc' in value_modifier:
                        value_modifier["Expires"] = dict_localisation.get(value_modifier['desc'])
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


def is_numeric_string(s):
    return re.match(r"^[-+]?\d*\.?\d+$", s) is not None


def JsonParser(data_input):

    data_json = data_input

    if "FEE_Vijayanagar_Events.1.OPT1" in data_json:
        filename = "Events"
        data_json = re.sub(r"'", "", data_json)
    elif "fee_naples_conspiracy_barons_1" in data_json:
        filename = "Disasters"
    elif "000_HIE_country_ideas" in data_json:
        filename = "Ideas"
    elif "gme_" in data_json:
        filename = "Monuments"
        data_json = re.sub(r"\n\t\tdate = 1.01.01", "", data_json)
    elif "_governments.txt" in data_input:
        filename = "Tiers"
    elif "" in data_input:
        filename = "Reforms"
    else:
        filename = "EventModifiers"

    if "\\" in data_input:
        try:
            with open(data_input, "r") as file:
                data_json = file.read()
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {data_input}")
            return None

    data_json = re.sub(r"#.*", "", data_json)  # Remove comments
    data_json = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data_json,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data_json = re.sub(r'"([^"]*)"', lambda m: m.group(0).replace(' ', '__SPACE__'), data_json)  # Temporarily protect spaces inside quotes
    data_json = re.sub(r'[\t ]+', '', data_json)  # Remove all tabs and spaces globally
    data_json = re.sub(r'__SPACE__', ' ', data_json)  # Restore the spaces inside quotes

    if definitions := re.findall(r"(@\w+)=(.+)", data_json):  # replace @variables with value
        for definition in definitions:
            data_json = re.sub(r"^@.+", "", data_json, flags=re.MULTILINE)
            data_json = re.sub(definition[0], definition[1], data_json)

    data_json = re.sub(r"\n{2,}", "\n", data_json)  # Remove excessive new lines
    data_json = re.sub(r"\n", "", data_json, count=1)  # Remove the first new line
    data_json = re.sub(r"{(?=\w)", "{\n", data_json)  # reformat one-liners
    data_json = re.sub(r"(?<=\w)}", "\n}", data_json)  # reformat one-liners
    data_json = re.sub(r"^[\w-]+(?=[\=\n><])", r'"\g<0>"', data_json, flags=re.MULTILINE)  # Add quotes around keys
    data_json = re.sub(
        r"(\=\s?)(?!-1$)(\d[\w.-]*[a-zA-Z]{2,}[\w.-]*)",  # Match numbers followed by at least two letters, but not `-1`
        r'\1"\2"',  # Add quotes around the matched value
        data_json
    )  # Add quotes around values starting with a number on the right side of '='
    data_json = re.sub(r"([^><])=", r"\1:", data_json)  # Replace = with : but not >= or <=
    data_json = re.sub(
        r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{},\n]+",
        r'"\g<0>"',
        data_json,
    )  # Add quotes around string values
    data_json = re.sub(r':"yes"', ":true", data_json)  # Replace yes with true
    data_json = re.sub(r':"no"', ":false", data_json)  # Replace no with false
    data_json = re.sub(r"([<>]=?)(.+)", r':{"value":\g<2>,"operand":"\g<1>"}', data_json)  # Handle < > >= <=
    data_json = re.sub(r"(?<![:{])\n(?!}|$)", ",", data_json)  # Add commas
    # data_json = re.sub(r"\s", "", data_json)  # remove all white space
    data_json = re.sub(r'{(("[a-zA-Z_]+")+)}', r"[\g<1>]", data_json)  # make lists
    data_json = re.sub(r'""', r'","', data_json)  # Add commas to lists
    data_json = re.sub(r'{("\w+"(,"\w+")*)}', r"[\g<1>]", data_json)
    data_json = re.sub(r"((\"hsv\")({\d\.\d{1,3}(,\d\.\d{1,3}){2}})),", r"{\g<2>:\g<3>},", data_json)  # fix hsv objects
    data_json = re.sub(r":{([^}{:]*)}", r":[\1]", data_json)  # if there's no : between list elements need to replace {} with []
    data_json = re.sub(r"\[(\w+)\]", r'"\g<1>"', data_json)
    data_json = re.sub(r"\",:{", '":{', data_json)  # Fix user_empire_designs
    data_json = "{" + data_json + "}"

    try:
        json_data = json.loads(data_json, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {filename}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(filename, time.time()))

        with open("./output/{}_{:.0f}.intermediate".format(filename, time.time()), "w") as output:
            output.write(data_json)

        return None

    # with open(f"{filename.json", "w") as file:
    #     json.dump(json_data, file, indent="\t")  # , separators=(",", ": "), ensure_ascii=False) #) #, sort_keys=True)
    print(f"\tParsed the {filename} into Json")

    return json_data


def _handle_duplicates(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if isinstance(d[k], list):
                d[k].append(v)
            else:
                d[k] = [d[k], v]
        else:
            d[k] = v
    return d


start()
