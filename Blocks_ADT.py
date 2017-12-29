from ADT import *
from CCG import *

import pprint

#https://stackoverflow.com/questions/14078357/python-how-can-idynamically-create-a-function-with-a-name-based-on-a-string-re
def make_global_vars(d):
    for k in d:
        globals()[k] = d[k]

Color = 'Color'
Act = 'Act'
Set = 'Set'
cons_dict = {Color : {'Cyan':[],
                  'Brown':[],
                  'Red':[],
                  'Orange':[]},
         Set : {'All':[],
                'With':[Color],
                'Not':[Set],
                'Int':[Set,Set],
                'Leftmost':[Set],
                'Rightmost':[Set]},
         #Note I use Int=intersection rather than Diff as originally, because Diff(f,g)=Int(f,Not(g))
         Act : {'Add':[Set,Color],
                'Remove':[Set]}} 
d=create_PL(cons_dict)

if __name__=='__main__':
    pp = pprint.PrettyPrinter(indent=4)
    make_global_vars(d)
    print(Add(With(Cyan),Orange))
    li = create_CCG(d)
    pp.pprint(li)
    blocksRules1 = [(Cyan(), "cyan"),
                    (Brown(), "brown"),
                    (Red(), "red"),
                    (Orange(), "orange"),
                    (Add(1,2), "Add $2 to $1"),
                    (Remove(1), "Remove $1"),
                    (All(), "all blocks"),
                    (With(1), "$1 blocks"),
                    (Not(1), "not $1"),
                    #(Not(1), "all but $1"),
                    (Int(1,2), "$1 that are $2"),
                    #(Diff(1,2), "$1 that are not $2"),
                    (Leftmost(All()), "leftmost block"),
                    (Rightmost(All()), "rightmost block"),
                    (Leftmost(1), "leftmost $1"),
                    (Rightmost(1), "rightmost $1")]
    def Diff(x,y):
        return Int(x,Not(y))
    blocksRules2 = [(Cyan(), "cyan"),
                    (Brown(), "brown"),
                    (Red(), "red"),
                    (Orange(), "orange"),
                    (Add(1,2), "Add $2 to $1"),
                    (Remove(1), "Remove $1"),
                    (All(), "all blocks"),
                    (With(1), "$1 blocks"),
                    #(Not(1), "all but $1"),
                    (Diff(1,2), "$1 except $2"),
                    (Int(1,2), "$1 that are $2"),
                    (Not(1), "not $1"),
                    (Leftmost(All()), "leftmost block"),
                    (Rightmost(All()), "rightmost block"),
                    (Leftmost(1), "leftmost $1"),
                    (Rightmost(1), "rightmost $1")]

    testInstructions = [Cyan(),
                        Add(With(Cyan()),Orange()),
                        Remove(With(Brown())),
                        Add(Leftmost(With(Orange())), Red()),
                        Add(All(), Brown()),
                        Remove(Leftmost(All())),
                        Add(Diff(With(Brown()),Rightmost(All())), Orange()),
                        Add(All(), Orange())]
    for tree in testInstructions:
        print(toNLUsingRules(blocksRules1, tree))
        print(toNLUsingRules(blocksRules2, tree))

