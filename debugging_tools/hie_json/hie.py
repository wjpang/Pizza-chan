import datetime
import json
import os
import re
import time
from os.path import basename

MOD_PATH = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2804377099"
# eu4_dir = r'C:\Program Files\Epic Games\EuropaUniversalis4'  # This is for EGS

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\HIE_country_ideas.json"

tags = parent + r"\\tags.txt"
ideas = parent + r"\ideas.txt"
database = parent + r"\database.txt"

ideas_hie_out_be4_json = MOD_PATH + r"\common\ideas\HIE_country_ideas.txt"

ideas_dict = {}
ideas_loc = {}
LOC_DIR = MOD_PATH + r"\localisation"


def start():
    JsonParser(ideas_hie_out_be4_json)

    create_localisation(LOC_DIR)

    build(ideas_dict)


def build(dictionary):
    # create/populate local_country_ideas json
    localized_datas = {}
    final_dict = {}
    with open(database, "r", encoding="utf-8") as file:
        for line in file:
            if len(line.strip().split("\t")) == 2:
                key, localized_data = line.strip().split("\t")
                localized_datas[key] = localized_data

    final_dict = recursive_process_dict(dictionary, localized_datas)

    with open(f"{os.path.dirname(finalpath)}\\HIE_country_ideas.json", "w", encoding="utf-8") as output:
        json.dump(final_dict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # ) #, sort_keys=True)

    print("succesfully created the final Json")


def recursive_process_dict(dictionary, loc_datas):
    for key, value in list(dictionary.items()):
        if key.startswith("HIE_"):
            new_key = key.replace("_ideas", "")
            new_key = new_key.replace("HIE_", "")
            new_key = loc_datas.get(new_key)
            dictionary[new_key] = dictionary.pop(key)
            recursive_process_dict(dictionary[new_key], loc_datas)
        elif key == "effect":
            new_key = key.replace("_", " ").title()
            if "custom_tooltip" in value:
                if "admirals_give_army_professionalism_tt" in value["custom_tooltip"]:
                    new_key = "Recruiting Admirals grants 0.5% Army Professionalism"
                    del dictionary[key]["custom_tooltip"]
                    del dictionary[key]["set_country_flag"]
            else:
                new_key = "Remove Temporary Colonist"
            new_value = True
            # else:
            #     new_value = recursive_process_dict(value, loc_datas)
        elif key.startswith("hie") or key in ("start", "bonus", "MFA_byzantine_claimants"):
            new_key = ideas_loc.get(key)
            dictionary[new_key] = dictionary.pop(key)
            new_value = recursive_process_dict(dictionary[new_key], loc_datas)
            dictionary[new_key] = new_value
        else:
            new_key = loc_datas.get(key)
            new_value = value

        if key in dictionary:
            dictionary[new_key] = dictionary.pop(key)
            dictionary[new_key] = new_value

    return dictionary


def create_localisation(loc_dir):
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0250

    filenames = hie_filter(loc_dir, "l_english.yml")

    for key in ideas_dict:

        if "trigger" in ideas_dict[key]:
            del ideas_dict[key]["trigger"]
        elif "free" in ideas_dict[key]:
            del ideas_dict[key]["free"]

        for key_sub in ideas_dict[key]:
            percentage = (index/(len(ideas_dict)*11)) * 100
            if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Time: {current_time} - Progress: {percentage:.1f}%")
            index += 1
            if key_sub == "start":
                ideas_loc[key_sub] = "Traditions"
                continue
            if key_sub == "bonus":
                ideas_loc[key_sub] = "Ambition"
                continue
            if key_sub == "MFA_byzantine_claimants":
                ideas_loc[key_sub] = "Last Claimants of Byzantium"
                continue

            ideas_loc[key_sub] = ""

            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        if ":" in line:
                            line_key_sub, line_value = line.split(":", 1)
                            if line_value.startswith(("0", "1")):
                                line_value = line[1:]
                            if line_key_sub.strip() == key_sub:
                                ideas_loc[key_sub] = line_value.strip().replace('"', "").replace(",", "").title()
                                break

    print("Created the Localisation Dictionary")


def hie_filter(gm_dir, gm_text):
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def JsonParser(ideas_hie_out_be4_json):
    global ideas_dict
    try:
        file = open(ideas_hie_out_be4_json, "r")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {ideas_hie_out_be4_json}")
        return None

    file_name = basename(ideas_hie_out_be4_json)

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"free=y.*", "", data)  # Remove tabs and spaces

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

    ideas_dict = json_data

    # with open(f"{file_name[:-4]}.json", "w") as file:
    #     json.dump(json_data, file, indent="\t")  # , separators=(",", ": "), ensure_ascii=False) #) #, sort_keys=True)
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
