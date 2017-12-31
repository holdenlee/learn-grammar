from ADT import *
from CCG import *
from utils import *
import math
import random

random.seed(1)

# Tests

def make_global_vars(d):
    for k in d:
        globals()[k] = d[k]

N = 'N'
S = 'S'

print("===Test 1===")
simple_dict = {N : {'A':[]},
               S : {'B':[N]}}
sd = create_PL(simple_dict)
make_global_vars(sd)
a = 0
b = 1
sparams = {('b',): {(FS(S,N),B(Var(0))): b},
           ('a',): {(N,A()): a}}
ssent = tuple(words('b a'))
sast = B(A())
scounts_lf = io_given_lf(ssent,sast,sparams,s_type='S',v=2)
scounts_all = io_all(ssent,sparams,v=2)
print("Counts LF")
print_lex(scounts_lf)
assert(scounts_lf[('a',)][(N,A())] == math.exp(1))
print("Counts all")
print_lex(scounts_all)

print("===Test 2===")
cons_dict = { N : {'N_Fruit':[],
                   'N_Flies':[],
                   'N_FruitFlies':[],
                   'N_Bananas':[],
                   'A_Fruit':[N]},
              S : {'V_Flies':[N],
                   'V_Like':[N,N],
                   'P_Like':[S,N]}}
#normally I would have `like:(S\N)\(S\N)/N` but that doesn't work with this simplified AST, so do something simpler here

d=create_PL(cons_dict)
make_global_vars(d)
r=random.random
n_fruit = r()
a_fruit =r()
n_flies=r()
v_flies=r()
v_like=r()
p_like=r()
n_bananas=r()
n_fruitflies=r()
li=[n_fruit,a_fruit,n_flies,v_flies,v_like,p_like,n_bananas,n_fruitflies]
print(li)
print(map(math.exp,li))

params={('fruit',): {(N, N_Fruit()) : n_fruit,
                     (FS(N,N), A_Fruit(Var(0))) : a_fruit},
        ('flies',): {(N, N_Flies()) : n_flies,
                     (BS(S,N), V_Flies(Var(0))) : v_flies},
        ('like',):  {(FS(BS(S,N),N), V_Like(Var(1),Var(0))) : v_like,
                     (FS(BS(S,S),N), P_Like(Var(1),Var(0))) : p_like},
        ('bananas',):{(N, N_Bananas()) : n_bananas},
        ('fruit','flies'): {(N, N_FruitFlies()) : n_fruitflies}}

sent = tuple(words('fruit flies like bananas'))
ast = V_Like(N_FruitFlies(),N_Bananas())
print("Counts LF")
counts_lf = io_given_lf(sent,ast,params,s_type='S',v=2)
print("Counts all")
counts_all = io_all(sent,params)
#print("Counts LF")
#print_lex(counts_lf)
v1 = math.exp(n_fruitflies+v_like+n_bananas)
v2 = math.exp(a_fruit+n_flies+v_like+n_bananas)
v3 = math.exp(n_fruit+v_flies+p_like+n_bananas)
print(v1,v2,v3)

def approx_eq(x,y):
    return abs(x-y)<=0.0001

assert(approx_eq(counts_lf[('fruit','flies')][(N, N_FruitFlies())],v1))
assert(approx_eq(counts_lf[('like',)][(FS(BS(S,N),N), V_Like(Var(1),Var(0)))],v1))
assert(approx_eq(counts_lf[('bananas',)][(N, N_Bananas())],v1))
#print("Counts all")
#print_lex(counts_all)
assert(approx_eq(counts_all[('fruit','flies')][(N, N_FruitFlies())],v1))
assert(approx_eq(counts_all[('like',)][(FS(BS(S,N),N), V_Like(Var(1),Var(0)))],v1+v2))
assert(approx_eq(counts_all[('bananas',)][(N, N_Bananas())],v1+v2+v3))

for i in params:
    for j in params[i]:
        params[i][j]=0

params = learn_ccg([(sent,ast)],init_params=params,decay_f=lambda x: 1/(1+0.1*x),step_size=0.1,T=50,epochs=10,init_theta=-5,s_type='S',word_limit=2,v=1)


#assert(counts_lf[('fruit','flies')] == 
#[0][3][('S',ast)] == math.exp(n_fruitflies + v_like + n_bananas))
#assert(
