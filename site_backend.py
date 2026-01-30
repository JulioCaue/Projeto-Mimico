import sqlite3
import os
from fastapi import FastAPI, HTTPException
from contextlib import closing
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import uvicorn
from dotenv import load_dotenv

#cria objeto app e pega nome do banco de dados
app = FastAPI()
dirbase = os.path.dirname(os.path.abspath(__file__))
NOME_BD = os.path.join(dirbase, 'coletor.db')

#Define permissões
app.add_middleware(
    CORSMiddleware,
    allow_origins=['localhost'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#pega conexão com banco de dados
def pegar_conexão_BD():
    if not os.path.exists(NOME_BD):
        return None
    conn = sqlite3.connect(NOME_BD)
    return conn

#cria modelo para status
class status_modelo(pydantic.BaseModel):
    total_de_ataques: int
    total_malware: int
    ips_unicos: int
    media_virus: float


#"link" root para confirmação que site está rodando
@app.get("/")
def root():
    return {"sistema": "Mimico Honeypot", "status": "online"}


#Call dos numeros gerais do banco de dados, stats
@app.get('/api/stats', response_model=status_modelo)
def pegar_stats():
    conn = pegar_conexão_BD()
    if not conn: 
        raise HTTPException(status_code=500, detail='BD não encontrado')
    
    with closing(conn):
        cursor = conn.cursor()
        total_de_ataques = cursor.execute('SELECT COUNT(*) FROM sessões').fetchone()[0]
        total_malware = cursor.execute('SELECT COUNT(*) FROM capturas WHERE Numero_de_votos_malicioso > 0').fetchone()[0]
        ips_unicos = cursor.execute('SELECT COUNT(DISTINCT IP_de_origem) FROM sessões').fetchone()[0]
        
        media_virus_res = cursor.execute('SELECT AVG(Numero_de_votos_malicioso) FROM capturas').fetchone()[0]
        media_virus = media_virus_res if media_virus_res else 0.0
    
    return status_modelo(
        total_de_ataques=total_de_ataques,
        total_malware=total_malware,
        ips_unicos=ips_unicos,
        media_virus=media_virus
    )

# Enpoint da api, pega informações de arquivos para grafico e logs
@app.get('/api/arquivos')
def pegar_arquivos():
    lista_de_arquivos=[]
    conn = pegar_conexão_BD()
    if not conn: 
        raise HTTPException(status_code=500, detail='BD não encontrado')
    with closing(conn):
        cursor=conn.cursor()
        ultimos_arquivos=cursor.execute('''
            select Nome_do_arquivo, Tamanho_do_arquivo, Numero_de_votos_malicioso, Status
            from capturas
            order by ID_da_captura desc limit 20''').fetchall()
        for linha in ultimos_arquivos:
            lista_de_arquivos.append(linha)

        itens_grafico_arquivos=cursor.execute('''
            select tipo_de_arquivo, COUNT(*) as count
            from capturas
            group by tipo_de_arquivo''').fetchall()

    return {'Linhas_Arquivos':lista_de_arquivos},{'Grafico_Arquivos':itens_grafico_arquivos}


#Endpoint de comandos, pega ultimos 50 comandos
@app.get('/api/comandos')
def pegar_comandos():
    lista_de_comandos=[]
    conn=pegar_conexão_BD()
    if not conn: 
        raise HTTPException(status_code=500, detail='BD não encontrado')
    with closing (conn):
        cursor=conn.cursor()
        ultimos_comandos=cursor.execute('''
        SELECT c.ID_do_comando, c.Timestamp, s.IP_de_origem, c.Comando, c.Argumento
        from comandos as c
        join sessões as s on c.ID_de_usuario = s.ID_de_usuario
        order by c.ID_do_comando desc limit 50
        ''').fetchall()
        for linha in ultimos_comandos:
            lista_de_comandos.append(linha)

    return {'log_de_comandos':lista_de_comandos}

@app.get('/api/geo')
def pegar_locais():
    lista_de_locais=[]
    conn=pegar_conexão_BD()
    if not conn: 
        raise HTTPException(status_code=500, detail='BD não encontrado')
    with closing(conn):
        cursor=conn.cursor()
        locais = cursor.execute('SELECT Latitude, longitude AS Longitude, IP_de_origem FROM geolocalização').fetchall()

        for local in locais:
            lista_de_locais.append(local)

    return lista_de_locais


load_dotenv()
porta = int(os.getenv("app_porta", 8080))
print("Iniciando Dashboard M.I.M.I.C")
uvicorn.run(app, host="localhost", port=porta)