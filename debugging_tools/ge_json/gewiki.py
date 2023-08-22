import codecs
import contextlib
import os
import random
import re
import shutil


def start():
    cwd = os.getcwd()
    governments = cwd + r"\common\governments\00_governments.txt"
    rText = cwd + r"\common\government_reforms"
    reforms = gmFilter(rText, "txt")
    rYml = cwd + r"\localisation"
    local = gmFilter(rYml, "yml")
    local.extend(
        gmFilter(
            r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation",
            "english.yml",
        )
    )

    monarchy = []
    republic = []
    tribal = []
    theocracy = []

    gmSort(monarchy, "monarchy", governments)
    gmSort(republic, "republic", governments)
    gmSort(tribal, "tribal", governments)
    gmSort(theocracy, "theocracy", governments)

    gmReforms(monarchy, reforms)
    gmReforms(republic, reforms)
    gmReforms(tribal, reforms)
    gmReforms(theocracy, reforms)

    gmLocal(monarchy, local)
    gmLocal(republic, local)
    gmLocal(tribal, local)
    gmLocal(theocracy, local)

    gmWiki(monarchy, "monarchy")
    gmWiki(republic, "republic")
    gmWiki(tribal, "tribal")
    gmWiki(theocracy, "theocracy")


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
                        for k in range(len(gmArray[j][8])):
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
