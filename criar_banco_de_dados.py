import os
import sqlite3

def criar_banco():
    if not os.path.exists('coletor.db'):
        with sqlite3.connect('coletor.db') as conexão:
            cursor=conexão.cursor()
            cursor.execute('''
            create table geolocalização(
            ID_Localização integer primary key autoincrement,
            ID_de_usuario integer unique,
            IP_de_origem text unique,
            Latitude text,
            longitude text,
            Foreign key (ID_de_usuario) REFERENCES sessões(ID_de_usuario))
            ''')
            cursor.execute('''
            create table capturas(
            ID_da_captura integer primary key autoincrement,
            ID_de_usuario integer,
            Nome_do_arquivo text,
            Tamanho_do_arquivo integer,
            Hash_do_arquivo text,
            Numero_de_votos_malicioso integer,
            tipo_de_arquivo text,
            categoria_arquivo text,
            Status text default pendente,
            Foreign key (ID_de_usuario) REFERENCES sessões(ID_de_usuario))
            ''')
            cursor.execute('''
            create table comandos(
            ID_do_comando integer primary key autoincrement,
            ID_de_usuario integer,
            Comando text,
            Argumento text,
            Timestamp text,
            Foreign key (ID_de_usuario) REFERENCES sessões(ID_de_usuario))
            ''')
            cursor.execute('''
            create table sessões(
            ID_de_usuario integer primary key autoincrement,
            IP_de_origem text,
            Porta_de_origem integer,
            Data_de_inicio text,
            Data_de_finalização text)
            ''')