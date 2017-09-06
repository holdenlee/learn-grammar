import csv
import utils
import numpy as np

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
        print(self.pos_to_num)
        self.rules_dict = {}
        self.rules_list = set([])
    def add_rules(self,li):
        for (x,y,z) in li:
            add_to_dict(self.rules_dict, x, (y,z))
        self.rules_list = self.rules_list | set(li)
    def parse(self, sent):
        words = sent.split(' ')
        w = len(words)
        mins = np.full((w,w,self.num_sym+2), np.inf)
        newrules = [[[[] for i in range(self.num_sym+2)] for j in range(w)] for k in range(w)]
        #newrules = np.ndarray.tolist(np.zeros((w,w,self.num_sym+2)))
        for i in range(w):
            for pos in self.wdict[words[i]]:
                n = self.pos_to_num[pos]
                mins[i,i,n] = 0
        for d in range(1,w):
            for s in range(0,w-d):
                for x in range(0,self.num_sym+2):
                    yzs = np.array([[[mins[s,t,y] + mins[t+1,s+d,z] + (0 if [y,z] in get_from_dict(self.rules_dict,x) else 1) for z in range(self.num_sym+2)] for y in range(self.num_sym+2)] for t in range(s,s+d)]) #OOB
                    # warning: this doesn't check if x->yz is already in newrules.
                    ns = [[[utils.list_union(newrules[s][t][y], newrules[t+1][s+d][z])+([] if (y,z) in get_from_dict(self.rules_dict,x) else [(x,y,z)]) for z in range(self.num_sym+2)] for y in range(self.num_sym+2)] for t in range(s,s+d)]
                    #find the min over yzs and take the corresponding ns's.
                    #print(yzs)
                    m = np.ndarray.min(yzs)
                    st = set([])
                    #print(yzs)
                    for i in range(s,s+d):
                        for j in range(self.num_sym+2):
                            for k in range(self.num_sym+2):
                                #print(yzs[i,j,k])
                                if yzs[i,j,k]==m:
                                    #print(ns[i][j][k])
                                    st = st | set(ns[i][j][k])
                    mins[s,s+d,x] = m
                    newrules[s][s+d][x] = list(st)
        print("%d rules need to be added" % mins[0,w-1,0])
        print(newrules[0][w-1][0])
        self.add_rules(newrules[0][w-1][0])
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
