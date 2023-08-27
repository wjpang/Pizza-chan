import json
import os


def main():
    loc_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation"
    eng = [loc_dir + "\\" + file for file in os.listdir(loc_dir) if file.endswith("_l_english.yml")]
    tags_loc = {}
    for file in eng:
        with open(file, "r", encoding="utf-8") as f:
            loc = f.readlines()
        for line in loc:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            line = line.split(":")
            if line[0].isupper() and len(line[0]) == 3:
                tags_loc[line[0]] = (
                    line[1]
                    .replace('"', "")
                    .replace("0", "")
                    .replace("1", "")
                    .replace("2", "")
                    .replace("3", "")
                    .strip()
                )

    tag_file = r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\common\country_tags\00_countries.txt"
    with open(tag_file, "r", encoding="utf-8") as f:
        tag = f.readlines()
    tags_final = {}
    for line in tag:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        line = line.split("=")
        tags_final[line[0].strip()] = tags_loc[line[0].strip()]

    with open(f"{os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))}\\data\\tags\\tags.json", "w", encoding="utf-8") as f:
        json.dump(tags_final, f, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)


if __name__ == "__main__":
    main()
