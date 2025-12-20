import socket
import time
import os
import sys
from datetime import datetime

# --- CONFIGURAÇÕES DO ATAQUE ---
TARGET_IP = 'localhost'
TARGET_PORT = 2121
FILE_TO_UPLOAD = 'teste.mp3'
LOG_DIR = 'logs_de_erro'
LOG_FILE = os.path.join(LOG_DIR, 'auditoria_ataque.txt')

# Tempos de Espera (em segundos)
WAIT_RETRY_CONNECT = 10  # Tempo de espera se a conexão falhar
WAIT_CYCLE_RESET = 5     # Tempo de descanso após um ataque completo

# Códigos de Cores (Visualização)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def setup_logs():
    """Cria a pasta e o arquivo de log se não existirem."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"{CYAN}[INFO] Diretório de logs criado.{RESET}")
    
    # Cria o arquivo vazio se não existir, apenas para garantir
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"--- INÍCIO DA AUDITORIA DE SEGURANÇA: {datetime.now()} ---\n")

def registrar_falha(etapa, descricao, resposta_raw="N/A"):
    """Escreve o erro no arquivo único de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entrada_log = (
        f"\n[{timestamp}] FALHA DETECTADA\n"
        f"   Etapa: {etapa}\n"
        f"   Descrição: {descricao}\n"
        f"   Resposta do Servidor: {resposta_raw}\n"
        f"   {'-'*40}"
    )
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entrada_log)
        print(f"{RED}[LOG] Falha registrada em {LOG_FILE}{RESET}")
    except Exception as e:
        print(f"{RED}[ERRO CRÍTICO] Não foi possível escrever no log: {e}{RESET}")

def receber_resposta(sock, buffer=4096, timeout=5):
    sock.settimeout(timeout)
    try:
        dados = sock.recv(buffer).decode('utf-8', errors='ignore').strip()
        return dados
    except socket.timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERRO_SOCKET: {e}"

