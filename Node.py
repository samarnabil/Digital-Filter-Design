import random

class Node():
    def __init__(self, R=None, I=None):

        self.Imaginary = round(random.uniform(0,1), 9)
        self.Real = round(random.uniform(-1,1), 9)
        if R!= None:
            self.Real = R
        if I!= None:
            self.Imaginary = I
        self.Conjugate = False
    
    def print(self):
        print("I={}, R={}".format(self.Imaginary, self.Real))

    def getImaginary(self):
        return self.Imaginary

    def getReal(self):
        return self.Real
    
    def SetConjugate(self, boolean):
        self.Conjugate = boolean
    
    def SetImaginary(self, y):
        self.Imaginary = y
    
    def SetReal(self, x):
        self.Real = x

    def GetConjugate(self):
        return Node(self.Real, - self.Imaginary)