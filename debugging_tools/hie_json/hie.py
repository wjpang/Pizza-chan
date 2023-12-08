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
finalpath = os.path.dirname(parent) + r"\data\HIE.json"

tags = parent + r"\\tags.txt"
ideas = parent + r"\ideas.txt"
database = parent + r"\database.txt"

ideas_hie_out_be4_json = MOD_PATH + r"\common\ideas\HIE_country_ideas.txt"

dict_ideas = {}
dict_loc = {}
LOC_DIR = MOD_PATH + r"\localisation"


def start():
    JsonParser(ideas_hie_out_be4_json)

    create_localisation(LOC_DIR)

    build(dict_ideas)


def build(dictionary):
    localized_datas = {}
    dict_final = {}
    with open(database, "r", encoding="utf-8") as file:
        for line in file:
            if len(line.strip().split("\t")) == 2:
                key, localized_data = line.strip().split("\t")
                localized_datas[key] = localized_data

    dict_final = recursive_process_dict(dictionary, localized_datas)

    with open(f"{os.path.dirname(finalpath)}\\HIE.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # ) #, sort_keys=True)

    print("succesfully created the final Json")


def recursive_process_dict(dictionary, loc_datas):
    for key, value in list(dictionary.items()):
        if key.startswith("HIE_"):
            key_new = key.replace("_ideas", "")
            key_new = key_new.replace("HIE_", "")
            key_new = loc_datas.get(key_new)
            dictionary[key_new] = dictionary.pop(key)
            value_new = dictionary[key_new]
            recursive_process_dict(dictionary[key_new], loc_datas)
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
            # else:
            #     value_new = recursive_process_dict(value, loc_datas)
        elif key.startswith("hie") or key in ("start", "bonus", "MFA_byzantine_claimants"):
            key_new = dict_loc.get(key)
            dictionary[key_new] = dictionary.pop(key)
            value_new = recursive_process_dict(dictionary[key_new], loc_datas)
            dictionary[key_new] = value_new
        else:
            key_new = loc_datas.get(key)
            value_new = value

        if key in dictionary:
            dictionary[key_new] = dictionary.pop(key)
            dictionary[key_new] = value_new

    return dictionary


def create_localisation(loc_dir):
    print("Started the creation of localisation")
    index = 0
    tolerance = 0.0250

    filenames = hie_filter(loc_dir, "l_english.yml")

    for key in dict_ideas:
        index += 1

        if "trigger" in dict_ideas[key]:
            del dict_ideas[key]["trigger"]
        elif "free" in dict_ideas[key]:
            del dict_ideas[key]["free"]

        for key_sub in dict_ideas[key]:
            percentage = (index/(len(dict_ideas)*11)) * 100
            if abs(percentage % 2.5 - 0) < tolerance or abs(percentage % 2.5 - 2.5) < tolerance:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Time: {current_time} - Progress: {percentage:.1f}%")
            index += 1
            if key_sub == "start":
                dict_loc[key_sub] = "Traditions"
                continue
            if key_sub == "bonus":
                dict_loc[key_sub] = "Ambition"
                continue
            if key_sub == "MFA_byzantine_claimants":
                dict_loc[key_sub] = "Last Claimants of Byzantium"
                continue

            dict_loc[key_sub] = ""

            for filename in filenames:
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        if ":" in line:
                            line_key_sub, line_value = line.split(":", 1)
                            if line_value.startswith(("0", "1")):
                                line_value = line[1:]
                            if line_key_sub.strip() == key_sub:
                                dict_loc[key_sub] = line_value.strip().replace('"', "").replace(",", "").title()
                                break

    print("Created the Localisation Dictionary")


def hie_filter(gm_dir, gm_text):
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def JsonParser(ideas_hie_out_be4_json):
    global dict_ideas
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

    dict_ideas = json_data

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
