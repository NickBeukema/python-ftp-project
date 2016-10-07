import socket
import threading
import os
import sys
import pdb

from lib2to3.fixer_util import String


# class ftp_data_thread(threading.Thread):
#     def __init__(self, socket):
#         self.socket = socket
#         self.current_dir = os.path.abspath('.')
#  
#         threading.Thread.__init__(self)
#  
#     def run(self):
#         f = open("file1.txt", "w+")
#         data = self.dataConn.recv(1024)
#         while data:
#             print("Receiving... ") 
#             f.write(data)
#             data = self.dataConn.recv(1024)
#         else:
#             print("data: not found")
#         f.close()
#         return



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
        self.openDataPort("LIST")
#         resp=str(self.ctrlSock.recv(256), "utf-8")
#         print("control " + resp)
#         pdb.set_trace()

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
        self.openDataPort("RETR")


    #STORE FUNCTION
    def stor(self, entry_array):

        #Make sure correct amount of parameters were passed
        if len(entry_array) != 2:
            print("Invalid command - STOR Parameters: <filename>")
            return
        
        self.send("STOR " + entry_array[1])
        self.openDataPort("STOR")


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
        
        
    def openDataPort(self, sentFrom):
        self.dataPort = 6548
        self.dataSock = socket.socket()
        self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.dataSock.bind(("127.0.0.1", self.dataPort))
        self.dataSock.listen(1)
        print("Sent from: " + sentFrom)
        
        while True:
            try:
                print ("Waiting for server to connect to data socket")
                self.dataConn, addr = self.dataSock.accept()
#                 print ("Accepted data connection: " + addr[0] + ":" + str(addr[1]))
                resp=str(self.ctrlSock.recv(256), "utf-8")
                print(resp) 
                
                #Print file list sent from server
                if sentFrom == "LIST":
                    data = str(self.dataConn.recv(1024), "utf-8")
                    print("Receiving file list... \n")
                    while data: 
                        print(data)
                        data = self.dataConn.recv(1024)
                        
#                 #Send file to server
#                 elif sentFrom == "STOR":
#                     f = open("file1.txt", "wb")
#                     data = self.dataConn.recv(1024)
#                     print("Sending file... \n") 
#                     while data:
#                         f.write(data)
#                         data = self.dataConn.recv(1024)
#                         
#                 #Retrieve file from server
#                 elif sentFrom == "RETR":
#                     f = open("file1.txt", "wb")
#                     data = self.dataConn.recv(1024)
#                     print("Retrieving file... \n") 
#                     while data:
#                         f.write(data)
#                         data = self.dataConn.recv(1024)
                        
                f.close()
                print("Done receiving")
                self.dataConn.close()
#                 self.fct = ftp_data_thread(self.dataConn)
#                 self.fct.start()

                return
            except:
                print ("Unexpected error: ", sys.exc_info()[0])
                self.dataSock.close()
                exit()

    
                
#     def closeDataPort(self):
                        

if __name__ == '__main__':
  client = ftp_client()
