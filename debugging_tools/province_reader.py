import json

# Steam
# path = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\prov_names_l_english.yml'
# path2 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\00_lanfang_l_english.yml'
# path3 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\emperor_content_l_english.yml'
# path4 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\emperor_map_l_english.yml'
# path5 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\leviathan_l_english.yml'
# path6 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\manchu_l_english.yml'
# path7 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\north_america_redone_l_english.yml'
# path8 = r'D:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\localisation\nw2_l_english.yml'

# EGS
path0 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\prov_names_l_english.yml"
path1 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\00_lanfang_l_english.yml"
path2 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\emperor_content_l_english.yml"
path3 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\emperor_map_l_english.yml"
path4 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\leviathan_l_english.yml"
path5 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\manchu_l_english.yml"
path6 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\north_america_redone_l_english.yml"
path7 = r"C:\Program Files\Epic Games\EuropaUniversalis4\localisation\nw2_l_english.yml"

path_lst = [path0, path1, path2, path3, path4, path5, path6, path7]

province_lst = []
lst = ["PROV1", "PROV2", "PROV3", "PROV4", "PROV5", "PROV6", "PROV7", "PROV8", "PROV9"]

for i in range(8):
    with open(path_lst[i], "r", encoding="utf-8") as f:
        temp = f.readlines()

    for line in temp:
        for item in lst:
            if item in line:
                line.strip()
                line = line.replace("PROV", "")
                line = line.replace(":0 ", ":")
                line = line.replace(":1 ", ":")
                line = line.replace(":2 ", ":")
                line = line.replace(":3 ", ":")
                line = line.replace('"', "")
                line = line.replace("\n", "")
                line = line.split(":")
                line[0] = int(line[0])
                province_lst.append(line)

province_lst = sorted(province_lst, key=lambda x: x[0])

province_dict = dict(province_lst)

with open(r"debugging_tools\provinces.json", "w", encoding="utf-8") as f:
    json.dump(province_dict, f, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
