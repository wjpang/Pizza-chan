import datetime
import glob
import json
import os
import re
import time
from os.path import basename

# all definitions
MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1596815683"
VANILLA_PATH = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
LOC_DIR = MOD_PATH + r"\localisation"
LOC_DIR_VAN = VANILLA_PATH + r"\localisation"
GOV_REF_DIR = MOD_PATH + r"\common\government_reforms"
GOV_REF = MOD_PATH + r"\common\governments\zzz_00_governments.txt"

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent)

tags = parent + "\\tags.txt"
database = parent + "\\database.txt"
provinces = parent + "\\provinces.json"

GOV_REF_INPUT = glob.glob(GOV_REF_DIR + r"\*.txt")

dict_original = {}
dict_reform = {}
dict_new = {}
localized_names = {}
dict_loc = {}


def start():
    """All shit"""
    json_parser(GOV_REF)
    merging_reforms(GOV_REF_INPUT)
    build_correct_json()
    create_localisation(LOC_DIR, LOC_DIR_VAN)

    build(dict_new)


def merging_reforms(goverment_reforms):
    """Merges all Government Reforms from GE's files into one json"""
    reforms_merged_txt = ""

    for reform_file in goverment_reforms:
        if reform_file.endswith("modified_by_GE.txt"):
            continue
        with open(reform_file, "r", encoding="utf-8") as reading_reforms:
            for line_reform in reading_reforms:
                if line_reform.strip().startswith("#") or len(line_reform) < 2 and line_reform != "}" or line_reform.strip().startswith("picture"):
                    continue
                line_reform = line_reform.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
                reforms_merged_txt += line_reform
                line_reform = line_reform.strip()
                if (
                    "{" not in line_reform
                    and line_reform.startswith("modifier = ")
                    or line_reform.startswith("name = ")
                    or (line_reform.endswith("yes") and line_reform.startswith("enables_") and not line_reform.endswith("idea_group = yes"))
                ):
                    localized_names[line_reform] = ""
        reforms_merged_txt += "\n"

    print("Merged all Government Reforms into one file")

    json_parser(reforms_merged_txt)
    print("Jsonised the Government Reforms")


def build_correct_json():
    """Final Build"""
    for key, value in dict_original.items():
        if key in "pre_dharma_mapping":
            continue
        dict_new[key] = {}
        for reform_key, reform_value in value.items():
            if reform_key != 'reform_levels':
                continue
            for list_name, list_reform in reform_value.items():
                dict_new[key][list_name] = {}
                localized_names[list_name] = ""
                for reform, reforms in list_reform.items():
                    for singular_reform in reforms:
                        if singular_reform not in dict_reform:
                            continue
                        dict_new[key][list_name][singular_reform] = dict_reform[singular_reform]
                        continue
                    continue
                continue
            break

    # with open("GE.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_new, output, indent="\t", separators=(",", ": "), ensure_ascii=False)
    print("Successfully fixed the json")


def build(dictionary):
    """Final Build"""
    localized_datas = {}
    final_dict = {}
    with open(database, "r", encoding="utf-8") as file:
        localized_datas = json.load(file)

    final_dict = recurse_process_dict(dictionary, localized_datas)

    with open("GE.json", "w", encoding="utf-8") as output:
        json.dump(final_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    # with open(f"{os.path.dirname(finalpath)}\\GE.json", "w", encoding="utf-8") as output:
    #     json.dump(final_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    print("Successfully created the final Json!")


def recurse_process_dict(dictionary, loc_datas):
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
            elif any(key_localisation_check) and key not in {"regional_kasbah_reform"}:
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
                if "modifiers" in value or "Modifiers" in value:
                    localized_name = dict_loc.get(key) or key.replace('_', ' ').title()
                    dictionary[localized_name] = dictionary.pop(key)
                    key = localized_name
                recurse_process_dict(value, loc_datas)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, (list, dict)) and len(item) > 1:
                        recurse_process_dict(item, loc_datas)
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
                elif dict_loc.get(value) != "" and new_key.replace("_", " ").title() in ("Has Reform", "Have Had Reform", "Remove Country Modifier", "Add Country Modifier", "Modifier", "Remove Country Modifier", "Name"):
                    new_key = key.replace("_", " ").title()
                    new_value = dict_loc.get(value)
                else:
                    new_value = value
                if key in dictionary:
                    dictionary[new_key] = dictionary.pop(key)
                    dictionary[new_key] = new_value

    return dictionary


