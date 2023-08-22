import json
import os
import re
import time
from os.path import basename

mod_dir = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
# eu4_dir = r'C:\Program Files\Epic Games\EuropaUniversalis4' # This is for EGS

path = os.getcwd()
parent = os.path.dirname(path)
finalpath = os.path.dirname(parent) + r"\data\00_country_ideas.json"

tags = parent + r"\\tags.txt"
ideas = parent + r"\ideas.txt"
data = parent + r"\database.txt"

ideas_vanilla_b4_json = mod_dir + r"\common\ideas\00_country_ideas.txt"

ideas_vanilla = "00_country_ideas.json"
localisation_dir = mod_dir + r"\localisation"


def start():
    JsonParser(ideas_vanilla_b4_json)

    # create_ideas(ideas_vanilla, ideas, localisation_dir)

    build(ideas_vanilla, tags, data, ideas, finalpath)


def build(ideas_vanilla, tags, data, ideas, finalpath):
    # create/populate local_country_ideas json
    with open(ideas_vanilla, "r+", encoding="utf8") as ideas_out:
        idea_lib = json.load(ideas_out)
        idea_lib2 = {}

        for i in idea_lib:
            with open(tags, "r+", encoding="utf8") as tags_loc:
                i_a = i

                for tagline in tags_loc:
                    tag_a = tagline.split("\t")
                    if tag_a[0] == i_a:
                        i_a = tag_a[1].strip()
                        break

                idea_lib2[i_a] = {}

                for j in idea_lib[i]:
                    if j in {"trigger", "free"}:
                        continue

                    with open(ideas, "r+", encoding="utf8") as ideasLoc:
                        jA = j

                        if j == "start":
                            jA = "Traditions"
                        elif j == "bonus":
                            jA = "Ambition"
                        else:
                            for idealine in ideasLoc:
                                ideaA = idealine.split("\t")
                                if ideaA[0] == jA:
                                    jA = ideaA[1].strip()
                                    break

                        idea_lib2[i_a].update({jA: {}})

                        for k in idea_lib[i][j]:
                            with open(data, "r+", encoding="utf8") as dataLoc:
                                kA = k

                                for dataline in dataLoc:
                                    datA = dataline.split("\t")
                                    if datA[0] == kA:
                                        kA = datA[1].strip()
                                        break

                                idea_lib2[i_a][jA].update({kA: idea_lib[i][j][k]})

        with open(f"{os.path.dirname(finalpath)}\\00_vanilla_country_ideas.json", "w", encoding="utf-8") as output:
            json.dump(idea_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("succesfully created the final Json")


def create_ideas(ideas_vanilla, ideas, localisation_dir):
    with open(ideas_vanilla, "r+", encoding="utf8") as ideas_out:
        idea_lib = json.load(ideas_out)
        array = []

        filenames = gmFilter(localisation_dir, "yml")
        filenames.extend(gmFilter(localisation_dir, "english.yml"))

        for i in idea_lib:
            for j in idea_lib[i]:
                if j in {"start", "bonus", "trigger", "free"}:
                    continue
                array.append([j, ""])
                for file in filenames:
                    with open(file, "r+", encoding="utf8") as localOut:
                        for line_b in localOut:
                            line_b = line_b.strip()
                            if line_b.find(":") != -1:
                                lineB2 = line_b.split(":", 1)
                                if lineB2[0].casefold() == array[-1][0].casefold():
                                    array[-1][1] = lineB2[1].split('"', 1)[1][:-1]
                                    break
                    if array[-1][1] != "":
                        break
                if array[-1][1] == "":
                    print(array[-1])

    with open(ideas, "w", encoding="utf8") as output:
        for i in array:
            output.write(i[0] + "\t" + i[1])
            output.write("\n")
    print("succesfully created the localisation file")


def gmFilter(gm_dir, gm_text):
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def JsonParser(ideas_vanilla_b4_json):
    try:
        file = open(ideas_vanilla_b4_json, "r")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {ideas_vanilla_b4_json}")
        return None

    file_name = basename(ideas_vanilla_b4_json)

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
    data = re.sub(r"jerusalem_ideas={", "KOJ={", data)
    data = re.sub(r"irish_ideas={", "IRE={", data)
    data = re.sub(r"_ideas={", "={", data)
    data = re.sub(r"_Ideas={", "={", data)
    data = re.sub(r"fulani_jihad", "SOK", data)
    data = re.sub(r"CHI={", "MNG={", data)
    data = re.sub(r"hausa", "KTS", data)
    data = re.sub(r"tongan", "TOG", data)
    data = re.sub(r"samoan", "SAM", data)
    data = re.sub(r"CHICK", "CHI", data)

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

    file_name = basename(ideas_vanilla_b4_json)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open("./output/{}_{:.0f}.intermediate".format(file_name, time.time()), "w") as output:
            output.write(data)

        return None

    with open(f"{file_name[:-4]}.json", "w") as file:
        json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
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
