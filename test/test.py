import pickle

class test:
    def __init__(self):
        a = 1
        b = 2

t = test()
t_str = pickle.dumps(t)
print(t_str)
