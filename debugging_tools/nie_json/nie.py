import json
import re
import time
from os.path import basename


def json_parser(ideas_nie_out_be4_json):
    """json parser"""

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

    try:
        with open(ideas_nie_out_be4_json, "r", encoding="utf-8") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {ideas_nie_out_be4_json}")
        return None

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces

    if definitions := re.findall(r"(@\w+)=(.+)", data):  # replace @variables with value
        for definition in definitions:
            data = re.sub(r"^@.+", "", data, flags=re.MULTILINE)
            data = re.sub(definition[0], definition[1], data)

    data = re.sub(r"\n{2,}", "\n", data)  # Remove excessive new lines
    data = re.sub(r"\n", "", data, count=1)  # Remove the first new line
    data = re.sub(r"{(?=\w)", "{\n", data)  # reformat one-liners
    data = re.sub(r"(?<=\w)}", "\n}", data)  # reformat one-liners
    data = re.sub(
        r"^[\w-]+(?=[\=\n><])", r'"\g<0>"', data, flags=re.MULTILINE
    )  # Add quotes around keys
    data = re.sub(r"([^><])=", r"\1:", data)  # Replace = with : but not >= or <=
    data = re.sub(
        r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{\n]+", r'"\g<0>"', data
    )  # Add quotes around string values
    data = re.sub(r':"yes"', ":true", data)  # Replace yes with true
    data = re.sub(r':"no"', ":false", data)  # Replace no with false
    data = re.sub(r"([<>]=?)(.+)", r':{"value":\g<2>,"operand":"\g<1>"}', data)  # Handle < > >= <=
    data = re.sub(r"(?<![:{])\n(?!}|$)", ",", data)  # Add commas
    data = re.sub(r"\s", "", data)  # remove all white space
    data = re.sub(r'{(("[a-zA-Z_]+")+)}', r"[\g<1>]", data)  # make lists
    data = re.sub(r'""', r'","', data)  # Add commas to lists
    data = re.sub(r'{("\w+"(,"\w+")*)}', r"[\g<1>]", data)
    data = re.sub(
        r"((\"hsv\")({\d\.\d{1,3}(,\d\.\d{1,3}){2}})),", r"{\g<2>:\g<3>},", data
    )  # fix hsv objects
    data = re.sub(
        r":{([^}{:]*)}", r":[\1]", data
    )  # if there's no : between list elements need to replace {} with []
    data = re.sub(r"\[(\w+)\]", r'"\g<1>"', data)
    data = re.sub(r"\",:{", '":{', data)  # Fix user_empire_designs
    data = "{" + data + "}"

    file_name = basename(ideas_nie_out_be4_json)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError as e:
        print(e)
        print(f"ERROR: Unable to parse {file_name}")
        print(f"Dumping intermediate code into file: {file_name}_{time.time():.0f}.intermediate")

        with open(
            f"./debugging_tools/nie_json/{file_name}_{time.time():.0f}.intermediate",
            "w",
            encoding="utf-8",
        ) as output:
            output.write(data)

        return None

    with open(
        "./debugging_tools/nie_json/NIE_country_ideas" + ".json", "w", encoding="utf-8"
    ) as file:
        json.dump(json_data, file, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("Successfully created the json file")


if __name__ == "__main__":
    json_parser(r".\debugging_tools\nie_json\000_NIE_country_ideas.txt")
    with open(r".\debugging_tools\nie_json\NIE_country_ideas.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    lst = [d[ideas]["trigger"] for ideas in d]
    lst2 = []
    for i, trigger in enumerate(lst):
        try:
            lst[i] = trigger["tag"]
        except KeyError:
            lst2.extend(iter(trigger["OR"]["tag"]))
            lst[i] = ""
    lst2.remove("H")
    lst2.remove("A")
    lst2.remove("B")
    lst2.extend(("HAB", "STY"))
    lst = sorted([*set(lst + lst2)])[1:]
    print(lst)
    # print(lst2)
