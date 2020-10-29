import pygame as pg
from network import Network
import random
import math
from functions import *
from objects import *
import time
import sys

########################################################################################################################
########################################################################################################################

class Operator:
    def __init__(self, ipp = None, name = None):

        self.nick = name
        self.turns = 1
        self.time_e = 0
        self.new = 0
        self.attack_units = 0
        self.status = 0
        self.toH = []
        self.toH2 = []
        self.fortify = []
        self.buttons = []
        self.prov_name = []
        self.prov_nameDATA = []

########################################################################################################################
        self.gameInit()  # pygame init

        if ipp is None:
            a, b = self.lobby()
            self.server_ip = b
        else:
            self.server_ip = ipp
            a = name
########################################################################################################################

        self.net = Network(self.server_ip)
        self.game = Risk()
        self.game = self.net.getP()
        while self.game is None:
            self.reconnect()
        print("Connected to server")

########################################################################################################################

        if self.nick != "Spec":
            self.nick = a
            self.addplayer()

########################################################################################################################

        self.map = pg.image.load('Data\\Maps\\' + self.game.mapname + '\\' + self.game.mapname + '.jpg')
        self.size = list(self.map.get_size())
        self.screen = pg.display.set_mode((self.size[0]+400, self.size[1]), pg.RESIZABLE)
        self.buttons.append(Button(self.size[0]+150, self.size[1]-100, 100, 50, "START", (0, 255, 0)))

        self.sound = [(pg.mixer.Sound("Data\\Sound\\cl.wav")), pg.mixer.Sound("Data\\Sound\\ex.wav"), pg.mixer.Sound("Data\\Sound\\ar.wav")]
        for x in self.sound:
            x.set_volume(0.05)


########################################################################################################################
########################################################################################################################

    @property
    def ID(self):
        for x in self.game.players:
            if x == self.nick:
                return self.game.players.index(x)

########################################################################################################################

    @property
    def myTurn(self):
        if self.ID == self.getround:
            return True
        else:
            return False

########################################################################################################################

    @property
    def getround(self):
        if len(self.game.players) <= 0:
            return 0
        else:
            return self.game.round % len(self.game.players)

########################################################################################################################

    @property
    def mProv(self):
        my_provinces = []
        for x in self.game.prov:
            if x.owner == self.nick:
                my_provinces.append(int(x.id))
        return my_provinces

########################################################################################################################

    @property
    def vProv(self):
        d = []
        for x in self.mProv:
            d = d + self.game.prov[x].con
        d = unique(d)
        for x in self.mProv:
            if x in d:
                d.remove(x)
        return d

########################################################################################################################

    @property
    def new_units(self):
        new = 0
        cont = []
        cont_own = []
        new += math.ceil(len(self.mProv)/3)
        for x in self.game.prov:
            if x.cont in cont:
                pass
            else:
                cont.append(x.cont)
                cont_own.append(0)
            if x.owner == self.nick:
                if cont_own[cont.index(x.cont)] != -1:
                    cont_own[cont.index(x.cont)] = x.bonus
            else:
                cont_own[cont.index(x.cont)] = -1

        for x in cont_own:
            if x < 0:
                x = 0
            new += x
        return new

########################################################################################################################

    def play_sound(self, no):
        pg.mixer.Sound.play(self.sound[no-1])
        if no == 3:
            N = self.sound[no-1].get_length()
            self.sound[no-1].fadeout(int(N * 150))

########################################################################################################################

    def dl(self):
        self.game.read = 1
        self.game = self.net.send(self.game)
        if self.game is None:
            try:
                self.reconnect()
            except Exception as e:
                print(e)
                pass
            self.dl()

########################################################################################################################

    def ul(self):
        self.game.read = 0
        self.net.send(self.game)
        if self.game is None:
            try:
                self.reconnect()
            except Exception as e:
                print(e)
                pass
            self.ul()

########################################################################################################################

    def reconnect(self):
        self.net = Network(self.server_ip)
        self.game = Risk()
        self.game = self.net.getP()
        print("Connecting to server...")
        time.sleep(1)


