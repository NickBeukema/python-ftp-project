import socket

class ftp_server:
    #basic class/socket setup
    def __init__(self):
        # self.port = 7710
        self.port = 80
        self.server_socket = socket.socket()
        self.server_socket.bind(("localhost", 80))
        self.server_socket.listen(5)
        self.loop()

    #establishes connection from a client, need to setup to receive commands and act accordingly
    def loop(self):
        while 1:
            self.server_socket.accept()
            print "accepted"

#kick it off
ftp_server()
