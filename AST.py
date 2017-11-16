
"""
#this changes d
def changeDict(d):
    d[1]=1

def changeDict2(d):
    #THIS WILL MODIFY d too
    #e=dict(d)
    e = d.copy()
    e[2]=2

def cd3(d):
    #DOES NOT MODIFY d
    d={1:1}

def cd4(d):
    d[1]=1
    d={}
    #d={1:1}
"""

def matchLists(tree, rule, indict):
    if type(tree) is not list:
        return (False, indict)
    d = indict.copy()
    for i in range(len(tree)):
        #print(tree[i], rule[i])
        j = rule[i]
        if type(j) is list:
            #recursively match
            (success, d) = matchLists(tree[i], j, d)
            if not success:
                return (False, indict)
        elif type(j) is int:
            d[j]=tree[i]
        elif tree[i]!=rule[i]:
            return (False, indict)
    return (True, d)

"""
def replaceArgs(string, d):
    #iterates over keys
    for k in d:
        print(string, k, d[k])
        string = string.replace("$"+str(k), d[k])
    return string
"""

# top down
# [(pattern, String)] * Tree -> String 
def toNLUsingRules(rlist, tree):
    d={}
    for (rule, string) in rlist:
        (success, d) = matchLists(tree, rule, d)
        if success:
            for k in d:
                if type(d[k])==list:
                    #print(d[k])
                    d[k] = toNLUsingRules(rlist, d[k])
                    #print(d[k])
                #print(string, k, d[k])
                string = string.replace("$"+str(k), d[k])
            #return replaceArgs(string, d)
            return string
    return None #failed

Cyan = ["Color", "Cyan"]
Brown = ["Color", "Brown"]
Red = ["Color", "Red"]
Orange = ["Color", "Orance"]

def Add(x, y):
    return ["Act", "Add", x, y] #s, c
def Remove(x):
    return ["Act", "Remove", x] #s
All = ["Set", "All"]
def With(x):
    return ["Set", "With", x] #c
def Not(x):
    return ["Set", "Not", x] #s
def Diff(x,y):
    return ["Set", "Diff", x, y] #s, s
def Leftmost(x):
    return ["Set", "Leftmost", x] #s
def Rightmost(x):
    return ["Set", "Rightmost", x] #s

blocksRules1 = [(Cyan, "cyan"),
                (Brown, "brown"),
                (Red, "red"),
                (Orange, "orange"),
                (Add(1,2), "Add $1 to $2"),
                (Remove(1), "Remove $1"),
                (All, "all blocks"),
                (With(1), "$1 blocks"),
                (Not(1), "All but $1"),
                (Diff(1,2), "$1 that are not $2"),
                (Leftmost(All), "leftmost block"),
                (Rightmost(All), "rightmost block"),
                (Leftmost(1), "leftmost $1"),
                (Rightmost(1), "rightmost $1")]

testInstructions = [Cyan,
    Add(With(Cyan),Orange),
                    Remove(With(Brown)),
                    Add(Leftmost(With(Orange)), Red),
                    Add(All, Brown),
                    Remove(Leftmost(All)),
                    Add(Diff(With(Brown),Rightmost(All)), Orange)]

if __name__=='__main__':
    for tree in testInstructions:
        print(toNLUsingRules(blocksRules1, tree))
