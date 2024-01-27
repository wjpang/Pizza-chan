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
database = parent + r"\database.json"

ideas_hie_out_be4_json = MOD_PATH + r"\common\ideas\HIE_country_ideas.txt"

dict_ideas = {}
dict_loc = {}
LOC_DIR = MOD_PATH + r"\localisation"

check_multiple_custom_tooltip = [
    'HIE_SPA_AND_FUERO_JUZGO_TT',
    'HIE_SPA_ARA_UNION_OF_CROWNS_ITALY_TT',
    'HIE_SPA_ARA_UNION_OF_CROWNS_IBERIA_TT',
    'HIE_SPA_LEO_REINFORCE_THE_CORTES_TT',
    'HIE_ITA_SIC_PARRAMENTU_SICILIANU_TT'
]


def start():
    JsonParser(ideas_hie_out_be4_json)

    create_localisation(LOC_DIR)

    build(dict_ideas)


def build(dictionary):
    localized_datas = {}
    dict_final = {}
    with open(database, "r", encoding="utf-8") as file:
        localized_datas = json.load(file)

    dict_final = recursive_process_dict(dictionary, localized_datas)

    with open(f"{os.path.dirname(finalpath)}\\HIE.json", "w", encoding="utf-8") as output:
        json.dump(dict_final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # ) #, sort_keys=True)

    print("succesfully created the final Json")


def recursive_process_dict(dictionary, loc_datas):
    for key, value in list(dictionary.items()):
        if key in {'removed_effect'}:
            del dictionary[key]
            continue

        if key.startswith("HIE_"):
            key_new = key.replace("_ideas", "")
            key_new = key_new.replace("HIE_", "")
            key_new = loc_datas.get(key_new)
            dictionary[key_new] = dictionary.pop(key)
            value_new = dictionary[key_new]
            recursive_process_dict(dictionary[key_new], loc_datas)
        elif key == "effect":
            # del dictionary[key]
            # continue
            key_new = key.replace("_", " ").title()
            if 'country_event' in value:
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
                    dictionary["Effect"][key_new] = value_new
                else:
                    if 'hie_ita_gpv_fanti_da_mar_modifier' in value["add_country_modifier"]["name"]:
                        transform_multiple_entry(dictionary["Effect"], value)
                        continue
                    result = transform_singular_entry(key, value["add_country_modifier"])
                    key_new, value_new = result if result is not None else (key, value["add_country_modifier"])
                    dictionary["Effect"][key_new] = value_new
                continue
                # result = transform_singular_entry(key, value)
                # key_new, value_new = result if result is not None else (key, value)
                # del dictionary[key]["custom_tooltip"]
                # del dictionary[key]["add_country_modifier"]
            else:
                del dictionary[key]
                continue
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


def transform_multiple_entry(dictionary, value):
    if "add_country_modifier" in value:
        if 'hie_ita_gpv_fanti_da_mar_modifier' in value["add_country_modifier"]["name"]:
            key_new = "Marines' Fire Damage"
            value_new = 0.10
            dictionary[key_new] = value_new
            key_new = "Marines' Shock Damage"
            value_new = 0.10
            dictionary[key_new] = value_new
            key_new = "Marines' Shock Damage Received"
            value_new = -0.10
            dictionary[key_new] = value_new
            return
    else:
        if 'HIE_SPA_AND_FUERO_JUZGO_TT' in value["custom_tooltip"]:
            key_new = "Culture Group Provinces' Local Unrest"
            value_new = -2
            dictionary[key_new] = value_new
            key_new = "Culture Group Provinces' Local Tax"
            value_new = 0.15
            dictionary[key_new] = value_new
            return
        elif 'HIE_SPA_ARA_UNION_OF_CROWNS_ITALY_TT' in value["custom_tooltip"]:
            key_new = "Italian Provinces' Local Unrest"
            value_new = -2
            dictionary[key_new] = value_new
            key_new = "Italian Provinces' Defensiveness"
            value_new = 0.10
            dictionary[key_new] = value_new
            return
        elif 'HIE_SPA_ARA_UNION_OF_CROWNS_IBERIA_TT' in value["custom_tooltip"]:
            key_new = "Iberian Provinces' Local Unrest"
            value_new = -2
            dictionary[key_new] = value_new
            key_new = "Iberian Provinces' Local Autonomy"
            value_new = -0.025
            dictionary[key_new] = value_new
            return
        elif 'HIE_SPA_LEO_REINFORCE_THE_CORTES_TT' in value["custom_tooltip"] or 'HIE_ITA_SIC_PARRAMENTU_SICILIANU_TT' in value["custom_tooltip"]:
            key_new = "Parliament Seat' Local Development Cost"
            value_new = -0.10
            dictionary[key_new] = value_new
            key_new = "Parliament Seat' Governing Cost Modifier"
            value_new = -0.15
            dictionary[key_new] = value_new
            "-10.0 Development Cost and -15.0 Governing Cost in Parliament Seat"
            return


def transform_singular_entry(key, value):
    if 'duration' not in value:
        if 'admirals_give_army_professionalism_tt' in value:
            return "Army Professionalism gained from recruiting Admirals", 0.5
        elif 'HIE_DEV_COST_REDUCTION_IN_ARCTIC_TT' in value:
            return "Arctic Provinces's Developmetn Cost", -0.30
        elif 'HIE_GOV_COST_REDUCTION_IN_PRUSSIAN_PROVINCES_TT' in value:
            return "Prussian Provinces' Governing Cost", -0.15
        elif 'HIE_RAG_ABOLITION_SLAVERY_TT' in value:
            return "This will result in the Abolition of Slavery", True
        elif 'HIE_SPA_BAS_REVITALIZE_CANTABRIAN_SHIPYARDS_TT' in value:
            return "Iberian Naval Supplies Provinces' Trade Goods", 0.50
        elif 'HIE_SPA_GAL_MODERNIZED_CAMINO_REAL_TT' in value:
            return "Expanded Infrastructure Provinces' Local Tax", 0.15
        elif 'HIE_SPA_GAL_ASIENTO_SYSTEM_TT' in value:
            return "Colonial Subjects' Trade Goods Modifier", 0.10
        elif 'HIE_TUS_THORNTON_EXPEDITION_TT' in value:
            return "Colonial Colombia's Local Settler Increase", 25
        elif 'HIE_ITA_CULLA_RINASCIMENTO_TT' in value:
            return "Italy Provinces' Build Cost", -0.10
        elif 'HIE_ITA_SAR_STATUTE_SABAUDIAE_TT' in value:
            return "Latin Provinces' Governing Cost", -0.15
        elif 'HIE_ITA_MFV_STELLA_FORTE_TT' in value:
            return 'Chance of Lux Stella on new heirs', 0.02
        elif 'HIE_ITA_CRU_DIO_LO_VUOLE_TT' in value:
            return 'Years of Manpower recovered in Religious War won', 1

    else:
        if 'hie_ven_fanti_mar_modifier' in value["name"]:
            return "Marines' Shock Damage", 0.10
        elif 'hie_hol_soldaten_ter_zee_modifier' in value["name"]:
            return "Marines' Infantry Combat Ability", 0.10
        elif 'hie_pga_braccio_montone_modifier' in value["name"]:
            return "Mercenaries' Shock Damage", "0.10"


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
            if abs(percentage % 5.0 - 0) < tolerance or abs(percentage % 5.0 - 5.0) < tolerance:
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
