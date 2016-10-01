import socket

class ftp_server:
    #basic class/socket setup
    def __init__(self):
        self.port = 7711
        # self.port = 80
        self.server_socket = socket.socket()
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen(1)

        #accept our command connection
        conn, addr = self.server_socket.accept()
        print (addr)
        self.loop(conn, addr)


    #establishes connection from a client, need to setup to receive commands and act accordingly
    def loop(self, conn, addr):
        print ("accepted connection with: " + addr[0] + ":" + str(addr[1]))
        while True:
            cmd = conn.recv(256)
            if cmd:
              print('Recieved:', cmd)

if __name__=='__main__':
  # kick it off
  ftp_server()
