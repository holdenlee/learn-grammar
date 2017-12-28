from DP import *

def getd(d,k):
    return d[k] if k in d else 0

#rules is dict {a: {(b,c): prob},...}
#terms is dict {a: {b: prob},...}
#x is list of words [a,b,c,...]
#parse is correct parsing of x
#0-indexed
def io_dp(rules, terms, x, parse):
    def fun(f,tup):
        n=len(x)
        if t=='mr':
            (t,(a,(b,c)),i,k,j)=tup
            return f('b',a,i,j)*rules[a][(b,c)]*f('a',b,i,k)*f('a',c,k+1,j)
        (t,a,i,j)=tup
        if t=='a':
            if i==j:
                return getd(terms[a],x[i])
            return sum([rules[a][(b,c)]*f('a',b,i,k)*f('a',c,k+1,j)
                     for k in range(i,j) for (b,c) in rules[a]])
        if t=='b':
            if i==0 and j==n-1:
                return 1 if parse==a else 0
            return sum([rules[b][(a,c)]*f('a',c,k,i-1)*f('b',b,k,j) for k in range(1,j) for (c, aa) in rules[b] if aa==a for b in rules]) + sum([rules[b][(a,c)]*f('a',c,j+1,k)*f('b',b,i,k) for k in range(j+1,n) for (aa, c) in rules[b] if aa==a for b in rules])
        if t=='m':
            return f('a',a,i,j)*f('b',a,i,j)
    return dp(fun)
