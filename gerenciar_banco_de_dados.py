import sqlite3
from contextlib import closing
import time
import requests
from dotenv import load_dotenv
import os

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
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''select IP_de_origem from sessões where ID_de_usuario=(?)''',(ID_de_usuario,))
                    IP_de_origem=cursor.fetchone()
        if IP_de_origem:
            IP_de_origem=IP_de_origem[0]

        localizador=f'http://ip-api.com/json/{IP_de_origem}?fields=lat,lon'
        localizador_dados=requests.get(localizador)
        dados_ip=localizador_dados.json()
        latitude=dados_ip.get('lat',0.0)
        longitude=dados_ip.get('lon',0.0)
        self.colocar_localização(ID_de_usuario,IP_de_origem,latitude,longitude,função_lock)
        time.sleep(1.5)
        

    def colocar_localização(self,ID_de_usuario,IP_de_origem,latitude,longitude,função_lock):
        with função_lock:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                with conexão:
                    cursor=conexão.cursor()
                    cursor.execute('''
                                insert or ignore into geolocalização
                                (ID_de_usuario,IP_de_origem,latitude,longitude)
                                values(?,?,?,?)''',(ID_de_usuario,IP_de_origem,latitude,longitude))

    def escanear_arquivo(self,hash_do_arquivo,ID_de_usuario,função_lock):
        load_dotenv()
        virus_total_header_api=os.getenv('virus_total')
        analisador=f'https://www.virustotal.com/api/v3/files/{hash_do_arquivo}'
        headers={
            'accept':"application/json",
            'x-apikey':f'{virus_total_header_api}'
            }
        
        try:
            dados_recebidos=requests.get(analisador, headers=headers)
            if dados_recebidos.status_code==200:
                data_analisada=dados_recebidos.json()
                #pega numero de votos para malicioso.
                votos_arquivo=data_analisada['data']['attributes']['last_analysis_stats']['malicious']
                #pega tipo do arquivo (Exemplo: win32 EXE)
                tipo_do_arquivo=data_analisada['data']['attributes']['type_description']
                #tenta pegar categoria, mas se der erro, diz que é generico.
                try:
                    categoria_arquivo = data_analisada['data']['threat_severity']['threat_severity_data']['popular_threat_category']
                except (KeyError, TypeError):
                    categoria_arquivo = 'generico'

            elif dados_recebidos.status_code == 404:
                votos_arquivo=0
                tipo_do_arquivo='desconhecido'
                categoria_arquivo='desconhecido'
            else:
                print(f"Erro na API VirusTotal: {dados_recebidos.status_code} - {dados_recebidos.text}")

            self.atualisar_tabela_capturas_scan(votos_arquivo,tipo_do_arquivo,categoria_arquivo,ID_de_usuario,função_lock)
        except Exception as e:
            print(f"Erro critico no scan: {e}")
    #Atualisa banco de dados com informações sobre o arquivo. Talvez seria melhor 
    #apenas se é inofensivo ou não ao invés de numero de votos?
    # Novo dia: numero é melhor. Tudo aqui, por definição, é malicioso.    
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
            ID_de_usuario,hash_do_arquivo=resultado
            return ID_de_usuario,hash_do_arquivo
        else:
            return None