from utils import *
import random
from functools import partial 
#Emulates algebraic data types

#constructors are assumed to be uniquely identified by name (no overloading)
class Constructor(object):
    def __init__(self,name,typ,args):
        self.name=name
        self.typ=typ
        self.args=args
    def __call__(self,*args):
        for (n,arg) in enumerate(args):
            if isinstance(arg,Var):
                arg.typ=self.args[n]
        #print('calling')
        #print(args)
        #print(type(args))
        return (self,args)
    def __repr__(self):
        return self.name
    def __eq__(self,other):
        return (type(other)==Constructor) and (other.name==self.name)
    def __hash__(self):
        return hash(self.name)
    def arity(self):
        return len(self.args)

def print_ast(ast):
    if isinstance(ast,Constructor):
        return ast.name
    if isinstance(ast,tuple):
        name = ast[0].name
        if name[0].isalpha() or ast[0].arity()!=2:
            return ("%s(%s)" % (name, ",".join([print_ast(ast2) for ast2 in ast[1]])))
        else: #assume infix
            return ("(%s%s%s)" % (print_ast(ast[1][0]), name, print_ast(ast[1][1])))
        print("a=%d,b=%d" % (f(x,n),g(x,n)))
    return str(ast)

def print_lex(lex):
    for (phrase,d) in lex.iteritems():
        print(phrase)
        for ((ccg_type,ast),theta) in d.iteritems():
            print(" "+print_ast(ccg_type)+" : "+print_ast(ast))
            print("  "+str(theta))

#traverse tree to get all names of constructors in an AST
def get_all_names(ast,s=set()):
    if not(isinstance(ast,tuple)):
        return s
    #print(ast[0].name)
    s.add(ast[0].name)
    for child in ast[1]:
        get_all_names(child,s)
    return s

#traverse tree to get all constructors in an AST
def get_all_cons(ast,s=set()):
    if not(isinstance(ast,tuple)):
        return s
    #print(ast[0].name)
    s.add(ast[0])
    for child in ast[1]:
        get_all_cons(child,s)
    return s

#`cons` is a dict of constructor descriptions, organized by type.
# For example, `Add : Set -> Color -> Act` would be described by
# "Add": ["Set", "Color"]
# and under the entry "Act":
# {"Act": {"Add": ["Set", "Color"],...},...}
def create_PL(cons):
    d={}
    for (typ,li) in cons.iteritems():
        for (con,args) in li.iteritems():
            d[con]=Constructor(con,typ,args)
    return d
        
#0-indexed
class Var(object):
    def __init__(self,num,typ='unknown'):
        self.num=num
        self.typ=typ
    def __repr__(self):
        return ('var'+str(self.num)+':'+self.typ)
    def __eq__(self,other):
        return self.num==other.num
    def __hash__(self):
        return hash(self.num)
    def decr(self):
        #self.num-=1 #need to copy
        return Var(self.num-1,self.typ)

def papply(ast, x):
    """
    Partial application
    Example:
    papply(cons(Var(1),Var(0)),x)==cons(Var(0),x)
    Substitutes x for Var(0).
    All other variables are decremented by 1.
    """
    return deepmap(lambda v:
                   (x if v.num==0 else v.decr()) if isinstance(v,Var) else v, ast)

def matchLists(tree, rule, indict={}):
    d = indict.copy()
    if isinstance(rule,Var):
        d[rule.num]=tree
        return (True, d)
    if type(rule)==int:
        d[rule]=tree
        return (True,d)
    if type(tree)!=tuple:
        return (False, indict)
    (cons, args) = tree
    (rcons, rargs) = rule
    if cons.name!=rcons.name:
        return (False, indict)
    for i in range(len(args)):
        (success, d) = matchLists(args[i], rargs[i], d)
        if not success:
            return (False, indict)
    return (True, d)

def toNLUsingRules(rlist, tree):
    d={}
    for (rule, string) in rlist:
        (success, d) = matchLists(tree, rule, d)
        if success:
            #print(d)
            for k in d:
                #if not bottomed out, recursively replace with NL
                #print(type(d[k]))
                if type(d[k])==tuple:
                    d[k] = toNLUsingRules(rlist, d[k])
                string = string.replace("$"+str(k), d[k])
            return string
    return None #failed

# typ = None means no type in particular, just sample regularly
def sample_func_of_type(dic, typ):
    is_done = False
    func = None 
    while(not is_done): 
        rkey = random.choice(dic.keys())
        if dic[rkey].typ == typ or (typ == None):
            is_done = True 
            func = dic[rkey]
    return func

def sample_func_with_no_args_of_type(dic, typ):
    is_done = False
    func = None 
    while(not is_done): 
        rkey = random.choice(dic.keys())
        if len(dic[rkey].args) == 0 and dic[rkey].typ == typ:
            is_done = True 
            func = dic[rkey]
    return func   

def build_random_func_recursive(dic, curr_typ, curr_depth, max_depth):
    if curr_depth < max_depth:
        curr_func = sample_func_of_type(dic, curr_typ)
    else:
        curr_func = sample_func_with_no_args_of_type(dic, curr_typ)
    curr_new_arg_typs = curr_func.args 
    arg_funcs = []
    for arg_typ in curr_new_arg_typs:
        new_func = build_random_func_recursive(dic, arg_typ, curr_depth + 1, max_depth)
        arg_funcs.append(new_func)
    if len(arg_funcs) == 0:
        iterated_func_application = [curr_func()]
    else:
        iterated_func_application = [curr_func]
        for i in range(len(arg_funcs)): 
            arg = arg_funcs[i]
            if i < len(arg_funcs) - 1:
                curr_app = partial(iterated_func_application[i], arg)
            else:
                curr_app = iterated_func_application[i](arg)
            iterated_func_application.append(curr_app)
    final_func = iterated_func_application[len(iterated_func_application) - 1]
    return final_func 

def build_random_function(dic, max_depth):
    return build_random_func_recursive(dic, None, 0, max_depth)
        
# N is number of data points
# T is depth 
def generate_training_data(dic, rules, N, T):
    data = []
    for i in range(N):
        # generate new tree
        tree = build_random_function(dic, T)
        tree_str = toNLUsingRules(rules, tree)
        print("tree: " + str(tree) + ", " + "tree_str: " + str(tree_str))
        data.append((tree, tree_str))
    return data

if __name__=='__main__':
    c = Constructor('Add', 'Act', ['Set','Color'])
    print(c(Var(0),Var(1)))
    a = Constructor('All','Set',[])
    print(c(a(),Var(0)))
    print(get_all_names(c(a(),Var(0))))
    print(papply(c(Var(1),Var(0)), 'x'))
    
