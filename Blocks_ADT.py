from ADT import *

#https://stackoverflow.com/questions/14078357/python-how-can-idynamically-create-a-function-with-a-name-based-on-a-string-re
def make_global_vars(d):
    for k in d:
        globals()[k] = d[k]

Color = 'Color'
Act = 'Act'
Set = 'Set'
d=create_PL(
        {Color : {'Cyan':[],
                  'Brown':[],
                  'Red':[],
                  'Orange':[]},
         Set : {'All':[],
                'With':[Color],
                'Not':[Set],
                'Int':[Set,Set],
                'Leftmost':[Set],
                'Rightmost':[Set]},
         #Note I use Int=intersection rather than Diff as originally, because Diff(f,g)=Int(f,Not(g))
         Act : {'Add':[Set,Color],
                'Remove':[Set]}})

if __name__=='__main__':
    make_global_vars(d)
    print(Add(With(Cyan),Orange))
