from ADT import *
import math
import pprint
from utils import *

"""
Creating CCG types.
For example, (A/B)\C is represented as

    BS(FS(A,B),C)
"""

# Forward and backward slash
FS = Constructor('/','*',['*','*'])
BS = Constructor('\\','*',['*','*'])
        
# type CCGEntry = (CCGType, AST)

def create_arity0(cons):
    return [(cons.typ, cons())]

def create_arity1(cons):
    t = cons.typ
    a = cons.args[0]
    return [(FS(t,a), cons(Var(0))),
            (BS(t,a), cons(Var(0)))]

def create_arity2(cons):
    t = cons.typ
    a = cons.args[0]
    b = cons.args[1]
    fw = cons(Var(0),Var(1))
    bw = cons(Var(1),Var(0))
    #8 possibilities: FS/BS for each argument, and 2 possible orders of arguments
    return [(FS(FS(t,a),b), bw),
            (FS(BS(t,a),b), bw),
            (BS(FS(t,a),b), bw),
            (BS(BS(t,a),b), bw),
            (FS(FS(t,b),a), fw),
            (FS(BS(t,b),a), fw),
            (BS(FS(t,b),a), fw),
            (BS(BS(t,b),a), fw)]

def create_CCG(consl):
    """
    given constructor list, create CCG entries
    """
    l = []
    for cons in consl:
        ar = cons.arity()
        li = create_arity0(cons) if ar==0 else \
             create_arity1(cons) if ar==1 else \
             create_arity2(cons)
        l += li
    return l

"""
Generate candidate parses.
"""

def gen_cands(log_form):
    """
    Generate candidate ASTs given program (logical form).
    This is one half of `genlex`. (The other half is coming up with the phrases, but that is done dynamically in `inside_lf`.)
    """
    consl = get_all_cons(log_form)
    return create_CCG(consl)

def get_subtrees(log_form, s=set()):
    """
    Get all subtrees of `log_form`.
    The output is fed to the parsing algorithm, so the only intermediate parses kept are valid subtrees. (Otherwise, there can be an exponential explosion.)
    """
    if isinstance(log_form, Constructor):
        return log_form
        #this isn't supposed to happen, but it does...
    cons = log_form[0]
    args = log_form[1]
    s.add(log_form)
    if cons.arity()==0:
        return s
    if cons.arity()==1:
        s.add(cons(Var(0)))
        get_subtrees(args[0],s)
        return s
    if cons.arity()==2:
        s = s.union(set([cons(Var(0),args[1]),
                         cons(args[0],Var(0)),
                         cons(Var(0),Var(1)),
                         cons(Var(1),Var(0))]))
        get_subtrees(args[0],s)
        get_subtrees(args[1],s)
        return s
    raise Exception("Arity >2 not implemented")

"""
lr_apps
"""
def lr_apps(f,arr,i,mid,j,has_ast=True):
    """
    Helper method for all CCG DP algorithms.
    Executes function `f` on arguments `i,mid,j,l_key,r_key,comb_key` whenever

    * arr[i][mid] is in form A/B and arr[mid+1][j] is in form B, or
    * arr[i][mid] is in form B and arr[mid+1][j] is in form A\B.
    """
    #look for A/B+B
    for l_key in arr[i][mid]:
        #l_entry = arr[i][mid][l_key]
        if has_ast:
            (ccg_type,ast)=l_key
        else:
            ccg_type=l_key
        (success, dic) = matchLists(ccg_type, FS(Var(0),Var(1)))
        if success:
            for r_key in arr[mid+1][j]:
                #r_entry = arr[mid+1][j][r_key]
                if has_ast:
                    (ccg_type2,ast2)=r_key
                else:
                    ccg_type2=r_key
                if ccg_type2==dic[1]:
                    if has_ast:
                        ast3 = papply(ast,ast2)
                        comb_key  =(dic[0],ast3)
                    else:
                        comb_key = dic[0]
                    #print(ast3 in subtrees)
                    f(i,mid,j,l_key,r_key,comb_key)
    #look for B+A\B
    for r_key in arr[mid+1][j]:
        if has_ast:
            (ccg_type,ast)=r_key
        else:
            ccg_type=r_key
        (success, dic) = matchLists(ccg_type, BS(Var(0),Var(1)))
        if success:
            for l_key in arr[i][mid]:
                #r_entry = arr[mid+1][j][r_key]
                if has_ast:
                    (ccg_type2,ast2)=l_key
                else:
                    ccg_type2 = l_key
                if ccg_type2==dic[1]:
                    if has_ast:
                        ast3 = papply(ast,ast2)
                        comb_key  =(dic[0],ast3)
                    else:
                        comb_key = dic[0]

                    f(i,mid,j,l_key,r_key,comb_key)        

