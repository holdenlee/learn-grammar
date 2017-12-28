from AST import *
from utils import *

def generate_rules(li):
    d = {}
    for f in li:
        nargs = len(f)-2
        nwords = len(f)-1
        argps = range(1,nargs+1)
        largps = map(lambda x:[x], argps)
        fname = f[1]
        if nargs > 0:
            binstrings = list_prod((nargs+1)*[[0,1]])
            #print(binstrings)
            rules = emap(lambda n,s: concat(alternate(emap(lambda m,x: [] if x==0 else [(fname,n,m)], s),largps)), binstrings)
            #print(rules)
        d[fname] = rules
    return d

"""
            rules = fors(list_prod(map(lambda n,i: [[],(str(f),i,
(nargs+1)*[0,1]), lambda li: alternate(map(lambda x: x, li), argps))
"""

#branch off rightmost each time
def convert_single_cnf(a, rhs, i, d): # add `hiddens` here?
    #what about length 1?
    if len(rhs)==2:
        d[(a,i)] = tuple(rhs) #need to add types
        return d
    for j in range(len(rhs)-2):
        if j==0:
            d[(a,'h',i,j)] = (rhs[0],rhs[1])
        else:
            d[(a,'h',i,j)] = ((a,'h',i,j-1), rhs[j+1])
    d[(a,i)] = ((a,'h',i,len(rhs)-3), rhs[-1])
    return d

#rules is a dictionary
def convert_cnf(rules):
    d = {}
    for a in rules:
        for (i,rhs) in enumerate(rules[a]):
            convert_single_cnf(a, rhs, i, d)
    return d

if __name__=='__main__':
    li = [Diff(1,2)]
    print(generate_rules(li))
    #[Remove(1), Diff(1,2), Add(1,2)]
    d = convert_cnf(generate_rules(li))
    #print(d)
    for k in d:
        print(k)
        print(" "+str(d[k]))

"""
class PCCG(Object):
    def __init__(self,n):
        self.a = {}
    def __get__(self, entry):
        (i,j)=entry
        if i==j:
"""        
        