########################################################################################################################

    def neighbor(self, id, block = False):
        list = []
        for x in self.game.prov[id].con:
            list.append(int(x))
        for x in self.mProv:
            if x in list:
                list.remove(x)
        if block:
            for x in list:
                if self.game.prov[x].owner in self.game.players:
                    list.remove(x)
        return list

########################################################################################################################

    def quit(self):
        if self.nick != "Spec":
            for x in self.game.players:
                if x == self.nick:
                    self.game.players.remove(x)
            self.ul()

########################################################################################################################

    def addplayer(self):
        if self.nick in self.game.players:
            pass
        else:
            self.game.players.append(self.nick)

        if len(self.mProv) < 1:
            for x in range(self.game.start_prov):
                adding = True
                while adding:
                    N = random.randrange(0, len(self.game.prov))
                    if self.game.prov[N].owner == 0 or self.game.prov[N].owner == "0":
                        self.game.prov[N].owner = self.nick
                        self.game.prov[N].units = self.game.start_units
                        adding = False
        self.ul()

########################################################################################################################

    def connected(self, id):
        id = list(id)
        new = False
        for x in id:
            for y in self.game.prov[x].con:
                if self.game.prov[int(y)].owner == self.nick:
                    if y in id:
                        pass
                    else:
                        new = True
                        id.append(y)
        if new:
            return self.connected(id)
        else:
            return id

########################################################################################################################

    def end_round(self):
        self.turns += 1
        self.game.round += 1
        self.game.start_turn_time = time.time()
        self.ul()
        self.fortify = []
        self.status = 0
        self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "START", (0, 255, 0))]
        self.toH2 = []
        self.toH = []

########################################################################################################################

    def show(self):
        self.screen.fill((255, 230, 179))
        self.screen.blit(self.map, (0, 0))
        if self.nick == "Spec":
            for x in range(len(self.game.prov)):
                self.game.prov[x].show(self.screen, self.game.players)
        for x in (self.vProv+self.mProv):
            self.game.prov[x].show(self.screen, self.game.players)
        for x in self.toH:
            x = int(x)
            self.game.prov[x].show2(self.screen)
        for x in self.toH2:
            x = int(x)
            self.game.prov[x].show2(self.screen, (255, 0, 0))
        if self.game.start_turn_time != 0:
            drawtext(self.screen,
                    self.size[0] + 200,10,
                    str("Time: " + str(self.game.max_time - int(self.game.gettime))),
                    10,(0,0,0))
        for i in range(len(self.game.players)):
            app = ""
            tur = ""
            if self.nick != "Spec":
                if i == self.game.players.index(self.nick):
                    tur = str(" Turn: "+str(self.turns))
            if self.getround == i:
                app = ">   "
            drawtext(self.screen,
                     self.size[0]+200+1,
                     50*(i+1)+1,
                     str(app+self.game.players[i] + tur),
                     20,
                     (0, 0, 0))
            drawtext(self.screen,
                     self.size[0]+200,
                     50*(i+1),
                     str(app+self.game.players[i] + tur),
                     20,
                     col[i+1])
        if self.myTurn:
            if len(self.game.players) > (configRead(4) - 1):
                for x in self.buttons + self.fortify:
                    x.show(self.screen)
        if len(self.game.toH2) == 2:
            if not self.myTurn:
                if self.game.prov[int(self.game.toH2[1])].owner == self.nick:
                    for x in self.game.toH2:
                        x = int(x)
                        self.game.prov[x].show2(self.screen, (255, 0, 0))
                    for x in self.game.dice:
                        x.show(self.screen)
        if self.myTurn:
            for x in self.game.dice:
                x.show(self.screen)
        for x in self.prov_name:
            drawtext(self.screen,
                     self.size[0]+200+1,
                     self.size[1]-25+1,
                     str("Province name: " + self.prov_name),
                     20,
                     (0, 0, 0))
            drawtext(self.screen,
                     self.size[0]+200,
                     self.size[1]-25,
                     str("Province name: " + self.prov_name),
                     20,
                     (255, 255, 255))

        pg.display.update()

