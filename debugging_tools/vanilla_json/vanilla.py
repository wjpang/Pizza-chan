import datetime
import glob
import json
import os
import re
import time
from os.path import basename

MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
# eu4_dir = r'C:\Program Files\Epic Games\EuropaUniversalis4' # This is for EGS
GOV_REF_DIR = MOD_PATH + r"\common\government_reforms"
LOC_DIR = MOD_PATH + r"\localisation"

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\Vanilla_ideas.json"

provinces = parent + "\\provinces.json"
tags = parent + r"\\tags.txt"
database = parent + r"\database.txt"

vanilla_ideas_b4_json = MOD_PATH + r"\common\ideas\00_country_ideas.txt"
vanilla_monuemnts_b4_json = MOD_PATH + r"\common\great_projects\01_monuments.txt"
vanilla_government_reformm_b4_json = MOD_PATH + r"\common\governments\00_governments.txt"
vanilla_reforms_b4_json = glob.glob(GOV_REF_DIR + r"\*.txt")

dict_vanilla = {}
dict_loc = {}
dict_reform = {}
dict_new = {}

loc_datas = {}
with open(database, "r", encoding="utf-8") as file:
    localized_datas = json.load(file)

with open(provinces, "r", encoding="utf-8") as file:
    loc_provinces = json.load(file)


def start():

    # ideas()

    monuments()

    # reforms()


