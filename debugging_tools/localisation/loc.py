import json
import logging
import os

# import deepl
from dotenv import load_dotenv

load_dotenv()
AUTH_KEY = os.getenv("DEEPL_AUTH_KEY", "")

logging.basicConfig()
logging.getLogger("deepl").setLevel(logging.DEBUG)

VANILLA_LOC_PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Europa Universalis IV\\localisation"
MOD_ROOT = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\236850\\"
EMF = {
    "ATE": "2737385499",
    "ASE": "2172666098",
    "FEE": "2185445645",
    "GE": "1596815683",
    "GME": "2469419235",
    "HIE": "2804377099",
    "HREE": "1352521684",
    "PTE": "2615504872",
    "SE": "1834079712",
    "TGE": "1770950522",
}


def generate_loc_json():
    """Generate a json which contains all localisation of vanilla and all EMF mods."""
    loc_dict = {"ATE": {}, "ASE": {}, "FEE": {}, "GE": {}, "GME": {}, "HIE": {}, "HREE": {}, "PTE": {}, "SE": {}, "TGE": {}}
    for mod, mod_id in EMF.items():
        path = f"{MOD_ROOT}{mod_id}\\localisation"
        file_lst = [path + "\\" + file for file in os.listdir(path) if file.endswith("_l_english.yml")]
        for file in file_lst:
            temp = {}
            with open(file, "r", encoding="utf-8-sig") as f:
                loc = f.readlines()
            for line in loc:
                line = line.strip()
                if line.startswith("#") or line == "" or line == "l_english:":
                    continue
                line = line.split(":")
                temp[line[0]] = line[1].replace('"', "").strip()
            loc_dict[mod][file[87:]] = temp
    with open("emf_loc.json", "w", encoding="utf-8") as f:
        json.dump(loc_dict, f, indent="\t", separators=(",", ": "), ensure_ascii=False)

    loc_dict = {}
    file_lst = [VANILLA_LOC_PATH + "\\" + file for file in os.listdir(VANILLA_LOC_PATH) if file.endswith("_l_english.yml")]
    for file in file_lst:
        with open(file, "r", encoding="utf-8-sig") as f:
            loc = f.readlines()
        for line in loc:
            line = line.strip()
            if line.startswith("#") or line == "" or line == "l_english:":
                continue
            line = line.split(":", 1)
            line[1] = line[1].replace('"', "").strip()
            if line[1] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                line[1] = ""
            if line[1] != "" and line[1][0] in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"} and line[1][1] == " ":  # Remove numbers at the beginning of the string
                line[1] = line[1][2:]
            loc_dict[line[0]] = line[1]
    with open("vanilla_loc.json", "w", encoding="utf-8") as f:
        json.dump(loc_dict, f, indent="\t", separators=(",", ": "), ensure_ascii=False)


def main():
    """Main function."""
    # translator = deepl.Translator(AUTH_KEY)
    generate_loc_json()


if __name__ == "__main__":
    main()
