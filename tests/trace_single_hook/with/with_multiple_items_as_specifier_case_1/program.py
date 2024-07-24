import os

dir_name = os.path.dirname(os.path.realpath(__file__))
file_path_one = os.path.join(dir_name, "expected.txt")
file_path_two = os.path.join(dir_name, "analysis.py")

file1 = open(file_path_one, "r")
file2 = open(file_path_two, "r")
with file1, file2:
    content = file1.readline()
    print("Line read from expected.txt: " + content)
    content = file2.readline()
    print("Line read from analysis.py: " + content)
    print("content has been read from the files")





