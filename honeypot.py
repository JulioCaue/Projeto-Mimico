import socket
import datetime 
import threading
import Comandos_Filesystem as fs
import criar_banco_de_dados
import gerenciar_banco_de_dados
import random
import time
import os
import requests
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
criar_banco_de_dados.criar_banco()
# CORREÇÃO: Uso da nova classe renomeada
gerenciador = gerenciar_banco_de_dados.GerenciadorBanco()

# Detecção de IP (Com fallback para depuração local)
def get_public_ip():
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
        print(f"[*] IP Público detectado: {ip}")
        return ip
    except:
        print("[!] Falha ao detectar IP Público. Usando 127.0.0.1 (Modo Local)")
        return '127.0.0.1'

IP_Publico = get_public_ip()

class Honeypot:
    def __init__(self):
        self.__host = '0.0.0.0'
        self.__porta = 21
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor.bind((self.__host, self.__porta))
        self.servidor.listen()
        
        self.maximo_de_conexões = 10
        self.conexões_ativas = 0
        self.lock = threading.Lock()
        
        self.thread_escaneadora = threading.Thread(target=self.escaneador_segundo_plano, daemon=True)
        self.thread_escaneadora.start()
        
        self.IP_Formatado = IP_Publico.replace('.', ',')

    def separar_comando(self, comando_recebido, socket_comunicação):
        try: return comando_recebido.split(' ', 1)[1]
        except: return ''
        
    def interagir_com_cliente(self, socket_comunicação, ID_de_usuario, IP_invasor):
        pasv_aconteceu = False
        socket_secundario = None
        função_lock = self.lock
        
        socket_comunicação.settimeout(60)
        
        try:
            # CORREÇÃO: Uso da nova classe renomeada
            comando = fs.LogicaArquivos()
            socket_comunicação.send(b'220 Welcome to FTP service.\r\n')
            
            while True:
                try:
                    dados = socket_comunicação.recv(1024)
                    if not dados: break
                    comando_recebido = dados.decode('utf-8', errors='ignore').strip()
                    if not comando_recebido: continue
                except socket.timeout:
                    break
                except Exception:
                    break

                horario = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')

                if comando_recebido.lower().startswith('user'):
                    socket_comunicação.send(b'331 Password required.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'user', self.separar_comando(comando_recebido, None), horario, função_lock)
                    continue
                
                if comando_recebido.lower().startswith('pass'):
                    socket_comunicação.send(b'230 Login successful.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'pass', '***', horario, função_lock)
                    continue

                cmd_verbo = comando_recebido.split()[0].lower()

                if cmd_verbo == 'list':
                    resp = comando.list()
                    if pasv_aconteceu and socket_secundario:
                        socket_comunicação.send(b'150 Here comes the directory listing.\r\n')
                        try:
                            socket_secundario.settimeout(10) 
                            conn_dados, _ = socket_secundario.accept()
                            if resp: conn_dados.send(f'{resp}\r\n'.encode())
                            else: conn_dados.send(b'\r\n')
                            conn_dados.close()
                            socket_comunicação.send(b'226 Directory send OK.\r\n')
                        except Exception as e:
                            socket_comunicação.send(b'425 Can not open data connection.\r\n')
                        socket_secundario.close()
                        pasv_aconteceu = False
                    else:
                        socket_comunicação.send(b'425 Use PASV first.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'list', '', horario, função_lock)

                elif cmd_verbo == 'pasv':
                    try:
                        porta_secundaria = random.randint(50000, 60000)
                        socket_secundario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_secundario.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        socket_secundario.bind((self.__host, porta_secundaria))
                        socket_secundario.listen(1)
                        
                        P1 = porta_secundaria // 256
                        P2 = porta_secundaria % 256
                        socket_comunicação.send(f'227 Entering Passive Mode ({self.IP_Formatado},{P1},{P2})\r\n'.encode())
                        pasv_aconteceu = True
                    except:
                        socket_comunicação.send(b'500 Error entering PASV.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'pasv', '', horario, função_lock)

                elif cmd_verbo == 'stor':
                    if pasv_aconteceu and socket_secundario:
                        socket_comunicação.send(b'150 Ok to send data.\r\n')
                        try:
                            socket_secundario.settimeout(15) # Timeout maior
                            conn_dados, _ = socket_secundario.accept()
                            
                            nome_arquivo = self.separar_comando(comando_recebido, None)
                            msg_retorno = comando.stor(conn_dados, nome_arquivo)
                            socket_comunicação.send(msg_retorno)
                            conn_dados.close()
                            
                            # Lógica crítica para garantir registro no Dashboard
                            if b'226' in msg_retorno:
                                hash_arquivo = comando.pegar_hash_arquivo_temporario()
                                
                                if hash_arquivo:
                                    tamanho = comando.pegar_tamanho_arquivo(hash_arquivo) # Tenta pegar tamanho antes de renomear (caso falhe o rename)
                                    sucesso_rename = comando.renomear_arquivo_final(hash_arquivo)
                                    
                                    # Se renomeou com sucesso, recalcula tamanho correto
                                    if sucesso_rename:
                                        tamanho = comando.pegar_tamanho_arquivo(hash_arquivo)
                                        
                                    print(f"[DEBUG] Registrando no DB: {nome_arquivo} | {hash_arquivo}")
                                    gerenciador.adicionar_data_arquivo(ID_de_usuario, nome_arquivo, tamanho, hash_arquivo, função_lock)
                                else:
                                    print("[!] Hash retornou vazio (falha no arquivo temporário).")
                            else:
                                print(f"[!] Falha no STOR: {msg_retorno}")

                        except Exception as e:
                            print(f"[!] Erro Crítico no Loop STOR: {e}")
                            socket_comunicação.send(b'451 Error.\r\n')
                        
                        socket_secundario.close()
                        pasv_aconteceu = False
                    else:
                        socket_comunicação.send(b"425 Use PASV first.\r\n")
                    gerenciador.adicionar_comandos(ID_de_usuario, 'stor', '', horario, função_lock)

                elif cmd_verbo == 'cwd':
                    arg = self.separar_comando(comando_recebido, None)
                    socket_comunicação.send(comando.cd(arg))
                    gerenciador.adicionar_comandos(ID_de_usuario, 'cwd', arg, horario, função_lock)
                
                elif cmd_verbo == 'pwd':
                    socket_comunicação.send(f'257 "{comando.pwd()}"\r\n'.encode())
                    gerenciador.adicionar_comandos(ID_de_usuario, 'pwd', '', horario, função_lock)

                elif cmd_verbo == 'quit':
                    socket_comunicação.send(b'221 Goodbye.\r\n')
                    break
                else:
                    socket_comunicação.send(b'502 Command not implemented.\r\n')
                    gerenciador.adicionar_comandos(ID_de_usuario, 'unknown', comando_recebido, horario, função_lock)

        except Exception as e:
            print(f"Erro conexão: {e}")
        finally:
            timestamp_final = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
            try: socket_comunicação.close()
            except: pass
            if socket_secundario:
                try: socket_secundario.close()
                except: pass
            
            gerenciador.finalizar_sessão(timestamp_final, ID_de_usuario, função_lock)
            with self.lock:
                self.conexões_ativas -= 1
            print(f'Desconexão [{IP_invasor}]. Ativos: {self.conexões_ativas}')

    def ligar_servidor(self):
        print(f"--- HONEYPOT FTP ATIVO NO IP: {IP_Publico} ---")
        while True:
            try:
                if self.conexões_ativas < self.maximo_de_conexões:
                    client, addr = self.servidor.accept()
                    IP_invasor, porta = addr
                    
                    with self.lock: self.conexões_ativas += 1
                    
                    print(f'Nova Conexão: {IP_invasor}')
                    horario = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')
                    ID_de_usuario = gerenciador.adicionar_nova_conexão(IP_invasor, porta, horario, self.lock)
                    
                    if ID_de_usuario:
                        threading.Thread(target=self.interagir_com_cliente, args=(client, ID_de_usuario, IP_invasor), daemon=True).start()
                        threading.Thread(target=gerenciador.pesquisar_local_do_ip, args=(ID_de_usuario, IP_invasor, self.lock), daemon=True).start()
                    else:
                        client.close()
                        with self.lock: self.conexões_ativas -= 1
                else:
                    time.sleep(1)
            except Exception as e:
                print(f"Erro loop servidor: {e}")

    def escaneador_segundo_plano(self):
        print("--- Scanner VT Ativo ---")
        while True:
            try:
                res = gerenciador.pegar_hash_arquivo_pendente(self.lock)
                if res:
                    ID_u, h_arq = res
                    gerenciador.escanear_arquivo(h_arq, ID_u, self.lock)
                else:
                    time.sleep(10)
            except Exception as e:
                print(f"Erro Scanner: {e}")
                time.sleep(10)

if __name__ == "__main__":
    server = Honeypot()
    server.ligar_servidor()