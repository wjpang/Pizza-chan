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

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\FEE.json"

tags = parent + "\\tags.txt"
database = parent + "\\database.txt"
provinces = parent + "\\provinces.json"

GOV_REF_JSON = "govRef.json"
REFO_LOC = "refLoc.txt"
GOV_REF_INPUT = glob.glob(GOV_REF_DIR + r"\*.txt")
GOV_REF_OUT_B4_JSON = "gov_ref.txt"

new_dict = {}


def start():
    """All shit"""
    merging_reforms(GOV_REF_INPUT)
    # create_localisation_file(REFO_LOC, LOC_DIR, LOC_DIR_VAN)

    # parse_correct_json()

    build(new_dict)


def merging_reforms(goverment_reforms):
    """Merges all Government Reforms from GE's files into one json"""
    print("Started Merging Government Reforms")
    modifiers_output = ""
    modifiers_to_update = []
    for modifiers_file in goverment_reforms:
        with open(modifiers_file, "r", encoding="utf-8") as reading_modifiers:
            for line_modifiers in reading_modifiers:
                if line_modifiers.strip().startswith("#") or len(line_modifiers) < 2 and line_modifiers != "}" or line_modifiers.strip().startswith("picture"):
                    continue
                modifiers_output += line_modifiers.split("#")[0].replace("= { }", "= {\n}").replace("= {}", "= {\n}").strip() + "\n"
        modifiers_output += "\n"

    print("Merged all Government Reforms into one file")
    json_parser(modifiers_output)
    print("Jsonised the Government Reforms")
    with open(GOV_REF_JSON, "r+", encoding="utf-8") as event_modif_file:
        event_mod_dict = json.load(event_modif_file)
        for key, value in event_mod_dict.items():
            if isinstance(value, dict):
                for modifier, number in value.items():
                    with open(database, "r+", encoding="utf_8") as data_mods:
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

    with open(GOV_REF_JSON, "w", encoding="utf-8") as file:
        json.dump(event_mod_dict, file, indent="\t", separators=(",", ": "), ensure_ascii=False)
    print("Localised the Government Reforms")


def build(new_dict):
    """Final Build"""
    print("Successfully localised the file!")


def json_parser(gov_file):
    """let's parse it all"""
    if not isinstance(gov_file, str):
        try:
            file = open(gov_file, "r", encoding="utf_8")
            data = file.read()
            file.close()
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
