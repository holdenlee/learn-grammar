from ADT import *
import math
import pprint

# Forward and backward slash
FS = Constructor('/','',['',''])
BS = Constructor('\\','',['',''])

"""
class CCGType(object):
    def __init__(self,typ):
        self.typ=()
"""
        
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

#given constructor list, create CCG entries
def create_CCG(consl):
    l = []
    for cons in consl:
        ar = cons.arity()
        li = create_arity0(cons) if ar==0 else \
             create_arity1(cons) if ar==1 else \
             create_arity2(cons)
        l += li
    return l

#this is basically genlex            
#generate candidates given program and ccg rules (in the form (list) output by create_ccg)
def gen_cands(log_form):
    #set of names
    consl = get_all_cons(log_form)
    return create_CCG(consl)
    """
    cons = get_all_names(log_form)
    li=[]
    for entry in names:
        (ccg_type,ast) = entry
        if ast[0].name in names:
            li+=entry
    return li
    """

def get_subtrees(log_form, s=set()):
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
    return None #arity>2 not implemented

def dict_add(d,k,v):
    if k in d:
        d[k] += v
    else:
        d[k]=v

#need to keep record high
#arr[i][j][(ccg_type,ast)]=[value, highest, highest_parse,hi_parse_set]
#hi_parse_set includes new things to add!
def update_dp_entry(arr,i,j,entry,l_entry,r_entry): #,mid
    #print(l_entry,r_entry)
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


def parse(sent,log_form,cands,params,s_type='Act',word_limit=2,default_theta=0.01):
    """
    Args:
        sent ([string]): sentence
        log_form (AST): logical form
        cands: output of `gen_cands`
        params (dict(tuple(string), dict((ccg_type,AST), float))): gives theta associated with a string of words and its parse
        s_type (string): type of sentence
        word_limit (int): max number of words in constant phrase
        default_theta (float): default score to assign candidate parses. Should be small.
    """
    #this is like n^5 time right now :(
    #these are possible intermediate parses. Only keep these.
    subtrees = get_subtrees(log_form)
    l = len(sent)
    arr = [[{} for i in range(l)] for j in range(l)]
    #0<=d<=l-1
    for d in range(l):
        #0<=i<=l-1-d
        for i in range(l-d):
            j=i+d
            if d<word_limit:
                words = tuple(sent[i:j+1])
                if words in params:
                    #parse strings of d+1 consecutive words
                    for key in params[words]:
                        #(ccg_type,ast)=key
                        theta=params[words][key]
                        val = math.exp(theta)
                        #create entry
                        arr[i][j][key] = [val,val, (i,j,key), set()]
                        #for now, assume that these parses can only be attained directly, and not from building up from subparses (TODO use `update_dp_entry` instead)
                for cand in cands:
                    #if candidate is not already included, parse it with score `default_theta`.
                    if not(words in params and cand in params[words]):
                        val = math.exp(default_theta)
                        #print("candidate",cand)
                        #create entry
                        arr[i][j][cand] = [val,val,(i,j,cand),set([(words,cand)])]
            #0<=k<d
            for k in range(d):
                #look for right apps
                for l_key in arr[i][i+k]:
                    l_entry = arr[i][i+k][l_key]
                    (ccg_type,ast)=l_key
                    (success, dic) = matchLists(ccg_type, FS(Var(0),Var(1)))
                    if success:
                        for r_key in arr[i+k+1][j]:
                            r_entry = arr[i+k+1][j][r_key]
                            (ccg_type2,ast2)=r_key
                            if ccg_type2==dic[1]:
                                #print("matched")
                                #print(" "+str(l_key))
                                #print(" "+str(r_key))
                                ast3 = papply(ast,ast2)
                                entry=(dic[0],ast3)
                                #print(ast3 in subtrees)
                                if ast3 in subtrees:
                                    update_dp_entry(arr,i,j,entry,l_entry,r_entry)
                #look for left apps
                for r_key in arr[i+k+1][j]:
                    (ccg_type,ast)=r_key
                    r_entry = arr[i+k+1][j][r_key]
                    (success, dic) = matchLists(ccg_type, BS(Var(0),Var(1)))
                    if success:
                        for l_key in arr[i][i+k]:
                            (ccg_type2,ast2)=l_key
                            l_entry = arr[i][i+k][l_key]
                            if ccg_type2==dic[1]:
                                ast3 = papply(ast,ast2)
                                entry=(dic[0],ast3)
                                if ast3 in subtrees:
                                    update_dp_entry(arr,i,j,entry,l_entry,r_entry)
    if not((s_type,log_form) in arr[0][l-1]):
        
        pp = pprint.PrettyPrinter(indent=1)
        #pp.pprint(arr)
        for i in range(l):
            for j in range(l):
                print((i,j))
                pp.pprint(arr[i][j])
        
        return "Failed to parse."
    #[value, highest, highest_parse] = arr[0][n-1][(s_type,log_form)]
    return arr[0][l-1][(s_type,log_form)]

