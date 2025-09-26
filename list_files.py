import os

def print_files_in_dir(directory: str, extensions=None):
    if extensions is None:
        extensions = [".py"]  # csak python fájlokat listáz alapból

    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                print("#" * 30, f" file {file} ", "#" * 30)
                with open(filepath, "r", encoding="utf-8") as f:
                    print(f.read())
                print()  # üres sor elválasztásnak

# Példa használat:
if __name__ == "__main__":
    print_files_in_dir("./engine")
