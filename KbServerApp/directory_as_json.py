import os
import json


def generate_directory_structure(root_dir):
    dir_structure = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        subtree = dir_structure
        dirpath_parts = dirpath.split(os.sep)

        for part in dirpath_parts[1:]:
            subtree = subtree.setdefault(part, {})

        for dirname in dirnames:
            subtree.setdefault(dirname, {})

        for filename in filenames:
            path = os.path.join(dirpath, filename)
            with open(path, 'r') as f:
                content = f.read()
            subtree[filename] = content

    return dir_structure


root_dir = "Memory"  # replace this with your directory path
dir_structure = generate_directory_structure(root_dir)
json_content = json.dumps(dir_structure, indent=4)

print(json_content)
