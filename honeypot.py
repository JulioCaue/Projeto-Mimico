import socket
import datetime 
import threading
import Comandos_Filesystem as fs
import criar_banco_de_dados
import gerenciar_banco_de_dados
import random
import time
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---
criar_banco = criar_banco_de_dados
criar_banco.criar_banco()
gerenciador = gerenciar_banco_de_dados.gerenciador_de_banco()

# AQUI ESTÁ A CORREÇÃO DO IP (CHUMBADO PARA FUNCIONAR)
IP_Publico = "163.176.251.249" 

class Honeypot:
    def __init__(self):
        self.__host = '0.0.0.0'
        self.__porta = 21
        self.conexões_ativas = 0
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # --- VACINA DE SOCKET (CORREÇÃO DE REINÍCIO) ---
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.servidor.bind((self.__host, self.__porta))
        self.servidor.listen()
        self.maximo_de_conexões = 10
        self.socket_secundario = None # Inicializa variavel
        self.lock = threading.Lock()
        self.thread_escaneadora = threading.Thread(target=self.escaneador_segundo_plano)
        self.thread_escaneadora.start()
        self.numero_de_conexões = 0
        self.IP_Publico = str(IP_Publico).replace('.', ',')

    def separar_comando(self, comando_recebido, socket_comunicação):
        comando_separado = comando_recebido.split(' ', 1)
        try:
            return comando_separado[1]
        except:
            socket_comunicação.send(b'501 Syntax error.\r\n')
            return ''
        
    def pegar_comando_separado(self, comando_recebido):
        comando_recebido = comando_recebido.split(' ', 1)
        verbo = comando_recebido[0]
        try:
            argumento = comando_recebido[1]
        except:
            argumento = 'sem_argumento'
        return verbo, argumento

    def interagir_com_cliente(self, socket_comunicação, ID_de_usuario):
        pasv_aconteceu = False
        função_lock = self.lock
        socket_secundario = None # Garante escopo local
        
        try:
            comando = fs.Logica_de_arquivos()
            sem_tentativa_usuario = True

            # --- SAUDAÇÃO E LOGIN ---
            socket_comunicação.send(b'220 welcome.\r\n')
            
            # BLINDAGEM CONTRA BOTS (CORREÇÃO UNICODE)
            comando_recebido = socket_comunicação.recv(1024).decode('utf-8', errors='ignore').strip()

            while not comando_recebido.lower().startswith('user'):
                socket_comunicação.send(b'530 Not logged in.\r\n')
                comando_recebido = socket_comunicação.recv(1024).decode('utf-8', errors='ignore').strip()

            socket_comunicação.send(b'331 Password required.\r\n')
            comando_recebido = socket_comunicação.recv(1024).decode('utf-8', errors='ignore').strip()
            
            while not comando_recebido.lower().startswith('pass'):
                socket_comunicação.send(b'530 Not logged in.\r\n')
                # Evita loop infinito se o cliente desconectar
                dados = socket_comunicação.recv(1024)
                if not dados: break
                comando_recebido = dados.decode('utf-8', errors='ignore').strip()

            socket_comunicação.send(b'230 Login successful.\r\n')
            
            horario_do_comando = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
            gerenciador.adicionar_comandos(ID_de_usuario, 'login', 'sucesso', horario_do_comando, função_lock)

            # --- LOOP PRINCIPAL ---
            while True:
                try:
                    dados_raw = socket_comunicação.recv(1024)
                    if not dados_raw:
                        raise ConnectionError("Cliente desconectou")
                    comando_recebido = dados_raw.decode('utf-8', errors='ignore').strip()
                except:
                    break

                horario_do_comando = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')

                # LIST
                if comando_recebido.lower().startswith('list'):
                    resp = comando.list()
                    if pasv_aconteceu and socket_secundario:
                        socket_comunicação.send(b'150 File status okay\r\n')
                        try:
                            # Timeout para não travar se o FileZilla demorar
                            socket_secundario.settimeout(10) 
                            conn_dados, addr = socket_secundario.accept()
                            if resp:
                                conn_dados.send(f'{resp}\r\n'.encode())
                            else:
                                conn_dados.send(b'\r\n')
                            conn_dados.close()
                            socket_comunicação.send(b'226 Transfer complete\r\n')
                        except Exception as e:
                            print(f"Erro no LIST PASV: {e}")
                            socket_comunicação.send(b'425 Can not open data connection.\r\n')
                        
                        socket_secundario.close()
                        pasv_aconteceu = False
                    else:
                        socket_comunicação.send(b'425 Use PASV first.\r\n')
                    
                    gerenciador.adicionar_comandos(ID_de_usuario, 'list', 'folder', horario_do_comando, função_lock)

                # CWD
                elif comando_recebido.lower().startswith('cwd'):
                    verbo, argumento = self.pegar_comando_separado(comando_recebido)
                    gerenciador.adicionar_comandos(ID_de_usuario, verbo, argumento, horario_do_comando, função_lock)
                    diretorio_novo = self.separar_comando(comando_recebido, socket_comunicação)
                    socket_comunicação.send(comando.cd(diretorio_novo))

                # PWD
                elif comando_recebido.lower().startswith('pwd'):
                    gerenciador.adicionar_comandos(ID_de_usuario, 'pwd', '', horario_do_comando, função_lock)
                    socket_comunicação.send(f'257 "{comando.pwd()}" is current directory.\r\n'.encode())

                # MKD
                elif comando_recebido.lower().startswith('mkd'):
                    verbo, argumento = self.pegar_comando_separado(comando_recebido)
                    nova_pasta = self.separar_comando(comando_recebido, socket_comunicação)
                    socket_comunicação.send(comando.mkdir(nova_pasta))
                    gerenciador.adicionar_comandos(ID_de_usuario, verbo, argumento, horario_do_comando, função_lock)

                # PASV (A PARTE CRÍTICA)
                elif comando_recebido.lower() == 'pasv':
                    while True:
                        try:
                            # PORTAS ALTAS (50000+) PARA FIREWALL DA ORACLE
                            porta_secundaria = random.randint(50000, 65535)
                            socket_secundario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            socket_secundario.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            socket_secundario.bind((self.__host, porta_secundaria))
                            socket_secundario.listen(1)
                            break
                        except:
                            continue

                    P1 = porta_secundaria // 256
                    P2 = porta_secundaria % 256
                    
                    # ENVIA O IP PÚBLICO CORRETO
                    socket_comunicação.send(f'227 Entering Passive Mode ({self.IP_Publico},{P1},{P2})\r\n'.encode())
                    pasv_aconteceu = True
                    gerenciador.adicionar_comandos(ID_de_usuario, 'pasv', '', horario_do_comando, função_lock)

                # STOR (UPLOAD)
                elif comando_recebido.lower().startswith('stor'):
                    if pasv_aconteceu and socket_secundario:
                        socket_comunicação.send(b'150 Opening data connection\r\n')
                        try:
                            socket_secundario.settimeout(10)
                            conn_dados, endereco_cliente = socket_secundario.accept()
                            
                            verbo = 'stor'
                            argumento = comando_recebido.split(' ', 1)[1] if len(comando_recebido.split(' ', 1)) > 1 else 'unknown'
                            gerenciador.adicionar_comandos(ID_de_usuario, verbo, argumento, horario_do_comando, função_lock)
                            
                            nome_arquivo = self.separar_comando(comando_recebido, socket_comunicação)
                            
                            # Salva o arquivo
                            socket_comunicação.send(comando.stor(conn_dados, nome_arquivo))
                            conn_dados.close()
                            
                            # Processa Hash e DB
                            tamanho_do_virus = comando.pegar_data_arquivo()
                            hash_do_arquivo = comando.pegar_hash_virus()
                            comando.trocar_nome_perigoso_para_hash(hash_do_arquivo)
                            gerenciador.adicionar_data_arquivo(ID_de_usuario, nome_arquivo, tamanho_do_virus, hash_do_arquivo, função_lock)

                        except Exception as e:
                            print(f"Erro no STOR: {e}")
                        
                        socket_secundario.close()
                        pasv_aconteceu = False
                    else:
                        socket_comunicação.send(b"425 Use PASV first.\r\n")

                # QUIT
                elif comando_recebido.lower().startswith('quit'):
                    socket_comunicação.send(b'221 Goodbye\r\n')
                    break 

                # OUTROS
                elif comando_recebido.lower().startswith('type'):
                    socket_comunicação.send(b'200 Type set to I\r\n')
                elif comando_recebido.lower().startswith('syst'):
                    socket_comunicação.send(b'215 UNIX Type: L8\r\n')
                elif comando_recebido.lower().startswith('feat'):
                    socket_comunicação.send(b'211-Features:\r\n PASV\r\n211 End\r\n')
                else:
                    socket_comunicação.send(b'502 Command not implemented.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'unknown', comando_recebido, horario_do_comando, função_lock)

        except Exception as e:
            print(f"Erro na thread cliente: {e}")
        finally:
            timestamp_final = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
            try:
                socket_comunicação.close()
            except: pass
            if socket_secundario:
                try: socket_secundario.close()
                except: pass
            gerenciador.finalizar_sessão(timestamp_final, ID_de_usuario, função_lock)
            self.numero_de_conexões -= 1
            print(f'Desconexão. ({self.numero_de_conexões}/{self.maximo_de_conexões})')

    def ligar_servidor(self):
        função_lock = self.lock
        print(f"--- SERVIDOR RODANDO NO IP {IP_Publico} ---")
        while True:
            try:
                socket_comunicação, endereço = self.servidor.accept()
                self.numero_de_conexões += 1
                IP_invasor, porta_invasor = endereço
                print(f'Nova Conexão: {IP_invasor}')
                
                horario_da_conexão = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                ID_de_usuario = gerenciador.adicionar_nova_conexão(IP_invasor, porta_invasor, horario_da_conexão, função_lock)
                
                threading.Thread(target=self.interagir_com_cliente, args=(socket_comunicação, ID_de_usuario), daemon=True).start()
                
                if ID_de_usuario:
                    threading.Thread(target=gerenciador.pesquisar_local_do_ip, args=(ID_de_usuario, função_lock), daemon=True).start()
            except Exception as e:
                print(f"Erro no loop principal: {e}")

    def escaneador_segundo_plano(self):
        função_lock = self.lock
        print("--- Scanner de Malware Iniciado (Segundo Plano) ---")
        while True:
            try:
                # Busca se tem alguem com status 'pendente' no banco
                resultado = gerenciador.pegar_hash_arquivo_pendente(função_lock)
                if resultado:
                    ID_de_usuario, hash_do_arquivo = resultado
                    print(f"[*] Arquivo pendente encontrado! Hash: {hash_do_arquivo}")
                    gerenciador.escanear_arquivo(hash_do_arquivo, ID_de_usuario, função_lock)
                else:
                    # Se nao tem nada, dorme por 10 segundos
                    time.sleep(10)
            except Exception as e:
                print(f"Erro na thread do scanner: {e}")
                time.sleep(10)

if __name__ == "__main__":
    servidor = Honeypot()
    servidor.ligar_servidor()