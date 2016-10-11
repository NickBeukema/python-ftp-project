import socket
import threading
import os
import sys
import pdb

from lib2to3.fixer_util import String
import cmd

ftp_client_default_port = 7712


class ftp_data_thread(threading.Thread):
  def __init__(self, cmd, filename):

    self.dataPort = 6548
    self.sock = socket.socket()
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind(("127.0.0.1", self.dataPort))
    self.sock.listen(1)
    self.sock.settimeout(1)

    self.cmd = cmd
    self.filename = filename
    self.current_dir = os.path.abspath("./ftp-downloads/")


    threading.Thread.__init__(self)

  def run(self):
    try:
      self.dataConn, addr = self.sock.accept()
    except:
      return

    if self.cmd == "list":
      self.list()
    elif self.cmd == "retr":
      self.retr()
    elif self.cmd == "stor":
      self.stor()
    else:
      print('Unhandled data thread command')

  def list(self):
    print("\nReceiving file list\n")
    total_payload = ""  # Concatenate list of files
    data = str(self.dataConn.recv(1024), "utf-8")
    while data:
      total_payload += data
      data = str(self.dataConn.recv(1024), "utf-8")

    # Print the entire list
    print("\nFTP File List\n--------------\n" + total_payload + "\n")
    self.dataConn.close()

  def retr(self):
    try:
      # Establish full directory path
      full_filename = os.path.join(self.current_dir, self.filename)
      print ("Full Dir: " + full_filename)
      f = open(full_filename, "wb+")    # Opens/creates file to copy data over
      print ("Retrieving file: " + self.filename)
      try:
        data = self.dataConn.recv(1024)
        while data:
          f.write(data)
          data = self.dataConn.recv(1024)

      except:
        print("Problem receiving data")

      f.close()
      print("File received.")
    except:
      if not f.closed:
        f.close()

      print("Cannot open file.")

    self.dataConn.close()

  def stor(self):

    # Establish full directory path
    full_filename = os.path.join(self.current_dir, self.filename)
    print("Full Dir " + full_filename)

    try:
      f = open(full_filename, "rb")  # Opens file, if it exists
      print("Storing to file: " + self.filename)
    except:
      print("File not found")
      self.dataConn.close()
      return

    # Send all data in file
    while True:
      self.data = f.read(8)
      if not self.data: break
      self.dataConn.sendall(self.data)

    f.close()

class response_thread(threading.Thread):
  def __init__(self, conn):

    self.conn = conn
    threading.Thread.__init__(self)

  def run(self):
    while True:
      self.empty()

  def empty(self):
    try:
      response = str(self.conn.recv(1024), "utf-8")
      print(response)
    except:
      return

class ftp_client:
  def __init__(self):
    self.ctrlSock = socket.socket()
    self.ctrlSock.settimeout(2)
    self.current_dir = os.path.abspath("./ftp-downloads/")

    if not os.path.exists(self.current_dir):
      os.makedirs(self.current_dir)

    # MAIN LOOP
    ################
    while True:
      entry_array = input("\nPlease enter command: ").lower().split(" ")
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
      else:
        print("Unknown command: '" + entry_array[0] + "'")

      self.response_thread.empty()

  # CONNECT FUNCTION
  def connect(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 3:
      print("Invalid command - CONNECT Parameters: <server name/IP address> <server port>")
      print("USING DEFAULT TO MAKE OUR LIVES EASIER")
      entry_array = ["connect", "127.0.0.1", 7711]

    # Parse control port to integer value
    try:
      ctrlPort = int(entry_array[2])
    except ValueError:
      print("Invalid port number")
      return

    # Establish control connection
    try:
      self.ctrlSock.connect((entry_array[1], ctrlPort))
      # after connection is established, we need to wait for the 220 response from the server "awaiting input"

      self.response_thread = response_thread(self.ctrlSock)
      self.response_thread.setDaemon(True)
      self.response_thread.start()

    except ConnectionRefusedError:
      print("Connection refused - check port number")
      return
    except OSError:
      print("Connect request was made on an already connected socket or the server not listening on that port.")
      return

    print("Connection established on port {}.".format(ctrlPort))


  # LIST FUNCTION
  def list(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
      print("Invalid command - LIST requires no additional parameters")
      return

    # Make sure ctrl connection is established
    try:
      self.send("LIST")
    except:
      print("You must connect to server before using this command")
      return

    # Open data port and receive list
    self.openDataPort(cmd="list")

  # RETRIEVE FUNCTION
  def retr(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - RETR Parameters: <filename>")
      return

    filename = entry_array[1]

    # Make sure ctrl connection is established
    try:
      self.send("RETR " + filename)
    except:
      print("You must connect to server before using this command")
      return

    #Open data port and retrieve file
    self.openDataPort(cmd="retr", filename=filename)


  # STORE FUNCTION
  def stor(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 2:
      print("Invalid command - STOR Parameters: <filename>")
      return

    filename=entry_array[1]

    # Make sure ctrl connection is established
    try:
      self.send("STOR " + filename)
    except:
      print("You must connect to server before using this command")
      return

    #Open data port and send file
    self.openDataPort(cmd="stor", filename=filename)

  # QUIT FUNCTION
  def quit(self, entry_array):

    # Make sure correct amount of parameters were passed
    if len(entry_array) != 1:
      print("Invalid command - QUIT requires no additional parameters")
      return
    else:
      self.send("QUIT")

      # self.ctrlSock().close()
      self.response_thread.empty()
      exit()

  def send(self, message, encoding="utf-8"):
      self.ctrlSock.sendall(bytearray(message + "\r\n", encoding))

  def openDataPort(self, cmd, filename=""):

    try:
      fct = ftp_data_thread(cmd=cmd, filename=filename)
      fct.start()
      fct.join()

    except:
      print("Unexpected error: ", sys.exc_info()[0])
      print("Unexpected error: ", sys.exc_info()[1])
      print("Unexpected error: ", sys.exc_info()[2])
      exit()

if __name__ == '__main__':
  client = ftp_client()
