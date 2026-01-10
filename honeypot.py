import socket
import datetime 
import threading
import Comandos_Filesystem as fs
import criar_banco_de_dados
import gerenciar_banco_de_dados
import random
import time


#cria o banco de dados caso não exista
criar_banco=criar_banco_de_dados
criar_banco.criar_banco()
gerenciador=gerenciar_banco_de_dados.gerenciador_de_banco()


#Cria a classe honeypot
class Honeypot:
    def __init__(self):
        self.__host='localhost'
        self.__porta=21
        self.conexões_ativas=0
        self.servidor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servidor.bind((self.__host,self.__porta))
        self.servidor.listen()
        self.maximo_de_conexões=10
        self.pasv_aconteceu=False
        socket_secundario=None
        self.lock=threading.Lock()

    #Separa o comando e retorna oque restar no index 1 
    #Caso de fato existam mais de duas palavras presentes.
    def separar_comando(self,comando_recebido,socket_comunicação):
        comando_separado=comando_recebido.split(' ',1)
        if len(comando_separado)>1:
            comando_recebido=comando_separado[1]
            return comando_recebido
        else:
            socket_comunicação.send(b'501 Syntax error in parameters or arguments.\r\n')
            return ''
        
    #Retorna o index 0 e 1 como verbo e argumento, em ordem. Sempre usar antes de separar comando.
    def pegar_comando_separado(self,comando_recebido):
        comando_recebido=comando_recebido.split(' ',1)
        verbo=comando_recebido[0]
        try:
            argumento=comando_recebido[1]
        except:
            argumento='sem_argumento'
        return verbo,argumento

    
    #Função que interage com cliente.
    def interagir_com_cliente(self,socket_comunicação,ID_de_usuario):
        try:
            comando=fs.Logica_de_arquivos()
            sem_tentativa_usuario=True


            #Sistema false de "login". Simples de proposito, mas deve ter alguma maneira de melhorar.

            #Envia saudação inicial
            socket_comunicação.send(b'220 welcome.\r\n')
            comando_recebido=socket_comunicação.recv(1024).decode().strip()

            #Faz login do usuario enviado (não é salvo no banco de dados)
            while comando_recebido.lower().startswith('user')==False:
                if sem_tentativa_usuario==True:
                    socket_comunicação.send(b'530 Not logged in.\r\n')
                    comando_recebido=socket_comunicação.recv(1024).decode().strip()
                    sem_tentativa_usuario=False
                else:
                    socket_comunicação.send(b'530 Not logged in.\r\n')
                    comando_recebido=socket_comunicação.recv(1024).decode().strip()

            #Pega a senha recebida e coloca no banco de dados.
            socket_comunicação.send(b'331 Please specify the password.\r\n')
            comando_recebido=socket_comunicação.recv(1024).decode().strip()
            while comando_recebido.lower().startswith('pass')==False:
                socket_comunicação.send(b'530 Not logged in.\r\n')
            socket_comunicação.send(b'230 Login successful.\r\n')
            horario_do_comando=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
            verbo='senha'
            if len(comando_recebido.split(' ',1))>1:
                argumento=str(comando_recebido.split(' ')[1])
            else:
                argumento=str(comando_recebido)
            self.lock.acquire()
            gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
            self.lock.release()


            #inicio do loop principal de interação
            while True:
                #Quebra a conexão caso os dados venham vazios. Também informa erros caso haja algum.
                try:
                    dados_raw = socket_comunicação.recv(1024)
                    if not dados_raw:
                        timestamp_final=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                        socket_comunicação.close()
                        self.lock.acquire()
                        gerenciador.finalizar_sessão(timestamp_final,ID_de_usuario)
                        self.lock.release() 
                        break
                    comando_recebido = dados_raw.decode('utf-8',errors='ignore').strip()
                except Exception as e:
                    print (f'Erro na conexão: {e}')
                    break

                #Salva horario que o comando foi enviado
                horario_do_comando=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')

                #Logica de listagem das pastas falsas. Requer pasv primeiro.
                if comando_recebido.lower().startswith('list'):
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
                        verbo='list'
                        argumento='sem_argumento'
                        self.lock.acquire()
                        gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                        self.lock.release()


                    else:
                        socket_comunicação.send(b'425 Use PASV first.\r\n')

                #Muda o diretorio no filesystem falso.
                elif comando_recebido.lower().startswith('cwd'):
                    verbo,argumento=self.pegar_comando_separado(comando_recebido)
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()
                    diretorio_novo=self.separar_comando(comando_recebido,socket_comunicação)
                    socket_comunicação.send(comando.cd(diretorio_novo))

                #Mostra diretorio atual no filesystem falso.
                elif comando_recebido.lower().startswith('pwd'):
                    verbo='pwd'
                    argumento='sem_argumento'
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()
                    socket_comunicação.send(f'257 "{comando.pwd()}" is current directory.\r\n'.encode())

                #Envia arquivo requisitado para o invasor
                elif comando_recebido.lower().startswith('retr'):
                    verbo,argumento=self.pegar_comando_separado(comando_recebido)
                    arquivo_requisitado=self.separar_comando(comando_recebido,socket_comunicação)
                    conteudo_do_arquivo,estado_do_arquivo = comando.retr(arquivo_requisitado)
                    if estado_do_arquivo==True:
                        socket_comunicação.send(b'150 File status okay\r\n')
                        conn_dados, addr = socket_secundario.accept()
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
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()
                    

                #cria pasta nova no filesystem
                elif comando_recebido.lower().startswith('mkd'):
                    verbo,argumento=self.pegar_comando_separado(comando_recebido)
                    nova_pasta=self.separar_comando(comando_recebido,socket_comunicação)
                    socket_comunicação.send(comando.mkdir(nova_pasta))
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()
                

                #Baixa arquivo do invasor para o filesystem (precisa implementar interação com banco!!)
                elif comando_recebido.lower().startswith('stor'):
                    if self.pasv_aconteceu:
                        socket_comunicação.send(b'150 Opening data connection\r\n')
                        conn_dados, endereco_cliente=socket_secundario.accept()
                    verbo='stor'
                    if len(comando_recebido.split(' ',1))>1:
                        argumento=comando_recebido.split(' ',1)[1]
                    else:argumento='sem_argumento'
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    comando_recebido=self.separar_comando(comando_recebido,socket_comunicação)
                    nome_virus_recebido=comando_recebido
                    socket_comunicação.send(comando.stor(conn_dados,comando_recebido))
                    conn_dados.close()
                    socket_secundario.close()
                    self.pasv_aconteceu=False
                    tamanho_do_virus=comando.pegar_data_arquivo(nome_virus_recebido)
                    hash_do_virus=comando.pegar_hash_virus(nome_virus_recebido)
                    self.lock.acquire()
                    gerenciador.adicionar_data_arquivo(ID_de_usuario,nome_virus_recebido,tamanho_do_virus,hash_do_virus)
                    self.lock.release()

                #Finaliza conexão formalmente, e loga data de finalização.
                elif comando_recebido.lower().startswith('quit'):
                    timestamp_final=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                    try:
                        socket_comunicação.send(b'221 Goodbye\r\n')
                    except ConnectionError:
                        print ('conexão cortada pelo cliente.')
                        socket_comunicação.close()
                    
                    timestamp_final=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                    self.lock.acquire()
                    gerenciador.finalizar_sessão(timestamp_final,ID_de_usuario)
                    self.lock.release()
                    break # Sai do loop

                #logica do comando help
                elif comando_recebido.lower().startswith('help'):
                    if len(comando_recebido.split())>=2:
                        socket_comunicação.send(b'504 Command not implemented for that parameter.')
                    else:
                        socket_comunicação.send(comando.help())
                        verbo=comando_recebido
                        argumento='sem_argumento'
                        self.lock.acquire()
                        gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                        self.lock.release()
                
                
                #Logica do comando syst
                elif comando_recebido.lower().startswith('syst'):
                    socket_comunicação.send(comando.syst())
                    verbo=comando_recebido
                    argumento='sem_argumento'
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()

                #Logica do comando type
                elif comando_recebido.lower().startswith('type'):
                    verbo,argumento=self.pegar_comando_separado(comando_recebido)
                    comando_recebido=self.separar_comando(comando_recebido,socket_comunicação)
                    socket_comunicação.send(comando.type(comando_recebido).encode())
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()

                #Logica do comando pasv
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
                    verbo='pasv'
                    argumento='sem_argumento'
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()


                #Logica para qualquer outro comando não implementado
                else:
                    socket_comunicação.send(b'502 Command not implemented.\r\n')
                    if len(comando_recebido.split(' ',1))<2>=3:
                        if len(comando_recebido.split(' ',1))<2:
                            verbo=comando_recebido
                            argumento="sem_argumento"
                        else:
                            verbo=comando_recebido.split(' ',1)[0]
                            argumento=comando_recebido.split(' ',1)[1]
                    else:
                        verbo,argumento=self.pegar_comando_separado(comando_recebido)
                    self.lock.acquire()
                    gerenciador.adicionar_comandos(ID_de_usuario,verbo,argumento,horario_do_comando)
                    self.lock.release()

                
                
        #Gerencia problema de conexão       
        except ConnectionError:
            timestamp_final=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
            socket_comunicação.close()
            self.lock.acquire()
            gerenciador.finalizar_sessão(timestamp_final,ID_de_usuario)
            self.lock.release()

    #Aceita as conexões de acordo com numero de threads
    def ligar_servidor(self):
        print('Esperando Conexão...')
        numero_de_conexões=0
        maximo_de_conexões=10
        while True:
            numero_de_conexões+=1
            socket_comunicação,endereço=self.servidor.accept()
            if numero_de_conexões>maximo_de_conexões:
                socket_comunicação.close()
            else:
                IP_invasor,porta_invasor=endereço
                print (f'Conexão estabelecida com endereço {IP_invasor}')
                horario_da_conexão=datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                ID_de_usuario=gerenciador.adicionar_nova_conexão(IP_invasor,porta_invasor,horario_da_conexão)
                #pega o ID e adiciona no banco de dados
                #print aqui funciona!!!! ou pelo menos é pra funcionar.
                t=threading.Thread(target=self.interagir_com_cliente,args=(socket_comunicação,ID_de_usuario),daemon=True)
                t.start()
                gerenciador.pesquisar_local_do_ip(ID_de_usuario)


#Liga o servidor.
servidor=Honeypot()
servidor_desligado=True

while True:
    if servidor_desligado:
        t=threading.Thread(target=servidor.ligar_servidor())
        t.start()
        servidor_desligado=False

    resultado=gerenciador.pegar_hash_arquivo_pendente()
    if resultado:
        ID_de_usuario,hash_do_arquivo=resultado
        gerenciador.escanear_arquivo(hash_do_arquivo,ID_de_usuario)
    time.sleep(21)