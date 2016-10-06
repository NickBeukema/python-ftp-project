import socket
import threading
import os
import sys
import pdb

from lib2to3.fixer_util import String


class ftp_data_thread(threading.Thread):
    def __init__(self, socket):
        self.socket = socket
        self.current_dir = os.path.abspath('.')

        threading.Thread.__init__(self)

    def run(self):
        #TODO data transfer
        print("Transfer some data here")
        return()



class ftp_client:
    def __init__(self):
        self.ctrlSock = socket.socket()

        #MAIN LOOP
        ################
        while True:
            entry_array = input("Please enter command: ").lower().split(" ")
            if entry_array[0] == "connect":
                self.connect(entry_array)
            elif entry_array[0] == "list":
                self.list(entry_array)
            elif entry_array[0] == "retr":
                self.retr(entry_array)
            elif entry_array[0] == "stor":
                self.stor(entry_array)
            elif entry_array[0] == "quit":
                self.quit(entry_array)
            elif entry_array[0] == "hi":
                self.hi()
            else:
                print("Unknown command: '" + entry_array[0] + "'")

    #CONNECT FUNCTION
    def connect(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 3:
            print("Invalid command - CONNECT Parameters: <server name/IP address> <server port>")
            return

        #Parse control port to integer value
        try:
            ctrlPort = int(entry_array[2])
        except ValueError:
            print("Invalid port number")
            return

        #Establish control connection
        #ctrlSock = socket.socket()
        try:
#             self.ctrlSock.connect(("127.0.0.1", 7711))
            self.ctrlSock.connect((entry_array[1], ctrlPort))
        except ConnectionRefusedError:
            print("Connection refused - check port number")
            return              

        print("Connection established on port {}.".format(ctrlPort))
        


    #LIST FUNCTION
    def list(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 1:
            print("Invalid command - LIST requires no additional parameters")
            return


        self.send("LIST")
        self.openDataPort()
        resp=self.ctrlSock.recv(256)

        pdb.set_trace()

        #TODO receive list of files
        #TODO print list of files
        #TODO close data port
        return
        


    #RETRIEVE FUNCTION
    def retr(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 2:
            print("Invalid command - RETR Parameters: <filename>")
            return
        
        self.send("RETR " + entry_array[1])


    #STORE FUNCTION
    def stor(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 2:
            print("Invalid command - STOR Parameters: <filename>")
            return
        
        self.send("STOR " + entry_array[1])


    #QUIT FUNCTION
    def quit(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 1:
            print("Invalid command - QUIT requires no additional parameters")
            return
        else:
            self.send("QUIT")
            print ("Quitting")
            #TODO: Should we exit program here or just end the connection with the server?
            exit()


    def hi(self):
        self.send("cmd param1 param2")


    def send(self, message, encoding="utf-8"):
        self.ctrlSock.sendall(bytearray(message + "\r\n", encoding))
        
        
    def openDataPort(self):
        dataPort = 6548    #Do we need to send this value to server or can we hard code it on both ends?
        dataSock = socket.socket()
        dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dataSock.bind(("127.0.0.1", dataPort))
        dataSock.listen(1)
        
        while True:
            try:
                print ("Waiting for server to connect to data socket")
                conn, addr = dataSock.accept()
                print ("accepted data connection: " + addr[0] + ":" + str(addr[1]))  
                fct = ftp_data_thread(conn)
                fct.start()
                return
            except:
                print ("Unexpected error: ", sys.exc_info()[0])
                dataSock.close()
                exit()

    
                
#     def closeDataPort(self):
                        

if __name__ == '__main__':
  client = ftp_client()