#f(i,mid,j,l_key,r_key,comb_key)
#search in arr for key
def lr_apps(f,arr,i,mid,j):
    #look for A/B+B
    for l_key in arr[i][mid]:
        #l_entry = arr[i][mid][l_key]
        (ccg_type,ast)=l_key
        (success, dic) = matchLists(ccg_type, FS(Var(0),Var(1)))
        if success:
            for r_key in arr[mid+1][j]:
                #r_entry = arr[mid+1][j][r_key]
                (ccg_type2,ast2)=r_key
                if ccg_type2==dic[1]:
                    ast3 = papply(ast,ast2)
                    comb_key  =(dic[0],ast3)
                    #print(ast3 in subtrees)
                    f(i,mid,j,l_key,r_key,comb_key)
    #look for B+A\B
    for r_key in arr[mid+1][j]:
        (ccg_type,ast)=r_key
        (success, dic) = matchLists(ccg_type, BS(Var(0),Var(1)))
        if success:
            for l_key in arr[i][mid]:
                #r_entry = arr[mid+1][j][r_key]
                (ccg_type2,ast2)=l_key
                if ccg_type2==dic[1]:
                    ast3 = papply(ast,ast2)
                    comb_key  =(dic[0],ast3)
                    #print(ast3 in subtrees)
                    f(i,mid,j,l_key,r_key,comb_key)        

def outside_given_lf(sent,log_form,params,s_type,alpha):
    l = len(sent)
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
    #INSIDE: just use parse.
    arr= parse(sent,log_form,[],params,s_type,word_limit=0,default_theta=0)
    #throw away the irrelevant information (best parse tree, etc.)
    alpha = deepmap(lambda d: map_vals(lambda v: v[0], d), arr)
    #OUTSIDE
    beta = outside_given_lf(sent,log_form,params,s_type,alpha)
    l = len(sent)
    counts={}
    for i in range(l):
        for k in beta[i][i]:
            dict_add(counts,k,alpha[i][i]*beta[i][i])
    return counts

def io_all(sent,params):
    pass

"""
if __name__=='__main__':
    #testing
    Add = Constructor('Add', 'A', ['S','C'])
    Orange = Constructor('Orange', 'C', [])
    Brown = Constructor('Brown', 'C', [])
    With = Constructor('With', 'S', ['C'])
    lf = Add(With(Brown),Orange())
    subtrees = get_subtrees(lf)
    (ccg_type, ast) = (FS(FS('A','S'),'C'), Add(Var(1),Var(0)))
    (success, dic) = matchLists(ccg_type, FS(Var(0),Var(1)))
    if success:
        (ccg_type2,ast2)=('C', Orange())
        if ccg_type2==dic[1]:
            ast3 = papply(ast,ast2)
            entry=(dic[0],ast3)
            #print(ast3 in subtrees)
            print(entry)
            print(ast3 in subtrees)
"""
