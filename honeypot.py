import socket
import datetime 
import threading
import Comandos_Filesystem as fs

class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=2121
        self.conexões_ativas=0
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()
        self.maximo_de_conexões=10

    def separar_comando(self,comando_recebido,socket_comunicação):
        comando_separado=comando_recebido.split(' ',1)
        if len(comando_separado)>1:
            comando_recebido=comando_separado[1]
            return comando_recebido
        else:
            socket_comunicação.send(b'501 Syntax error in parameters or arguments.\r\n')
            return ''

    def interagir_com_cliente(self,socket_comunicação,endereço):
        #Cria variavel comando para usar comandos e envia mensagem inivial ao invasor.
        comando=fs.Logica_de_arquivos()
        socket_comunicação.send(b'220 welcome\r\n')
        comando_recebido=socket_comunicação.recv(1024).decode()

        #sistema basico de login para enganar
        if comando_recebido.startswith('user'):
            socket_comunicação.send(b'331 Please specify the password.\r\n')
        else: socket_comunicação.send(b'530 Not logged in.\r\n')
        comando_recebido=socket_comunicação.recv(1024).decode()
        if comando_recebido.startswith('pass'):
            socket_comunicação.send(b'230 Login successful.')
        else: socket_comunicação.send(b'530 Not logged in.\r\n')


        while True:
            comando_recebido=socket_comunicação.recv(1024).decode().lower()

            if comando_recebido.startswith('list'):
                socket_comunicação.send(f'{comando.list()}'.encode())

            elif comando_recebido.startswith('cd'):
                diretorio_novo=self.separar_comando(comando_recebido,socket_comunicação)
                socket_comunicação.send(comando.cd(diretorio_novo,socket_comunicação))

            elif comando_recebido.startswith('pwd'):
                socket_comunicação.send(f'{comando.pwd()}'.encode())

            elif comando_recebido.startswith('retr'):
                arquivo_requisitado=self.separar_comando(comando_recebido,socket_comunicação)
                conteudo = comando.retr(arquivo_requisitado)
                if isinstance (conteudo,str):
                    socket_comunicação.send(conteudo.encode())
                else:
                    socket_comunicação.send(conteudo)
            
            elif comando_recebido.startswith('mkdir'):
                nova_pasta=self.separar_comando(comando_recebido,socket_comunicação)
                comando.mkdir(nova_pasta)
            
            elif comando_recebido.startswith('stor'):
                comando.stor(socket_comunicação,comando_recebido)

            elif comando_recebido=='quit':
                socket_comunicação.send(b'221 Goodbye')
                socket_comunicação.close()

            else:
                socket_comunicação.send(b'502 Command not implemented.\r\n')


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