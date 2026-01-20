import sqlite3
from contextlib import closing
import time
import vt  # Biblioteca oficial do VirusTotal
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
# Carrega o arquivo .env
load_dotenv()

# Pega a chave da variavel 'virus_total'
API_KEY_VT = os.getenv('virus_total')

class gerenciador_de_banco():
    def adicionar_nova_conexão(self,IP_invasor,porta_invasor,horario_da_conexão,função_lock):
        with função_lock:
            while True:
                with closing(sqlite3.connect('coletor.db')) as conexão:
                    try:
                        with conexão:
                            cursor=conexão.cursor()
                            cursor.execute('''insert into sessões 
                                                (IP_de_origem,Porta_de_origem,Data_de_inicio)
                                                values (?,?,?)''',(IP_invasor,porta_invasor,horario_da_conexão))
                            ID_de_usuario = cursor.lastrowid
                            return ID_de_usuario
                    except sqlite3.IntegrityError:
                        time.sleep(2)

    def adicionar_comandos(self,ID_de_usuario,verbo,argumento,horario_do_comando,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''insert into comandos
                                        (ID_de_usuario,Comando,Argumento,Timestamp)
                                        values (?,?,?,?)''',(ID_de_usuario,verbo,argumento,horario_do_comando))

    def adicionar_data_arquivo(self,ID_de_usuario,nome_perigoso_virus_recebido,tamanho_do_virus,hash_do_virus,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''insert into capturas
                                        (ID_de_usuario,Nome_do_arquivo,Tamanho_do_arquivo,Hash_do_arquivo)
                                        values (?,?,?,?)''',(ID_de_usuario,nome_perigoso_virus_recebido,tamanho_do_virus,hash_do_virus))

    def finalizar_sessão(self,timestamp_final,ID_de_usuario,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''update sessões
                                        set Data_de_finalização = (?)
                                        where ID_de_usuario = (?)''',(timestamp_final,ID_de_usuario))

    def pesquisar_local_do_ip(self,ID_de_usuario,função_lock):
        # Geo placeholder
        pass 

    def escanear_arquivo(self,hash_do_arquivo,ID_de_usuario,função_lock):
        print(f"[*] Iniciando Scan VT para: {hash_do_arquivo}")
        
        if not API_KEY_VT:
            print("[!] ERRO CRÍTICO: Variável 'virus_total' não encontrada no arquivo .env!")
            return

        try:
            # Usa a biblioteca oficial com a chave do .env
            with vt.Client(API_KEY_VT) as client:
                try:
                    arquivo = client.get_object(f"/files/{hash_do_arquivo}")
                    
                    stats = arquivo.last_analysis_stats
                    votos_arquivo = stats.get('malicious', 0)
                    tipo_do_arquivo = getattr(arquivo, 'type_description', 'desconhecido')
                    
                    # Tenta pegar categoria de ameaca
                    try:
                        categoria_arquivo = arquivo.popular_threat_category
                    except:
                        categoria_arquivo = 'generico'
                        
                    print(f"[+] Sucesso VT: {votos_arquivo} detectaram.")

                except vt.APIError as e:
                    if e.code == "NotFoundError":
                        print("[-] Arquivo limpo ou desconhecido (Hash nao encontrado no VT).")
                        votos_arquivo = 0
                        tipo_do_arquivo = 'desconhecido'
                        categoria_arquivo = 'limpo'
                    else:
                        raise e 

            self.atualisar_tabela_capturas_scan(votos_arquivo,tipo_do_arquivo,categoria_arquivo,ID_de_usuario,função_lock)
            
        except Exception as e:
            print(f"[!] Erro no Scan VT: {e}")

    def atualisar_tabela_capturas_scan(self,votos_arquivo,tipo_do_arquivo,categoria_arquivo,ID_de_usuario,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''
                    update capturas
                    set Numero_de_votos_malicioso=(?),tipo_de_arquivo=(?),categoria_arquivo=(?),status='verificado'
                    where ID_de_usuario=(?)''',(votos_arquivo,tipo_do_arquivo,categoria_arquivo,ID_de_usuario))
    
    def pegar_hash_arquivo_pendente(self,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''
                select 
                ID_de_usuario,
                Hash_do_arquivo 
                from capturas where status='pendente'
                ''',)
                resultado=cursor.fetchone()
        if resultado:
            return resultado
        else:
            return None