########################################################################################################################

    def drag(self, pos):

        self.displayProvName(pos) #display prov name in right corner

        if self.myTurn and self.status == 0:
            self.skipStartButton()  #if game already started, skip START button

        elif self.status == 1:
            self.showProv2addUnit(pos)  #if user is adding units, higlight prov

        elif self.status == 2:
            self.showProvs2attack(pos) #highlight provs that are possible to attack

        elif self.status == 6:
            self.showConnectedProvs(pos) #while user if fortifying, highlight possible options

########################################################################################################################

    def click(self, pos):

        self.dl()               #download server info

        self.play_sound(1)      #play "click" sound

        if self.status == 0:    #only if game didn't started yet, starts timer and adds units to add
            self.START(pos)

        elif self.status == 1:  #add new unit to owned province
            self.addUnit(pos)

        elif self.status == 2:  #choose attacker province
            self.chooseAttacker(pos)

        elif self.status == 3:  #choose victim to attack
            self.chooseVictim(pos)

        elif self.status == 4:  #choose number of attackers
            self.chooseUnitsNumber(pos)

        elif self.status == 45: #choose what to do, ROLL, BLITZ, ESCAPE
            self.chooseTactic(pos)

        elif self.status == 5:  #choose number of units to go back
            self.chooseUnitsNumber2(pos)

        elif self.status == 6:  #choose supporter province
            self.chooseSupporter(pos)

        elif self.status == 7:  #choose supported province
            self.chooseSupported(pos)

        elif self.status == 8:  #choose number of units to move
            self.chooseUnitsNumber3(pos)
        self.ul()
########################################################################################################################

    def war(self, Blitz = False):

        att = min(self.attack_units, 3)
        deff = min(self.game.prov[int(self.toH2[1])].units, 2)
        text = str(self.attack_units) +" VS "+str(self.game.prov[int(self.toH2[1])].units)
        att_dice = []
        deff_dice = []

        for x in range(att):
            att_dice.append(random.randint(1, 6))
        for x in range(deff):
            deff_dice.append(random.randint(1, 6))
        att_dice.sort(reverse=True)
        deff_dice.sort(reverse=True)


        if not Blitz:

            self.buttons = []
            self.game.dice = []
            self.game.dice.append(Button(self.size[0] + 150, self.size[1] - 150, 100, 50, text, (128, 128, 128)))
            for x in range(att):
                self.game.dice.append(Button(self.size[0] + 170, self.size[1] - 90 + x*30, 25, 25, str(att_dice[x]), self.game.prov[int(self.toH2[0])].getcol(self.game.players)))
            for x in range(deff):
                self.game.dice.append(Button(self.size[0] + 205, self.size[1] - 90 + x*30, 25, 25, str(deff_dice[x]), self.game.prov[int(self.toH2[1])].getcol(self.game.players)))
            self.ul()
            self.show()
            time.sleep(1)

        for i in range(min(att, deff)):
            if att_dice[i] > deff_dice[i]:
                if not Blitz:
                    self.game.dice[i+1].X += 18
                    self.game.dice[att+i+1].X += 300
                    self.play_sound(2)
                self.game.prov[int(self.toH2[1])].units -= 1
                if not Blitz:
                    self.game.dice[0].text = str(self.attack_units) + " VS " + str(self.game.prov[int(self.toH2[1])].units)
            else:
                if not Blitz:
                    self.game.dice[i+1].X += 300
                    self.game.dice[att+i+1].X -= 17
                    self.play_sound(2)
                self.attack_units -= 1
                if not Blitz:
                    self.game.dice[0].text = str(self.attack_units) + " VS " + str(self.game.prov[int(self.toH2[1])].units)
            if not Blitz:
                #halo
                self.ul()
                self.show()
                time.sleep(1)
            self.ul()
            self.show()

        if not Blitz:
            self.game.dice = []
            self.buttons = []
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "ROLL", (0, 255, 0)))
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 175, 100, 50, "BLITZ", (0, 255, 0)))
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ESCAPE", (0, 255, 0)))
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 325, 100, 50, "UNITS: "+str(self.attack_units)))
            self.ul()

