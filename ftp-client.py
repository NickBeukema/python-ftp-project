import socket
import threading
import os
import sys
import pdb

from lib2to3.fixer_util import String

ftp_client_default_port = 7712


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
    self.current_dir = os.path.abspath("./ftp-downloads/")
    # MAIN LOOP
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

  # CONNECT FUNCTION
  def connect(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 3:
      print("Invalid command - CONNECT Parameters: <server name/IP address> <server port>")
      print("USING DEFAULT TO MAKE OUR LIVES EASIER")
      entry_array = ["connect", "127.0.0.1", 7711]
      # return

    # Parse control port to integer value
    try:
      ctrlPort = int(entry_array[2])
    except ValueError:
      print("Invalid port number")
      return

    # Establish control connection
    # ctrlSock = socket.socket()
    try:
      #             self.ctrlSock.connect(("127.0.0.1", 7711))
      self.ctrlSock.connect((entry_array[1], ctrlPort))
      # after connection is established, we need to wait for the 220 response from the server "awaiting input"
      self.get_response()
    except ConnectionRefusedError:
      print("Connection refused - check port number")
      return

    print("Connection established on port {}.".format(ctrlPort))

  # LIST FUNCTION
  def list(self, entry_array):

    # Make sure correct amount of parameters were passed
    # Can we pass in a directory?
    if len(entry_array) != 1:
      print("Invalid command - LIST requires no additional parameters")
      return

    self.send("LIST")
    self.openDataPort()

    total_payload = ""
    data = str(self.dataConn.recv(1024), "utf-8")
    total_payload += data

    print("Receiving file list... \n")
    while data:
      data = self.dataConn.recv(1024)
      if data:
        total_payload += data

    # Handle Payload
    print(total_payload)

    # Close data port
    self.closeDataPort()

  # RETRIEVE FUNCTION
  def retr(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - RETR Parameters: <filename>")
      return

    filename = entry_array[1]
    self.send("RETR " + filename)
    self.openDataPort()

    print ("filename: " + filename)

    local_filename = self.current_dir + "\\" + filename
    f = open(local_filename, "wb+")
    data = self.dataConn.recv(1024)

    while data:
      f.write(data)
      data = self.dataConn.recv(1024)

    f.close()
    # Retrieve file from server
    # f = open("file1.txt", "wb")
    # data = self.dataConn.recv(1024)
    # print("Retrieving file... \n")
    # while data:
    #   f.write(data)
    #   data = self.dataConn.recv(1024)
    #
    # f.close()

    self.closeDataPort()

  # STORE FUNCTION
  def stor(self, entry_array):
    filename = self.current_dir + "\\" + entry_array[1]
    print("stor filename: " + filename)

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - STOR Parameters: <filename>")
      return

    self.send("STOR " + entry_array[1])
    #self.openDataPort()
    print ("connecting to server")
    self.openDataPort()
    print ("connected to server")

    file = open(filename, "rb")
    while True:
      data = file.read(1024)
      if not data: break
      self.dataConn.sendall(data)

    # Send file to server
    # f = open("file1.txt", "wb")
    # data = self.dataConn.recv(1024)
    # print("Sending file... \n")
    # while data:
    #   f.write(data)
    #   data = self.dataConn.recv(1024)

    file.close()
    self.closeDataPort()

  # QUIT FUNCTION
  def quit(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
      print("Invalid command - QUIT requires no additional parameters")
      return
    else:
      self.send("QUIT")
      response = self.get_response()
      self.ctrlSock().close()
      # TODO: Should we exit program here or just end the connection with the server?
      # exit()

  def get_response(self):
    response = self.ctrlSock.recv(1024)
    self.parse_response(response.decode("utf-8"))

  def parse_response(self, response):
    if (len(response) == 3):
      response_code = response
      response_message = ""
    else:
      response_code = response[:3]
      response_message = response[4:]

    if response_code == "221":
      print("response code: " + response_code + ", message: " + response_message)
      print("quitting")
      self.ctrlSock.close()
      exit()
    else:
      print("response code: " + response_code + ", message: " + response_message)

  def hi(self):
    self.send("cmd param1 param2")

  def send(self, message, encoding="utf-8"):
    self.ctrlSock.sendall(bytearray(message + "\r\n", encoding))

  def openDataPort(self):
    #       self.fct = ftp_data_thread(self.dataConn)
    #       self.fct.start()
    self.dataPort = 6548
    self.dataSock = socket.socket()
    self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.dataSock.bind(("127.0.0.1", self.dataPort))
    self.dataSock.listen(1)
    self.dataConn, addr = self.dataSock.accept()

    while True:
      try:
        print("Waiting for server to connect to data socket")


        # print ("Accepted data connection: " + addr[0] + ":" + str(addr[1]))

        resp = str(self.ctrlSock.recv(256), "utf-8")
        print(resp)

        #                 self.fct = ftp_data_thread(self.dataConn)
        #                 self.fct.start()

        return
      except:
        print("Unexpected error: ", sys.exc_info()[0])
        self.dataSock.close()
        exit()

  def closeDataPort(self):
    print("Done receiving")
    self.dataConn.close()


if __name__ == '__main__':
  client = ftp_client()
