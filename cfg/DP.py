class DP(object):
    def __init__(self, get, is_base=lambda x:return False, base_get=lambda x:return None):
        self.get=get
        self.is_base=is_base
        self.base_get=base_get
        self.d={}
    def __getitem__(self, k):
        #print(k)
        if k in self.d:
            return self.d[k]
        if self.is_base(k):
            self.d[k] = self.base_get(k) 
            return self.d[k]
        else:
            self.d[k]=self.get(self,k)
            return self.d[k]

if __name__=='__main__':
    # Example
    fib = DP(lambda f, n: f[n-1]+f[n-2],
             lambda n: n<=1,
             lambda n: 1 if n==1 else 0)
    #print(fib[10])
    for i in range(40):
        print(fib[i])

         
