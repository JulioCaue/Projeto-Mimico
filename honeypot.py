import socket
import datetime 

#Cria classe honeypot, defininindo os parametros que ela começa.
class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=2121
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()
    #define como o honeypot roda
    def rodar_honeypot(self):
        #cria o loop externo
        while  True:
            #espera conexão até alguém se conectar
            print('Esperando Conexão...')
            socket_comunicação,endereço=self.servidor.accept()
            usuario_tentado=False
            senha_tentada=False
            print(f'conexão estabelecida com endereço {endereço}.')
            socket_comunicação.send('220 welcome'.encode())
            pass

            try:
                while True: #recebe e checa o conteudo da mensagem
                    recebida=socket_comunicação.recv(1024).decode().strip()
                    if not recebida:
                        socket_comunicação.close()
                        break
                        
                    else: #age de acordo com o conteudo
                        if recebida!=('quit'):


                            #se user for  o primeiro comando do loop, continua normalmente
                            if recebida.startswith('user'):
                                usuario_tentado=recebida.replace('user',' ').strip()
                                socket_comunicação.send('331'.encode())

                                #Se pass for o segundo comando do loop, envia as informações para o log
                                if recebida.startswith('pass'):
                                    senha_tentada=recebida.replace('pass',' ').strip()
                                    socket_comunicação.send('530'.encode())
                                    data_formatada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    ip_limpo = endereço[0]
                                    if usuario_tentado != False and usuario_tentado != False:
                                        acessos=f'[{data_formatada}] {ip_limpo} - USER: {usuario_tentado}] - PASS: {senha_tentada}'
                                        with open ('Honeypot.log','a') as log:
                                            log.write (f'{acessos}\n')

                                    #Se por algum motivo não houver senha, ele envia  apenas o usuario tentado.
                                    elif senha_tentada is False:
                                        acessos=f'[{data_formatada}] {ip_limpo} - USER: {usuario_tentado} - [Sem senha tentada]'
                                        with open ('Honeypot.log','a') as log:
                                            log.write (f'{acessos}\n')
                                        socket_comunicação.close()
                                        print (f'conexão encerrada com {endereço}')
                                        break

                                    #Qualquer outra coisa  fecha o loop interno.
                                    else:
                                        socket_comunicação.close()
                                        print (f'conexão encerrada com {endereço}')
                                        break

                                #Se user não for o primeiro comando do loop, da erro e volta o loop.
                                else:
                                    socket_comunicação.send('500'.encode())

                            #se pass for o primeiro comando do loop, da erro e reseta.
                            elif recebida.startswith('pass'):
                                socket_comunicação.send('530'.encode())

                        
                            else:
                                socket_comunicação.send('500'.encode())
                            
                        else:
                            socket_comunicação.send('221'.encode())
                            socket_comunicação.close()
                            print (f'conexão encerrada com {endereço}')
                            break

            # Mostra o erro  caso ocorra
            except Exception as erro:
                #lida com erro caso usuario desconecte.
                if erro==('Um erro ocorreu: [WinError 10054] Foi forçado o cancelamento de uma conexão existente pelo host remoto'):
                    acessos=f'[{data_formatada}] {ip_limpo} - Usuario cancelou a conexão. - USER: {usuario_tentado} - PASS: {senha_tentada}'
                    with open ('Honeypot.log','a') as log:
                        log.write (f'{acessos}\n')
                    socket_comunicação.close()
                    print (f'conexão encerrada com {endereço}')
                    break
                else:
                    print(f'Um erro ocorreu: {erro}')

#dá uma variavel ao honeypot
servidor=Honeypot()

#Inicia o sercidor
servidor.rodar_honeypot()