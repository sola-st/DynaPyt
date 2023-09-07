a = 30
if a < 20:
    b = 20
    while a < b:
        a += 1
        if a > 15:
            continue
        elif a < 35:
            break
        print(a)
else:
    print("a < 20")
