import csv
import utils
import numpy as np
from random import *
import sys

def add_to_dict(d, k, v):
    if k in d.keys():
        d[k] = d[k] + [v]
    else:
        d[k] = [v]
    return d

def get_from_dict(d,k):
    if k in d.keys():
        return d[k]
    else:
        return []

class CFG(object):
    def __init__(self, pdict, wdict):
        self.pdict=pdict
        self.wdict=wdict
        poss = pdict.keys()
        self.num_sym=len(poss)+1
        self.pos_to_num=dict(zip(poss, range(1,self.num_sym)))
        self.num_to_pos=['S']+poss
        print(self.pos_to_num)
        self.rules_dict = {}
        self.rules_list = set([])
    def rand_phrase(self, li, rules_dict=None, rule=None):
        #want to make sure it uses the rule...
        if rules_dict==None:
            rules_dict = self.rules_dict
        li2=[]
        for x in li:
            if x<= len(self.num_to_pos)+1 and x!=0 and (randint(0,1)==0 or not (x in self.pdict.keys()+[rule[0]])):
                pos = self.num_to_pos[x]
                words = self.pdict[pos]
                li2.append(words[randint(0,len(words)-1)])
            else:
                rules = get_from_dict(rules_dict,x)
                if rule != None and (x==rule[0] and (len(rules)==0 or randint(0,1)==0)):
                    li2 = li2 + self.rand_phrase([rule[1],rule[2]], rules_dict, rule)
                else:
                    li2 = li2+self.rand_phrase(list(rules[randint(0,len(rules)-1)]), rules_dict, rule)
        return li2
    def test_rules(self, newrules, runs=10):
        approved_rules=[]
        for rule in newrules:
            print("Testing rule", rule)
            for i in range(runs):
                temp_rules_dict = dict(self.rules_dict)
                add_to_dict(temp_rules_dict,rule[0], (rule[1],rule[2]))
                print(" ".join(self.rand_phrase([0], rule=rule))) 
                                                #temp_rules_dict)))
            print("Is this valid (Y/N)?")
            sys.stdout.flush()
            ans = raw_input()
            if ans != 'N':
                approved_rules.append(rule)
        return(approved_rules)
    def add_rules(self,li):
        for (x,y,z) in li:
            add_to_dict(self.rules_dict, x, (y,z))
        self.rules_list = self.rules_list | set(li)
    def parse(self, sent):
        print(sent)
        news = 1
        print("rules:", self.rules_dict,self.rules_list)
        words = sent.split(' ')
        w = len(words)
        mins = np.full((w,w,self.num_sym+news), np.inf)
        newrules = [[[[] for i in range(self.num_sym+news)] for j in range(w)] for k in range(w)]
        #newrules = np.ndarray.tolist(np.zeros((w,w,self.num_sym+2)))
        for i in range(w):
            for pos in self.wdict[words[i]]:
                n = self.pos_to_num[pos]
                mins[i,i,n] = 0
        for d in range(1,w):
            for s in range(0,w-d):
                for x in range(0,self.num_sym+news):
                    yzs = np.array([[[mins[s,t,y] + mins[t+1,s+d,z] + (0 if (y,z) in get_from_dict(self.rules_dict,x) else 1) for z in range(self.num_sym+news)] for y in range(self.num_sym+news)] for t in range(s,s+d)]) #OOB
                    # warning: this doesn't check if x->yz is already in newrules.
                    ns = [[[utils.list_union(newrules[s][t][y], newrules[t+1][s+d][z])+([] if (y,z) in get_from_dict(self.rules_dict,x) else [(x,y,z)]) for z in range(self.num_sym+news)] for y in range(self.num_sym+news)] for t in range(s,s+d)]
                    #find the min over yzs and take the corresponding ns's.
                    #print(yzs)
                    m = np.ndarray.min(yzs)
                    st = set([])
                    #print(yzs)
                    for i in range(0,d):
                        for j in range(self.num_sym+news):
                            for k in range(self.num_sym+news):
                                #print(yzs[i,j,k])
                                if yzs[i,j,k]==m:
                                    #print(ns[i][j][k])
                                    st = st | set(ns[i][j][k])
                    mins[s,s+d,x] = m
                    newrules[s][s+d][x] = list(st)
        print("%d rules need to be added" % mins[0,w-1,0])
        nr = newrules[0][w-1][0]
        print(nr)
        approved_rules = self.test_rules(nr,10)
        self.add_rules(approved_rules)
        num_sym = max([max(tup) for tup in self.rules_list]) + 1
        # now mins[0,w-1,0] is the minimum number of new rules needed to be added
        # and newrules[0,w-1,0] is a list of the rules that could be added

pos_dict = {}
word_dict = {}

with open('dict.csv', 'rb') as csvfile:
    vocab_reader = csv.reader(csvfile, delimiter=',')
    for row in vocab_reader:
        word = row[0]
        for p in row[1:]:
            add_to_dict(pos_dict, p, word)
            add_to_dict(word_dict, word, p)

print(pos_dict)
print(word_dict)

c = CFG(pos_dict,word_dict)

c.parse("cat drink")
c.parse("dog eat")
c.parse("dog eat dog")
c.parse("cat eat dog")
c.parse("big cat eat dog")
c.parse("big tall cat eat dog")
c.parse("dog go to house")
# won't create a new one because always better to use old...
c.parse("dog eat and drink")
