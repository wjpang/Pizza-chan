import argparse
import glob
import json
import logging
import os
import re
import sys
import time
from os import listdir
from os.path import basename, isdir, isfile, join
from pdb import post_mortem
from unittest import skip

import pandas as pd
import requests
from tqdm import tqdm


def write_csv_file():
    df = pd.read_csv("tagsVIK.txt", sep="\t")
    df.to_csv("tagsVIK.csv", encoding="utf-8", index=False)


write_csv_file()


def start():
    eu4DIR = r"D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"

    modpath = r"D:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2262234791"
    pathfolder = os.getcwd()
    parent = os.path.dirname(pathfolder)

    tag = r"D:\Program Files\Steam\steamapps\workshop\content\236850\2262234791\common\country_tags\00_countries.txt"
    tags = "tagsVIK.txt"
    ideas = "ideas_vik.txt"
    data = parent + "\\database.txt"

    ideas_vikBeforeJson = r"D:\Program Files\Steam\steamapps\workshop\content\236850\2262234791\common\ideas\00_country_ideas.txt"
    localDIR = eu4DIR + r"\localisation"
    modDIR = modpath + r"\localisation"

    # create_tag(tag, [modDIR, localDIR])
    # JsonParser(ideas_vikBeforeJson)
    ideas_vik = "00_country_ideas.json"
    # create_ideas(ideas_vik, ideas, [modDIR, localDIR])
    # build(ideas_vik, tags, data, ideas)


def build(ideas_vik, tags, data, ideas):
    # create/populate local_country_ideas json
    with open(ideas_vik, "r+", encoding="utf8") as ideasOut:
        idea_lib = json.load(ideasOut)
        idea_lib2 = {}

        for i in idea_lib:
            with open(tags, "r+", encoding="utf8") as tagsLoc:
                iA = i

                for tagline in tagsLoc:
                    tagA = tagline.split("\t")
                    if tagA[0] == iA:
                        iA = tagA[1].strip()
                        break

                idea_lib2[iA] = {}

                for j in idea_lib[i]:
                    if j == "trigger":
                        continue
                    if j == "free":
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

                        idea_lib2[iA].update({jA: {}})

                        for k in idea_lib[i][j]:
                            with open(data, "r+", encoding="utf8") as dataLoc:
                                kA = k

                                for dataline in dataLoc:
                                    datA = dataline.split("\t")
                                    if datA[0] == kA:
                                        kA = datA[1].strip()
                                        break

                                idea_lib2[iA][jA].update({kA: idea_lib[i][j][k]})

        with open("Viking_country_ideas.json", "w", encoding="utf8") as output:
            json.dump(idea_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


def create_ideas(ideas_vik, ideas, DIR):
    with open(ideas_vik, "r+", encoding="utf8") as ideasOut:
        idea_lib = json.load(ideasOut)
        array = []

        filenames = gmFilter(DIR[0], "yml")
        filenames.extend(gmFilter(DIR[1], "english.yml"))

        for i in idea_lib:
            for j in idea_lib[i]:
                if j in {"start", "bonus", "trigger", "free"}:
                    continue
                array.append([j, ""])
                for file in filenames:
                    with open(file, "r+", encoding="utf8") as localOut:
                        for lineB in localOut:
                            lineB = lineB.strip()
                            if lineB.find(":") != -1:
                                lineB2 = lineB.split(":", 1)
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

    print("successfully populated the ideas file")


def create_tag(tag, DIR):
    with open(tag, "r+", encoding="utf8") as tagsOut:
        array = []

        filenames = gmFilter(DIR[0], "yml")
        filenames.extend(gmFilter(DIR[1], "english.yml"))

        for i in tagsOut:
            for j in tagsOut:
                if j[:1] == "# ":
                    continue
                array.append([j[:3], ""])
                for file in filenames:
                    with open(file, "r+", encoding="utf8") as localOut:
                        for lineB in localOut:
                            lineB = lineB.strip()
                            if lineB.find(":") != -1:
                                lineB2 = lineB.split(":", 1)
                                if lineB2[0].casefold() == array[-1][0].casefold():
                                    array[-1][1] = lineB2[1].split('"', 1)[1][:-1]
                                    break
                    if array[-1][1] != "":
                        break
                if array[-1][1] == "":
                    print(array[-1])

    with open("tagsVik.txt", "w", encoding="utf8") as output:
        output.write("tag" + "\t" + "country")
        for i in array:
            output.write(i[0] + "\t" + i[1])
            output.write("\n")

    print("successfully created the tag file")


def gmFilter(gmDir, gmText):
    gmArray = os.listdir(gmDir)
    return [gmDir + "\\" + file for file in gmArray if file.endswith(gmText)]


def JsonParser(ideas_vikBeforeJson):
    try:
        with open(ideas_vikBeforeJson, "r") as file:
            data = file.read()
    except FileNotFoundError:
        print("ERROR: Unable to find file: " + ideas_vikBeforeJson)
        return None

    file_name = basename(ideas_vikBeforeJson)

    data = re.sub(r"# .*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"date = 1.01.01", "", data)

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

    file_name = basename(ideas_vikBeforeJson)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open("./output/{}_{:.0f}.intermediate".format(file_name, time.time()), "w") as output:
            output.write(data)

        return None

    with open(file_name[:-4] + ".json", "w") as file:
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
