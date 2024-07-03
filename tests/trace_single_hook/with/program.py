import os

dir_name = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_name, "expected.txt")
with open(file_path, "r") as file:
    content = file.readline()
    print("Line read from expected.txt: ", content)
    print("content has been read from the file")

print("file has been closed")
