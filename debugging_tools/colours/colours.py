import itertools

# Generate all possible color combinations in RGB mode
colors = list(itertools.product(range(0, 256, 10), range(0, 256, 10), range(0, 256, 10)))

# Open a file for writing
with open("color_combinations_reduced10.txt", "w") as f:
    # Write each color combination to the file
    f.write("apply_random_country_color = {\n\trestore_country_color = yes\n\trandom_list={")
    for color in colors:
        f.write("\n\t\t1 = { change_country_color = { color = { ")
        f.write(f"{color[0]} {color[1]} {color[2]}")
        f.write(" } } }")
    f.write("\n	}\n}")
