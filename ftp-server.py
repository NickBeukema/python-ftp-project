import socket
import threading
import sys
import os

class ftp_command_thread(threading.Thread):
    def __init__(self, socket):
        self.socket = socket
        self.current_dir = os.path.abspath('.')

        threading.Thread.__init__(self)

    def run(self):
        while True:
            cmd = str(self.socket.recv(256), "utf-8")
            if cmd:
                if not cmd.endswith("\r\n"):
                    print ("ERRONEOUS CMD FROM CLIENT")
                    print (cmd)
                    continue
                else:
                    cmd = cmd.rstrip("\r\n")

                split = cmd.lower().split(" ")
                if split[0] == "quit":
                    #disconnect socket and discard thread
                    print ("quitting")
                else:
                    print("Unhandled command: " + split[0])
                print (split)
                print ("cmd: " + cmd)

    def list():
      ## TODO: Start data connection
      files_in_dir = os.listdir(self.current_dir).sort()

      file_string = "\n".join(files_in_dir)

      ## TODO: Send file list
      ## TODO: Close data connection

    def retr(filename):
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


class ftp_server:
    #basic class/socket setup
    def __init__(self):
        self.port = 7711
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen(1)

        while True:
            try:
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
