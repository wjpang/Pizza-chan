import json
import os
import re

from PIL import Image

TGE_PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\236850\\1770950522\\"
GOODS = f"{TGE_PATH}common\\tradegoods\\00_tradegoods.txt"
PRICES = f"{TGE_PATH}common\\prices\\00_tge_prices.txt"
IMAGES = f"{TGE_PATH}gfx\\interface\\resources.dds"


def parse(data):
    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)", "\n", data, flags=re.MULTILINE)  # Seperate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"free=yes", "", data)  # Remove free=yes

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
    data = re.sub(r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{\n]+", r'"\g<0>"', data)  # Add quotes around string values
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
    data = "{" + data + "}"  # Add curly braces on entire data for json
    return data


def _handle_duplicates(ordered_pairs):
    res = {}
    for key, val in ordered_pairs:
        if key in res:
            if isinstance(res[key], list):
                res[key].append(val)
            else:
                res[key] = [res[key], val]
        else:
            res[key] = val
    return res


def main():
    # Goal:
    # {
    #     [good_name]: {
    #         "Price": [value],
    # 	      "Province bonus": [modifier],
    # 	      "Trade leader bonus": [modifier]
    #     },
    #     ...
    # }
    final = {}

    # Special Province bonuses/Trade leader bonuses
    special = {
        # Province bonuses
        "metalworking": "Production Efficiency in Provinces with Production Building +5%",
        # Trade leader bonuses
        "indigo": "Goods Produced in provinces with Indigo +15%",
        "llama": "Development Cost in Mountain/Hills/Highlands Provinces -10%",
        "camel": "Development Cost in Arid Owned Province -10%",
        "chocolate": "Morale of Armies in Colonies/Subjects and Client States +10%",
        "cigars": "Base Tax in New Colonies +2",
    }

    # Load TGE loc
    with open(f"{os.path.dirname(os.getcwd())}\\localisation\\emf_loc.json", "r", encoding="utf-8") as f:
        tge_loc = json.load(f)["TGE"]["trade_goods_marcin_l_english.yml"]
    # Load vanilla loc
    with open(f"{os.path.dirname(os.getcwd())}\\localisation\\vanilla_loc.json", "r", encoding="utf-8") as f:
        van_loc = json.load(f)
    # Load modifier loc
    with open(f"{os.path.dirname(os.getcwd())}\\localisation\\modifiers\\modifiers.json", "r", encoding="utf-8") as f:
        mod_loc = json.load(f)

    # Goods' names & prices
    with open(PRICES, "r", encoding="utf-8") as f:
        prices = json.loads(parse(f.read()), object_pairs_hook=_handle_duplicates)
    for good, price in prices.items():
        try:
            final[tge_loc[good]] = {"Price": str(price["base_price"])}
        except KeyError:
            final[van_loc[good]] = {"Price": str(price["base_price"])}

    # Goods' province bonuses, trade leader bonuses
    with open(GOODS, "r", encoding="utf-8") as f:
        goods = json.loads(parse(f.read()), object_pairs_hook=_handle_duplicates)
    for good, data in goods.items():
        if good in {"unknown", "gold", "silver"}:
            continue
        try:
            province = f"{mod_loc[list(data['province'].keys())[0]]} {list(data['province'].values())[0]}"
            modifier = f"{mod_loc[list(data['modifier'].keys())[0]]} {list(data['modifier'].values())[0]}"
        except AttributeError:
            if not list(data["province"]):
                province = special[good]
                modifier = f"{mod_loc[list(data['modifier'].keys())[0]]} {list(data['modifier'].values())[0]}"
            else:
                province = f"{mod_loc[list(data['province'].keys())[0]]} {list(data['province'].values())[0]}"
                modifier = special[good]
        try:
            final[tge_loc[good]]["Province bonus"] = province
            final[tge_loc[good]]["Trade leader bonus"] = modifier
        except KeyError:
            final[van_loc[good]]["Province bonus"] = province
            final[van_loc[good]]["Trade leader bonus"] = modifier

    # Final TGE json
    with open(f"{os.path.dirname(os.path.dirname(os.getcwd()))}\\data\\TGE.json", "w", encoding="utf-8") as output:
        json.dump(final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)

    # Goods' images
    with Image.open(IMAGES) as im:
        print(im.format, im.size, im.mode)


if __name__ == "__main__":
    main()
