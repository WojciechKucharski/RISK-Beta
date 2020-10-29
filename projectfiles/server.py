try:
    import socket
    from _thread import *
    from objects import *
    import pickle
    from functions import *
except Exception as e:
    print("Server Import Error")
    print(e)

########################################################################################################################

server = configRead(0) #informations from config
port = configRead(1)

########################################################################################################################

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating socket
try:
    s.bind((server, port))  #try binding
except socket.error as e:
    print(str(e))
s.listen(10)

########################################################################################################################

game = Risk() #create empty Risk object
game.init(configRead(7))    #init game with MAP name from config
G = [game]  #put game to list (won't work other way)
print("Waiting for connection, Server Started")

########################################################################################################################

def threaded_client(conn):
    conn.send(pickle.dumps(G[0]))   # self.p from Network class
    while True:
        try:
            data = pickle.loads(conn.recv(3*2048)) #try read data
            if data.read == 0:  #if read = 0, overwrite server data with sent data
                G[0] = data
            if not data:
                break
            else:
                pass
            conn.sendall(pickle.dumps(G[0]))#return data from server (if read = 1)
            if data.read == -1:
                break
        except Exception as e:
            print(e)
            break
    print("Lost connection")
    conn.close()                #close connection if error occured

########################################################################################################################

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))  #create connection threads

########################################################################################################################
