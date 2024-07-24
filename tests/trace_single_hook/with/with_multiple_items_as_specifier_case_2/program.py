import os

dir_name = os.path.dirname(os.path.realpath(__file__))
file_path_one = os.path.join(dir_name, "expected.txt")
file_path_two = os.path.join(dir_name, "expected.txt")
file_path_three = os.path.join(dir_name, "analysis.py")

file1 = open(file_path_one, "r")
file3 = open(file_path_three, "r")
with file1, open(file_path_two, "r") as file2, file3:
    content = file1.readline()
    print("Line read from expected.txt: " + content)
    content = file2.readline()
    print("Line read from expected.txt: " + content)
    content = file3.readline()
    print("Line read from analysis.py: " + content)
    print("content has been read from the files")