def localise_reform_tiers(dictionary, dict_loc):
    """localises the reform file's tiers"""
    counter = len(dictionary)
    for key, value in dictionary.items():
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
        elif counter == 4 and key == "Sacred War Organization":
            key = "separation_of_power_theocracy"
        elif counter == 3 and key == "Religious Enforcement":
            key = "nature_of_faith"
        elif counter == 2 and key == "Secularization?":
            key = "culture_within_the_state"
        elif counter == 1 and key == "Clergy In Administration":
            key = "faith_and_the_world"
        counter = counter - 1
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
        if counter == 0:
            break

    return dictionary


def create_localisation(loc_dir, loc_dir_vanilla):
    """Creates the Localisation Array as [key\tlocalised_key,]"""
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0125

    filenames = ge_filter(loc_dir, "l_english.yml")
    # filenames.extend(ge_filter(loc_dir_vanilla, "l_english.yml"))

    for key in dict_reform:
        if key not in localized_names:
            localized_names[key] = ""

    for key in localized_names:
        percentage = (index/len(localized_names)) * 100
        if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {current_time} - Progress: {percentage:.1f}%")
        index += 1

        if key.startswith("enables_"):
            new_key = 'mechanic_' + key.split("=")[0].strip() + '_yes'
        elif key.startswith(("name =", "modifier =")):
            new_key = key.split("=")[1].strip()
        else:
            new_key = key
        dict_loc[new_key] = ""

        if new_key == "feudalism_vs_autocracy":
            dict_loc[new_key] = "Feudalism vs Autocracy"
            continue

        for filename in filenames:
            if len(dict_loc[new_key]) > 1:  # exit the search for the current key once it's found
                break
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    if ":" in line:
                        line_key, line_value = line.split(":", 1)
                        if line_value.startswith(("0", "1")):
                            line_value = line[1:]
                        if line_key.strip() == new_key:
                            if not new_key.startswith("enables_") and ":" in line_value:
                                line_value = line_value.split(":")[1]
                                if line_value.startswith(("0", "1")):
                                    line_value = line_value[1:]
                            dict_loc[new_key] = line_value.strip().replace('"', "").replace(",", "").title()
                            break

        # Print everything that is not in the vnailla files to manually add it before
        if len(dict_loc[new_key]) == 0:
            print(new_key)

    print("Created the Localisation Dictionary")

    # with open("GELoc.json", "w", encoding="utf-8") as output:
    #     json.dump(dict_loc, output, indent="\t", separators=(",", ": "), ensure_ascii=False)


def ge_filter(gm_dir, gm_text):
    """filter"""
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def json_parser(gov_file):
    """let's parse it all"""
    global dict_original
    global dict_reform

    if "\\" in gov_file:
        try:
            with open(gov_file, "r", encoding="utf_8") as file:
                data = file.read()
            file_name = basename(gov_file)
        except FileNotFoundError:
            print(f"ERROR: Unable to find file: {gov_file}")
            return None
    else:
        data = gov_file
        file_name = "govRef.txt"

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
        print(f"Dumping intermediate code into file: {file_name}_{time.time():.0f}.intermediate")

        with open(f"./output/{file_name}_{time.time():.0f}.intermediate", "w", encoding="utf-8") as output:
            output.write(data)

        return None

    if "\\" in gov_file:
        dict_original = json_data
    else:
        dict_reform = json_data

    # with open(f"{file_name[:-4]}.json", "w", encoding="utf_8") as file:
    #     json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
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