########################################################################################################################

    def gameInit(self):  # PyGame init
        pg.init()
        pg.display.set_caption("The Game of RISK! - Client ")  # window name
        icon = pg.image.load('Data\\Icon\\logo.png')  # loading icon
        pg.display.set_icon(icon)  # setting icon
        pg.mixer.music.load("Data\\Sound\\bg.wav")  # playing music in loop
        pg.mixer.music.set_volume(0.01)  # adjusting music volume
        pg.mixer.music.play(-1)  # loop music forever

########################################################################################################################

    def main(self):
        leave = 0
        running = True
        if True:
            while running:  # game loop
                if True:
                    self.show()  # print graphics

                    if len(self.game.players) > 0:  # react to mouse drag if enought players
                        pos = pg.mouse.get_pos()
                        self.drag(pos)  # drag reaction function
                    for event in pg.event.get():
                        if len(self.game.players) > 0:  # react to mouse clicl if enought players
                            if event.type == pg.MOUSEBUTTONDOWN and self.myTurn:
                                self.click(pos)  # click reaction function
                        if event.type == pg.QUIT:  # leave the game if user used [x]
                            leave += 1
                            if leave > 1:  # avoid random leave
                                self.quit()  # leaving game safe
                                running = False  # break loop
                                break

                    if not self.myTurn:  # if it's not users turn, download data every second
                        time.sleep(2)
                        Before = self.mProv
                        self.dl()
                        After = self.mProv
                        if Before != After:  # comparing if between downloads any province was lost
                            self.play_sound(2)  # if lost, then play sound

                    lost = True
                    for x in self.game.prov:
                        if x.owner == self.nick:  # checking if all provinces were lost
                            lost = False
                            break

                    if lost:
                        self.quit()  # if user have 0 provinces, leave GAME and turn to SPECTATOR
                        self.nick = "Spec"

                    if self.game.start_turn_time != 0:  # take turn from user if time is up
                        if self.game.gettime > self.game.max_time:
                            if self.attack_units > 0:  # check if user is in middle of attack
                                self.game.prov[
                                    int(self.toH2[0])].units += self.attack_units  # if yes, then give units back
                            self.end_round()  # skip to next round

                    if self.game.start_turn_time == 0:
                        self.dl()  # download data if game no started so user can see players


########################################################################################################################

    def lobby(self):

        ips = []
        data = []
        refreshing = False
        self.screen = pg.display.set_mode((800, 500),pg.RESIZABLE)
        f = open("Data\\servers.txt", "r")

        for x in f:
            data.append(str(x).replace("\n", ""))
        playername = data[0]

        if len(data) > 1:
            for x in data[1:]:
                ips.append(x)
        if configRead(0) in ips:
            pass
        else:
            ips.append(configRead(0))
        f.close()


        button = Button(260, 212, 75, 25, "Refresh", (0, 255, 0))
        join_buttons = []


        while True:

            pg.display.update()
            self.screen.fill((0, 0, 0))
            if refreshing:
                join_buttons = []
                ips2 = []
                for x in ips:
                    obj = Network(x)
                    if not obj.p is None:
                        ips2.append(x)
                        join_buttons.append(Button(200, 250 + 50 * len(join_buttons), 400, 25,
                                                   "Join " + x + " Players: " + str(len(obj.p.players)), (0, 255, 0)))
                        obj.p.read = -1
                        obj.send(obj.p)
                refreshing = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    raise Exception("lol")


                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        if len(playername)>0:
                            playername = playername[0:-1]
                    else:
                        if len(playername) < 6:
                            playername += event.unicode


                elif event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    if button.isOver(pos):
                        refreshing = True

                    else:
                        for x in join_buttons:
                            if x.isOver(pos):
                                pg.display.update()
                                self.screen.fill((0, 0, 0))
                                drawtext(self.screen,
                                         400,
                                         150,
                                         "CONNECTING",
                                         60,
                                         (255, 255, 255))
                                pg.display.update()
                                self.update_name(playername)
                                return playername, ips2[join_buttons.index(x)]


            drawtext(self.screen, 400, 150, "Nick: " + playername, 40, (255, 255, 255))
            drawtext(self.screen, 400, 225, "Servers:", 20, (255, 255, 255))
            if not refreshing:
                button.show(self.screen)
            for x in join_buttons:
                x.show(self.screen)

