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
            
#generate candidates given program and ccg rules (in the form (list) output by create_ccg)
def gen_cands(program,ccg):
    names = get_all_names(program)
    li=[]
    for entry in names:
        (ccg_type,ast) = entry
        if ast[0].name in names:
            li+=entry
    return li

