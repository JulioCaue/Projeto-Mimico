import sqlite3
from contextlib import closing
import time
import vt
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY_VT = os.getenv('virus_total')

class GerenciadorBanco():  # CORREÇÃO: Nome da classe em PascalCase
    def adicionar_nova_conexão(self, IP_invasor, porta_invasor, horario_da_conexão, função_lock):
        with função_lock:
            tentativas = 0
            while tentativas < 5:
                with closing(sqlite3.connect('coletor.db')) as conexão:
                    try:
                        with conexão:
                            cursor = conexão.cursor()
                            cursor.execute('''insert into sessões 
                                                (IP_de_origem, Porta_de_origem, Data_de_inicio)
                                                values (?,?,?)''', (IP_invasor, porta_invasor, horario_da_conexão))
                            ID_de_usuario = cursor.lastrowid
                            return ID_de_usuario
                    except sqlite3.IntegrityError:
                        time.sleep(1)
                        tentativas += 1
            print("[!] Erro DB: Falha ao inserir nova conexão.")
            return None

    def adicionar_comandos(self, ID_de_usuario, verbo, argumento, horario_do_comando, função_lock):
        if not ID_de_usuario: return
        with função_lock:
            try:
                with closing(sqlite3.connect('coletor.db')) as conexão:
                    with conexão:
                        cursor = conexão.cursor()
                        cursor.execute('''insert into comandos
                                            (ID_de_usuario, Comando, Argumento, Timestamp)
                                            values (?,?,?,?)''', (ID_de_usuario, verbo, argumento, horario_do_comando))
            except Exception as e:
                print(f"[!] Erro ao salvar comando: {e}")

    def adicionar_data_arquivo(self, ID_de_usuario, nome_perigoso, tamanho, hash_arquivo, função_lock):
        if not ID_de_usuario: return
        with função_lock:
            try:
                with closing(sqlite3.connect('coletor.db')) as conexão:
                    with conexão:
                        cursor = conexão.cursor()
                        cursor.execute('''insert into capturas
                                            (ID_de_usuario, Nome_do_arquivo, Tamanho_do_arquivo, Hash_do_arquivo)
                                            values (?,?,?,?)''', (ID_de_usuario, nome_perigoso, tamanho, hash_arquivo))
                print(f"[+] Arquivo registrado no Banco: {nome_perigoso}")
            except Exception as e:
                print(f"[!] Erro ao registrar arquivo no DB: {e}")

    def finalizar_sessão(self, timestamp_final, ID_de_usuario, função_lock):
        if not ID_de_usuario: return
        with função_lock:
            try:
                with closing(sqlite3.connect('coletor.db')) as conexão:
                    with conexão:
                        cursor = conexão.cursor()
                        cursor.execute('''update sessões
                                            set Data_de_finalização = (?)
                                            where ID_de_usuario = (?)''', (timestamp_final, ID_de_usuario))
            except:
                pass

    def pesquisar_local_do_ip(self, ID_de_usuario, IP_alvo, função_lock):
        if IP_alvo in ['127.0.0.1', 'localhost', '0.0.0.0']: return

        try:
            response = requests.get(f"http://ip-api.com/json/{IP_alvo}", timeout=5)
            data = response.json()
            
            if data['status'] == 'success':
                lat = str(data['lat'])
                lon = str(data['lon'])
                
                with função_lock:
                    with closing(sqlite3.connect('coletor.db')) as conexão:
                        with conexão:
                            cursor = conexão.cursor()
                            try:
                                cursor.execute('''insert into geolocalização 
                                (ID_de_usuario, IP_de_origem, Latitude, longitude) 
                                values (?,?,?,?)''', (ID_de_usuario, IP_alvo, lat, lon))
                            except sqlite3.IntegrityError:
                                pass 
        except Exception as e:
            print(f"[!] Erro GeoIP: {e}")

    def escanear_arquivo(self, hash_do_arquivo, ID_de_usuario, função_lock):
        print(f"[*] Iniciando Scan VT para: {hash_do_arquivo}")
        
        if not API_KEY_VT:
            print("[!] ERRO: 'virus_total' não definido no .env!")
            return

        try:
            with vt.Client(API_KEY_VT) as client:
                try:
                    arquivo = client.get_object(f"/files/{hash_do_arquivo}")
                    stats = arquivo.last_analysis_stats
                    votos_arquivo = stats.get('malicious', 0)
                    tipo_do_arquivo = getattr(arquivo, 'type_description', 'desconhecido')
                    try: categoria_arquivo = arquivo.popular_threat_category
                    except: categoria_arquivo = 'generico'
                    print(f"[+] VT: {votos_arquivo} votos.")
                except vt.APIError as e:
                    if e.code == "NotFoundError":
                        votos_arquivo = 0
                        tipo_do_arquivo = 'desconhecido'
                        categoria_arquivo = 'limpo'
                    else:
                        raise e 

            self.atualisar_tabela_capturas_scan(votos_arquivo, tipo_do_arquivo, categoria_arquivo, ID_de_usuario, função_lock)
            
        except Exception as e:
            print(f"[!] Erro Scan VT: {e}")

    def atualisar_tabela_capturas_scan(self, votos, tipo, categoria, ID_de_usuario, função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor = conexão.cursor()
                    cursor.execute('''
                    update capturas
                    set Numero_de_votos_malicioso=(?), tipo_de_arquivo=(?), categoria_arquivo=(?), status='verificado'
                    where ID_de_usuario=(?)''', (votos, tipo, categoria, ID_de_usuario))
    
    def pegar_hash_arquivo_pendente(self, função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor = conexão.cursor()
                    cursor.execute('''select ID_de_usuario, Hash_do_arquivo from capturas where status='pendente' LIMIT 1''')
                    return cursor.fetchone()