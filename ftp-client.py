import socket
from lib2to3.fixer_util import String

class ftp_client:

  def __init__(self):
    self.ctrlSock = None
    self.dataSock = None

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
    self.ctrlSock = socket.socket()
    try:
      # ctrlSock.connect(("127.0.0.1", 80))
      self.ctrlSock.connect((entry_array[1], ctrlPort))
    except ConnectionRefusedError:
      print("Connection refused - check port number")
      return
        
    print("Connection established on port {}.".format(ctrlPort))
    
    #TODO: Data socket connection
      
          
  #LIST FUNCTION
  def list(self, entry_array):
      
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
      print("Invalid command - LIST requires no additional parameters")
      return

    self.ctrlSock.send(b'list\r\n')
      
      
  #RETRIEVE FUNCTION
  def retr(self, entry_array):
      
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - RETR Parameters: <filename>")
      return
      
      
  #STORE FUNCTION
  def stor(self, entry_array):
      
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - STOR Parameters: <filename>")
      return
      
      
  #QUIT FUNCTION
  def quit(self, entry_array):
    
    #Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
      print("Invalid command - QUIT requires no additional parameters")
      return 




#MAIN LOOP
################
if __name__=='__main__':
  client = ftp_client()
  while True:
    entry_array = input("Please enter command: ").split(" ")
    
    if entry_array[0] == "CONNECT":
      client.connect(entry_array)
    elif entry_array[0] == "LIST":
      client.list(entry_array)
    elif entry_array[0] == "RETR":
      client.retr(entry_array)
    elif entry_array[0] == "STOR":
      client.stor(entry_array)
    elif entry_array[0] == "QUIT":
      client.quit(entry_array)
    else:
      print("Unknown command")
