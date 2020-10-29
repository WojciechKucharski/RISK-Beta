import pygame as pg
import math
from datetime import datetime, date

########################################################################################################################

def printError(e): #saving error message to file

    try:
        dateC ="Data\\Crash\\" + date.today().strftime("%d_%m_%Y") + ".txt" #current date
        now = datetime.now().strftime("%H_%M_%S") + str(e) +"\n"       #current time + error message
        with open(dateC, "a") as myfile:
            myfile.write(now)
        myfile.close() #close file
    except Exception as e:
        print(e)

########################################################################################################################

#Variable with colors
col = [(128, 128, 128), (255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 255), (0, 0, 255),
       (127, 0, 255), (255, 0, 255)]


########################################################################################################################

def drawtext(screen, X, Y, text, fontsize, color=(0, 0, 0)): #draw text on screen, screen object; middle X; left middle Y etc.

    try:
        font = pg.font.Font("Data\\Font\\arial.ttf", math.floor(fontsize * 1)) #getting font file from Data folder
        TextSurf = font.render(text, True, color) #creating text object
        TextRect = TextSurf.get_rect()
        TextRect.center = (X, Y)
        screen.blit(TextSurf, TextRect) #printing text object
    except Exception as e:
        print("Creating text from FONT failed")
        print(e)
        printError(e)

########################################################################################################################

def connect_csv(path): #reading CSV file

    obj = []
    try:
        with open(path) as f:
            lis = [line.split(",") for line in f] #splits line with ,
            for i, x in enumerate(lis):
                x[-1] = x[-1][:-1]
                obj.append(x)
    except Exception as e:
        print("CSV file reading failed")
        print(e)
        printError(e)

    return obj #returns list of lists, lines in first, values in second

########################################################################################################################

def unique(List): #returns unique INT variables from LIST

    newList = []
    try:
        for x in List:
            if x in newList:
                pass
            else:
                newList.append(int(x))
    except Exception as e:
        print("unique() failed")
        print(e)
        printError(e)
    return newList

########################################################################################################################

def configRead(id, file ="Data\\config.txt"): #reading CONFIG from txt file

    config = []
    try:
        f = open(file, "r")  # open file
        for x in f:  # extracting data
            x = x[0:-1]
            x = x.split("=")
            if len(x) == 2:
                x = x[1]
                config.append(x)  # extracting data

        config[0] = str(config[0])  # IPv4 must be a string
        config[7] = str(config[7])  # map name must be a string
        config[8] = int(config[8])  # peacful must be an integer
        for i in range(6):
            config[i + 1] = int(config[i + 1])  # rest variables must be an integer

        f.close()  # close file
    except Exception as e:
        print("Config reading failed")
        print(e)
        printError(e)
        return []
    return config[id] #0IP, 1PORT, 2STARTUNITS, 3STARTPROV, 4MINPLAYERS, 5BARBARIANS, 6PEACEFULROUNDS, 7MAPNAME, 8TURNTIME

########################################################################################################################