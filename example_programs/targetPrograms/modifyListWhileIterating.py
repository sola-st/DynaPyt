# inspired by https://www.toptal.com/python/top-10-mistakes-that-python-programmers-make

if __name__ == "__main__":
    '''
    Modifies a list while iterating over it, which is
    considered an anti-pattern in Python, but does not
    raise any exception.
    '''
    l = [0, 1, 2, 3]
    for i in range(len(l)):
        print(i)
        if i % 2 == 0:
            print("appending")
            l.append(7)
        else:
            print("deleting")
            del l[i]
        print(l[i])
    print("done")
