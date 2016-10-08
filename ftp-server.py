import socket
import threading
import sys
import os
import pdb

command_port = 7711
data_port = command_port - 1
ftp_client_default_port = 7712 #we can't use default ports on the same computer, in a real ftp client the default port for the client is the command_port

class ftp_data_thread(threading.Thread):
    def __init__(self, socket, init=False):
        # self.data_socket = socket.socket()
        # self.current_dir = os.path.abspath("./ftp-files/")
        threading.Thread.__init__(self)

    def run(self):
      print ("running data thread")

class ftp_command_thread(threading.Thread):
    def __init__(self, socket):
        self.socket = socket
        self.current_dir = os.path.abspath("./ftp-files/")
        self.data_socket = None
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.socket.send("220 awaiting input")

            #wait for commands
            cmd = str(self.socket.recv(1024), "utf-8")

            if cmd:
                if not cmd.endswith("\r\n"):
                    print ("ERRONEOUS CMD FROM CLIENT")
                    print (cmd)
                    continue
                else:
                    cmd = cmd.rstrip("\r\n")

                split = cmd.lower().split(" ")

                if split[0] == "quit":
                    self.quit()
                elif split[0] == "list":
                    print ("list")
                    # if len(split) == 2:
                    #     self.list(split[1])
                    # else:
                    #     self.list()
                elif split[0] == "retr":
                    print ("retr")
                #   if len(split) == 2:
                #     self.retr(split[1])
                #   else:
                #     #error, must supply filename
                #     print ("retr error no filename")
                elif split[0] == "stor":
                    print ("stor")
                #   if len(split) == 2:
                #     self.stor(split[1])
                #   else:
                #     print ("stor error no filename")
                else:
                    print("Unhandled command: " + split[0])

                print ("cmd: " + cmd)

    def send_ctrl_response(self, message, encoding="utf-8"):
      self.socket.sendall(bytearray(message + "\r\n", encoding))

    def open_data_socket(self):
        if self.data_socket is None:
          self.send_ctrl_response('150 About to open data connection.')
          try:
            self.data_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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
        print ("quitting")

    def list(self):
        # Open data connection
        self.open_data_socket()

        try:
          files_in_dir = os.listdir(self.current_dir)
          files_in_dir.sort()
          file_string = ""
          for file in files_in_dir:
            file_string = file_string + file + "\n"
          self.data_socket.sendall(bytearray(file_string + "\r\n", "utf-8"))
        except:
          self.send_ctrl_response('451 Requested action aborted: local error in processing.')

        self.close_data_socket()

    def retr(self, filename):
      # Open data connection
      self.openDataConn()

      the_file = open(filename, 'rb')
      data = the_file.read(1024)

      while data:
        ## TODO: Send the file part
        ## self.data_sock.send(data)
        data = the_file.read(1024)

      ## Can we send it all at once?
      ## self.data_sock.send(the_file.read())

      the_file.close()
      ## TODO: Close data connection
      self.socket.send('226 Transfer complete.\r\n')

    def stor(self, filename):
        print ("storing file " + filename)


class ftp_server:
    #basic class/socket setup
    def __init__(self):
        #self.port = 7711
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", command_port))

        #listen for 1 client
        self.server_socket.listen(1)

        while True:
            try:
                print ("waiting for connection on " + self.server_socket)
                conn, addr = self.server_socket.accept()

                print ("accepted command connection: " + addr[0] + ":" + str(addr[1]))
                fct = ftp_command_thread(conn)
                fct.start()
            except:
                print ("Unexpected error: ", sys.exc_info()[0])
                self.server_socket.close()
                exit()

if __name__ == '__main__':
  # kick it off
  server = ftp_server()
