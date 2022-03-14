def convertdictToList(dict):
    list = []
    for x in dict:
        sp = ""
        sp2 = "   "
        for y in range(35 - len(dict[x][0])):
            sp = sp + " "
        if str(dict[x][1]).upper == "ABSENT":
            sp2 = "  "
        # print(sp, xn)
        list.append(str(x) + "       " +
                    str(dict[x][0] + sp + str(dict[x][1])) + sp2)
    return list


# convertdictToList({"hg": ["hgh", "jhj"], "ty": [1, 45]})

# dict = {"PUL075BCT065": ["Ravi Pandey", "Present"],
#         "PUL075BCT066": ["Rohan Chhetry", "Absent"]}
# for x in dict:
#     sp = ""
#     xn = 0
#     for y in range(30 - len(dict[x][0])):
#         sp = sp + " "
#         xn = xn+1
#     print(sp, xn)
#     print(str(x) + "    " + str(dict[x][0] + sp + str(dict[x][1])))
