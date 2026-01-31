import sqlite3
import os
from fastapi import FastAPI, HTTPException
from contextlib import closing
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import uvicorn
from dotenv import load_dotenv
from fastapi.responses import FileResponse

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



#cria modelos para endpoints
class status_modelo(pydantic.BaseModel):
    total_de_ataques: int
    total_malware: int
    ips_unicos: int
    media_virus: float


class item_arquivos_logs(pydantic.BaseModel):
    Nome_do_arquivo:str
    Tamanho_do_arquivo:int
    Numero_de_votos_malicioso:int
    Status:str


class item_arquivo_grafico(pydantic.BaseModel):
    tipo_de_arquivo:str
    contagem_votos:int


class retornar_arquivos(pydantic.BaseModel):
    logs_arquivos:list[item_arquivos_logs]
    Grafico_Arquivos:list[item_arquivo_grafico]


class retornar_comandos(pydantic.BaseModel):
    ID_do_comando:int
    Timestamp:str
    IP_de_origem:str 
    Comando:str
    Argumento:str

class ListaComandos(pydantic.BaseModel):
    log_de_comandos: list[retornar_comandos]

class retornar_geolocalização(pydantic.BaseModel):
    Latitude:str
    Longitude:str
    IP_de_origem:str


#"link" root para confirmação que site está rodando
@app.get("/",summary='Status do Sistema')
def root():
    """
    Verifica a conectividade da API.
    Retorna um objeto JSON simples confirmando que o Mimico Honeypot está online.
    """

    return {"sistema": "Mimico Honeypot", "status": "online"}


#Endpoint dos numeros gerais do banco de dados, stats
@app.get('/api/stats', response_model=status_modelo,summary='Estatísticas Gerais')
def pegar_stats():
    """
    Obtém métricas consolidadas do banco de dados.

    Retorna:
    - Total de sessões de ataque.
    - Contagem de arquivos classificados como malware.
    - Quantidade de IPs únicos de origem.
    - Média de 'votos maliciosos' dos arquivos capturados.
    """
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

# Endpoint da api, pega informações de arquivos para grafico e logs
@app.get('/api/arquivos',response_model=retornar_arquivos,summary='Logs e Gráficos de Arquivos')
def pegar_arquivos():
    """
    Recupera dados sobre transferências de arquivos.

    Retorna dois conjuntos de dados:
    1. Lista detalhada dos últimos 20 arquivos capturados (nome, tamanho, status).
    2. Dados agregados por 'tipo de arquivo' para geração de gráficos de pizza ou barras.
    """
    lista_de_arquivos=[]
    lista_grafico_arquivos=[]
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
            linha=item_arquivos_logs(
                Nome_do_arquivo=linha[0],
                Tamanho_do_arquivo=linha[1],
                Numero_de_votos_malicioso=linha[2],
                Status=linha[3]
            )
            lista_de_arquivos.append(linha)

        linhas_grafico_arquivos=cursor.execute('''
            select tipo_de_arquivo, 
            COUNT(tipo_de_arquivo) as count
            from capturas
            group by tipo_de_arquivo''').fetchall()
        for linha in linhas_grafico_arquivos:
            linha=item_arquivo_grafico(
                tipo_de_arquivo=linha[0],
                contagem_votos=linha[1]
            )
            lista_grafico_arquivos.append(linha)

    return retornar_arquivos(
        logs_arquivos=lista_de_arquivos,
        Grafico_Arquivos=lista_grafico_arquivos
    )

#Endpoint de comandos, pega ultimos 50 comandos
@app.get('/api/comandos',response_model=ListaComandos,summary='Histórico de Comandos')
def pegar_comandos():
    """
    Lista os comandos shell executados pelos atacantes.

    Retorna os últimos 50 registros contendo:
    - Timestamp da execução.
    - IP de origem.
    - O comando e seus argumentos.
    """
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
            linha=retornar_comandos(
                ID_do_comando=linha[0],
                Timestamp=linha[1],
                IP_de_origem=linha[2],
                Comando=linha[3],
                Argumento=linha[4]
            )
            lista_de_comandos.append(linha)

    return {'log_de_comandos':lista_de_comandos}

#Api de localizações.
@app.get('/api/geo',response_model=list[retornar_geolocalização],summary='Mapa de Ameaças')
def pegar_locais():
    """
    Dados de geolocalização para visualização em mapa.

    Retorna uma lista de objetos contendo Latitude, Longitude e IP de origem
    de todas as conexões registradas.
    """
    lista_de_locais=[]
    conn=pegar_conexão_BD()
    if not conn: 
        raise HTTPException(status_code=500, detail='BD não encontrado')
    with closing(conn):
        cursor=conn.cursor()
        locais = cursor.execute('SELECT Latitude, longitude AS Longitude, IP_de_origem FROM geolocalização').fetchall()

        for local in locais:
            local=retornar_geolocalização(
                Latitude=local[0],
                Longitude=local[1],
                IP_de_origem=local[2]
            )
            lista_de_locais.append(local)

    return lista_de_locais


@app.get('/favicon.ico',summary='Icone')
def imagem_aba():
    '''Define o icone da aba.'''
    return FileResponse(path='icon/icon.png')


#Pega porta definda no env, inicia site em localhost+porta. 8080 se não achar nenhuma.
load_dotenv()
porta = int(os.getenv("app_porta", 8080))
print("Iniciando Dashboard M.I.M.I.C")
uvicorn.run(app, host="localhost", port=porta)