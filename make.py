
file_name_list = [
    "daemonconfigfile",
    "shutdownscript",
    "powerbuttonscript",
    "daemonfanservice",
    "removescript",
    "configscript",
]
files: dict[str, list[str]]
files = {filename: [] for filename in file_name_list}

with open("argon1.sh") as f:
    for line in f:
        if line.lstrip().startswith("echo"):
            for filename in file_name_list:
                if line.endswith(filename):
                    line = (
                        line.lstrip()
                        .removeprefix("echo")
                        .lstrip()
                        .lstrip("\"'")
                        .removesuffix(filename)
                        .rstrip()
                        .removesuffix(">>")
                        .rstrip()
                        .rstrip("\"'")
                    )
                    files[filename].append(line)
for filename, lines in files.items():
    with open(filename, "w") as f:
        f.writelines(lines)