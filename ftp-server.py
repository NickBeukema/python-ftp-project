import socket
import threading
import sys
import os
import pdb

command_port = 7711
data_port = command_port - 1
ftp_client_default_port = 7712  # we can't use default ports on the same computer, in a real ftp client the default port for the client is the command_port

data_thread_status = ""
c = threading.Condition()


class ftp_data_thread(threading.Thread):
  def __init__(self, socket, cmd, data, filename=""):
    self.data_socket = socket
    self.cmd = cmd
    self.data = data
    self.filename = filename

    threading.Thread.__init__(self)

  def run(self):
    print("running data thread")
    if self.cmd == "list":
      self.list()
    elif self.cmd == "retr":
      self.retr()
    elif self.cmd == "stor":
      self.stor(self.filename)
    else:
      print('unhandled data_thread command')

  def retr(self):
    global data_thread_status
    print('data_thread retr')
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
      self.data_socket.sendall(bytearray(self.data))
      self.data_socket.close()
    except:
      data_thread_status = "425 Can't open data connection"

    data_thread_status = "226 Closing data connection. Requested file action successful"

  def stor(self, filename):
    global data_thread_status
    print('data_thread stor')
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
    except:
      data_thread_status = "425 Can't open data connection"

    try:
      print ("storing to file: " + filename)
      file = open(filename, "wb")
      try:
        while True:
          data = self.data_socket.recv(1024)
          if not data:
            print ('no data...')
            break
          print (data)
          file.write(data)
        file.close()
      except:
        data_thread_status = "problem receiving data"
    except:
      data_thread_status = "cant open file status"

    self.data_socket.close()
    data_thread_status = "226 Closing data connection. Requested file action successful"

  def list(self):
    global data_thread_status
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
      self.data_socket.sendall(bytearray(self.data, "utf-8"))
      self.data_socket.close()
    except:

      data_thread_status = "425 Can't open data connection"

    data_thread_status = "226 Closing data connection. Requested file action successful"

class ftp_command_thread(threading.Thread):
  def __init__(self, socket):
    self.socket = socket
    self.current_dir = os.path.abspath("./ftp-files/")
    self.data_socket = None
    threading.Thread.__init__(self)

  def run(self):
    while True:
      self.send_ctrl_response("220 awaiting input")

      # wait for commands
      cmd = str(self.socket.recv(1024), "utf-8")

      if cmd:
        if not cmd.endswith("\r\n"):
          print("ERRONEOUS CMD FROM CLIENT")
          print(cmd)
          continue
        else:
          cmd = cmd.rstrip("\r\n")

        split = cmd.lower().split(" ")

        if split[0] == "quit":
          self.quit()
          # return ends the thread?
          return
        elif split[0] == "list":
          print("list")
          if len(split) == 2:
            self.list(split[1])
          else:
            self.list(self.current_dir)
        elif split[0] == "retr":
          print("retr")
          if len(split) == 2:
            self.retr(split[1])
          else:
            # error, must supply filename
            print("retr error no filename")
        elif split[0] == "stor":
          print("stor")
          if len(split) == 2:
            self.stor(split[1])
          else:
            print("stor error no filename")
        else:
          print("Unhandled command: " + split[0])

      print("cmd: " + cmd)

  def send_ctrl_response(self, message, encoding="utf-8"):
    print ("sending ctrl response: " + message)
    self.socket.sendall(bytearray(message + "\r\n", encoding))

  def open_data_socket(self):
    if self.data_socket is None:
      self.send_ctrl_response('150 About to open data connection.')
      try:
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.connect(("127.0.0.1", 6548))
        print("Data connection established.")
      except:
        self.send_ctrl_response('425 Can’t open data connection.')
    else:
      self.send_ctrl_response('125 Data connection already open, transfer starting')

  def close_data_socket(self):
    self.data_socket.close()
    self.data_socket = None
    self.send_ctrl_response('226 Closing data connection.  Requested file action successful.')

  def quit(self):
    self.send_ctrl_response("221 closing control connection")
    self.socket.close()
    print("quitting")

  def list(self, dir):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
      files_in_dir = os.listdir(self.current_dir)
      files_in_dir.sort()
      file_string = ""
      for file in files_in_dir:
        file_string = file_string + file + "\n"

      data_thread = ftp_data_thread(socket=data_socket, cmd="list", data=file_string)
      self.send_ctrl_response('150 About to open data connection.')
      data_thread.start()
      data_thread.join()
      if data_thread_status == "":
        self.send_ctrl_response("226 Closing data connection, requested file action successful")
      else:
        self.send_ctrl_response(data_thread_status)
    except:
      self.send_ctrl_response('451 Requested action aborted: local error in processing.')

  def retr(self, filename):
    print ("server received retr cmd filename: " + filename)
    filename = self.current_dir + "\\" + filename
    print ("abs path: " + filename)
    if not os.path.exists(filename):
      self.send_ctrl_response("550 File Unavailable")
      return
    print ("file exists")

    if os.access(filename, os.R_OK):
      data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      file_data = ""
      try:
        file = open(filename, 'rb')
        file_data = file.read()
        data_thread = ftp_data_thread(socket=data_socket, cmd="retr", data=file_data)
        self.send_ctrl_response('150 About to open data connection.')
        print('start retr thread')
        data_thread.start()
        data_thread.join()
        if data_thread_status == "":
          self.send_ctrl_response("226 Closing data connection, requested file action successful")
        else:
          self.send_ctrl_response(data_thread_status)
      except:
        self.send_ctrl_response("450 File Unavailable")
    else:
      self.send_ctrl_response("550 File Unavailable")
      return

  def stor(self, filename):
    filename = self.current_dir + "\\" + filename
    print ("abs path: " + filename)

    if os.access(filename, os.R_OK) or not os.path.isfile(filename):
      data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
        data_thread = ftp_data_thread(socket=data_socket, cmd="stor", data="", filename=filename)
        self.send_ctrl_response('150 About to open data connection.')
        print('starting stor thread')
        data_thread.start()
        data_thread.join()
        if data_thread_status == "":
          self.send_ctrl_response("226 Closing data connection, requested file action successful")
        else:
          self.send_ctrl_response(data_thread_status)
      except:
        self.send_ctrl_response("450 File Unavailable")
    else:
      self.send_ctrl_response("550 File Unavailable")
      return



class ftp_server:
  # basic class/socket setup
  def __init__(self):
    # self.port = 7711
    self.server_socket = socket.socket()
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_socket.bind(("localhost", command_port))

    # listen for 1 client
    self.server_socket.listen(1)

    while True:
      try:
        print("waiting for connection on " + self.server_socket.getsockname()[0] + ":" + str(
          self.server_socket.getsockname()[1]))
        conn, addr = self.server_socket.accept()

        print("accepted command connection: " + addr[0] + ":" + str(addr[1]))
        fct = ftp_command_thread(conn)
        fct.start()
      except:
        print("Unexpected error: ", sys.exc_info()[0])
        print("Unexpected error: ", sys.exc_info()[1])
        print("Unexpected error: ", sys.exc_info()[2])
        self.server_socket.close()
        exit()


if __name__ == '__main__':
  # kick it off
  server = ftp_server()
