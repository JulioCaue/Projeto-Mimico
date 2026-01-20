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
    
    return jsonify({
        "recent_files": [dict(ix) for ix in files],
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
    app.run(host='0.0.0.0', port=5000)