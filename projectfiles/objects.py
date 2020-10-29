import random
import time
from functions import *


########################################################################################################################
########################################################################################################################

class province:
    def __init__(self, data, m):
        self.mapname = m
        self.id = int(data[1])
        self.owner = str(data[4])
        self.units = int(data[5])
        if configRead(5) > 0:
            self.units += random.randint(1, configRead(5))     #adding barbarians from config

########################################################################################################################

    def loadData(self, input):
        self.data = input
    def readData(self):
        return self.data

########################################################################################################################
    @property
    def data(self):
        return connect_csv('Data\\Maps\\' + self.mapname + '\\' + self.mapname + '.csv')[self.id]
    @property
    def name(self):
        return str(self.data[0])
    @property
    def X(self):
        return int(self.data[2])
    @property
    def Y(self):
        return int(self.data[3])
    @property
    def cont(self):
        return str(self.data[6])
    @property
    def bonus(self):
        return int(self.data[7])
    @property
    def con(self):
        return list(map(int, self.data[8:-1]))

########################################################################################################################

    def isOver(self, pos):
        dx = abs(pos[0]-self.X)
        dy = abs(pos[1] - self.Y)
        dist = math.sqrt(dx**2+dy**2)
        if dist <= 20:
            return True
        else:
            return False

########################################################################################################################

    def show(self, screen, pl):

        pg.draw.circle(screen, self.getcol(pl), (self.X, self.Y), 15, 0) #drawing colored background in circle
        pg.draw.circle(screen, (0, 0, 0), (self.X, self.Y), 20, 5) #drawing black circle
        drawtext(screen, self.X, self.Y, str(self.units), 15) #drawing text, number of units

########################################################################################################################

    def show2(self, screen, col = (255, 255, 255)): #standard color - white

        pg.draw.circle(screen, col, (self.X, self.Y), 22, 5)  #draw circle around province

########################################################################################################################

    def getcol(self, pl):   #getting OWNER color
        if self.owner in pl:
            return(col[pl.index(self.owner)+1])
        return col[0]

########################################################################################################################
########################################################################################################################

class Risk:
    def __init__(self): #init creates empty object ready to R E A D from server
        self.read = 1
    def init(self, name): #object init, this is done by server
        self.max_time = configRead(8)   #max round time from config
        self.start_turn_time = 0        #initial time, if equals 0, it means that game didn't started yet
        self.peacful = configRead(6)    #how many turns before war between player, from config
        self.start_units = configRead(2)#from config, tells how many units player gets while entering game
        self.start_prov = configRead(3) #as above, but no. of prov
        self.round = 0                  #initial round value
        self.read = 0                   #object is not in read state now
        self.mapname = name             #name of map, from config
        self.prov = []                  #empty list for provinces
        self.players = []               #empty list for players
        self.toH2 = []                  #empty list of provinces for HIGHLIGHT
        self.dice = []                  #dices of war, empty list for objects
        for x in connect_csv('Data\\Maps\\'+name+'\\'+name+'.csv'): #reading provinces info
            self.prov.append(province(x, self.mapname))                           #creating province objects

########################################################################################################################

    @property
    def gettime(self):
        return time.time() - self.start_turn_time #get turn time in seconds

########################################################################################################################
########################################################################################################################

class Button:
    def __init__(self, X, Y, dx, dy, text, color = (128, 128, 128)): #button object init, if no color given, GRAY
        self.X = X #left corner X
        self.Y = Y #left corner Y
        self.dx = dx #width
        self.dy = dy #height
        self.text = text
        self.color = color

########################################################################################################################

    def isOver(self, pos): #function that tells if mouse is over this object
        if pos[0] <=(self.X + self.dx) and pos[0] >= (self.X):
            if pos[1] <= (self.Y + self.dy) and pos[1] >= (self.Y):
                return True
        return False

########################################################################################################################

    def show(self, screen): #drawing button
        pg.draw.rect(screen, self.color, (self.X, self.Y, self.dx, self.dy), 0) #background rectangle
        pg.draw.rect(screen, (0, 0, 0), (self.X, self.Y, self.dx, self.dy), 3) #border
        drawtext(screen, self.X + self.dx/2, self.Y + self.dy/2, str(self.text), 12, (0, 0, 0)) #text

########################################################################################################################