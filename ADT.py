#Emulates algebraic data types

class Constructor(object):
    def __init__(self,name,typ,args):
        self.name=name
        self.typ=typ
        self.args=args
    def __call__(self,*args):
        for (n,arg) in enumerate(args):
            if isinstance(arg,Var):
                arg.typ=self.args[n]
        return (self,args)
    def __repr__(self):
        return self.name

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
        
class Var(object):
    def __init__(self,num):
        self.num=num
        self.typ='unknown'
    def __repr__(self):
        return ('var'+str(self.num)+':'+self.typ)

if __name__=='__main__':
    c = Constructor('Add', 'Act', ['Set','Color'])
    print(c(Var(1),Var(2)))

