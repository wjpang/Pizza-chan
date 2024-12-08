import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
if "\\" in os.getcwd():
    MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
# eu4_dir = r'C:\Program Files\Epic Games\EuropaUniversalis4' # This is for EGS
else:
    MOD_PATH = r"/home/atimpone/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Europa Universalis IV"

GOV_REF_DIR = os.path.join(MOD_PATH, "common", "government_reforms")
LOC_DIR = os.path.join(MOD_PATH, "localisation")

path = os.path.abspath(os.path.join(os.getcwd()))  # debugging-tools
path_final = os.path.join(os.path.dirname(path), "data")

database = os.path.join(path, "database.json")
provinces = os.path.join(path, "provinces.json")
tags = os.path.join(path, "tags.txt")

vanilla_ideas_b4_json = os.path.join(MOD_PATH, "common", "ideas", "00_country_ideas.txt")
vanilla_monuemnts_b4_json = os.path.join(MOD_PATH, "common", "great_projects", "01_monuments.txt")
vanilla_government_reformm_b4_json = os.path.join(MOD_PATH, "common", "governments", "00_governments.txt")
vanilla_reforms_b4_json = glob.glob(os.path.join(GOV_REF_DIR, "*.txt"))

dict_vanilla = {}
dict_loc = {}
dict_reform = {}
dict_new = {}

with open(database, "r", encoding="utf-8") as file:
    loc_datas = json.load(file)

with open(provinces, "r", encoding="utf-8") as file:
    loc_provinces = json.load(file)


def start():

    create_localisation()

    ideas()

    monuments()

    reforms()


def create_localisation():
    localisation_files = glob.glob(os.path.join(LOC_DIR, "*l_english.yml"))

    for file in localisation_files:
        with open(file, "r", encoding="utf-8-sig") as f:
            loc = f.readlines()
        for line in loc:
            line = line.strip()
            if line.startswith("#") or line == "" or line == "l_english:" or line.startswith("PROV"):
                continue
            line = line.split(":", 1)
            line[1] = line[1].replace('"', "").strip()
            if line[1] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                line[1] = ""
            if line[1] != "" and line[1][0] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"} and line[1][1] == " ":  # Remove numbers at the beginning of the string
                line[1] = line[1][2:]
            dict_loc[line[0]] = line[1].title()

    dict_loc["start"] = "Traditions"
    dict_loc["bonus"] = "Ambition"
    dict_loc["enables_nepotism"] = "Can re-elect from ruling family."
    dict_loc["enables_estate_janissaries"] = "Enables Janissaries estate"
    dict_loc["enables_pronoias"] = "'May establish Pronoia Subjects."
    dict_loc["enables_recruit_foreign_generals"] = "Enables the Recruit Foreign General Diplomatic Action"
    dict_loc["enables_timurid_diwan"] = "We will receive additional modifiers based on our current National Focus"
    dict_loc["enables_estate_church"] = "Enables Clergy estate."
    dict_loc["enables_estate_burghers"] = "Enables Burghers estate."
    dict_loc["NEEDS_REGULAR_ELECTIONS"] = "Ruler must not rule for life."
    dict_loc["enables_estate_cossacks"] = "Enables Cossacks estate."
    dict_loc["MUST_BE_IN_TRIBAL_LAND_TO_SETTLE"] = "Must be in Tribal Land to settle."
    dict_loc["NEEDS_NATIVE_SPONSOR"] = "Neighboring country to reform off."
    dict_loc["enables_estate_nobles"] = "Enables Nobles estate."
    dict_loc["feudalism_vs_autocracy"] = "Feudalism Vs Autocracy"

    print("Created the Localisation Dictionary")


def ideas():
    print("Creating the Idea Json")
    JsonParser(vanilla_ideas_b4_json)
    # create_localisation(LOC_DIR)

    dict_final = recursive_process_ideas_dict(dict_vanilla, loc_datas)

    with open(os.path.join(path_final, "Vanilla_ideas.json"), "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Succesfully created the Ideas Json")


