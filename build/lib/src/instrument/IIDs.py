from collections import namedtuple
from os import path
import json


Location = namedtuple("Location", ["file", "line", "column"])


class IIDs:
    def __init__(self, file_path):
        if file_path is None:
            file_path = "iids.json"
            self.next_iid = 1
            self.iid_to_location = {}
        else:
            with open(file_path, "r") as file:
                json_object = json.load(file)
            self.next_iid = json_object["next_iid"]
            self.iid_to_location = json_object["iid_to_location"]
        self.file_path = file_path

    def new(self, file, line, column):
        self.iid_to_location[self.next_iid] = Location(file, line, column)
        self.next_iid += 1
        return self.next_iid

    def store(self):
        all_data = {
            "next_iid": self.next_iid,
            "iid_to_location": self.iid_to_location,
        }
        json_object = json.dumps(all_data, indent=2)
        with open(self.file_path, "w") as file:
            file.write(json_object)