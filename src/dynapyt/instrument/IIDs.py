from collections import namedtuple
from os import path
import json


Location = namedtuple(
    "Location", ["file", "start_line", "start_column", "end_line", "end_column"]
)


class IIDs:
    def __init__(self, file_path):
        if file_path.endswith(".py.orig"):
            file_path = file_path[:-8] + "-dynapyt.json"
        else:
            file_path = file_path[:-3] + "-dynapyt.json"
        if not path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({"next_iid": 0, "iid_to_location": {}}, f)
            self.next_iid = 0
            self.iid_to_location = {}
            self.location_to_iid = {}
        else:
            with open(file_path, "r") as file:
                json_object = json.load(file)
            self.next_iid = json_object["next_iid"]
            self.iid_to_location = {
                int(k): Location(**v) for k, v in json_object["iid_to_location"].items()
            }
            self.location_to_iid = {
                Location(*v): k for k, v in self.iid_to_location.items()
            }
        self.file_path = file_path

    def new(self, file, start_line, start_column, end_line, end_column):
        this_location = Location(file, start_line, start_column, end_line, end_column)
        if this_location in self.location_to_iid:
            return self.location_to_iid[this_location]
        self.iid_to_location[self.next_iid] = this_location
        self.next_iid += 1
        return self.next_iid - 1

    def store(self):
        all_data = {
            "next_iid": self.next_iid,
            "iid_to_location": dict(
                map(
                    lambda item: (item[0], item[1]._asdict()),
                    self.iid_to_location.items(),
                )
            ),
        }
        json_object = json.dumps(all_data, indent=2)
        with open(self.file_path, "w") as file:
            file.write(json_object)
