import os
import re
import pyperclip

if __name__ == '__main__':
    # 提取可能点集
    f = open("possible.txt", "r")
    poss = [re.findall(r"\d", i) for i in f.readlines()]
    dim = len(poss[0])

    with open("C:/Users/Yeon/TT.txt", "w") as f:
        f.write(f".i {dim}\n.o 1\n")
        for pi in poss:
            for j in pi:
                f.write(j)
            f.write("|1\n")
    os.system('"C:/Users/Yeon\MILES.exe"')
    end = input()

    f = open("C:/Users/Yeon/LinearInequalities.txt", "r")
    coef = f.readlines()
    coef = [ci.split(" ") for ci in coef]
    Tans = {"0": 0, "+": 1, "-": -1}
    # print(coef)
    result = [[0 for j in range(dim + 1)] for i in range(1, len(coef))]
    for i in range(1, len(coef)):
        for j in range(dim):
            result[i - 1][j] = Tans[coef[i][j]]
        result[i - 1][dim] = -int(coef[i][dim].rstrip("\n"))
    print(result)
    print("sage:")
    for i in range(len(result)):
        result[i][-1] = -result[i][-1]
        result[i].append(0)
    for i in result:
        print(i)
