from random import randint
from functools import partial 
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
Orange = ["Color", "Orange"]
All = ["Set", "All"]

def Add(x, y):
    return ["Act", "Add", x, y] #s, c
def Remove(x):
    return ["Act", "Remove", x] #s
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
                (Add(1,2), "Add $2 to $1"),
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
                    Add(Diff(With(Brown),Rightmost(All)), Orange),
                    Add(All, Orange)]


# set up hierarchy so we can tune the distribution as we want

# KEY
# ==================
# OUTPUT
# ACTION: output type 0
# COLOR: output type 1
# SET: output type 2

# INPUT
# NONE: input type 0
# COLOR: input type 1
# SET: input type 2
# SET-COLOR: input type 3
# SET-SET: input type 4
# ==================

# no valid functions: # (0, 0), (3, 1), (3, 2), (1, 1), (1, 0), (2, 1), (4, 1), (4, 0)

# only valid functions: (3, 0), (2, 0), (0, 1), (0, 2), (1, 2), (2, 2), (4, 2)

func_defs = {'add':(Add, 3, 0, 1), 'remove': (Remove, 2, 0, 1), 'cyan':(Cyan, 0, 1, 0), 'brown': (Brown, 0, 1, 0), 'orange': (Orange, 0, 1, 0), 'red': (Red, 0, 1, 0),
'all': (All, 0, 2, 0), 'with': (With, 1, 2, 1), 'not': (Not, 2, 2, 1), 'diff': (Diff, 4, 2, 1), 'leftmost': (Leftmost, 2, 2, 1), 'rightmost': (Rightmost, 2, 2, 1)}

valid_input_output_func_types = [(3, 0), (2, 0), (0, 1), (0, 2), (1, 2), (2, 2), (4, 2)]

# organize based on output
# (function, input_type, output_type, added_depth)
# added_depth just means how many more layers of a tree will be added. 
# basically, functions which take in no arguments add zero extra layers, 
# and functions which take in any amount of arguments will add 1 extra layer. 
action_funcs = ['add', 'remove']
color_funcs = ['cyan', 'brown', 'orange', 'red']
set_funcs = ['all', 'with', 'not', 'diff', 'leftmost', 'rightmost']

all_funcs1 = [action_funcs, color_funcs, set_funcs]

input_func_dict = {0:['all', 'cyan', 'brown', 'orange', 'red'], 1: ['with'], 2: ['remove', 'not', 'leftmost', 'rightmost'], 3: ['add'], 4: ['diff']}
output_func_dict = {0: action_funcs, 1: color_funcs, 2: set_funcs}

# maps from input_type to a list of function argument (use output_func_dict) in order
input_type_to_valid_func_outputs = {0: [], 1:[1], 2:[2], 3:[2, 1], 4:[2, 2]}

# func_type is a tuple (func_input_type, func_output_type) or None
# curr_depth keeps track of what depth the function is at
# max_depth is the maximum allowed depth
def build_random_func_recursive(input_type, output_type, curr_depth, max_depth):
    if (input_type, output_type) == (None, None):
        input_type, output_type = valid_input_output_func_types[randint(0, len(valid_input_output_func_types)-1)]
    elif (input_type == None) and (output_type != None):
        # can't recurse anymore at this point, must have final layer be something
        # with no inputs
        if curr_depth >= max_depth - 1:
            input_type = 0
        else:
            input_type = randint(0, 4)
            while((input_type, output_type) not in valid_input_output_func_types):
                input_type = randint(0, 4)
    elif (output_type == None) and (input_type is not None):
        output_type = randint(0, 2)
        while((input_type, output_type) not in valid_input_output_func_types):
            output_type = randint(0, 2)
    assert((input_type, output_type) in valid_input_output_func_types)
    function_class = all_funcs1[output_type]
    valid_funcs = filter(lambda fname: (func_defs[fname][1] == input_type), function_class)
    assert(((curr_depth == max_depth - 1) and (output_type == 0)) == False)
    if (curr_depth == max_depth - 1):
        valid_funcs2 = filter(lambda fname: (func_defs[fname][3] == 0), valid_funcs)
        valid_funcs = valid_funcs2
    assert(len(valid_funcs) >= 1)
    fname = valid_funcs[randint(0, len(valid_funcs) - 1)]
    f = func_defs[fname][0]
    # we have now picked a function (randomly) with correct input_type and correct output_type
    # now we need to look at the input_type, and use it to find the correct output_type for the elements of the recursion
    list_of_valid_funcs = input_type_to_valid_func_outputs[input_type]
    iterated_func_application = [f]
    for arg_num in range(len(list_of_valid_funcs)):
        curr_arg_type = list_of_valid_funcs[arg_num]
        curr_arg = build_random_func_recursive(None, curr_arg_type, curr_depth + 1, max_depth)
        if arg_num < len(list_of_valid_funcs) - 1:
            curr_app = partial(iterated_func_application[arg_num], curr_arg)
        else:
            curr_app = iterated_func_application[arg_num](curr_arg)
        iterated_func_application.append(curr_app)
    return iterated_func_application[len(iterated_func_application)-1]




# generates a bunch of test instructions automatically
# then runs toNLUsingRules on the test instructions
# the pairs are the data (program, natural language)
# N is number of datapoints to generate
# T is max tree depth
def generate_program_nl_data(N, T):
    data = []
    for i in range(N):
        # generate new tree
        tree = build_random_func_recursive(None, None, 0, T)
        tree_str = toNLUsingRules(blocksRules1, tree)
        print("tree: " + str(tree) + ", " + "tree_str: " + tree_str)
        data.append((tree, tree_str))
    return data



if __name__=='__main__':
    generate_program_nl_data(30, 6)
    #for tree in testInstructions:
    #    print(toNLUsingRules(blocksRules1, tree))