########################################################################################################################

    def update_name(self, playername):
        a_file = open("Data\\servers.txt", "r")
        list_of_lines = a_file.readlines()
        list_of_lines[0] = playername + "\n"

        a_file = open("Data\\servers.txt", "w")
        a_file.writelines(list_of_lines)
        a_file.close()

########################################################################################################################

    def displayProvName(self, pos):
        for x in range(len(self.game.prov)):
            if self.game.prov[x].isOver(pos):
                self.prov_name = self.game.prov[x].name
                break
            else:
                self.prov_name = []

########################################################################################################################

    def skipStartButton(self):

        if self.game.start_turn_time != 0:
            self.units2add

        else:
            pass

########################################################################################################################

    def showProv2addUnit(self, pos):

        for x in self.mProv:
            if self.game.prov[x].isOver(pos):
                self.toH = [x]
                break
            else:
                self.toH = []

########################################################################################################################

    def showProvs2attack(self, pos):
        #self.fortify = [Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "FORTIFY", (0, 255, 0))]
        clear = True
        for x in self.mProv:
            if self.game.prov[x].isOver(pos):
                Block = False
                if self.game.peacful > self.turns:
                    Block = True
                self.toH = [x] + self.neighbor(x, Block)
                clear = False

        if clear:
            self.toH = []

########################################################################################################################

    def showConnectedProvs(self, pos):

        clear = True
        for x in self.mProv:
            if self.game.prov[x].isOver(pos):
                self.toH = [x]
                for y in self.connected([int(x)]):
                    if self.game.prov[int(y)].owner == self.nick:
                        self.toH += [self.game.prov[int(y)].id]
                clear = False
        if clear:
            self.toH = []

########################################################################################################################

    def START(self, pos): #status 0 - waitng for start

        if self.buttons[0].isOver(pos):

            if self.game.start_turn_time == 0:
                self.game.start_turn_time = time.time()

            self.units2add()

########################################################################################################################

    def units2add(self):
        self.new = self.new_units
        self.buttons[0].text = "ADD: " + str(self.new)
        self.buttons[0].color = (128, 128, 128)
        self.status = 1
        self.play_sound(3)

########################################################################################################################

    def skip2attack(self):
        self.status = 2
        self.buttons[0].text = "ATTACK"
        self.buttons[0].color = (128, 128, 128)
        self.fortify = [Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "FORTIFY", (0, 255, 0))]
        self.toH = []

########################################################################################################################

    def skip2fortify(self):
        self.status = 6
        self.fortify = [Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "READY", (0, 255, 0))]
        self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "FORTIFY")]

########################################################################################################################

    def addUnit(self, pos): #status 1 - adding units

        if self.new == 0:
            self.skip2attack()

            return 0
        for x in self.mProv:
            if self.game.prov[x].isOver(pos):
                self.game.prov[x].units += 1
                self.new -= 1
                self.buttons[0].text = "ADD: " + str(self.new)

                if self.new == 0:
                    self.skip2attack()

########################################################################################################################

    def chooseAttacker(self, pos): #status 2 - choosing attacker
        self.fortify = [Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "FORTIFY", (0, 255, 0))]
        if self.fortify[0].isOver(pos):
            self.skip2fortify()
        else:
            for x in self.mProv:
                if self.game.prov[x].isOver(pos):
                    if self.game.prov[x].units > 1:
                        self.toH2.append(x)
                        self.fortify = []
                        self.status = 3

