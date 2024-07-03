import os

try:
    dir_name = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_name, "expected.txt")
    file = open(file_path, "r")
    with file:
        content = file.readline()
        print("Line read from expected.txt: " + content)
        print("content has been read from the file")

    file.readline()
except Exception as e:
    print("An error occurred: ", e)




