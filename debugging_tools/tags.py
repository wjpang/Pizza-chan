import os
import re
from distutils import text_file

eu4DIR = r"A:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV"
# eu4DIR = r'C:\Program Files\Epic Games\EuropaUniversalis4'  # This is for EGS. Ignore this --Vielor

culture_input = eu4DIR + "\common\cultures\\00_cultures.txt"
localisation_dir = eu4DIR + r"\localisation"
culture_output = "cultures_exported.txt"


def start():
    # buildtag(tag, [modDIR, localDIR])
    buildCultures(culture_input, culture_output, localisation_dir)


def buildCultures(input_file, culture_output, localized_folder):
    with open(input_file, "r") as file:
        data = file.read()

    current_group = None

    pattern_culture_group = re.compile(r"(\w+)\s*=\s*{")
    pattern_culture = re.compile(r"\s+(\w+)\s*=\s*{")

    culture_groups = []
    cultures = []
    localized_values = {}

    with open(culture_output, "w", encoding="utf-8") as out_file:
        for line in data.split("\n"):
            if (
                line.strip().startswith("female_names")
                or line.strip().startswith("male_names")
                or line.strip().startswith("dynasty_names")
                or line.strip().startswith("primary")
                or line.strip().startswith("graphical_culture")
                or line.strip().startswith("#")
                or line.strip().startswith("country")
                or line.strip().startswith("province")
            ):
                continue

            if line.startswith("}") and current_group:
                current_group = None

            if match_group := pattern_culture_group.match(line):
                current_group = match_group[1]
                culture_groups.append(current_group)

            match_culture = pattern_culture.match(line)
            if match_culture and current_group:
                culture_name = match_culture[1]
                cultures.append(culture_name)

        for filename in os.listdir(localized_folder):
            if filename.endswith("l_english.yml"):
                with open(
                    os.path.join(localized_folder, filename), "r", encoding="utf-8"
                ) as loc_file:
                    for line in loc_file:
                        line = line.strip()
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = (
                                value.strip()
                                .strip('"')
                                .replace('0 "', "")
                                .replace('1 "', "")
                                .replace('2 "', "")
                            )
                            localized_values[key] = value

        for group in culture_groups:
            localized_value = localized_values.get(group, "")
            out_file.write(f"{group}\t{localized_value}\n")

        for culture in cultures:
            localized_value = localized_values.get(culture, "")
            out_file.write(f"{culture}\t{localized_value}\n")


def buildtag(tag, DIR):
    with open(tag, "r+", encoding="utf8") as tagsOut:
        array = []

        filenames = gmFilter(DIR[0], "yml")
        filenames.extend(gmFilter(DIR[1], "english.yml"))

        for i in tagsOut:
            for j in tagsOut:
                if j[:1] == "#":
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

    with open("tags.txt", "w", encoding="utf8") as output:
        for i in array:
            output.write(i[0] + "\t" + i[1])
            output.write("\n")


def gmFilter(gmDir, gmText):
    gmArray = os.listdir(gmDir)
    return [gmDir + "\\" + file for file in gmArray if file.endswith(gmText)]


start()
