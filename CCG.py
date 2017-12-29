from ADT import *

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
def gen_cands(log_form,ccg):
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

#under construction
def parse(sent,log_form,cands,params):
    """
    Args:
        sent ([string]): sentence
        log_form (AST): logical form
        cands: output of `gen_cands`
        params (dict(tuple(string), dict((ccg_type,AST), float))): gives theta associated with a string of words and its parse
    """
    l = len(sent)
    arr = [[{} for i in range(l)] for j in range(l)]
    #0<=d<=l-1
    for d in range(l):
        #0<=i<=l-1-d
        for i in range(l-d):
            j=i+d
            #0<=k<d
            for k in range(d):
                #look for right apps
                for (ccg_type,ast) in arr[i][i+k]:
                    (success, d) = matchLists(ccg_type, FS(Var(0),Var(1)))
                    if success:
                        pass
