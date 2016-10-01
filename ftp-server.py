import socket

class ftp_server:
    #basic class/socket setup
    def __init__(self):
        # self.port = 7710
        self.port = 7710
        self.server_socket = socket.socket()
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen(1)

        self.get_connection()

    def get_connection(self):
        conn, addr = self.server_socket.accept()
        self.loop(conn, addr)

    #establishes connection from a client, need to setup to receive commands and act accordingly
    def loop(self, conn, addr):
        print ("accepted connection with: " + addr[0] + ":" + str(addr[1]))
        while True:
            cmd = conn.recv(256)
            if cmd:
                if not cmd.endswith("\r\n"):
                    print ("ERRORONIOUS CMD FROM CLIENT")
                    continue
                else:
                    cmd = cmd.rstrip("\r\n")

                print (len(cmd))
                split = cmd.lower().split(" ")
                if split[0] == "quit":
                    #disconnect socket and discard thread
                else:
                    print("Unhandled command: " + split[0])
                print (split)
                print ("cmd: " + cmd)

#kick it off
ftp_server()
