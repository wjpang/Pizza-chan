import json
import os
import re
import time
import tkinter as tk
from os.path import basename
from tkinter import filedialog, messagebox

parent = r"C:\Users\AlexI\Dropbox\Pizza-chan\debugging_tools"

tags = parent + r"\\tags.txt"
ideas = parent + r"\ideas.txt"
data = parent + r"\database.json"

file_path_var = None


def center_window(width, height):
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (width / 2))
    y_coordinate = int((screen_height / 2) - (height / 2))
    app.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def FEE():
    sub_frame.config(text="Check Traces in Scenario")

    # Clear any existing widgets in the sub_frame
    for widget in sub_frame.winfo_children():
        widget.destroy()

    # Add new widgets to the sub_frame
    label = tk.Label(sub_frame, text="Hello There", justify="left")
    label.pack(pady=10)

    # Create a frame to hold the Label, Entry, and Submit Button widgets
    entry_frame = tk.Frame(sub_frame)
    entry_frame.pack(pady=10)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(entry_frame, text="Annex:")
    label_text.pack(side=tk.LEFT)

    entry = tk.Entry(entry_frame, label_text="Hello")
    entry.pack(side=tk.LEFT, padx=10)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(entry_frame, text="Choose Annex")
    submit_button.pack(side=tk.LEFT, padx=10)


def GME():
    messagebox.showinfo("Function 2 called", "Under Development")


def HIE():
    mod_dir = r"A:\Program Files (x86)\Steam\steamapps\workshop\content\236850\2804377099"
    finalpath = os.path.dirname(parent) + r"\data\HIE_country_ideas.json"

    ideas_hie_out_be4_json = mod_dir + r"\common\ideas\HIE_country_ideas.txt"
    ideas_hie = "HIE_country_ideas.json"
    localisation_dir = mod_dir + r"\localisation"

    sub_frame.config(text="Check Traces in Scenario")

    # Clear any existing widgets in the sub_frame
    for widget in sub_frame.winfo_children():
        widget.destroy()

    # Add new widgets to the sub_frame
    label = tk.Label(sub_frame, text="Historical Ideas Expanded", justify="left")
    label.pack(pady=10)

    # Create a frame to hold the Label, Entry, and Submit Button widgets
    entry_frame = tk.Frame(sub_frame)
    entry_frame.pack(pady=50)
    second_entry_frame = tk.Frame(sub_frame)
    second_entry_frame.pack(pady=100)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(entry_frame, text="Ideas.txt file:")
    label_text.pack(side=tk.LEFT)

    global file_path_var  # Access the global variable

    entry = tk.Entry(entry_frame, textvariable=file_path_var)
    entry.pack(side=tk.LEFT, padx=10)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(entry_frame, text="Choose file", command=lambda: process_file(entry))
    submit_button.pack(side=tk.LEFT, padx=10)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(entry_frame, text="Localisation Folder:")
    label_text.pack(side=tk.LEFT)

    entry = tk.Entry(entry_frame, textvariable=file_path_var)
    entry.pack(side=tk.LEFT, padx=10)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(entry_frame, text="Choose folder", command=lambda: process_file(entry))
    submit_button.pack(side=tk.LEFT, padx=10)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(second_entry_frame, text="Json Parser")
    label_text.pack(side=tk.LEFT)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(
        second_entry_frame,
        text="Create the Json file",
        command=lambda: JsonParser(ideas_hie_out_be4_json),
    )
    submit_button.pack(side=tk.LEFT, padx=10)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(second_entry_frame, text="Extrapolate Localisation")
    label_text.pack(side=tk.LEFT)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(
        second_entry_frame,
        text="Create the ideas.txt file",
        command=lambda: create_ideas(ideas_hie, ideas, localisation_dir),
    )
    submit_button.pack(side=tk.LEFT, padx=10)

    # Add Label and Entry widgets side by side
    label_text = tk.Label(second_entry_frame, text="Build Final Json")
    label_text.pack(side=tk.LEFT)

    # Add the Submit button and associate it with process_file function
    submit_button = tk.Button(
        second_entry_frame,
        text="Create the ideas.txt file",
        command=lambda: buildHIEideas(ideas_hie, tags, data, ideas, localisation_dir, finalpath),
    )
    submit_button.pack(side=tk.LEFT, padx=10)


def process_file(entry_widget):
    file_path = entry_widget.get()


app = tk.Tk()
app.title("Multiple Buttons App")
app.geometry("1280x720")

center_window(1280, 720)

# Create a frame to hold the buttons on the left
buttons_frame = tk.Frame(app, width=50, bg="lightgray")
buttons_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create a canvas to put buttons_frame inside
canvas = tk.Canvas(buttons_frame, bg="lightgray", width=150)
canvas.pack(side=tk.LEFT, fill=tk.Y)

