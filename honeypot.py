import socket
import datetime 
import threading
import time

#Cria classe honeypot, defininindo os parametros que ela começa.
class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=2121
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()
        self.conexões_ativas=0


    #define como o honeypot roda
    def interagir_com_cliente(self,socket_comunicação,endereço):
        usuario_tentado='null'
        senha_tentada='null'
        #recebe e checa o conteudo da mensagem   
        try:
            while True: 
                senha_tentada='null'
                recebida=socket_comunicação.recv(1024).decode().strip()
                if not recebida:
                    socket_comunicação.close()
                    self.conexões_ativas-=1
                    break
                    
                else: #age de acordo com o conteudo
                    if recebida!=('quit'):
                        #se user for  o primeiro comando do loop, continua normalmente
                        if recebida.startswith('user'):
                            usuario_tentado=recebida.replace('user',' ').strip()
                            socket_comunicação.send('331'.encode())

                        #Se pass for o segundo comando do loop, envia as informações para o log
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

                                #Qualquer outra coisa  fecha o loop interno.
                                else:
                                    socket_comunicação.close()
                                    self.conexões_ativas-=1
                                    print (f'conexão encerrada com {endereço}')
                                    break



                        else:
                            socket_comunicação.send('500'.encode())
                        
                    else:
                        if senha_tentada=='null':
                            acessos=f'[{data_formatada}] {ip_limpo} - USER: {usuario_tentado} - [Sem senha tentada]'
                            with open ('Honeypot.log','a') as log:
                                log.write (f'{acessos}\n')
                                usuario_tentado='null'
                                senha_tentada='null'
                        socket_comunicação.send('221'.encode())
                        socket_comunicação.close()
                        self.conexões_ativas-=1
                        print (f'conexão encerrada com {endereço}')
                        break

        # Mostra o erro  caso ocorra
        except Exception as erro:
            if senha_tentada!='null':
                data_formatada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ip_limpo = endereço[0]
                acessos=f'[{data_formatada}] {ip_limpo} - Usuario cancelou a conexão. - USER: {usuario_tentado} - PASS: {senha_tentada}'
                with open ('Honeypot.log','a') as log:
                    log.write (f'{acessos}\n')
            socket_comunicação.close()
            self.conexões_ativas-=1
            print(f'Um erro ocorreu: {erro}')
            print (f'conexão encerrada com {endereço}')




    def rodar_honeypot(self):
        while True:
            if self.conexões_ativas<=3:
                print('Esperando Conexão...')
                socket_comunicação,endereço=self.servidor.accept()
                print(f'conexão estabelecida com endereço {endereço}.')
                socket_comunicação.send('220 welcome'.encode())
                t=threading.Thread(target=self.interagir_com_cliente,args=(socket_comunicação,endereço),daemon=True)
                t.start()
                self.conexões_ativas+=1
            else:
                socket_comunicação.send("421 Too many users, try again later\r\n".encode())
                print ('Maximo de conexões ativas foi atingido. Esperando liberação...')
                time.sleep(10)


#dá uma variavel ao honeypot
servidor=Honeypot()

#Inicia o sercidor
servidor.rodar_honeypot()