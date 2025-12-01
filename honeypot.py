import socket
import datetime 
import threading
import time

class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=2121
        self.conexões_ativas=0
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()

    def interagir_com_cliente(self,socket_comunicação,endereço):
        usuario_tentado='null'
        senha_tentada='null'
        socket_comunicação.send('220 welcome'.encode())   
        try:
            while True: 
                senha_tentada='null'
                recebida=socket_comunicação.recv(1024).decode().strip()
                if not recebida:
                    self.conexões_ativas-=1
                    socket_comunicação.close()
                    break
                else:
                    if recebida!=('quit'):
                        if recebida.startswith('user'):
                            usuario_tentado=recebida.replace('user',' ').strip()
                            socket_comunicação.send('331'.encode())
                        elif recebida.startswith('pass'):
                            if usuario_tentado=='null':
                                socket_comunicação.send('500'.encode())
                            else:
                                senha_tentada=recebida.replace('pass',' ').strip()
                                socket_comunicação.send('530'.encode())
                                data_formatada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                ip_limpo = endereço[0]
                                if usuario_tentado != 'null' and senha_tentada != 'null':
                                    acessos=f'[{data_formatada}] {ip_limpo} - USER: {usuario_tentado} - PASS: {senha_tentada}'
                                    with open ('Honeypot.log','a') as log:
                                        log.write (f'{acessos}\n')
                                        usuario_tentado='null'
                                        senha_tentada='null'
                                else:
                                    self.conexões_ativas-=1
                                    socket_comunicação.close()
                                    print (f'conexão encerrada com {endereço}')
                                    break
                        else:
                            socket_comunicação.send('500'.encode())
                    else:
                        socket_comunicação.send('221'.encode())
                        self.conexões_ativas-=1
                        socket_comunicação.close()
                        print (f'conexão encerrada com {endereço}')
                        break
        except Exception as erro:
            if senha_tentada!='null':
                data_formatada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ip_limpo = endereço[0]
                acessos=f'[{data_formatada}] {ip_limpo} - Usuario cancelou a conexão. - USER: {usuario_tentado} - PASS: {senha_tentada}'
                with open ('Honeypot.log','a') as log:
                    log.write (f'{acessos}\n')
            self.conexões_ativas-=1
            socket_comunicação.close()
            print(f'Um erro ocorreu: {erro}')
            print (f'conexão encerrada com {endereço}')

    def rodar_honeypot(self):
        while True:
            print('Esperando Conexão...')
            socket_comunicação,endereço=self.servidor.accept()
            if self.conexões_ativas<3:        
                self.conexões_ativas+=1
                print(f'conexão estabelecida com endereço {endereço}. {self.conexões_ativas} de 3 estão ativas.')
                t=threading.Thread(target=self.interagir_com_cliente,args=(socket_comunicação,endereço),daemon=True)
                t.start()
            else:
                socket_comunicação.send("421 Too many users, try again later\r\n".encode())
                socket_comunicação.close()
                print ('Maximo de conexões ativas foi atingido. Esperando liberação...')

servidor=Honeypot()
servidor.rodar_honeypot()