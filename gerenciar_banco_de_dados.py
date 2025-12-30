import sqlite3
from contextlib import closing
import time

class gerenciador_de_banco():
    def adicionar_nova_conexão(self,IP_invasor,porta_invasor,horario_da_conexão):
        while True:
            with closing(sqlite3.connect('coletor.db')) as conexão:
                cursor=conexão.cursor()
                cursor.execute('''select id from sessões where IP_de_origem = (?)''',(IP_invasor,))
                ID_de_usuario = cursor.fetchone()
                if ID_de_usuario:
                    cursor.close()
                    return ID_de_usuario
                else:
                    try:
                        cursor.execute('''insert into sessões 
                                            (IP_de_origem,Porta_de_origem,Data_de_inicio)
                                            values (?,?,?)''',(IP_invasor,porta_invasor,horario_da_conexão))
                        cursor.close()
                        return ID_de_usuario
                    except sqlite3.IntegrityError:
                        time.sleep(2)

    def adicionar_comandos(self,ID_de_usuario,verbo,argumento,horario_do_comando):
        with closing(sqlite3.connect('coletor.db')) as conexão:
            cursor=conexão.cursor()
            cursor.execute('''insert into comandos
                                ID_de_usuario,Comando,Argumento,Timestamp
                                values (?,?,?,?)''',(ID_de_usuario,verbo,argumento,horario_do_comando))
        cursor.close()

    def adicionar_data_arquivo(self,ID_de_usuario,nome_virus_recebido,tamanho_do_virus,hash_do_virus):
        with closing(sqlite3.connect('coletor.db')) as conexão:
            cursor=conexão.cursor()
            cursor.execute('''insert into capturas
                                ID_de_usuario,Nome_do_arquivo,Tamanho_do_arquivo,Hash_do_arquivo
                                values (?,?,?,?)''',(ID_de_usuario,nome_virus_recebido,tamanho_do_virus,hash_do_virus))
        cursor.close()

    def finalizar_sessão(self,timestamp_final,ID_de_usuario):
        with closing(sqlite3.connect('coletor.db')) as conexão:
            cursor=conexão.cursor()
            cursor.execute('''update sessões
                                set Data_de_finalização = (?)
                                where ID_de_usuario = (?)''',(timestamp_final,ID_de_usuario))
        cursor.close()