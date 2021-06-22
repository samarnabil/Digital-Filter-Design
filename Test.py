import matplotlib.pyplot as plt
from Node import Node 
from math import inf, pi, sin, cos, sqrt, tan, atan, atan2
from scipy.signal import zpk2tf
import matplotlib.gridspec as gridspec
from AllPassFilter import AllPass
import random
NO_OF_ZEROS = 0
NO_OF_POLES = 0
NO_OF_AllPass = 0

class ZTransform():
    def __init__(self):
        self.Zeros = []
        self.Poles = []
        self.AllPassFilter = []
        self.UnitCircle = []
        gridspace = gridspec.GridSpec(2, 2)
        self.CircleGraph = plt.subplot(gridspace[:,0])
        self.MagnitudeResponse = plt.subplot(gridspace[0,1])
        self.PhaseResponse = plt.subplot(gridspace[1,1])
        self.SetUnitCircle()
        self.applied_index = None
        #self.CustomZeroAndPole()
        # for i in range(NO_OF_ZEROS):
        #     self.SetZero()

        # for i in range(NO_OF_POLES):
        #     self.SetPole()
        
        # for i in range(NO_OF_AllPass):
        #     self.SetAllPass()    

    def setZero(self,x,y):
        self.Zeros.append(Node(x,y))
    
    def setPole(self,x,y):
        self.Poles.append(Node(x,y))
    
    def update_zeros(self,zeros):
        self.Zeros.clear()
        self.Zeros=zeros
    
    def update_poles(self,poles):
        self.Poles.clear()
        self.Poles=poles
        
    def SetAllPass(self):
        filter = AllPass()
        self.AllPassFilter.append(filter)
        # filter.SetPole(round(random.uniform(-1,1), 9), round(random.uniform(0,1), 9))
    
    def print(self):
        print("Zeros:")
        for n in self.Zeros:
            n.print()
        print("\nPoles:")
        for n in self.Poles:
            n.print()
        print("\nAll-Pass:")
        for n in self.AllPassFilter:
            n.GetZero().print()
            n.GetPole().print()
    
    def get_AllPassFilter(self):
        # for x in self.Zeros:
        #     print('zeros:',x.GetZero().getReal(),',', x.GetPole().getImaginary())
        return self.AllPassFilter

    def getZeros(self):
        for x in self.Zeros:
            print('zeros:',x.getReal(),',', x.getImaginary())

        for x in self.Poles:
            print('poles:',x.getReal(),',', x.getImaginary())


        
    def PlotUnitCircle(self):
        x1 = [I.getReal() for I in self.Zeros]
        x2 = [I.getReal() for I in self.Poles]
        y1 = [I.getImaginary() for I in self.Zeros]
        y2 = [I.getImaginary() for I in self.Poles]
        
        if self.AllPassFilter:
            x1 += [[I.GetZero().getReal() for I in self.AllPassFilter]]
            y1 += [I.GetZero().getImaginary() for I in self.AllPassFilter]
            x2 += [I.GetPole().getReal() for I in self.AllPassFilter]
            y2 += [I.GetPole().getImaginary() for I in self.AllPassFilter]

        circle = plt.Circle((0, 0), 1, fill = False)
        self.CircleGraph.add_patch(circle)
        # self.CircleGraph.scatter(list(zip(*self.UnitCircle))[0], list(zip(*self.UnitCircle))[1])
        self.CircleGraph.scatter(x1,y1, color = 'r', label = 'Zeros')
        self.CircleGraph.scatter(x2,y2, color = 'b', label = 'Poles')
        self.CircleGraph.legend()
        self.CircleGraph.axhline(y=0, color='k')
        self.CircleGraph.axvline(x=0, color='k')
        self.CircleGraph.set_aspect('equal')
        self.CircleGraph.set_xlim(-2,2)
        self.CircleGraph.set_ylim(-2,2)

    def SetUnitCircle(self):
        for i in range(101):
            angle = i*(pi/100)
            tangent = tan(angle)
            #print(tangent)
            sine = sin(angle)
            cosine = cos(angle)
            if tangent==0:
                self.UnitCircle.append((1, 0, angle))
                # print("x: {}, y: {}".format(1,0))
                continue
            adj = round(sine/tangent,4)
            opp = round(tan(angle)*cosine,4)
            self.UnitCircle.append((adj, opp, angle))
            # print("x: {}, y: {}".format(adj, opp))
    
    def PlotMagnitude(self):
        magnitude = []
        for Ux, Uy, _ in self.UnitCircle:
            polemag = 1
            zeromag = 1
            for pole in self.Poles:
                factor = sqrt(((Ux-pole.getReal())**2) + ((Uy-pole.getImaginary())**2))
                polemag*=factor
            
            for zero in self.Zeros:
                factor = sqrt(((Ux-zero.getReal())**2) + ((Uy-zero.getImaginary())**2))
                zeromag*=factor

            if self.applied_index != None:
                filter = self.AllPassFilter[self.applied_index]
                for zero_node,pole_node in zip(filter.GetZero(),filter.GetPole()):
                    zfactor = sqrt(((Ux-zero_node.getReal())**2) + ((Uy-zero_node.getImaginary())**2))
                    zeromag*=zfactor
                    
                    pfactor = sqrt(((Ux-pole_node.getReal())**2) + ((Uy-pole_node.getImaginary())**2))
                    polemag*=pfactor
            ######################################################3
            if polemag!=0:
                # if zeromag/polemag ==1:
                #     magnitude.append(0)
                # else:
                magnitude.append(zeromag/polemag)
            else:
                magnitude.append(inf) 
            #########################################################3
        # self.MagnitudeResponse.title.set_text("Magnitude response")
        #####
        # self.MagnitudeResponse.plot(list(zip(*self.UnitCircle))[2], magnitude)
        x= list(list(zip(*self.UnitCircle))[2])
        return x,magnitude
        #####
    def PlotPhase(self):
        phase = []
        for Ux, Uy, _ in self.UnitCircle:
            polephase = 0
            zerophase = 0
            for pole in self.Poles:
                ang= self.CalculateAngle(pole.getReal(), pole.getImaginary(), Ux, Uy)
                polephase += ang
            for zero in self.Zeros:
                ang = self.CalculateAngle(zero.getReal(), zero.getImaginary(), Ux, Uy)
                zerophase += ang

            if self.applied_index != None:
                filter = self.AllPassFilter[self.applied_index]
                for zero_node,pole_node in zip(filter.GetZero(),filter.GetPole()):
                    # zfactor = sqrt(((Ux-zero_node.getReal())**2) + ((Uy-zero_node.getImaginary())**2))
                    zfactor = self.CalculateAngle(zero_node.getReal(), zero_node.getImaginary(), Ux, Uy)
                    zerophase+=zfactor
                    
                    pfactor = self.CalculateAngle(pole_node.getReal(), pole_node.getImaginary(), Ux, Uy)
                    polephase+=pfactor
            angle = zerophase - polephase
            phase.append(angle)

        self.PhaseResponse.title.set_text('Phase response')
        self.PhaseResponse.plot(list(zip(*self.UnitCircle))[2], phase)
        x= list(list(zip(*self.UnitCircle))[2])
        return x,phase


    ##version 2 
    def PlotAllPassPhase_V2(self,index):
        phase = []
        for Ux, Uy, _ in self.UnitCircle:
            polephase = 0
            zerophase = 0
            # for filter in self.AllPassFilter:
            filter = self.AllPassFilter[index]
            for zero_node,pole_node in zip(filter.GetZero(),filter.GetPole()):
                    # zfactor = sqrt(((Ux-zero_node.getReal())**2) + ((Uy-zero_node.getImaginary())**2))
                    zfactor = self.CalculateAngle(zero_node.getReal(), zero_node.getImaginary(), Ux, Uy)
                    zerophase+=zfactor
                    
                    pfactor = self.CalculateAngle(pole_node.getReal(), pole_node.getImaginary(), Ux, Uy)
                    polephase+=pfactor
            angle = zerophase - polephase
            # print("Zero phase: {}, Pole phase: {}".format(zerophase, polephase))
            phase.append(angle)

        self.PhaseResponse.title.set_text('Phase response')
        self.PhaseResponse.plot(list(zip(*self.UnitCircle))[2], phase)
        # plt.show()
        x= list(list(zip(*self.UnitCircle))[2])
        return x,phase

    def PlotCustomPhase(self,filter):
        phase = []
        for Ux, Uy, _ in self.UnitCircle:
            polephase = 0
            zerophase = 0

            for zero_node,pole_node in zip(filter.GetZero(),filter.GetPole()):
                    # zfactor = sqrt(((Ux-zero_node.getReal())**2) + ((Uy-zero_node.getImaginary())**2))
                    zfactor = self.CalculateAngle(zero_node.getReal(), zero_node.getImaginary(), Ux, Uy)
                    zerophase+=zfactor
                    
                    pfactor = self.CalculateAngle(pole_node.getReal(), pole_node.getImaginary(), Ux, Uy)
                    polephase+=pfactor
            angle = zerophase - polephase
            # print("Zero phase: {}, Pole phase: {}".format(zerophase, polephase))
            phase.append(angle)

        self.PhaseResponse.title.set_text('Phase response')
        self.PhaseResponse.plot(list(zip(*self.UnitCircle))[2], phase)
        # plt.show()
        x= list(list(zip(*self.UnitCircle))[2])
        return x,phase
    ###########################################

    def getAppliedIndex(self):
        return self.applied_index

    def setAppliedIndex(self,index):
        self.applied_index = index