########################################################################################################################

    def chooseVictim(self, pos): #status 3 - choosing victim

        goback = True
        if self.toH2[0] in self.toH:
            self.toH.remove(self.toH2[0])
        for x in self.toH:
            if self.game.prov[int(x)].isOver(pos):
                victim = x
                goback = False
        if goback:
            self.toH2 = []
            self.status = 2
        else:
            self.toH2.append(victim)
            self.status = 4
            self.toH = []
            self.createNumberButtons(self.game.prov[self.toH2[0]].units - 1)

########################################################################################################################

    def createNumberButtons(self, N):
        self.buttons = []
        for i in range(N):
            self.buttons.append(
                Button(self.size[0] + 5 + 20 * ((i + 1) // 25), 15 + 20 * ((i + 1) % 25), 16, 16, str(i + 1),
                       (0, 255, 0)))

########################################################################################################################

    def chooseUnitsNumber(self, pos):

        if pos[0] <= self.size[0]:
            self.toH2 = []
            self.status = 2
            self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ATTACK")]
        else:
            self.attack_units = 0
            for x in range(len(self.buttons) - 1):
                if self.buttons[x + 1].isOver(pos):
                    self.attack_units = x + 1
                    break
            if self.attack_units == 0:
                self.toH2 = []
                self.status = 2
                self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ATTACK")]
            else:
                if int(self.game.prov[int(self.toH2[1])].units) == 0:
                    self.game.prov[int(self.toH2[0])].units -= self.attack_units
                    self.game.prov[int(self.toH2[1])].units = self.attack_units
                    self.game.prov[int(self.toH2[1])].owner = self.nick
                    self.play_sound(2)
                    self.attack_units = 0
                    self.ul()
                    self.status = 5
                    self.createNumberButtons(self.game.prov[int(self.toH2[1])].units - 1)
                else:
                    self.status = 45
                    self.game.toH2 = self.toH2
                    self.ul()
                    self.game.prov[int(self.toH2[0])].units -= self.attack_units
                    self.buttons = []
                    self.buttons.append(
                        Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "ROLL", (0, 255, 0)))
                    self.buttons.append(
                        Button(self.size[0] + 150, self.size[1] - 175, 100, 50, "BLITZ", (0, 255, 0)))
                    self.buttons.append(
                        Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ESCAPE", (0, 255, 0)))
                    self.buttons.append(
                        Button(self.size[0] + 150, self.size[1] - 325, 100, 50, "UNITS: " + str(self.attack_units)))

########################################################################################################################

    def chooseTactic(self,pos):
        self.game.toH2 = self.toH2
        self.ul()
        if self.buttons[2].isOver(pos):
            self.game.prov[int(self.toH2[0])].units += self.attack_units
            self.attack_units = 0
            self.game.toH2 = []
            self.ul()
            self.toH2 = []
            self.status = 2
            self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ATTACK")]
        elif self.buttons[1].isOver(pos):
            w = True
            if self.attack_units == 0 or int(self.game.prov[int(self.toH2[1])].units) == 0:
                w = False
            while w:
                try:
                    self.war(True)
                except:
                    pass
                if self.attack_units == 0:
                    w = False
                elif int(self.game.prov[int(self.toH2[1])].units) == 0:
                    w = False
            self.game.toH2 = []
            self.play_sound(2)
            self.ul()
            if self.attack_units == 0:
                self.game.toH2 = []
                self.ul()
                self.toH2 = []
                self.status = 2
                self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ATTACK")]
            elif int(self.game.prov[int(self.toH2[1])].units) == 0:
                self.game.prov[int(self.toH2[1])].units = self.attack_units
                self.game.prov[int(self.toH2[1])].owner = self.nick
                self.attack_units = 0
                self.ul()
                self.status = 5
                self.buttons = [Button(self.size[0] + 125, self.size[1] - 100, 150, 50, "MOVE BACK")]
                for i in range(int(self.game.prov[int(self.toH2[1])].units - 1)):
                    self.buttons.append(
                        Button(self.size[0] + 5 + 20 * ((i + 1) // 25), 15 + 20 * ((i + 1) % 25), 16, 16, str(i + 1),
                               (0, 255, 0))
                    )
        elif self.buttons[0].isOver(pos):
            self.war()
            self.game.toH2 = []
            self.ul()
            self.buttons = []
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 250, 100, 50, "ROLL", (0, 255, 0)))
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 175, 100, 50, "BLITZ", (0, 255, 0)))
            self.buttons.append(Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ESCAPE", (0, 255, 0)))
            self.buttons.append(
                Button(self.size[0] + 150, self.size[1] - 325, 100, 50, "UNITS: " + str(self.attack_units)))

            if self.attack_units == 0:
                self.game.toH2 = []
                self.ul()
                self.toH2 = []
                self.status = 2
                self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "ATTACK")]

            elif int(self.game.prov[int(self.toH2[1])].units) == 0:
                self.game.prov[int(self.toH2[1])].units = self.attack_units
                self.game.prov[int(self.toH2[1])].owner = self.nick
                self.attack_units = 0
                self.ul()
                self.status = 5
                self.buttons = [Button(self.size[0] + 125, self.size[1] - 100, 150, 50, "MOVE BACK")]
                for i in range(int(self.game.prov[int(self.toH2[1])].units - 1)):
                    self.buttons.append(
                        Button(self.size[0] + 5 + 20 * ((i + 1) // 25), 15 + 20 * ((i + 1) % 25), 16, 16, str(i + 1),
                               (0, 255, 0))
                    )

########################################################################################################################

    def chooseUnitsNumber2(self, pos):
        if int(self.game.prov[int(self.toH2[1])].units) == 1:
            pass
        else:
            moving_units = 0
            for x in range(len(self.buttons) - 1):
                if self.buttons[x + 1].isOver(pos):
                    moving_units = x + 1
                    break
            self.game.prov[int(self.toH2[1])].units -= moving_units
            self.game.prov[int(self.toH2[0])].units += moving_units
        self.ul()
        self.toH2 = []
        self.buttons = [Button(self.size[0] + 150, self.size[1] - 100, 100, 50, "FORTIFY")]
        self.status = 2

########################################################################################################################

    def chooseSupporter(self, pos):
        if self.fortify[0].isOver(pos):
            self.end_round()
        else:
            for x in self.mProv:
                if self.game.prov[x].isOver(pos):
                    if self.game.prov[x].units > 1:
                        self.toH2.append(x)
                        self.status = 7

########################################################################################################################

    def chooseSupported(self, pos):
        if self.fortify[0].isOver(pos):
            self.end_round()
        else:
            goback = True
            if self.toH2[0] in self.toH:
                self.toH.remove(self.toH2[0])
            for x in self.toH:
                if self.game.prov[int(x)].isOver(pos):
                    victim = x
                    goback = False
            if goback:
                self.toH2 = []
                self.status = 6
            else:
                self.toH2.append(victim)
                self.status = 8
                self.toH = []
                for i in range(self.game.prov[self.toH2[0]].units - 1):
                    self.buttons.append(
                        Button(self.size[0] + 5 + 20 * ((i + 1) // 25), 15 + 20 * ((i + 1) % 25), 16, 16, str(i + 1),
                               (0, 255, 0))
                    )

########################################################################################################################

    def chooseUnitsNumber3(self, pos):
        if self.fortify[0].isOver(pos):
            self.play_sound(3)
            self.end_round()
        else:
            moving_units = 0
            for x in range(len(self.buttons) - 1):
                if self.buttons[x + 1].isOver(pos):
                    moving_units = x + 1
                    break
            self.game.prov[int(self.toH2[0])].units -= moving_units
            self.game.prov[int(self.toH2[1])].units += moving_units
            self.play_sound(3)
            self.end_round()