def ideas():
    JsonParser(vanilla_reforms_b4_json)
    create_localisation(LOC_DIR)

    dict_final = recursive_process_ideas_dict(dict_vanilla, loc_datas)

    with open(f"{os.path.dirname(finalpath)}\\Vanilla_ideas.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("succesfully created the Ideas Json")


def monuments():
    JsonParser(vanilla_monuemnts_b4_json)
    create_localisation(LOC_DIR)

    dict_final = recursive_process_monument_dict(dict_vanilla, dict_loc, loc_datas, loc_provinces)

    with open(f"{os.path.dirname(finalpath)}\\Vanilla_monuments.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("succesfully created the Monuments Json")


def reforms():
    JsonParser(vanilla_government_reformm_b4_json)
    merging_reforms(vanilla_reforms_b4_json)
    build_correct_json()
    create_localisation(LOC_DIR)

    dict_final = recrusive_process_reform_dict(dict_new, dict_loc, loc_datas)

    with open(f"{os.path.dirname(finalpath)}\\Vanilla_reforms.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)

    print("succesfully created the Reform Json")


def recursive_process_ideas_dict(dictionary, loc_datas):
    for key, value in list(dictionary.items()):
        if key in ("free", "trigger"):
            del dictionary[key]
            continue

        if key.endswith("_ideas"):
            key_new = key
            if key == "jerusalem_ideas":
                key_new = "KOJ"
            elif key == "irish_ideas":
                key_new = "IRE"
            elif key == "ERANSHAHR_ideas":
                key_new = "ERS"
            elif key == "fulani_jihad_ideas":
                key_new = "SOK"
            elif key == "CHI_ideas":
                key_new = "MNG"
            elif key == "hausa_ideas":
                key_new = "KTS"
            elif key == "tongan_ideas":
                key_new = "TOG"
            elif key == "samoan_ideas":
                key_new = "SAM"
            elif key == "CHICK_ideas":
                key_new = "CHI"
            key_new = key_new.replace("_ideas", "")
            key_new = loc_datas.get(key_new)
            dictionary[key_new] = dictionary.pop(key)
            value_new = dictionary[key_new]
            recursive_process_ideas_dict(dictionary[key_new], loc_datas)
        elif key == "effect":
            key_new = key.replace("_", " ").title()
            if "custom_tooltip" in value:
                if "admirals_give_army_professionalism_tt" in value["custom_tooltip"]:
                    key_new = "Recruiting Admirals grants 0.5% Army Professionalism"
                    del dictionary[key]["custom_tooltip"]
                    del dictionary[key]["set_country_flag"]
            else:
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
                    if key.endswith('religion_group'):
                        value_new = loc_datas.get(dictionary[key]["religion_group"])
                    elif key.endswith('religion'):
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
                        if isinstance(value, list):
                            for i, values in enumerate(value):
                                localized_data = loc_datas.get(values)
                                localized_name = loc_names.get(values)
                                dictionary[key_new][i] = localized_data if localized_data is not None else localized_name
                        else:
                            localized_data = loc_datas.get(value)
                            localized_name = loc_names.get(value)
                            dictionary[key_new] = localized_data if localized_data is not None else localized_name
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
        if key in {"icon", "legacy_equivalent", "allow_normal_conversion", "valid_for_nation_designer", "nation_designer_trigger", "nation_designer_cost", "ai", "hidden_effect", "effect", "removed_effect"}:  # noqa
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

            if key in {"monarchy", "republic", "tribal", "native", "theocracy", "modifiers", "custom_attributes", "potential", "trigger", "conditional", "check_variable", "change_variable", "allow", "government_abilities", "effect", "removed_effect", "post_removed_effect"} or "_opinion" in key or "country_modifier" in key:  # noqa
                localized_name = key.replace("_", " ").title()
                if key in {"monarchy", "republic", "tribal", "native", "theocracy"}:
                    value = localise_reform_tiers(value, dict_loc)
                dictionary[localized_name] = dictionary.pop(key)
                key = localized_name
            elif any(key_localisation_check):
                new_key = "Country" if key == "tag" else key.replace("_", " ").title()
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                if not isinstance(value, (list, dict)) and (key == "custom_tooltip"):
                    localized_name = dict_loc.get(value) or value.replace('_', ' ').title()
                    dictionary[new_key] = localized_name
                elif isinstance(value, dict):
                    continue
                elif isinstance(value, list):
                    for i, values in enumerate(value):
                        localized_data = loc_datas.get(values) or values.replace('_', ' ').title()
                        dictionary[new_key][i] = localized_data
                else:
                    localized_data = loc_datas.get(value) or value.replace('_', ' ').title()
                    dictionary[new_key] = localized_data
            if isinstance(value, dict):
                if key == "custom_trigger_tooltip":
                    key_new = dict_loc.get(dictionary[key]["tooltip"])
                    value = True
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value
                    continue
                elif key == 'has_unlocked_government_reform':
                    value_new = dict_loc.get(dictionary[key]["government_reform"])
                    key_new = key.replace('_', ' ').title()
                    dictionary[key_new] = dictionary.pop(key)
                    dictionary[key_new] = value_new
                elif "modifiers" in value or "Modifiers" in value:
                    localized_name = dict_loc.get(key) or key.replace('_', ' ').title()
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
                        new_key, new_value = dict_loc.get(key).split(":")
                    else:
                        new_key = dict_loc.get(key)
                else:
                    new_key = loc_datas.get(key)
                if new_key is None or "_" in new_key:
                    new_key = key.replace("_", " ").title()
                if isinstance(value, str) and value.title().endswith("Influence"):
                    new_value = value.replace("_", " ").title()
                elif dict_loc.get(value) != "" and new_key.replace("_", " ").title() in ("Has Reform", "Have Had Reform", "Remove Country Modifier", "Add Country Modifier", "Modifier", "Remove Country Modifier", "Name", "Hase Estate Privilege", "Mission Completed"):  # noqa
                    new_key = key.replace("_", " ").title()
                    if new_key == "Mission Completed":
                        new_value = dict_loc.get(value + '_title') or value.replace('_', ' ').title()
                    else:
                        new_value = dict_loc.get(value) or value.replace('_', ' ').title()
                else:
                    if new_key in ("Has Country Flag", "Has Global Flag"):
                        new_value = value.replace("_", " ").title()
                    else:
                        new_value = value
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                    dictionary[new_key] = new_value

    return dictionary


def localise_reform_tiers(dictionary, dict_loc):
    """localises the reform file's tiers"""
    counter = len(dictionary)
    for key in dictionary:
        if 'theocratic_leadership' in dictionary:
            print('theocratic_leadership')
        if counter == 4 and key == "Separation Of Power":
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
        if key == 'military_doctrines':
            if "Feudalism vs Autocracy" in dictionary or "feudalism_vs_autocracy" in dictionary:
                new_key = "Royal Military Organization"
            elif "Republican Virtues" in dictionary or "republican_virtues" in dictionary:
                new_key = "People's War Organization"
            else:
                new_key = "Sacred War Organization"
        elif key.startswith('economical_matters'):
            if "Feudalism vs Autocracy" in dictionary or "feudalism_vs_autocracy" in dictionary:
                new_key = "Crown Economics"
            elif "Republican Virtues" in dictionary or "republican_virtues" in dictionary:
                new_key = "State Economics"
            else:
                new_key = "Divine Economics"
        else:
            new_key = dict_loc.get(key) or key.replace('_', ' ').title()
        dictionary[new_key] = dictionary.pop(key)
        counter = counter - 1
        if counter == 0:
            break

    return dictionary


def create_localisation(loc_dir):
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0125

    if 'hagia_sophia' in dict_vanilla:
        filenames = [
            f"{LOC_DIR}/domination_l_english.yml",
            f"{LOC_DIR}/king_of_kings_l_english.yml",
            f"{LOC_DIR}/leviathan_l_english.yml",
            f"{LOC_DIR}/modifers_l_english.yml",
            f"{LOC_DIR}/powers_and_ideas_l_english.yml",
            f"{LOC_DIR}/scandinavia_l_english.yml",
            f"{LOC_DIR}/tmm_l_english.yml",
        ]
    else:
        # fuck you pdx to not have everything in "singular" files instead of spread all over
        filenames = vanillaFilter(loc_dir, "l_english.yml")

    for key in list(dict_vanilla):
        if 'pre_dharma_mapping' in dict_vanilla:
            continue
        dict_loc[key] = ""
        if 'norse_ideas' in dict_vanilla:
            for key_sub in dict_vanilla[key]:
                if key_sub == "start":
                    dict_loc[key_sub] = "Traditions"
                    continue
                if key_sub == "bonus":
                    dict_loc[key_sub] = "Ambition"
                    continue
                if key_sub == "trigger" or key == "free":
                    continue

                dict_loc[key_sub] = ""
        elif 'hagia_sophia' in dict_vanilla:
            file = open(vanilla_monuemnts_b4_json)
            input = file.readlines()
            for line in input:
                if '\ttooltip' in line:
                    if line.split('=')[1].strip() != '{':
                        dict_loc[line.split('=')[1].strip()] = ""

    for key in dict_loc:
        index += 1
        percentage = (index / len(dict_loc)) * 100

        if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {current_time} - Progress: {percentage:.1f}%")

        process_key_sub(key, filenames, dict_loc)

    print("Created the Localisation Dictionary")


def process_key_sub(key_sub, filenames, dict_loc):
    for filename in filenames:
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
                    if line_reform.endswith('= yes'):
                        line_reform = line_reform.split('=')[0].strip()
                    else:
                        if line_reform.startswith('mission_completed'):
                            line_reform = line_reform.split('=')[1].strip() + '_title'
                        else:
                            line_reform = line_reform.split('=')[1].strip()
                    dict_loc[line_reform] = ""
        reforms_merged_txt += "\n"

    print("Merged all Government Reforms into one file")

    JsonParser(reforms_merged_txt)
    print("Jsonised the Government Reforms")


def build_correct_json():
    """Final Build"""
    for key, value in dict_vanilla.items():
        if key in "pre_dharma_mapping":
            continue
        dict_new[key] = {}
        for reform_key, reform_value in value.items():
            if reform_key != 'reform_levels':
                continue
            for list_name, list_reform in reform_value.items():
                dict_new[key][list_name] = {}
                dict_loc[list_name] = ""
                for reform, reforms in list_reform.items():
                    for singular_reform in reforms:
                        if singular_reform not in dict_reform:
                            continue
                        dict_loc[singular_reform] = ""
                        dict_new[key][list_name][singular_reform] = dict_reform[singular_reform]
                        continue
                    continue
                continue
            break

    print("Constructed the correct Reform Json")

    # with open("VanillaReform.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_new, output, indent="\t", separators=(",", ": "), ensure_ascii=False)


def vanillaFilter(gm_dir, gm_text):
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def JsonParser(vanilla_file_input):
    global dict_vanilla
    global dict_reform

    if "\\" in vanilla_file_input:
        try:
            file = open(vanilla_file_input, "r")
            data = file.read()
            file.close()
            file_name = basename(vanilla_file_input)
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {vanilla_file_input}")
            return None
    else:
        data = vanilla_file_input
        file_name = "govRef.txt"

    if 'monuments' in file_name:
        data = re.sub(r"^\tdate.*", "", data, flags=re.MULTILINE)
    else:
        data = data

    data = re.sub(r"_ideas={", "={", data)
    data = re.sub(r"_Ideas={", "={", data)

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

    if '\\' in vanilla_file_input:
        dict_vanilla = json_data
    else:
        dict_reform = json_data

    # with open(f"{file_name[:-4]}.json", "w") as file:
    #    json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Successfully created the json file")


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
