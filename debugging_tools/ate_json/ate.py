import json
import os
import re

ATE_PATH = "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\236850\\2737385499\\common\\advisortypes"
ATE_PATH = "A:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\236850\\2737385499\\common\\advisortypes"


def _handle_duplicates(ordered_pairs):
    res = {}
    for key, val in ordered_pairs:
        if key in res:
            if isinstance(res[key], list):
                res[key].append(val)
            else:
                res[key] = [res[key], val]
        else:
            res[key] = val
    return res


def main():
    """Main function."""
    with open(f"{ATE_PATH}\\advisor_types_expanded_advisor_types.txt", "r", encoding="utf-8") as f:
        data = f.read()

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)", "\n", data, flags=re.MULTILINE)  # Seperate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"free=yes", "", data)  # Remove free=yes

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
    data = re.sub(r"(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{\n]+", r'"\g<0>"', data)  # Add quotes around string values
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

    # Other replaces not caught by the regex subs above
    data = data.replace("5_gov_cap_bonus_flag", '"5_gov_cap_bonus_flag"')

    json_data = json.loads(data, object_pairs_hook=_handle_duplicates)

    intermediate = {
        "ADM": {},
        "DIP": {},
        "MIL": {},
    }

    # Load ATE localisation
    with open(f"{os.path.dirname(os.getcwd())}\\localisation\\emf_loc.json", "r", encoding="utf-8") as f:
        loc = json.load(f)["ATE"]["advisor_types_expanded_l_english.yml"]
    # Load modifier localisation
    with open(f"{os.path.dirname(os.getcwd())}\\localisation\\modifiers\\modifiers.json", "r", encoding="utf-8") as f:
        mod_loc = json.load(f)

    for key in json_data:
        # Remove unnecessary keys
        del json_data[key]["chance"]
        del json_data[key]["ai_will_do"]
        if "allow_only_male" in json_data[key]:
            del json_data[key]["allow_only_male"]
        if "allow_only_owner_religion" in json_data[key]:
            del json_data[key]["allow_only_owner_religion"]

        # Remove universal scaled modifiers
        for i, scaled_modifier in enumerate(json_data[key]["skill_scaled_modifier"]):
            try:
                if (
                    ("has_government_mechanic" in scaled_modifier["trigger"]["owner"] and scaled_modifier["trigger"]["owner"]["has_government_mechanic"] == "russian_modernization")
                    or (
                        "has_government_attribute" in scaled_modifier["trigger"]["owner"]
                        and scaled_modifier["trigger"]["owner"]["has_government_attribute"] in {"reform_progress_from_advisors", "republican_tradition_from_advisors"}
                    )
                    or (
                        "has_country_flag" in scaled_modifier["trigger"]["owner"]
                        and scaled_modifier["trigger"]["owner"]["has_country_flag"]
                        in {
                            "5_gov_cap_bonus_flag",
                            "fin_fine_finances_flag",
                            "mng_dev_per_adm_advisor_level_flag",
                            "jap_dip_advisor_culture_conversion_cost_flag",
                            "mng_trade_eff_per_dip_advisor_level_flag",
                        }
                    )
                    or ("has_country_modifier" in scaled_modifier["trigger"]["owner"] and scaled_modifier["trigger"]["owner"]["has_country_modifier"] == "eng_foreign_religious_control")
                    or (key != "ate_advisor_imperial_bureaucrat" and "is_emperor_of_china" in scaled_modifier["trigger"]["owner"] and scaled_modifier["trigger"]["owner"]["is_emperor_of_china"])
                ):
                    json_data[key]["skill_scaled_modifier"][i] = None
            except KeyError:
                continue

        # Remove Nones from json_data[key]["skill_scaled_modifier"]
        json_data[key]["skill_scaled_modifier"] = [non_null for non_null in json_data[key]["skill_scaled_modifier"] if non_null is not None]

        # Remove skill_scaled_modifier if list is empty
        if len(json_data[key]["skill_scaled_modifier"]) == 0:
            del json_data[key]["skill_scaled_modifier"]
        else:
            json_data[key]["skill_scaled_modifier"] = json_data[key]["skill_scaled_modifier"][0]["modifier"]

        # Localise key
        key_localised = loc[key][6:].title()

        # Organise by MP type
        intermediate[json_data[key]["monarch_power"]][key_localised] = json_data[key]
        del intermediate[json_data[key]["monarch_power"]][key_localised]["monarch_power"]

    final = {
        "ADM": {},
        "DIP": {},
        "MIL": {},
    }

    # Localise modifiers
    for mp_type, advisors in intermediate.items():
        for advisor, modifiers in advisors.items():
            final[mp_type][advisor] = {}
            for modifier in modifiers:
                if modifier != "skill_scaled_modifier":
                    final[mp_type][advisor][mod_loc[modifier]] = intermediate[mp_type][advisor][modifier]
                else:
                    final[mp_type][advisor]["Skill Scaled Modifier"] = intermediate[mp_type][advisor][modifier]
                    for key, val in list(intermediate[mp_type][advisor][modifier].items()):
                        final[mp_type][advisor]["Skill Scaled Modifier"][mod_loc[key]] = val
                        del final[mp_type][advisor]["Skill Scaled Modifier"][key]

    with open(f"{os.path.dirname(os.path.dirname(os.getcwd()))}\\data\\ATE.json", "w", encoding="utf-8") as output:
        json.dump(final, output, indent="\t", separators=(",", ": "), ensure_ascii=False)


if __name__ == "__main__":
    main()
