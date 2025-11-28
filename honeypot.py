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
            
            print('Esperando Conexão...')
            socket_comunicação,endereço=self.servidor.accept()
            usuario_tentado='null'
            senha_tentada='null'
            print(f'conexão estabelecida com endereço {endereço}.')
            socket_comunicação.send('220 welcome'.encode())
            pass

            try:
                while True:
                    recebida=socket_comunicação.recv(1024).decode().strip()
                    if not recebida:
                        socket_comunicação.close()
                        break
                        
                    else:
                        if recebida!=('quit'):
                            if recebida.startswith('user'):
                                usuario_tentado=recebida.replace('user',' ').strip()
                                socket_comunicação.send('331'.encode())
                            elif recebida.startswith('pass'):
                                senha_tentada=recebida.replace('pass',' ').strip()
                                socket_comunicação.send('530'.encode())
                                data_formatada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                ip_limpo = endereço[0]
                                acessos=f'[{data_formatada}] {ip_limpo} - [USER: {usuario_tentado}] - [PASS: {senha_tentada}]'
                                if senha_tentada != 'null' and usuario_tentado != 'null':
                                    with open ('Honeypot.log','a') as log:
                                        log.write (f'{acessos}\n')
                            else:
                                socket_comunicação.send('500'.encode())
                            
                        else:
                            socket_comunicação.send('221'.encode())
                            socket_comunicação.close()
                            print (f'conexão encerrada com {endereço}')
                            break
            except Exception as erro:
                print(f'Um erro ocorreu: {erro}')

servidor=Honeypot()

servidor.rodar_honeypot()