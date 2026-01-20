import sqlite3
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
DB_NAME = 'coletor.db'

def get_db_connection():
    if not os.path.exists(DB_NAME):
        return None
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD não encontrado"}), 500
    
    cursor = conn.cursor()
    
    # KPIs
    total_attacks = cursor.execute('SELECT COUNT(*) FROM sessões').fetchone()[0]
    total_malware = cursor.execute('SELECT COUNT(*) FROM capturas WHERE Numero_de_votos_malicioso > 0').fetchone()[0]
    unique_ips = cursor.execute('SELECT COUNT(DISTINCT IP_de_origem) FROM sessões').fetchone()[0]
    avg_virus = cursor.execute('SELECT AVG(Numero_de_votos_malicioso) FROM capturas').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "total_attacks": total_attacks,
        "total_malware": total_malware,
        "unique_ips": unique_ips,
        "avg_virus": round(avg_virus if avg_virus else 0, 1)
    })

@app.route('/api/files')
def get_files():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD não encontrado"}), 500
    
    # Busca os dados brutos (Tamanho vem em Bytes agora)
    files = conn.execute('''
        SELECT Nome_do_arquivo, Tamanho_do_arquivo, Numero_de_votos_malicioso, Status, tipo_de_arquivo
        FROM capturas 
        ORDER BY ID_da_captura DESC LIMIT 20
    ''').fetchall()
    
    types_data = conn.execute('''
        SELECT tipo_de_arquivo, COUNT(*) as count 
        FROM capturas 
        GROUP BY tipo_de_arquivo
    ''').fetchall()
    
    conn.close()
    
    # --- FORMATAÇÃO DOS DADOS ---
    lista_formatada = []
    for f in files:
        # Converte a linha do banco (Row) para Dicionário editável
        item = dict(f)
        tamanho_bytes = item['Tamanho_do_arquivo']
        
        # Lógica de formatação inteligente
        try:
            # Se for None ou 0, mostra 0 Bytes
            if not tamanho_bytes:
                item['Tamanho_do_arquivo'] = "0 Bytes"
            else:
                # Converte para float para garantir a conta
                bytes_val = float(tamanho_bytes)
                
                # Se for menor que 1 MB, mostra em KB ou Bytes
                if bytes_val < 1024:
                    item['Tamanho_do_arquivo'] = f"{int(bytes_val)} Bytes"
                elif bytes_val < 1048576: # Menor que 1 MB
                    kb_val = bytes_val / 1024
                    item['Tamanho_do_arquivo'] = f"{kb_val:.1f} KB"
                else: # Maior que 1 MB
                    mb_val = bytes_val / 1048576
                    item['Tamanho_do_arquivo'] = f"{mb_val:.2f} MB"
        except Exception as e:
            # Em caso de erro (dado sujo no banco antigo), mostra erro mas não quebra o site
            item['Tamanho_do_arquivo'] = "N/A"
            
        lista_formatada.append(item)
    
    return jsonify({
        "recent_files": lista_formatada,
        "file_types": [dict(ix) for ix in types_data]
    })

@app.route('/api/commands')
def get_commands():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD não encontrado"}), 500
    
    query = '''
        SELECT c.Timestamp, s.IP_de_origem, c.Comando, c.Argumento
        FROM comandos c
        JOIN sessões s ON c.ID_de_usuario = s.ID_de_usuario
        ORDER BY c.Timestamp DESC LIMIT 50
    '''
    cmds = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify([dict(ix) for ix in cmds])

@app.route('/api/geo')
def get_geo():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD não encontrado"}), 500
    
    locations = conn.execute('SELECT Latitude, longitude AS Longitude, IP_de_origem FROM geolocalização').fetchall()
    conn.close()
    
    return jsonify([dict(ix) for ix in locations])

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Iniciando Dashboard M.I.M.I.C")
    app.run(host='127.0.0.1', port=5000)