###################
    def CalculateAngle(self, x, y, circlex, circley):
        if circlex>=x:
            if circley<y:
                circley=2*(y-circley)+circley
            if circlex==x:
                angle = pi/2
                return angle
            Slope = (circley-y)/(circlex-x)
            angle = atan(Slope)
        else:
            circlex=2*(x-circlex)+circlex
            if circley<y:
                circley=2*(y-circley)+circley
                Slope = (circley-y)/(circlex-x)
                angle = atan(Slope)
                angle = pi-angle
                return angle
            Slope = (circley-y)/(circlex-x)
            angle = atan(Slope)
            angle = pi-angle
        return angle

    def CustomZeroAndPole(self):
        zero = Node()
        zero1 = Node()
        pole = Node()
        pole1 = Node()
        zero.SetImaginary(0)
        zero.SetReal(-1)
        zero1.SetImaginary(-0.9)
        zero1.SetReal(0.2)
        # zero1.SetImaginary(-0.8612)
        # zero1.SetReal(0.508)

        pole.SetImaginary(0.8)
        pole.SetReal(-0.25)
        pole1.SetImaginary(0)
        pole1.SetReal(1)
        self.Zeros.append(zero)
        # self.Zeros.append(zero1)
        # self.Poles.append(pole)
        #self.Poles.append(pole1)
    
    
    
        
        
# Z=ZTransform()
# Z.print()
# Z.PlotUnitCircle()
# Z.PlotMagnitude()
# Z.PlotPhase()

#bokeh serve --show show.py