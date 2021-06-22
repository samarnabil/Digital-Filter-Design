from Node import Node
class AllPass():
    def __init__(self):
        self.Zero = []
        self.Pole = []
    
    def SetPole(self, a, b):
        self.Pole.append(Node(a,b))
        
        denominator = a**2+b**2
        self.Zero.append(Node(a/denominator,b/denominator))
        # self.Zero.SetReal(a/denominator)
        # self.Zero.SetImaginary(b/denominator)

    def SetZero(self, a, b):
        self.Zero.append(Node(a,b))
        
        denominator = a**2+b**2
        self.Pole.append(Node(a/denominator,b/denominator))
        # self.Zero.SetReal(a/denominator)
        # self.Zero.SetImaginary(b/denominator)

    def GetZero(self):
        return self.Zero

    def GetPole(self):
        return self.Pole

    def ClearAll(self):
        self.Zero.clear()
        self.Pole.clear()