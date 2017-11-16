import csv
from utils import *
import numpy as np
from random import *
import sys
from grammar import *

def generate(c,rules, trules, start=0):
    m=rules.shape[0]
    t=trules.shape[1]
    to_samp = [([i,j],rules[start,i,j]) for i in range(m) for j in range(m)]+[([i], trules[start,i]) for i in range(t)]
    print('genprobs')
    print(to_samp)
    li = sample_wp(to_samp)
    if len(li)==1:
        return [c.pdict[c.num_to_pos[li[0]+1]]]
    else:
        return generate(c,rules, trules,li[0])+generate(c,rules,trules,li[1])

def io(rules, trules, sents,n):
    for i in range(n):
        (rules, trules) = em_step(rules, trules,sents)
    return (rules, truels)

def em_step(rules, trules, sents):
    (tc, tct) = counts(rules, trules, sents)
    m = rules.shape[0] # number of symbols
    t = trules.shape[1] # number of terminals
    q=np.zeros(shape(rules))
    qt=np.zeros(shape(trules))
    for a in range(m):
        s = sum([rules[a,b,c] for b in range(m) for c in range(m)]) + sum([trules[a,g] for g in range(t)])
        for b in range(m):
            for c in range(m):
                q = rules[a,b,c]/s
        for g in range(t):
            qt = rules[a,g]/s
    return (q,qt)    

def counts(rules, trules, sents):
    tc=0
    tct=0
    for sent in sents:
        (count, countt) = count1(rules, trules, sent)
        #print('count')
        #print(count, countt)
        tc += count
        tct += countt
    return (tc, tct)

def count1(rules, trules, sent,ep=0):
    l = len(sent)
    m = rules.shape[0] # number of symbols
    t = trules.shape[1] # number of terminals
    alpha = np.zeros(rules.shape)
    beta = np.zeros(rules.shape)
    count = np.zeros(rules.shape)
    countt = np.zeros((m,t))
    mu = np.zeros((m,l,l))
    for d in range(l):
        for i in range(l-d):
            for a in range(m):
                if d==0:
                    alpha[a][i][i] = trules[a][sent[i]]
                else:
                    j = i+d
                    alpha[a,i,j] = sum([rules[a,b,c]*alpha[b,i,k]*alpha[c,k+1,j] for b in range(m) for c in range(m) for k in range(i,j)])
    for d in reversed(range(l)): #or: range(start, stop, step)
        for i in range(l-d):
            j=i+d
            if d==l-1:
                #start symbol is 0
                beta[0,i,j] = 1
                mu[0,i,j]= alpha[0,i,j]
            else:
                for a in range(m):    
                    beta[a,i,j]= sum([rules[b,c,a]*alpha[c,k,i-1]*beta[b,k,j] for b in range(m) for c in range(m) for k in range(i)]) + sum([rules[b,a,c]*alpha[c,j+1,k]*beta[b,i,k] for b in range(m) for c in range(m) for k in range(i)])
    z = alpha[0,0,l-1]
    #print('z')
    #print(z)
    count = np.asarray([[[(sum([beta[a,i,j]*rules[a,b,c]*alpha[b,i,k]*alpha[c,k+1,j] for i in range(l) for j in range(i,l) for k in range(i,j-1)])+ep/(2*(m*m+t)))/z for c in range(m)] for b in range(m)] for a in range(m)])
    countt = np.asarray([[sum([alpha[a,i,i]*beta[a,i,i] for i in range(l) if sent[i]==x])/z for x in range(t)] for a in range(m)])
    return (count, countt)

if __name__=='__main__':
    (pos_dict, word_dict) = read_dict()
    c = CFG(pos_dict,word_dict)
    sents = ['cat sleep',
             'dog talk',
             'dog eat food',
             'cat drink water',
             'big cat eat food',
             'big tall cat eat food',
             'dog go to house',
             'dog eat and drink']
    psents = map(lambda sent: parse_sent(c.wdict, sent, c.pos_to_num),sents)
    #print(psents)
    t = len(c.num_to_pos)-1
    s = 10
    ep=0.01
    rules = (np.random.rand(s,s,s)+1)/(2*s)
    trules = (np.random.rand(s,t)+1)/(2*t)
    #rules = np.full((s,s,s),1.0/(2*s))
    #trules = np.full((s,t),1.0/(2*t))
#np.full((w,w,self.num_sym+news), np.inf)
    print(rules[0])
    for i in range(100):
        (rules, trules) = counts(rules, trules, psents)
        print(i)
        #slice
        print(rules[0])
        for n in range(10):
            print(generate(c,rules, trules,0))
#parse_sent(word_dict, sent, pos_to_num)

