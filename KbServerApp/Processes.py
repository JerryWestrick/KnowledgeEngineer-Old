import jsonpickle as jsonpickle
from step import Step


def ProcessList_save(pl):
    # Write JSON data with Unicode characters to file
    file_path = "ProcessList.json"
    process_list_json = jsonpickle.encode(pl, indent=2)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(process_list_json)


def ProcessList_load() -> dict[str, list[Step]]:
    file_path = "ProcessList.json"
    with open(file_path, "r") as read_file:
        file_string = read_file.read()
    jo = jsonpickle.decode(file_string)
    pl = {}
    for key in sorted(jo.keys()):
        pl[key] = jo[key]
    return pl


ProcessList: dict[str, list[Step]] = ProcessList_load()
