import socket

class invasor:
    def __init__(self):
        self.host='localhost'
        self.porta=2121
        self.cliente=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def invadir(self):
        self.cliente.connect((self.host,self.porta))