"""
Parsing & IO algorithm when logical form is given.
"""
def update_dp_entry(arr,i,j,entry,l_entry,r_entry,extended=True): #,mid
    """
    Helper method for parsing.
    When `extended`, 

    arr[i][j][(ccg_type,ast)]=[value, highest, highest_parse,hi_parse_set]
    
    `hi_parse_set` includes new things to add.
    When not `extended`:

    arr[i][j][(ccg_type,ast)]=value
    
    """
    if extended:
        val = l_entry[0]*r_entry[0]
        hival = l_entry[1]*r_entry[1]
        if not(entry in arr[i][j]):
            arr[i][j][entry]=[0,0,None,set()]
            arr[i][j][entry][0]+=val
        if hival==arr[i][j][entry][1]:
            #add to hi_parse_set
            arr[i][j][entry][3]=arr[i][j][entry][3].union(l_entry[3])
            arr[i][j][entry][3]=arr[i][j][entry][3].union(r_entry[3])
        if hival>arr[i][j][entry][1]:
            arr[i][j][entry][1]=hival
            arr[i][j][entry][2]=(i,j,l_entry[2],r_entry[2])
            arr[i][j][entry][3]=l_entry[3].union(r_entry[3])
    else:
        val = l_entry*r_entry
        dict_add(arr[i][j],entry,val)

def inside_lf(sent,log_form,params,cands=[],word_limit=2,default_theta=0.01,extended=True):
    """
    Runs the `inside` part of the IO algorithm when the logical form of the sentence is given. Only subtrees of the logical form are kept.
    Args:
        sent ([string]): sentence
        log_form (AST): logical form
        params (dict(tuple(string), dict((ccg_type,AST), float))): gives theta associated with a string of words and its parse
        cands ([(CCGType,AST)]): output of `gen_cands`
        word_limit (int): max number of words in constant phrase
        default_theta (float): default score to assign candidate parses. Should be small.
    """
    #this is like n^5 time right now :(
    #these are possible intermediate parses. Only keep these.
    subtrees = get_subtrees(log_form)
    l = len(sent)
    arr = [[{} for i in range(l)] for j in range(l)]
    phrase_locs = {}
    if extended:
        def comb_fun(i,j,k,l_key,r_key,comb_key):
            l_entry=arr[i][j][l_key]
            r_entry=arr[j+1][k][r_key]
            update_dp_entry(arr,i,k,comb_key,l_entry,r_entry)
    else:
        def comb_fun(i,j,k,l_key,r_key,comb_key):
            dict_add(alpha[i][k], comb_key, alpha[i][j][l_key]*alpha[j+1][k][r_key])
    #0<=d<=l-1
    for d in range(l):
        #0<=i<=l-1-d
        for i in range(l-d):
            j=i+d
            if d<word_limit:
                phrase = tuple(sent[i:j+1])
                if phrase in params:
                    #parse strings of d+1 consecutive words
                    for key in params[phrase]:
                        #(ccg_type,ast)=key
                        theta=params[phrase][key]
                        val = math.exp(theta)
                        #create entry
                        arr[i][j][key] = [val,val, (i,j,key), set()] if extended else val
                        dict_ladd(phrase_locs,phrase,(i,j))
                for cand in cands:
                    #if candidate is not already included, parse it with score `default_theta`.
                    if not(phrase in params and cand in params[phrase]):
                        val = math.exp(default_theta)
                        #create entry
                        arr[i][j][cand] = [val,val,(i,j,cand),set([(phrase,cand)])] if extended else val
            #0<=k<d
            for k in range(d):
                lr_apps(comb_fun,arr,i,i+k,j,has_ast=True)
    return arr,phrase_locs

def parse(sent,log_form,params,cands=[],s_type='Act',word_limit=2,default_theta=0.01,verbose=True):
    """
    Finds highest-scoring parses.

    Args: See inside_lf
        s_type (string): type of sentence
    """
    l=len(sent)
    arr,_ = inside_lf(sent,log_form,params,cands,word_limit,default_theta,extended=True)
    if not((s_type,log_form) in arr[0][l-1]):
        if verbose:
            pp = pprint.PrettyPrinter(indent=1)
            for i in range(l):
                for j in range(l):
                    print((i,j))
                    pp.pprint(arr[i][j])
        return "Failed to parse."
    #[value, highest, highest_parse] = arr[0][n-1][(s_type,log_form)]
    return arr[0][l-1][(s_type,log_form)]

