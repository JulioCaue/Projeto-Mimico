import socket

class Invasor:
    def __init__(self):
        self.host='localhost'
        self.porta=2121
        self.cliente=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def invadir(self):
        self.cliente.connect((self.host,self.porta))
        while True:
            self.cliente.send(input().encode())
            mensagem_recebida=self.cliente.recv(1024).decode()
            print(mensagem_recebida)
            if mensagem_recebida=='221':
                break




programa_invadir=Invasor()

programa_invadir.invadir()