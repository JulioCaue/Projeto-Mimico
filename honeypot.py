import socket
import datetime
import os

class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=2121
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()

    def rodar_honeypot(self):
        while  True:
            if os.path.exists('honeypot.log'):
                lista_de_endereços=[]
                with open ('Honeypot.log','r') as log:
                    for linha in log:
                        lista_de_endereços.append(linha.strip())
            else:
                lista_de_endereços=[]
            
            print('Esperando Conexão...')
            socket_comunicação,endereço=self.servidor.accept()
            usuario_tentado='null'
            senha_tentada='null'
            print(f'conexão estabelecida com endereço {endereço}.')
            socket_comunicação.send('220 welcome'.encode())
            pass

            try:
                while True:
                    recebida=socket_comunicação.recv(1024).decode()
                    if not recebida==False:
                        if recebida!=('quit'):
                            if recebida.startswith('user'):
                                usuario_tentado=recebida
                                socket_comunicação.send('331'.encode())
                            elif recebida.startswith('pass'):
                                senha_tentada=recebida
                                socket_comunicação.send('530'.encode())
                                acessos=f'[{datetime.datetime.now()}]: [{endereço}] - [Usuario tentado: {usuario_tentado}] - [Senha tentada: {senha_tentada}]'
                                lista_de_endereços.append(acessos)
                                if senha_tentada != 'null' and usuario_tentado != 'null':
                                    with open ('Honeypot.log','w') as log:
                                        for endereços in lista_de_endereços:
                                            log.write (f'{endereços}\n')
                            else:
                                socket_comunicação.send('500'.encode())
                            
                        else:
                            socket_comunicação.send('221'.encode())
                            socket_comunicação.close()
                            print (f'conexão encerrada com {endereço}')
                            break
                    else:
                        socket_comunicação.close()
                        print (f'conexão encerrada com {endereço}')
                        break
            except Exception as erro:
                print(f'Um erro ocorreu: {erro}')

servidor=Honeypot()

servidor.rodar_honeypot()