def outside_given_lf(sent,log_form,params,s_type,alpha):
    """
    Runs the `outside` part of the IO algorithm when the logical form of the sentence is given. Requires `alpha` output of `inside_lf`.
    """
    beta = [[{} for i in range(l)] for j in range(l)]
    #B->AC
    def comb_fun_l(i,j,k,l_key,r_key,comb_key):
        if comb_key in alpha[i][k]:
            if not(l_key in beta[i][j]):
                beta[i][j][l_key]=0
            beta[i][j][l_key] += alpha[j+1][k][r_key]*beta[i][k][comb_key]
    #B->CA
    def comb_fun_r(i,j,k,l_key,r_key,comb_key):
        if comb_key in alpha[i][k]:
            if not(r_key in beta[j+1][k]):
                beta[j+1][k][r_key]=0
            beta[j+1][k][r_key] += alpha[i][j][l_key]*beta[i][k][comb_key]
    for d in range(l-1,-1,-1):
        for i in range(l-d):
            j=i+d
            if d==l-1:
                beta[i][j][(s_type,log_form)]=1
            for k in range(j+1,l):
                #B->AC
                lr_apps(comb_fun_l,alpha,i,j,k)
            for k in range(0,i):
                #B->CA
                lr_apps(comb_fun_r,alpha,k,i-1,j)
    return beta
    #mu(A,i,j)=alpha(A,i,j)beta(A,i,j)
                    
def io_given_lf(sent,log_form,params,s_type='Act'):
    """
    Full IO algorithm given logical form
    """
    #INSIDE
    alpha, phrase_locs = inside_lf(sent,log_form,params,cands=[],word_limit=0,default_theta=0,extended=False)
    #OUTSIDE
    beta = outside_given_lf(sent,log_form,params,s_type,alpha)
    l = len(sent)
    counts={}
    for (phrase,li) in phrase_locs.iteritems():
        if not(phrase in counts):
            counts[phrase]={}
        for key in params[phrase]:
            counts[phrase][entry] = params[phrase][entry]*sum([beta[i][j][entry] for (i,j) in li])
    return counts

"""
Parsing & IO algorithm when logical form is not given. We use coarser information than parsing when the logical form is given.
Namely, we only keep CCGType, and not (CCGType,AST).
This is important because there are too many possible AST's.
"""
def inside_all(sent,params):
    l = len(sent)
    alpha = [[{} for i in range(l)] for j in range(l)]
    phrase_locs = {}
    def comb_fun(i,j,k,l_key,r_key,comb_key):
        dict_add(alpha[i][k], comb_key, alpha[i][j][l_key]*alpha[j+1][k][r_key])
    for d in range(l):
        for i in range(l-d):
            j=i+d
            phrase = tuple(sent[i:j+1])
            #terminals
            if (phrase,typ_d) in params.iteritems():
                for (typ,val) in typ_d.iteritems():
                    alpha[i][j][typ]=val
                    dict_ladd(phrase_locs,phrase,(i,j))
            #combinations
            for k in range(d):
                lr_apps(comb_fun,alpha,i,i+k,j,has_ast=False)
    return alpha, phrase_locs

def outside_all(sent,params,alpha):
    l = len(sent)
    beta = [[{} for i in range(l)] for j in range(l)]
    #B->AC
    def comb_fun_l(i,j,k,l_key,r_key,comb_key):
        if not(l_key in beta[i][j]):
            beta[i][j][l_key]=0
        beta[i][j][l_key] += alpha[j+1][k][r_key]*beta[i][k][comb_key]
    #B->CA
    def comb_fun_r(i,j,k,l_key,r_key,comb_key):
        if not(r_key in beta[j+1][k]):
            beta[j+1][k][r_key]=0
        beta[j+1][k][r_key] += alpha[i][j][l_key]*beta[i][k][comb_key]
    for d in range(l-1,-1,-1):
        for i in range(l-d):
            j=i+d
            if d==l-1:
                for typ in alpha[0][l-1]:
                    beta[0][l-1][typ]=1
            for k in range(j+1,l):
                #B->AC
                lr_apps(comb_fun_l,alpha,i,j,k)
            for k in range(0,i):
                #B->CA
                lr_apps(comb_fun_r,alpha,k,i-1,j)
    return beta

def io_all(sent,params):
    """
    Full IO algorithm, not given logical form
    `params` is in form `{tuple(string): {(ccg_type, ast): float}}`
    """
    #we first drop the ast info
    #params2 is {tuple(string): {ccg_type:float}}
    #in exp space
    params2 = {}
    for phrase in params:
        params2[phrase] ={}
        for k in params[phrase]:
            (ccg_type,ast)=k
            dict_add(params2[phrase],ccg_type,math.exp(params[k])) #exponentiate here
    alpha, phrase_locs = inside_all(sent, params2)
    beta = outside_all(sent, params2,alpha, phrase_locs)
    counts={}
    for (phrase,li) in phrase_locs.iteritems():
        if not(phrase in counts):
            counts[phrase]={}
        for key in params[phrase]:
            counts[phrase][entry] = params[phrase][entry]*sum([beta[i][j][entry] for (i,j) in li])
    return counts    

#RECYCLE BIN

#given constructor dictionary, create CCG entries
"""
def create_CCG(consd):
    l = []
    for k in consd:
        cons = consd[k]
        ar = cons.arity()
        li = create_arity0(cons) if ar==0 else \
             create_arity1(cons) if ar==1 else \
             create_arity2(cons)
        l += li
    return l
"""