# Create a scrollbar for the canvas
scrollbar = tk.Scrollbar(buttons_frame, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create a frame inside the canvas to hold the buttons
frame_in_canvas = tk.Frame(canvas, bg="lightgray")
canvas.create_window((0, 0), window=frame_in_canvas, anchor="nw")

# Create buttons and associate them with their respective functions
button1 = tk.Button(frame_in_canvas, text="Flavour Events Expanded", command=FEE)
button1.pack(pady=25, expand=True, fill="both")

button2 = tk.Button(frame_in_canvas, text="Great Monuments Expanded", command=GME)
button2.pack(pady=25, expand=True, fill="both")

button3 = tk.Button(frame_in_canvas, text="Historical Ideas Expanded", command=HIE)
button3.pack(pady=25, expand=True, fill="both")

# Create a frame to display the sub-interface on the right
sub_frame = tk.LabelFrame(app, text="Validation Tools", width=600, height=400)
sub_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

sub_label = tk.Label(sub_frame, text="")
sub_label.pack(pady=50)

app.mainloop()


def JsonParser(ideas_hie_out_be4_json):
    try:
        file = open(ideas_hie_out_be4_json, "r")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print(f"ERROR: Unable to find file: {ideas_hie_out_be4_json}")
        return None

    file_name = basename(ideas_hie_out_be4_json)

    data = re.sub(r"#.*", "", data)  # Remove comments
    data = re.sub(
        r"(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)",
        "\n",
        data,
        flags=re.MULTILINE,
    )  # Separate one line lists
    data = re.sub(r"[\t ]", "", data)  # Remove tabs and spaces
    data = re.sub(r"free=y.*", "", data)  # Remove tabs and spaces

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

    file_name = basename(ideas_hie_out_be4_json)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        print(f"ERROR: Unable to parse {file_name}")
        print("Dumping intermediate code into file: {}_{:.0f}.intermediate".format(file_name, time.time()))

        with open("./output/{}_{:.0f}.intermediate".format(file_name, time.time()), "w") as output:
            output.write(data)

        return None

    with open(f"{file_name[:-4]}.json", "w") as file:
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


def gmFilter(gm_dir, gm_text):
    gm_array = os.listdir(gm_dir)
    return [gm_dir + "\\" + file for file in gm_array if file.endswith(gm_text)]


def create_ideas(ideas_hie, ideas, localisation_dir):
    with open(ideas_hie, "r+", encoding="utf8") as ideas_out:
        idea_lib = json.load(ideas_out)
        array = []

        filenames = gmFilter(localisation_dir, "yml")
        filenames.extend(gmFilter(localisation_dir, "english.yml"))

        for i in idea_lib:
            for j in idea_lib[i]:
                if j in {"start", "bonus", "trigger", "free"}:
                    continue
                array.append([j, ""])
                for file in filenames:
                    with open(file, "r+", encoding="utf8") as localOut:
                        for line_b in localOut:
                            line_b = line_b.strip()
                            if line_b.find(":") != -1:
                                lineB2 = line_b.split(":", 1)
                                if array[-1][0].casefold() == "mfa_byzantine_claimants":
                                    array[-1][1] = "Last Claimants of Byzantium"
                                elif lineB2[0].casefold() == array[-1][0].casefold():
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
    print("succesfully created the localisation file")


def buildHIEideas(ideas_hie, tags, data, ideas, localisation_dir, finalpath):
    # create ideas.txt (Basically just call the create_ideas function)
    create_ideas(ideas_hie, ideas, localisation_dir)

    # create/populate local_country_ideas json
    with open(ideas_hie, "r+", encoding="utf8") as ideas_out:
        idea_lib = json.load(ideas_out)
        idea_lib2 = {}

        for i in idea_lib:
            with open(tags, "r+", encoding="utf8") as tags_loc:
                i_a = i[4:-6]

                for tagline in tags_loc:
                    tag_a = tagline.split("\t")
                    if tag_a[0] == i_a:
                        i_a = tag_a[1].strip()
                        break

                idea_lib2[i_a] = {}

                for j in idea_lib[i]:
                    if j == "trigger":
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

                        idea_lib2[i_a].update({jA: {}})

                        for k in idea_lib[i][j]:
                            with open(data, "r+", encoding="utf8") as dataLoc:
                                kA = k

                                for dataline in dataLoc:
                                    datA = dataline.split("\t")
                                    if datA[0] == kA:
                                        kA = datA[1].strip()
                                        break

                                idea_lib2[i_a][jA].update({kA: idea_lib[i][j][k]})

        with open(f"{os.path.dirname(finalpath)}\\HIE_country_ideas.json", "w", encoding="utf-8") as output:
            json.dump(idea_lib2, output, indent="\t", separators=(",", ": "), ensure_ascii=False)  # , sort_keys=True)
    print("succesfully created the final Json")
