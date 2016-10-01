import socket
from lib2to3.fixer_util import String

#CONNECT FUNCTION
def connect(entry_array):
    
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
    ctrlSock = socket.socket()
    try:
#         ctrlSock.connect(("127.0.0.1", 80))
        ctrlSock.connect((entry_array[1], ctrlPort))
    except ConnectionRefusedError:
        print("Connection refused - check port number")
        return
        
    print("Connection established on port {}.".format(ctrlPort))
    
    #TODO: Data socket connection
    
        
#LIST FUNCTION
def list(entry_array):
    
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
        print("Invalid command - LIST requires no additional parameters")
        return
    
    
#RETRIEVE FUNCTION
def retr(entry_array):
    
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
        print("Invalid command - RETR Parameters: <filename>")
        return
    
    
#STORE FUNCTION
def stor(entry_array):
    
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
        print("Invalid command - STOR Parameters: <filename>")
        return
    
    
#QUIT FUNCTION
def quit(entry_array):
    
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
        print("Invalid command - QUIT requires no additional parameters")
        return 




#MAIN LOOP
################
while True:
    entry_array = input("Please enter command: ").split(" ")
    
    if entry_array[0] == "CONNECT":
        connect(entry_array)
    elif entry_array[0] == "LIST":
        list(entry_array)
    elif entry_array[0] == "RETR":
        retr(entry_array)
    elif entry_array[0] == "STOR":
        stor(entry_array)
    elif entry_array[0] == "QUIT":
        quit(entry_array)
    else:
        print("Unknown command")
