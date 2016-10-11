import socket
import threading
import sys
import os
import pdb
import queue

command_port = 7711
data_port = command_port - 1
ftp_client_default_port = 7712  # we can't use default ports on the same computer, in a real ftp client the default port for the client is the command_port

data_thread_status = ""
c = threading.Condition()


class ftp_data_thread(threading.Thread):
  def __init__(self, socket, cmd, data, filename="", q=None):
    self.data_socket = socket
    self.cmd = cmd
    self.data = data
    self.filename = filename
    self.q = q

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

    return

  def retr(self):
    global data_thread_status
    print('data_thread retr')
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
      self.data_socket.sendall(bytearray(self.data))
      self.data_socket.close()
    except:
      self.set_thread_status("425 Can't open data connection")

    self.set_thread_status("226 Closing data connection. Requested file action successful")

  def stor(self, filename):
    global data_thread_status
    print('data_thread stor')
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
    except:
      self.set_thread_status("425 Can't open data connection")

    try:
      file = open(filename, "wb+")
      print ("storing to file: " + filename)
      try:
        while True:
          data = self.data_socket.recv(1024)
          if not data:
            print ('no data...')
            break
          print (data)
          file.write(data)
        file.close()
        self.set_thread_status("226 Closing data connection. Requested file action successful")
      except:
        data_thread_status = "problem receiving data"
    except:
      data_thread_status = "Can't open file status"

    self.data_socket.close()

  def list(self):
    global data_thread_status
    try:
      self.data_socket.connect(("127.0.0.1", 6548))
      print ("Sending file list")
      self.data_socket.sendall(bytearray(self.data, "utf-8"))
      self.data_socket.close()
      self.set_thread_status("226 Closing data connection. Requested file action successful\r\n")
    except:
      self.set_thread_status("425 Can't open data connection\r\n")

  def set_thread_status(self, message):
    print (message)
    self.q.put(message)

class ftp_command_thread(threading.Thread):
  def __init__(self, socket):
    self.socket = socket
    self.current_dir = os.path.abspath("./ftp-files/")
    self.data_socket = None
    threading.Thread.__init__(self)
    self.finished_running = False

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
        print("cmd: " + cmd)

        try:

          # Dynamically call the command passing along the entire
          # command array
          getattr(self, split[0])(split)

        except:
          print("Unknown command: '" + split[0] + "'")
          self.send_ctrl_response("500 Syntax error, command unrecognized.")

      if self.finished_running:
        return

  def send_ctrl_response(self, message, encoding="utf-8"):
    print ("Sending CTRL response: " + message)
    self.socket.sendall(bytearray(message + "\r\n", encoding))


  def quit(self, commands):
    self.send_ctrl_response("221 closing control connection")
    self.socket.close()
    print("quitting")

    # Set finished_running so that the main loop will
    # finish running
    self.finished_running = True

  def send_parameter_error_response(self):
    self.send_ctrl_response("501 Syntax error in parameters or arguments.")

  def send_data_thread_status(self, q):
    while not q.empty():
      self.send_ctrl_response(q.get())

  def list(self, commands):
    global data_thread_status

    if len(commands) > 2:
      self.send_parameter_error_response()
      print("LIST error: Too many parameters.")
      return

    # If there is a path given, use this, otherwise default
    # to the current directory
    dir = commands[1] if len(commands) == 2 else self.current_dir

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
      files_in_dir = os.listdir(self.current_dir)
      files_in_dir.sort()
      file_string = ""
      for file in files_in_dir:
        file_string = file_string + file + "\n"

      data_thread_status_q = queue.Queue()
      data_thread = ftp_data_thread(socket=data_socket, cmd="list", data=file_string, q=data_thread_status_q)
      self.send_ctrl_response('150 About to open data connection.')
      data_thread.start()
      data_thread.join()

      self.send_data_thread_status(data_thread_status_q)

    except:
      self.send_ctrl_response('451 Requested action aborted: local error in processing.')

  def retr(self, commands):

    if len(commands) is not 2:
      self.send_parameter_error_response()
      print("RETR error: No filename.")
      return

    filename = commands[1]

    print ("server received retr cmd filename: " + filename)
    filename = os.path.join(self.current_dir, filename)
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

        data_thread_status_q = queue.Queue()

        data_thread = ftp_data_thread(socket=data_socket, cmd="retr", data=file_data, q=data_thread_status_q)
        self.send_ctrl_response('150 About to open data connection.')
        print('start retr thread')
        data_thread.start()
        data_thread.join()

        self.send_data_thread_status(data_thread_status_q)

      except:
        self.send_ctrl_response("450 File Unavailable")
    else:
      self.send_ctrl_response("550 File Unavailable")
      return

  def stor(self, commands):

    if len(commands) is not 2:
      self.send_parameter_error_response()
      print("STOR error: No filename.")
      return

    filename = commands[1]

    filename = os.path.join(self.current_dir, filename)
    print ("abs path: " + filename)

    if os.access(filename, os.R_OK) or not os.path.isfile(filename):
      data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:

        data_thread_status_q = queue.Queue()

        data_thread = ftp_data_thread(socket=data_socket, cmd="stor", data="", filename=filename, q=data_thread_status_q)
        self.send_ctrl_response('150 About to open data connection.')
        print('starting stor thread')
        data_thread.start()
        data_thread.join()

        self.send_data_thread_status(data_thread_status_q)

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