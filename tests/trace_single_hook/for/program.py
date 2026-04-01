for i in range(10, -1, -1):
    print(i)
else:
    print("done!")

for i in range(10, -1, -1):
    print(i)
    if i % 3 == 0:
        break
else:
    print("done!")
