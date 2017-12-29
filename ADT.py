from utils import *
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

if __name__=='__main__':
    c = Constructor('Add', 'Act', ['Set','Color'])
    print(c(Var(0),Var(1)))
    a = Constructor('All','Set',[])
    print(c(a(),Var(0)))
    print(get_all_names(c(a(),Var(0))))
    print(papply(c(Var(1),Var(0)), 'x'))
    
