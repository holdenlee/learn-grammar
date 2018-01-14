from ADT import *
from CCG import *
from utils import *

import pprint 
import time

#https://stackoverflow.com/questions/14078357/python-how-can-idynamically-create-a-function-with-a-name-based-on-a-string-re
def make_global_vars(d):
    for k in d:
        globals()[k] = d[k]

Color = 'Color'
Act = 'Act'
Set = 'Set'
cons_dict = {Color : {'Cyan':[],
                  'Brown':[],
                  'Red':[],
                  'Orange':[]},
         Set : {'All':[],
                'With':[Color],
                'Not':[Set],
                'Int':[Set,Set],
                'Leftmost':[Set],
                'Rightmost':[Set]},
         Act : {'Add':[Set,Color],
                'Remove':[Set]}} 
#Note I use Int=intersection rather than Diff as originally, because Diff(f,g)=Int(f,Not(g))


if __name__=='__main__':
    dic=create_PL(cons_dict)
    pp = pprint.PrettyPrinter(indent=4)
    make_global_vars(dic)
    #print(Add(With(Cyan),Orange))
    blocksRules1 = [(Cyan(), "cyan"),
                    (Brown(), "brown"),
                    (Red(), "red"),
                    (Orange(), "orange"),
                    (Add(1,2), "Add $2 to $1"),
                    (Remove(1), "Remove $1"),
                    (All(), "all blocks"),
                    (With(1), "$1 blocks"),
                    (Not(1), "not $1"),
                    #(Not(1), "all but $1"),
                    (Int(1,2), "$1 that are $2"),
                    (Leftmost(All()), "leftmost block"),
                    (Rightmost(All()), "rightmost block"),
                    (Leftmost(1), "leftmost $1"),
                    (Rightmost(1), "rightmost $1")]
    asts = [Remove(With(Brown())),
            Remove(With(Orange())),
            Remove(With(Cyan())),
            Remove(With(Red())),
            Remove(All()),
            Add(All(), Brown()),
            Add(All(), Orange()),
            Add(All(),Cyan()),
            Add(All(),Red())]
    #print("EXS")
    #exs = map(lambda x: (toNLUsingRules(blocksRules1,x),x),asts)
    #pp.pprint(exs)

    # test learning execution time for datasets with depth 2
    code_execution_time_data_set_size = []
    for data_set_size in range(10, 1010, 100):
        print("DATA: Size = " + str(data_set_size))
        data = generate_training_data(dic, blocksRules1, 'Act', data_set_size, 2)
        #pp.pprint(data)
        #test learning
        start_time = time.time()
        params = learn_ccg(data,init_params={},decay_f=lambda x: 1/(1+0.1*x),step_size=0.1,T=10,epochs=10,init_theta=0.01,v=0)
        end_time = time.time()
        print("Execution time:" + str(end_time - start_time) + " seconds")
        print("===============================")
        #print_lex(params)
        code_execution_time_data_set_size.append((data_set_size, end_time - start_time))
    print code_execution_time_data_set_size



    """
    def Diff(x,y):
        return Int(x,Not(y))
    blocksRules2 = [(Cyan(), "cyan"),
                    (Brown(), "brown"),
                    (Red(), "red"),
                    (Orange(), "orange"),
                    (Add(1,2), "Add $2 to $1"),
                    (Remove(1), "Remove $1"),
                    (All(), "all blocks"),
                    (With(1), "$1 blocks"),
                    (Diff(1,2), "$1 except $2"),
                    (Int(1,2), "$1 that are $2"),
                    (Not(1), "not $1"),
                    (Leftmost(All()), "leftmost block"),
                    (Rightmost(All()), "rightmost block"),
                    (Leftmost(1), "leftmost $1"),
                    (Rightmost(1), "rightmost $1")]
    testInstructions = [Cyan(),
                        Add(With(Cyan()),Orange()),
                        Remove(With(Brown())),
                        Add(Leftmost(With(Orange())), Red()),
                        Add(All(), Brown()),
                        Remove(Leftmost(All())),
                        Add(Diff(With(Brown()),Rightmost(All())), Orange()),
                        Add(All(), Orange())]
    for tree in testInstructions:
        #print(toNLUsingRules(blocksRules1, tree))
        #print(toNLUsingRules(blocksRules2, tree))
        pass
    """
    """
    log_form = Remove(With(Brown()))
    sent = words(toNLUsingRules(blocksRules1, log_form))
    print(log_form, sent)
    cands = gen_cands(log_form)
    params = {}
    #NEED TO ADD IDENTITY PARSES
    pp.pprint(parse(sent,log_form,params,cands))
    """
    #A longer sentence
    
    #log_form = Add(Diff(With(Brown()),Rightmost(All())), Orange())
    #sent = words(toNLUsingRules(blocksRules1, log_form))
    #sent = words("Add orange brown blocks that are not rightmost block.")
    #print(print_ast(FS(BS('A','B'),'C')))
    """
    asts = [Remove(With(Brown())),
            Remove(With(Orange())),
            Remove(With(Cyan())),
            Remove(With(Red())),
            Remove(All()),
            Add(With(Cyan()),Orange()),
            Add(Leftmost(With(Orange())), Red()),
            Add(All(), Brown()),
            Add(All(), Orange()),
            Add(All(),Cyan()),
            Add(All(),Red()),
            Remove(Leftmost(All())),
            Add(Diff(With(Brown()),Rightmost(All())), Orange())]
    exs = map(lambda x: (toNLUsingRules(blocksRules1,x),x),asts)
    exs = map(lambda x: (lambda ast: (toNLUsingRules(blocksRules1,ast),ast))(Remove(With(x))), [Brown(), Orange(), Cyan(), Red()])
    """

    """
    for (sent,ast) in exs:
        print(sent)
        print(just_parse(words(sent),ast,params))
    """