def monuments():
    print("Creating the Monument Json")
    JsonParser(vanilla_monuemnts_b4_json)
    # create_localisation(LOC_DIR)

    dict_final = recursive_process_monument_dict(dict_vanilla, dict_loc, loc_datas, loc_provinces)

    with open(os.path.join(path_final, "Vanilla_monuments.json"), "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("Succesfully created the Monuments Json")


def reforms():
    print("Creating the Reform Json")
    JsonParser(vanilla_government_reformm_b4_json)
    merging_reforms(vanilla_reforms_b4_json)
    build_correct_json()
    # create_localisation(LOC_DIR)

    dict_final = recrusive_process_reform_dict(dict_new, dict_loc, loc_datas)

    with open(os.path.join(path_final, "Vanilla_reforms.json"), "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("succesfully created the Reform Json")


def recursive_process_ideas_dict(dictionary, loc_datas):
    for key, value in list(dictionary.items()):
        if key in ("free", "trigger"):
            del dictionary[key]
            continue

        if key.endswith("_ideas") or key.endswith("_Ideas") or key.endswith("_ideas_2"):
            if key == "CHICK_ideas":
                key_new = "CHI"
            elif key == "CHI_ideas":
                key_new = "MNG"
            elif key == "ERANSHAHR_ideas":
                key_new = "ERS"
            elif key == "fulani_jihad_ideas":
                key_new = "SOK"
            elif key == "hausa_ideas":
                key_new = "KTS"
            elif key == "irish_ideas":
                key_new = "IRE"
            elif key == "jerusalem_ideas":
                key_new = "KOJ"
            elif key == "samoan_ideas":
                key_new = "SAM"
            elif key == "tongan_ideas":
                key_new = "TOG"
            elif key == "voc_ideas":
                key_new = "VOC"
            elif key == "VEN_ideas_2":
                key_new = "VEN2"
            else:
                key_new = key
            key_new = loc_datas.get(key_new.replace("_ideas", "").replace("_Ideas", ""))
            dictionary[key_new] = dictionary.pop(key)
            value_new = dictionary[key_new]
            recursive_process_ideas_dict(value_new, loc_datas)
        elif key == "effect":
            key_new = key.replace("_", " ").title()
            if "custom_tooltip" in value:
                if "admirals_give_army_professionalism_tt" in value["custom_tooltip"]:
                    key_new = "Recruiting Admirals grants 0.5% Army Professionalism"
                    del dictionary[key]["custom_tooltip"]
                    del dictionary[key]["set_country_flag"]
            else:
                del dictionary[key]
                continue
                key_new = "Remove Temporary Colonist"
            value_new = True
        elif isinstance(key, str) and isinstance(value, (dict, list)):
            key_new = dict_loc.get(key)
            dictionary[key_new] = dictionary.pop(key)
            if isinstance(value, dict):
                value_new = recursive_process_ideas_dict(dictionary[key_new], loc_datas)
            else:
                value_new = value
            dictionary[key_new] = value_new
        else:
            key_new = loc_datas.get(key)
            value_new = value

        if key in dictionary:
            dictionary[key_new] = dictionary.pop(key)
            dictionary[key_new] = value_new

    return dictionary


def recursive_process_monument_dict(dictionary, loc_names, loc_datas, loc_provinces):
    global check

    for key, value in list(dictionary.items()):
        if key in (
            "build_cost",
            "build_trigger",
            "can_be_moved",
            "can_use_modifiers_trigger",
            "cost_to_upgrade",
            "keep_trigger",
            "move_days_per_unit_distance",
            "on_built",
            "on_destroyed",
            "on_upgraded",
            "tier_0",
            "time",
            "type",
            "upgrade_time",
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
                if key == "can_upgrade_trigger":
                    key_new = "Monument Trigger"
                elif "tier_1" in value:
                    key_new = loc_names.get(key)
                else:
                    key_new = key.replace("_", " ").title()
                    if key == "custom_trigger_tooltip":
                        key_new = loc_names.get(dictionary[key]["tooltip"])
                        value = True
                        dictionary[key_new] = dictionary.pop(key)
                        dictionary[key_new] = value
                        continue
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value
                key = key_new
                recursive_process_monument_dict(value, loc_names, loc_datas, loc_provinces)
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
                        recursive_process_monument_dict(value, loc_names, loc_datas, loc_provinces)
                    elif isinstance(value, list):
                        for values in value:
                            if isinstance(values, dict):
                                recursive_process_monument_dict(values, loc_names, loc_datas, loc_provinces)
            elif isinstance(key, str):
                if key == "start":
                    key_new = "Province"
                    value_new = loc_provinces.get(str(value))
                else:
                    if isinstance(value, bool) or key == "starting_tier" or any(key_localisation_check):
                        key_new = key.replace("_", " ").title()
                    else:
                        key_new = loc_datas.get(key)
                    value_new = loc_datas.get(value)
                if key_new is None:
                    key_new = key
                if value_new is None:
                    value_new = value
                dictionary[key_new] = dictionary.pop(key)
                dictionary[key_new] = value_new
                key = key_new
                value = value_new

    return dictionary


def recrusive_process_reform_dict(dictionary, dict_loc, loc_datas):
    """Final parser"""
    for key, value in list(dictionary.items()):
        if isinstance(value, str) and 'Lions' in value:
            print(key, value)
        if key in {
            "icon",
            "legacy_equivalent",
            "allow_normal_conversion",
            "valid_for_nation_designer",
            "nation_designer_trigger",
            "nation_designer_cost",
            "ai",
            "hidden_effect",
            "effect",
            "removed_effect",
            "assimilation_cultures",
        }:  # noqa
            del dictionary[key]
        else:
            key_localisation_check = [
                key == "primary_culture"
                or key == "add_building"
                or key == "add_ruler_personality"
                or key == "advisor"
                or key == "accepted_culture"
                or key == "change_culture"
                or key == "change_trade_goods"
                or key == "current_age"
                or key == "custom_tooltip"
                or key == "disaster"
                or key == "has_building"
                or key == "has_country_modifier"
                or key == "has_dlc"
                or key == "has_idea_group"
                or key == "full_idea_group"
                or key == "has_reform"
                or key == "remove_building"
                or key == "remove_country_modifier"
                or key == "ruler_has_personality"
                or key == "tag"
                or key == "technology_group"
                or key == "trade_goods"
                or key == "trait"
                or key == "was_tag"
                or key.startswith("area")
                or key.startswith("continent")
                or (key.startswith("culture") and not key.startswith("culture_conversion"))
                or key.startswith("owned_by")
                or key.startswith("region")
                or key.startswith("religion")
                or key.startswith("superregion")
            ]

            if (
                key
                in {
                    "monarchy",
                    "republic",
                    "tribal",
                    "native",
                    "theocracy",
                    "modifiers",
                    "custom_attributes",
                    "potential",
                    "trigger",
                    "conditional",
                    "check_variable",
                    "change_variable",
                    "allow",
                    "government_abilities",
                    "effect",
                    "removed_effect",
                    "post_removed_effect",
                }
                or "_opinion" in key
                or "country_modifier" in key
            ):
                localized_name = key.replace("_", " ").title()
                if key in {"monarchy", "republic", "tribal", "native", "theocracy"}:
                    value = localise_reform_tiers(value, dict_loc)
                dictionary[localized_name] = dictionary.pop(key)
                key = localized_name
            elif any(key_localisation_check):
                key_new = "Country" if key == "tag" else key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                if not isinstance(value, (list, dict)) and (key == "custom_tooltip"):
                    localized_name = dict_loc.get(value) or value.replace("_", " ").title()
                    dictionary[key_new] = localized_name
                elif isinstance(value, dict):
                    continue
                elif isinstance(value, list):
                    for i, values in enumerate(value):
                        if key.replace("_", " ").title() == "Has Dlc":
                            localized_data = loc_datas.get(f"{values}DLC")
                        else:
                            localized_data = loc_datas.get(values) or values.replace("_", " ").title()
                        dictionary[key_new][i] = localized_data
                else:
                    if key.replace("_", " ").title() == "Has Dlc":
                        localized_data = loc_datas.get(f"{value}DLC")
                    else:
                        localized_data = loc_datas.get(value) or value.replace("_", " ").title()
                    dictionary[key_new] = localized_data
            if isinstance(value, dict):
                if key == "custom_trigger_tooltip":
                    key_new = dict_loc.get(dictionary[key]["tooltip"])
                    value = True
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value
                    continue
                elif key == "has_unlocked_government_reform":
                    value_new = dict_loc.get(dictionary[key]["government_reform"])
                    key_new = key.replace("_", " ").title()
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                elif "modifiers" in value or "Modifiers" in value:
                    localized_name = dict_loc.get(key) or key.replace("_", " ").title()
                    dictionary[localized_name] = dictionary.pop(key)
                    key = localized_name
                recrusive_process_reform_dict(value, dict_loc, loc_datas)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, (list, dict)) and len(item) > 1:
                        recrusive_process_reform_dict(item, dict_loc, loc_datas)
            else:
                if value and key.startswith("enables_") and not key.endswith("idea_group"):
                    if dict_loc.get(key) is not None and ":" in dict_loc.get(key):
                        key_new, value_new = dict_loc.get(key).split(":")
                    else:
                        key_new = dict_loc.get(key)
                else:
                    key_new = loc_datas.get(key)
                if key_new is None or "_" in key_new:
                    key_new = key.replace("_", " ").title()
                if isinstance(value, str) and value.title().endswith("Influence"):
                    value_new = value.replace("_", " ").title()
                elif dict_loc.get(value) != "" and key_new.replace("_", " ").title() in (
                    "Has Reform",
                    "Have Had Reform",
                    "Remove Country Modifier",
                    "Add Country Modifier",
                    "Modifier",
                    "Remove Country Modifier",
                    "Name",
                    "Hase Estate Privilege",
                    "Mission Completed",
                ):
                    key_new = key.replace("_", " ").title()
                    if key_new == "Mission Completed":
                        value_new = dict_loc.get(f"{value}_title")
                    else:
                        if "_" in value:
                            value_new = dict_loc.get(value)
                        else:
                            value_new = value
                elif key_new in ("Has Country Flag", "Has Global Flag"):
                    value_new = value.replace("_", " ").title()
                else:
                    value_new = value
                if key in dictionary:
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new

    return dictionary


def localise_reform_tiers(dictionary, dict_loc):
    """localises the reform file's tiers"""
    counter = len(dictionary)
    for key in dictionary:
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
        elif counter == 4 and key == "Secularization?":
            key = "separation_of_power_theocracy"
        elif counter == 3 and key == "Clergy In Administration":
            key = "nature_of_faith"
        elif counter == 2 and key == "Divine Economics":
            key = "culture_within_the_state"
        elif counter == 1 and key == "Divine Cause":
            key = "faith_and_the_world"

        new_key = dict_loc.get(key)

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


def process_key_sub(key_sub, localisation_files, dict_loc):
    for filename in localisation_files:
        if len(dict_loc[key_sub]) > 1:
            break
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                if ":" in line:
                    line_key_sub, line_value = line.split(":", 1)
                    if line_key_sub.strip() == key_sub:
                        if ":" in line_value:
                            line_value = line_value.split(":", 1)[-1].strip()
                        if line_value.startswith(("0", "1")):
                            line_value = line_value[1:]
                        dict_loc[key_sub] = line_value.strip().replace('"', "").replace(",", "").title()
                        break


def merging_reforms(goverment_reforms):
    """Merges all Government Reforms from GE's files into one json"""
    reforms_merged_txt = ""

    for reform_file in goverment_reforms:
        with open(reform_file, "r+", encoding="utf-8") as reading_reforms:
            for i, line_reform in enumerate(reading_reforms):
                if line_reform.strip().startswith("#") or len(line_reform) < 2 and line_reform != "}" or line_reform.strip().startswith("picture"):
                    continue
                line_reform = line_reform.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
                reforms_merged_txt += line_reform
                line_reform = line_reform.strip()
                if (
                    "{" not in line_reform
                    and line_reform.startswith("modifier =")
                    or line_reform.startswith("government_reform =")
                    or line_reform.startswith("has_estate_privilege =")
                    or line_reform.startswith("have_had_reform =")
                    or line_reform.startswith("mission_completed =")
                    or line_reform.startswith("name = ")
                    or line_reform.startswith("tooltip =")
                    or (line_reform.endswith("yes") and line_reform.startswith("enables_") and not line_reform.endswith("idea_group = yes"))
                ):
                    if line_reform.endswith("= yes"):
                        line_reform = line_reform.split("=")[0].strip()
                    elif line_reform.startswith("mission_completed"):
                        line_reform = line_reform.split("=")[1].strip() + "_title"
                    else:
                        line_reform = line_reform.split("=")[1].strip()
                    line_reform = line_reform.replace("\"", "").replace("\'", "")
                    if line_reform not in dict_loc:
                        print(f"\t\tnot in dict loc: {line_reform}")
                        dict_loc[line_reform] = ""
        reforms_merged_txt += "\n"

    print("\tMerged all Government Reforms into one file")

    JsonParser(reforms_merged_txt)
    print("\tJsonised the Government Reforms")


def build_correct_json():
    """Final Build"""
    for key, value in dict_vanilla.items():
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

    print("\tConstructed the correct Reform Json")

    # with open("VanillaReform.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_new, output, indent="\t", separators=(",", ": "), ensure_ascii=False)


def JsonParser(vanilla_file_input):
    global dict_vanilla
    global dict_reform

    if "\\" in vanilla_file_input or "/home/" in vanilla_file_input:
        try:
            with open(vanilla_file_input, "r") as file:
                data = file.read()
            file_name = basename(vanilla_file_input)
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {vanilla_file_input}")
            return None
    else:
        data = vanilla_file_input
        file_name = "govRef.txt"

    if "monuments" in file_name:
        data = re.sub(r"^\tdate.*", "", data, flags=re.MULTILINE)
    else:
        data = data

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"free=yes", "", data)

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
        r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{\n]+",
        r'"\g<0>"',
        data,
    )  # Add quotes around string values
    data = re.sub(r':"yes"', ":true", data)  # Replace yes with true
    data = re.sub(r':"no"', ":false", data)  # Replace no with false
    data = re.sub(r"([<>]=?)(.+)", r':{"value":\g<2>,"operand":"\g<1>"}', data)  # Handle < > >= <=
    data = re.sub(r"(?<![:{])\n(?!}|$)", ",", data)  # Add commas
    data = re.sub(r"\s", "", data)  # remove all white space
    data = re.sub(r'{(("[a-zA-Z_]+")+)}', r"[\g<1>]", data)  # make lists
    data = re.sub(r'""', r'","', data)  # Add commas to lists
    data = re.sub(r'{("\w+"(,"\w+")*)}', r"[\g<1>]", data)
    data = re.sub(r"((\"hsv\")({\d\.\d{1,3}(,\d\.\d{1,3}){2}})),", r"{\g<2>:\g<3>},", data)  # fix hsv objects
    data = re.sub(r":{([^}{:]*)}", r":[\1]", data)  # if there's no : between list elements need to replace {} with []
    data = re.sub(r"\[(\w+)\]", r'"\g<1>"', data)
    data = re.sub(r"\",:{", '":{', data)  # Fix user_empire_designs
    data = "{" + data + "}"

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open("./output/{}_{:.0f}.intermediate".format(file_name, time.time()), "w") as output:
            output.write(data)

        return None

    if "\\" in vanilla_file_input or "/home/" in vanilla_file_input:
        dict_vanilla = json_data
    else:
        dict_reform = json_data

    # with open(f"{file_name[:-4]}.json", "w") as file:
    #    json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("\tSuccessfully created the starting json file")


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
