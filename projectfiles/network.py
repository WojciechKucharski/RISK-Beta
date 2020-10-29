

try:    #Import packages, functions, variables
    import socket
    import pickle
    from functions import *
    print("Network import Success")

except Exception as e:
    print(e)
    print("Import Error")

########################################################################################################################

class Network:
    def __init__(self, ipv4 = None):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating socket
        if ipv4 == None:
            self.server = configRead(0)
        else:
            self.server = str(ipv4) #server IPv4
        self.port = configRead(1) #server port
        self.addr = (self.server, self.port) #creating addres
        self.p = self.connect() #connecting to server, server returns "Risk" object

########################################################################################################################

    def connect(self):
        try:
            self.client.connect(self.addr) #connecting to server
            return pickle.loads(self.client.recv(3*2048)) #server returns first "Risk" object
        except socket.error as e:
            print("Server not found")
            print(e)
            printError(e)

########################################################################################################################

    def send(self, data):
        try:
            print(len(pickle.dumps(data)), 'bytes')
            self.client.send(pickle.dumps(data)) #client sends "Risk" object to server
            return pickle.loads(self.client.recv(3*2048))
        except socket.error as e:
            print("Connection lost?")
            print(e)
            printError(e)

########################################################################################################################

    def getP(self):
        return self.p #get first "Risk" object

########################################################################################################################