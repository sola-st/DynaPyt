import os

dir_name = os.path.dirname(os.path.realpath(__file__))
file_path_1 = os.path.join(dir_name, "expected.txt")
file_path_2 = os.path.join(dir_name, "analysis.py")
with open(file_path_1, "r") as file1, open(file_path_2, "r") as file2:
    content = file1.readline()
    print("Line read from expected.txt: ", content)
    content = file2.readline()
    print("Line read from analysis.py: ", content)
    print("content has been read from the files")

print("file has been closed")
