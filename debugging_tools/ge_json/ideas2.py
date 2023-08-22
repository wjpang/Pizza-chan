"""
Localise GE Reform Modifiers
By LoStack: https://github.com/stackpoint
"""

import codecs
import json
import os
import random
import re
import shutil


def start():
    eu4DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"

    tags = "tags.txt"
    ideas = "ideas.txt"
    data = "database.txt"

    ideasNIE1 = "monarchy_reforms.json"
    ideasNIE2 = "republic_reforms.json"
    ideasNIE3 = "theocracy_reforms.json"
    ideasNIE4 = "tribal_reforms.json"
    localDIR = eu4DIR + r"\localisation"
    modDIR = os.getcwd() + r"\localisation"

    # scLocal(tags, ideasNIE, [localDIR, modDIR], 1)
    # scLocal(ideas, ideasNIE, [modDIR, localDIR], 2)
    # scLocal(data, ideasNIE, [localDIR, modDIR], 3)

    scBuild(data, ideasNIE4)


def scBuild(data, ideasNIE):
    with open(ideasNIE, "r+", encoding="utf8") as ideasOut:
        with open(f"local_{ideasNIE}", "w", encoding="utf8") as output:
            bracket = 0
            for lineA in ideasOut:
                lineA2 = lineA.strip()
                if lineA.find("}") != -1:
                    bracket -= 1
                    output.write(lineA)
                    continue
                elif lineA2 == "":
                    output.write(lineA)
                    continue

                if bracket == 0 and lineA2.find("{") != -1:
                    bracket += 1
                    output.write(lineA)
                    continue

                if bracket > 0 and bracket < 4:
                    lineA3 = lineA2.split('"')[1]

                    if bracket == 1:
                        bracket += 1
                        output.write(lineA)
                        continue
                    elif bracket == 2:
                        if lineA.find("{") != -1:
                            bracket += 1
                        output.write(lineA)
                        continue
                    elif bracket == 3:
                        file = data

                    with open(file, "r+", encoding="utf8") as fileOut:
                        for lineB in fileOut:
                            lineB2 = lineB.split("\t")
                            if lineA3.casefold() == lineB2[0].casefold():
                                lineA4 = lineA.split(lineA3)
                                if bracket == 3:
                                    if lineB2[1] != "":
                                        output.write(lineA4[0] + lineB2[1].strip())
                                    else:
                                        output.write(lineA4[0] + lineB2[0].strip())
                                    lineA5 = lineA4[1].strip()
                                    if lineA5[-1] == ",":
                                        lineA5 = lineA5[:-1]
                                    if lineA5[-3:] == "yes" or lineA5[-2:] == "no":
                                        output.write(lineA4[1])
                                        break
                                    lineA6 = re.findall("-*[0-9]+\.*[0-9]*", lineA5)[-1]
                                    lineA7 = ""
                                    if lineB2[2].strip() != "1":
                                        lineA7 = str(float(lineA6) * float(lineB2[2]))
                                    if lineB2[3] == "True":
                                        if not lineA7:
                                            lineA7 = lineA6
                                        lineA7 = f"{lineA7}%"
                                    if lineA7 == "":
                                        output.write(lineA4[1])
                                    else:
                                        output.write(
                                            lineA4[1].split(lineA6)[0]
                                            + lineA7
                                            + lineA4[1].split(lineA6)[1]
                                        )
                                    break
                                elif lineB2[1] != "":
                                    output.write(lineA4[0] + lineB2[1].strip() + lineA4[1])
                                else:
                                    output.write(lineA)
                                break

                if lineA.find("{") != -1:
                    bracket += 1


def scLocal(outName, ideasNIE, DIR, level):
    with open(ideasNIE, "r+", encoding="utf8") as ideasOut:
        bracket = 0
        if level == 2:
            filenames = gmFilter(DIR[0], "yml")
            filenames.extend(gmFilter(DIR[1], "english.yml"))
        else:
            filenames = gmFilter(DIR[0], "english.yml")
            filenames.extend(gmFilter(DIR[1], "yml"))
        array = []
        for lineA in ideasOut:
            lineA = lineA.strip()
            if lineA.find("}") != -1:
                bracket -= 1
                continue
            elif lineA == "":
                continue
            if bracket == level:
                lineA2 = lineA.split('"')[1]
                if level == 2:
                    if lineA2.casefold() in {
                        "Ambition".casefold(),
                        "Tradition".casefold(),
                    }:
                        bracket += 1
                        continue
                elif level == 3:
                    flag = any(i[0].casefold() == lineA2.casefold() for i in array)
                    if flag:
                        continue

                array.append([lineA2, ""])

                if level == 3:
                    for i in range(9):
                        for file in filenames:
                            with open(file, "r+", encoding="utf8") as localOut:
                                for lineB in localOut:
                                    lineB = lineB.strip()
                                    if lineB.find(":") != -1:
                                        lineB2 = lineB.split(":", 1)
                                        if (
                                            (
                                                i == 5
                                                and lineB2[0].casefold() == array[-1][0].casefold()
                                            )
                                            or (
                                                i == 0
                                                and lineB2[0].casefold()
                                                == "MODIFIER_".casefold() + array[-1][0].casefold()
                                            )
                                            or (
                                                i == 7
                                                and lineB2[0].casefold() + "_MODIFIER".casefold()
                                                == array[-1][0].casefold()
                                            )
                                            or (
                                                i == 6
                                                and lineB2[0].casefold() + "_SPEED".casefold()
                                                == array[-1][0].casefold()
                                            )
                                            or (
                                                i == 1
                                                and lineB2[0].casefold()
                                                == array[-1][0].casefold() + "_MOD".casefold()
                                            )
                                            or (
                                                i == 4
                                                and array[-1][0].find("_") != -1
                                                and lineB2[0].casefold()
                                                == array[-1][0].split("_", 1)[0].casefold()
                                                + array[-1][0].split("_", 1)[1].casefold()
                                            )
                                            or (
                                                i == 2
                                                and lineB2[0].casefold() + "_MODIFIER".casefold()
                                                == "MODIFIER_".casefold() + array[-1][0].casefold()
                                            )
                                            or (
                                                i == 3
                                                and lineB2[0].casefold()
                                                == "YEARLY_".casefold() + array[-1][0].casefold()
                                            )
                                            or (
                                                i == 8
                                                and "GLOBAL_".casefold() + lineB2[0].casefold()
                                                == array[-1][0].casefold()
                                            )
                                        ):
                                            array[-1][1] = lineB2[1].split('"', 1)[1][:-1]
                                            break
                            if array[-1][1] != "":
                                break
                        if array[-1][1] != "":
                            break
                    array[-1].append(1)
                    array[-1].append(False)
                else:
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

            if lineA.find("{") != -1:
                bracket += 1

    with open(outName, "w", encoding="utf8") as output:
        for i in array:
            output.write(i[0] + "\t" + i[1])
            if level == 3:
                output.write("\t" + str(i[2]) + "\t" + str(i[3]))
            output.write("\n")

    print(array)


def gmFilter(gmDir, gmText):
    gmArray = os.listdir(gmDir)
    return [gmDir + "\\" + file for file in gmArray if file.endswith(gmText)]


start()