def executar_ataque():
    """
    Simula um invasor tentando explorar todas as funções do honeypot.
    Retorna True se completou o ciclo (mesmo com falhas internas), False se a conexão caiu.
    """
    
    # Validação do arquivo de carga
    if not os.path.exists(FILE_TO_UPLOAD):
        print(f"{RED}[ERRO FATAL] Arquivo {FILE_TO_UPLOAD} não encontrado na pasta do script.{RESET}")
        return False # Para o script para você corrigir isso

    print(f"\n{YELLOW}--- BUSCANDO ALVO EM {TARGET_IP}:{TARGET_PORT} ---{RESET}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 1. TENTATIVA DE CONEXÃO
    try:
        sock.connect((TARGET_IP, TARGET_PORT))
        print(f"{GREEN}[+] Conexão estabelecida! Iniciando script de teste...{RESET}")
    except ConnectionRefusedError:
        print(f"{RED}[!] Conexão recusada. Alvo offline.{RESET}")
        print(f"{CYAN}[INFO] Aguardando {WAIT_RETRY_CONNECT} segundos para tentar novamente...{RESET}")
        time.sleep(WAIT_RETRY_CONNECT)
        return True # Retorna True para manter o loop rodando, mas aborta este ciclo

    try:
        # 2. BANNER GRABBING
        banner = receber_resposta(sock)
        if "220" in banner:
            print(f"{GREEN}[OK] Banner recebido: {banner}{RESET}")
        else:
            print(f"{RED}[FAIL] Banner incorreto.{RESET}")
            registrar_falha("Conexão Inicial", "Banner não contém código 220", banner)

        # 3. AUTENTICAÇÃO
        sock.send(b"user admin\r\n")
        resp_user = receber_resposta(sock)
        
        sock.send(b"pass 12345\r\n")
        resp_pass = receber_resposta(sock)

        if "230" in resp_pass:
            print(f"{GREEN}[OK] Login efetuado com sucesso.{RESET}")
        else:
            print(f"{RED}[FAIL] Login falhou.{RESET}")
            registrar_falha("Autenticação", "Não recebeu 230 Login successful", f"User: {resp_user} | Pass: {resp_pass}")

        # 4. NAVEGAÇÃO BÁSICA
        comandos_nav = [
            ("PWD", b"pwd\r\n", ["/", "\\"]),
            ("LIST", b"list\r\n", []) # Lista vazia significa que aceitamos qualquer resposta não vazia
        ]

        for nome, cmd, validadores in comandos_nav:
            sock.send(cmd)
            resp = receber_resposta(sock)
            
            sucesso = False
            if validadores:
                if any(v in resp for v in validadores): sucesso = True
            else:
                if len(resp) > 2 and "50" not in resp: sucesso = True # Checa se não é erro 50x

            if sucesso:
                print(f"{GREEN}[OK] {nome} funcionou.{RESET}")
            else:
                print(f"{RED}[FAIL] {nome} retornou resposta inválida.{RESET}")
                registrar_falha(f"Comando {nome}", "Resposta inesperada", resp)

        # 5. UPLOAD (STOR) - PONTO CRÍTICO
        print(f"{YELLOW}[*] Iniciando teste de UPLOAD (STOR) com {FILE_TO_UPLOAD}...{RESET}")
        
        tamanho_arquivo = os.path.getsize(FILE_TO_UPLOAD)
        sock.send(f"stor {FILE_TO_UPLOAD}\r\n".encode())
        
        # Delay minúsculo para simular latência de rede e não "colar" os pacotes TCP instantaneamente
        time.sleep(0.1) 
        
        with open(FILE_TO_UPLOAD, 'rb') as f:
            dados = f.read()
            sock.sendall(dados)
        
        print(f"{CYAN}[INFO] {tamanho_arquivo} bytes enviados. Aguardando confirmação...{RESET}")
        
        # O servidor precisa responder que recebeu. Se ele travar aqui, é TIMEOUT.
        resp_stor = receber_resposta(sock, timeout=3)
        
        if "226" in resp_stor or "250" in resp_stor or "success" in resp_stor.lower():
             print(f"{GREEN}[OK] Servidor confirmou recebimento.{RESET}")
        elif resp_stor == "TIMEOUT":
             print(f"{RED}[FAIL] Timeout no STOR. Servidor provavelmente travou lendo o arquivo.{RESET}")
             registrar_falha("Comando STOR", "Timeout aguardando confirmação (Servidor travou?)", "Sem resposta")
        else:
             print(f"{RED}[FAIL] Erro no STOR.{RESET}")
             registrar_falha("Comando STOR", "Erro retornado pelo servidor", resp_stor)

        # 6. DOWNLOAD (RETR) - VALIDAR INTEGRIDADE
        print(f"{YELLOW}[*] Verificando arquivo enviado via RETR...{RESET}")
        sock.send(f"retr {FILE_TO_UPLOAD}\r\n".encode())
        
        # Lê apenas o início para ver se vêm dados
        inicio_arquivo = sock.recv(1024)
        
        if len(inicio_arquivo) > 0:
            print(f"{GREEN}[OK] O servidor enviou dados de volta.{RESET}")
        else:
            print(f"{RED}[FAIL] O arquivo voltou vazio.{RESET}")
            registrar_falha("Comando RETR", "Arquivo recebido com 0 bytes", "Vazio")

        # 7. ENCERRAMENTO
        sock.send(b"quit\r\n")
        print(f"{GREEN}[OK] Ciclo finalizado. Desconectando.{RESET}")
        sock.close()
        return True

    except (socket.error, BrokenPipeError) as e:
        print(f"{RED}[CRASH] A conexão caiu inesperadamente durante o teste!{RESET}")
        registrar_falha("Conexão Geral", f"Socket fechado abruptamente: {e}", "N/A")
        return True # Retorna True para tentar reconectar no próximo loop

# --- LOOP PRINCIPAL ---
if __name__ == "__main__":
    setup_logs()
    print("=== SCRIPT INVASOR AUTOMATIZADO (MODO PERSISTENTE) ===")
    print(f"Log: {LOG_FILE}")
    print("Pressione CTRL+C para parar.\n")
    
    try:
        while True:
            executar_ataque()
            print(f"{CYAN}--- Aguardando {WAIT_CYCLE_RESET}s para próximo ataque ---\n{RESET}")
            time.sleep(WAIT_CYCLE_RESET)
            
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Script interrompido pelo usuário.{RESET}")