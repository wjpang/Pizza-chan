"""
Trade Goods Expanded to JSON
By LoStack: https://github.com/stackpoint
"""


import codecs
import contextlib
import json
import os
import random
import re
import shutil
import subprocess
import time

import requests
from bs4 import BeautifulSoup


def start():
    database = "database.txt"

    gmJSON2(database)


def gmJSON2(database):
    with open(database, "r+", encoding="utf8") as data:
        with open("modifier_cache.json", "w", encoding="utf8") as output:
            modifierJSON = {}

            for lineA in data:
                modifier = lineA.split("\t")
                if modifierJSON.get(modifier[0]) is None:
                    modifierJSON[modifier[0]] = {
                        "localisation": modifier[1],
                        "multiplier": float(modifier[2]),
                        "percent": bool(modifier[3].strip()),
                    }
            json.dump(modifierJSON, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


def imageCache(tradegood):
    imgDict = {}

    with open("image_cache.json", "r", encoding="utf8") as data:
        imgDict = json.load(data)
        if imgDict.get(tradegood) not in {None, ""}:
            return imgDict.get(tradegood)

    with open("image_cache.json", "w", encoding="utf8") as output:
        return _extracted_from_imageCache_10(tradegood, imgDict, output)


# TODO Rename this here and in `imageCache`
def _extracted_from_imageCache_10(tradegood, imgDict, output):
    img = str()

    img = gmImage(f"https://eu4.paradoxwikis.com/File:{tradegood}.png")
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood + '_mug222.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood[:3] + '_mug222.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood + '_d.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood[:4] + '.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood + '2.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood + '6.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood + 'a.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood[:3] + '.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood[:5] + '.png')
    # img = gmImage('https://eu4.paradoxwikis.com/File:' + tradegood[:-3] + '.png')
    if img == "https://central.paradoxwikis.com/images/a/a7/Ad_EU4_Emperor.png":
        img = ""
        print(tradegood)

    imgDict[tradegood] = img
    json.dump(imgDict, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    return img


def gmImage(url):
    time.sleep(1)
    # get contents from url
    content = requests.get(url).content
    # get soup
    soup = BeautifulSoup(content, "html.parser")
    # find the tag : <img ... >
    image_tags = soup.findAll("img")
    # print out image urls
    return image_tags[0].get("src")


def gmJSON(gmArray, name):
    text = ""

    tiers = [gmArray[i] for i in range(len(gmArray)) if type(gmArray[i]) == str]
    with open(f"{name}_reforms.json", "w", encoding="utf8") as output:
        for k in range(len(tiers) // 2):
            text += (
                f""""{tiers[k * 2 + 1]}"""
                + """": {
"""
            )
            for i in range(len(gmArray)):
                if type(gmArray[i]) != list:
                    continue
                if gmArray[i][1] is None:
                    continue
                if gmArray[i][2] != k:
                    continue

                link = "https://eu4.paradoxwikis.com/File:"

                if gmArray[i][4][-7:] == "_reform":
                    link += f"""Reform_{gmArray[i][4][:-7]}"""
                elif gmArray[i][4] in {
                    "kingdom_of_god",
                    "regionally_elected_commanders",
                }:
                    link += f"""Reform_{gmArray[i][4]}"""
                elif gmArray[i][4][-12:] == "_highlighted":
                    link += gmArray[i][4]
                else:
                    link += f"""Gov_{gmArray[i][4]}"""

                link += ".png"

                text += (
                    f"""    "{gmArray[i][1]}"""
                    + '''": {
        "Image": "'''
                    + gmImage(link)
                    + """",
        "Effects": {"""
                )
                if len(gmArray[i][6]) > 0:
                    for j in range(len(gmArray[i][6])):
                        if len(gmArray[i][6][j].split("=")) < 2:
                            continue
                        text = (
                            text
                            + '''
            "'''
                            + gmArray[i][6][j].split("=")[0].strip()
                            + """": """
                            + gmArray[i][6][j].split("=")[1].strip()
                            + """"""
                        )
                        if j != len(gmArray[i][6]) - 1:
                            text = f"""{text},"""
                text = (
                    text
                    + """
        }
    },
"""
                )
            text = (
                text[:-2]
                + """
},
"""
            )
        output.write(text[:-2])


def gmWiki(gmArray, name):
    tiers = [gmArray[i] for i in range(len(gmArray)) if type(gmArray[i]) == str]
    with open(f"eu4wiki_{name}.txt", "w", encoding="utf8") as output:
        text = """__NOTOC__
{{mod header|Governments Expanded}}

=[[Governments_Expanded/Monarchy|Monarchy]] | [[Governments_Expanded/Republic|Republic]] | [[Governments_Expanded/Theocracy|Theocracy]] | [[Governments_Expanded/Tribal|Tribal]]=

{| class="eu4box-inline mw-collapsible" style="text-align: center; margin: auto; max-width: 730px;"
|+ <span style="white-space: nowrap;">\'\'\'Reform Tiers\'\'\'</span>

"""
        for i in range(len(tiers) // 2):
            text = (
                text
                + """|-
! class="gridBG header" style="text-align: left; color: white; padding-left: 5px;" | Tier """
                + str(i + 1)
                + """: [[#"""
                + tiers[i * 2 + 1]
                + """|"""
                + tiers[i * 2 + 1]
                + """]]
|-
| {{box wrapper}}
"""
            )
            for j in range(len(gmArray)):
                if type(gmArray[j]) != list:
                    continue
                if gmArray[j][2] == i:
                    with contextlib.suppress(Exception):
                        if gmArray[j][4][-7:] == "_reform":
                            text = text + """{{Navicon|Reform_""" + gmArray[j][4][:-7]
                        elif gmArray[j][4] in {
                            "kingdom_of_god",
                            "regionally_elected_commanders",
                        }:
                            text = text + """{{Navicon|Reform_""" + gmArray[j][4]
                        elif gmArray[j][4][-12:] == "_highlighted":
                            text = text + """{{Navicon|""" + gmArray[j][4]
                        else:
                            text = text + """{{Navicon|Gov_""" + gmArray[j][4]
                        text = (
                            f"""{text}|{gmArray[j][1]}"""
                            + """}}
"""
                        )
                elif gmArray[j][2] > i:
                    text = (
                        text
                        + """{{end box wrapper}}

"""
                    )
                    break
        text = (
            text
            + """{{end box wrapper}}
|}

== Reform Tiers ==

"""
        )
        for i in range(len(tiers) // 2):
            text = (
                f"""{text}=== {tiers[i * 2 + 1]}"""
                + """ ===
{| class="mildtable sortable" style="width:100%"
! style="width:150px" | Type
! style="width:300px" class="unsortable" | Effects
! class="unsortable" | Description & notes

"""
            )
            for j in range(len(gmArray)):
                if type(gmArray[j]) != list:
                    continue
                if gmArray[j][2] == i:
                    if type(gmArray[j][1]) == str:
                        text = (
                            f"""{text}|- id="{gmArray[j][1]}"""
                            + """"
| \'\'\'"""
                            + gmArray[j][1]
                            + """\'\'\'
|
"""
                        )
                        for k in range(len(gmArray[j][6])):
                            text = f"{text}* {gmArray[j][6][k]}" + "\n"
                        text = (
                            text
                            + """|
{{desc|"""
                            + gmArray[j][1]
                            + """|"""
                            + gmArray[j][3]
                            + "|image="
                        )
                        if gmArray[j][4][-7:] == "_reform":
                            text = f"{text}Reform_{gmArray[j][4][:-7]}" + "}}\n"
                        elif gmArray[j][4] in {
                            "kingdom_of_god",
                            "regionally_elected_commanders",
                        }:
                            text = f"{text}Reform_{gmArray[j][4]}" + "}}\n"
                        elif gmArray[j][4][-12:] == "_highlighted":
                            text = text + gmArray[j][4] + "}}\n"
                        else:
                            text = f"{text}Gov_{gmArray[j][4]}" + "}}\n"
                        for k in range(0, len(gmArray[j][8])):
                            text = f"{text}* {gmArray[j][8][k]}" + "\n"
                        text = text + "\n"
                elif gmArray[j][2] > i:
                    text = text + "|}\n"
                    break
        text = text + "|}\n\n[[Category:Governments Expanded]]"

        output.write(text)


def gmLocal(gmArray, gmText):
    skip = False
    for i in range(len(gmArray)):
        if skip:
            skip = False
            continue
        elif type(gmArray[i]) == str:
            gmArray[i + 1] = gmFind(gmArray[i], gmText)
            skip = True
        else:
            gmArray[i][1] = gmFind(gmArray[i][0], gmText)
            gmArray[i][3] = gmFind(f"{gmArray[i][0]}_desc", gmText)

    print(gmArray)


def gmFind(gmRef, gmText):
    for file in gmText:
        with open(file, "r+", encoding="utf8") as gmFile:
            for lineA in gmFile:
                lineA = lineA.split("#")[0].strip()
                if lineA.find(f"{gmRef}:") == 0:
                    # print(lineA)
                    return lineA.split('"', 1)[1].strip()[:-1]


def gmFilter(gmDir, gmText):
    gmArray = os.listdir(gmDir)
    return [gmDir + "\\" + file for file in gmArray if file.endswith(gmText)]


def gmReforms(gmArray, gm_reforms):
    for ref in gmArray:
        for file in gm_reforms:
            if type(ref) == str:
                break
            with open(file, "r+") as gmFile:
                for lineA in gmFile:
                    lineA = lineA.split("#")[0]
                    if lineA.find(ref[0]) == 0:
                        ref.extend(["", "", "", "", "", ""])
                        for lineB in gmFile:
                            lineB = lineB.split("#")[0]
                            if lineB.find("icon") >= 0:
                                ref[4] = lineB.split("=")[1].strip()
                                if ref[4].find('"') >= 0:
                                    ref[4] = ref[4][1:-1]
                            elif lineB.find("modifiers") >= 0:
                                ref[6] = []
                                for lineC in gmFile:
                                    if lineC.find("}") == -1:
                                        ref[6].append(lineC.strip())
                                    else:
                                        break
                            elif lineB.find("custom_attributes") >= 0:
                                ref[8] = []
                                for lineC in gmFile:
                                    if lineC.find("}") == -1:
                                        ref[8].append(lineC.strip())
                                    else:
                                        break
                            elif lineB.find("}") == 0:
                                break
                        break
            if len(ref) > 4:
                break

    # print(gmArray)


def gmSort(gmArray, gmText, governments):
    with open(governments, "r+") as gmFile:
        for lineA in gmFile:
            lineA = lineA.split("#")[0]
            if lineA.find(gmText) == 0:
                num = 0
                for lineB in gmFile:
                    lineB = lineB.split("#")[0]
                    if lineB.strip() == "reforms = {":
                        for lineC in gmFile:
                            lineC = lineC.split("#")[0].strip()
                            if lineC.find("}") == 0:
                                num += 1
                                for lineD in gmFile:
                                    if lineD.find("}") >= 0:
                                        for lineE in gmFile:
                                            if lineE.find("}") < 0:
                                                gmArray.extend([lineE.split("=")[0].strip(), ""])
                                            break
                                    break
                                break
                            elif lineC != "":
                                gmArray.append([lineC, "", num, ""])
                    elif lineB.find("}") == 0:
                        break
                    elif lineB.find("reform_levels") >= 0:
                        for lineC in gmFile:
                            gmArray.extend([lineC.split("=")[0].strip(), ""])
                            break
                break

    # print(gmArray)


start()
