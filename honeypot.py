import socket
import datetime 
import threading
import Comandos_Filesystem as fs
import criar_banco_de_dados
import gerenciar_banco_de_dados
import random

criar_banco=criar_banco_de_dados
criar_banco.criar_banco()

class Honeypot:
    def __init__(self):
        self.__host='127.0.0.1'
        self.__porta=21
        self.conexões_ativas=0
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()
        self.maximo_de_conexões=10
        self.pasv_aconteceu=False
        socket_secundario=None

    def separar_comando(self,comando_recebido,socket_comunicação):
        comando_separado=comando_recebido.split(' ',1)
        if len(comando_separado)>1:
            comando_recebido=comando_separado[1]
            comando_recebido=comando_recebido.strip()
            return comando_recebido
        else:
            socket_comunicação.send(b'501 Syntax error in parameters or arguments.\r\n')
            return ''

    def interagir_com_cliente(self,socket_comunicação,endereço):
        #Cria variavel comando para usar comandos e envia mensagem inivial ao invasor.
        comando=fs.Logica_de_arquivos()
        socket_comunicação.send(b'220 welcome\r\n')
        # Adicionado tamanho do buffer
        comando_recebido=socket_comunicação.recv(1024).decode()
        user=False

        #sistema basico de login para enganar
        while True:
            if comando_recebido.startswith ('USER') and user!=True:
                socket_comunicação.send(b'331 Please specify the password.\r\n')
                user=True
            else: socket_comunicação.send(b'530 Not logged in.\r\n')
            # Adicionado tamanho do buffer
            comando_recebido=socket_comunicação.recv(1024).decode()
            if comando_recebido.startswith ('PASS') and user==True:
                socket_comunicação.send(b'230 Login successful.\r\n')
                break
            else: 
                socket_comunicação.send(b'530 Not logged in.\r\n')
                user=False


        while True:
            try:
                dados_raw = socket_comunicação.recv(1024)
                if not dados_raw: break # Se cliente desconectar, encerra loop
                comando_recebido = dados_raw.decode('utf-8',errors='ignore').strip()
            except Exception as e:
                print (f'Erro na conexão: {e}')
                break

            if comando_recebido.startswith('LIST'):
                resp = comando.list()
                if self.pasv_aconteceu:
                    if resp:
                        socket_comunicação.send(b'150 File status okay\r\n')
                        conn_dados, addr = socket_secundario.accept()
                        conn_dados.send(f'{resp}\r\n'.encode())
                    else:
                        conn_dados.send(b' \r\n') # Envia vazio se nada listar

                    socket_comunicação.send(b'226 Closing data connection\r\n')
                    conn_dados.close()
                    socket_secundario.close()
                    self.pasv_aconteceu=False


                else:
                    socket_comunicação.send(b'425 Use PASV first.\r\n')

            elif comando_recebido.lower().startswith('cwd'):
                diretorio_novo=self.separar_comando(comando_recebido,socket_comunicação)
                socket_comunicação.send(comando.cd(diretorio_novo))

            elif comando_recebido.lower().startswith('pwd'):
                socket_comunicação.send(f'257 "{comando.pwd()}" is current directory.\r\n'.encode())

            elif comando_recebido.lower().startswith('retr'):
                arquivo_requisitado=self.separar_comando(comando_recebido,socket_comunicação)
                conteudo_do_arquivo,estado_do_arquivo = comando.retr(arquivo_requisitado)
                if estado_do_arquivo==True:
                    socket_comunicação.send(b'150 File status okay\r\n')
                    conn_dados, addr = socket_secundario.accept()
                    #todo: encode ou não dependendo se for strings.
                    if isinstance(conteudo_do_arquivo,str):
                        conn_dados.sendall(conteudo_do_arquivo.encode())
                    elif isinstance(conteudo_do_arquivo,bytes):
                        conn_dados.sendall(conteudo_do_arquivo)
                    socket_comunicação.send(b'226 Closing data connection\r\n')
                    conn_dados.close()
                    socket_secundario.close()
                    self.pasv_aconteceu=False
                else:
                    socket_comunicação.send(b'550 File not found.\r\n')
                

            
            elif comando_recebido.lower().startswith('mkd'):
                nova_pasta=self.separar_comando(comando_recebido,socket_comunicação)
                socket_comunicação.send(comando.mkdir(nova_pasta)) # Adicionado send que faltava
            
            elif comando_recebido.lower().startswith('stor'):
                if self.pasv_aconteceu:
                    socket_comunicação.send(b'150 Opening data connection\r\n')
                    conn_dados, endereco_cliente=socket_secundario.accept()
                comando_recebido=self.separar_comando(comando_recebido,socket_comunicação)
                socket_comunicação.send(comando.stor(conn_dados,comando_recebido))
                conn_dados.close()
                socket_secundario.close()
                self.pasv_aconteceu=False

            elif comando_recebido.lower()=='quit':
                try:
                    socket_comunicação.send(b'221 Goodbye\r\n')
                except ConnectionError:
                    print ('conexão cortada pelo cliente.')
                    socket_comunicação.close()
                    break # Sai do loop


            elif comando_recebido.lower()=='help':
                socket_comunicação.send(comando.help())
            

            elif comando_recebido.lower()=='syst':
                socket_comunicação.send(comando.syst())

            elif comando_recebido.lower().startswith('type'):
                comando_recebido=self.separar_comando(comando_recebido,socket_comunicação)
                socket_comunicação.send(comando.type(comando_recebido).encode())

            elif comando_recebido.lower()==('pasv'):
                porta_secundaria=random.randint(49152,65535)
                P1=porta_secundaria//256
                P2=porta_secundaria%256
                porta_secundaria=((P1*256)+P2)

                socket_secundario=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                socket_secundario.bind((self.__host,porta_secundaria))
                socket_secundario.listen()
                socket_comunicação.send(f'227 Entering Passive Mode (127,0,0,1,{P1},{P2})\r\n'.encode())
                self.pasv_aconteceu=True

            else:
                socket_comunicação.send(b'502 Command not implemented.\r\n')

            print (comando_recebido)


    def gerenciar_conexões(self):
        lista_de_conexões=[]
        print('Esperando Conexão...')
        while True:
            socket_comunicação,endereço=self.servidor.accept()
            self.conexões_ativas+=1
            if self.conexões_ativas<=self.maximo_de_conexões:        
                lista_de_conexões.append(self.conexões_ativas)
                if len(lista_de_conexões)==10 or self.conexões_ativas==self.maximo_de_conexões:
                    print(f'conexão estabelecida com endereço {endereço}. {self.conexões_ativas} de {self.maximo_de_conexões} estão ativas.')
                    lista_de_conexões=[]
                t=threading.Thread(target=self.interagir_com_cliente,args=(socket_comunicação,endereço),daemon=True)
                t.start()
            else:
                socket_comunicação.send("421 Too many users, try again later\r\n".encode())
                socket_comunicação.close()
                print ('Maximo de conexões ativas foi atingido. Esperando liberação...')

servidor=Honeypot()
servidor.gerenciar_conexões()