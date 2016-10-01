import socket

class ftp_server:
    #basic class/socket setup
    def __init__(self):
        # self.port = 7710
        self.port = 80
        self.server_socket = socket.socket()
        self.server_socket.bind(("localhost", 80))
        self.server_socket.listen(1)

        #accept our command connection
        conn, addr = self.server_socket.accept()
        print (addr)
        self.loop(conn, addr)


    #establishes connection from a client, need to setup to receive commands and act accordingly
    def loop(self, conn, addr):
        print ("accepted connection with: " + addr[0] + ":" + str(addr[1]))
        while True:
            print ("true")

#kick it off
ftp_server()
