# import shutil
import json

# import random
# import codecs
import os
import re


def start():
    eu4DIR = r"D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
    # eu4DIR = r'C:\Program Files\Epic Games\EuropaUniversalis4'  # This is for EGS. Ignore this --Vielor

    modpath = r"D:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2262234791"
    pathfolder = os.getcwd()
    parent = os.path.dirname(pathfolder)

    tags = parent + "\\tags.txt"
    ideas = parent + "\ideas.txt"
    data = parent + "\database.txt"

    ateAdvisor = "advisor_types_expanded_advisor_types.json"
    localDIR = eu4DIR + r"\localisation"
    modDIR = modpath + r"\localisation"

    build(ateAdvisor, tags, data, ideas, [modDIR, localDIR])


def build(ateAdvisor, tags, data, ideas, DIR):
    # create ideas.txt (Basically just call the create_ideas function)
    create_ideas(ateAdvisor, ideas, DIR)

    # create/populate local_country_ideas json
    with open(ateAdvisor, "r+", encoding="utf8") as ideasOut:
        ideaLib = json.load(ideasOut)
        ideaLib2 = {}

        for i in ideaLib:
            with open(tags, "r+", encoding="utf8") as tagsLoc:
                iA = i

                for tagline in tagsLoc:
                    tagA = tagline.split("\t")
                    if tagA[0] == iA:
                        iA = tagA[1].strip()
                        break

                ideaLib2[iA] = {}

                for j in ideaLib[i]:
                    if j == "chance":
                        continue
                    if j == "ai_will_do":
                        continue

                    with open(ideas, "r+", encoding="utf8") as ideasLoc:
                        jA = j

                        for idealine in ideasLoc:
                            ideaA = idealine.split("\t")
                            if ideaA[0] == jA:
                                jA = ideaA[1].strip()
                                break

                        ideaLib2[iA].update({jA: {}})

                        for k in ideaLib[i][j]:
                            with open(data, "r+", encoding="utf8") as dataLoc:
                                kA = k

                                for dataline in dataLoc:
                                    datA = dataline.split("\t")
                                    if datA[0] == kA:
                                        kA = datA[1].strip()
                                        break

                                ideaLib2[iA][jA].update({kA: ideaLib[i][j][k]})

        with open("ATE", "w", encoding="utf8") as output:
            json.dump(ideaLib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


def create_ideas(ateAdvisor, ideas, DIR):
    with open(ateAdvisor, "r+", encoding="utf8") as ideasOut:
        ideaLib = json.load(ideasOut)
        array = []

        filenames = gmFilter(DIR[0], "yml")
        filenames.extend(gmFilter(DIR[1], "english.yml"))

        for i in ideaLib:
            for j in ideaLib[i]:
                if j in {"start", "bonus", "chance", "ai_will_do"}:
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


def gmFilter(gmDir, gmText):
    gmArray = os.listdir(gmDir)
    return [gmDir + "\\" + file for file in gmArray if file.endswith(gmText)]


start()
