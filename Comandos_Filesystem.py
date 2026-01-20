import socket
import os
import random
import hashlib
import Pastas_filesystem as filesystem

class Logica_de_arquivos:
    def __init__(self):
        self.filesystem = filesystem.dados
        self.diretorio_atual = self.filesystem['/']
        self.caminho_atual = []
        self.nome_temporario_arquivo = 'nome_temporario'

    def list(self):
        lista_de_arquivos = []
        for arquivo, conteudo in self.diretorio_atual.items():
            # Gera dados falsos realistas
            random.seed(arquivo)
            mes = random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'])
            dia = f"{random.randint(1, 28):02d}"
            hora = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
            data = f"{mes} {dia} {hora}"

            if isinstance(conteudo, dict):
                perm = "drwxr-xr-x"
                size = 4096
            else:
                perm = "-rw-r--r--"
                size = len(conteudo)
            
            lista_de_arquivos.append(f"{perm} 1 root root {size} {data} {arquivo}")

        if not lista_de_arquivos:
            return None
        return '\r\n'.join(lista_de_arquivos)

    def cd(self, diretorio_novo):
        if diretorio_novo == '..':
            if not self.caminho_atual: # Ja esta na raiz
                return b'250 OK\r\n'
            self.caminho_atual.pop()
            # Recalcula diretorio atual do zero
            self.diretorio_atual = self.filesystem['/']
            for pasta in self.caminho_atual:
                self.diretorio_atual = self.diretorio_atual[pasta]
            return b"250 Directory changed.\r\n"
        
        elif diretorio_novo == '/':
            self.caminho_atual = []
            self.diretorio_atual = self.filesystem['/']
            return b"250 Directory changed.\r\n"

        # Simples navegação para frente
        partes = diretorio_novo.strip('/').split('/')
        temp_dir = self.diretorio_atual
        
        for parte in partes:
            if parte in temp_dir and isinstance(temp_dir[parte], dict):
                temp_dir = temp_dir[parte]
            else:
                return b'550 Not a directory.\r\n'
        
        self.diretorio_atual = temp_dir
        for parte in partes:
            if parte: self.caminho_atual.append(parte)
            
        return b"250 Directory changed.\r\n"

    def pwd(self):
        path = '/' + '/'.join(self.caminho_atual)
        if len(path) > 1 and path.endswith('/'): path = path[:-1]
        return path

    def stor(self, conexao_dados, nome_arquivo):
        if not os.path.exists('quarentena'):
            os.makedirs('quarentena')

        conexao_dados.settimeout(2.0)
        caminho_temp = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
        
        try:
            with open(caminho_temp, 'wb') as f:
                while True:
                    try:
                        data = conexao_dados.recv(4096)
                        if not data: break
                        f.write(data)
                    except socket.timeout:
                        break
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return b'451 Error writing file.\r\n'

        # Adiciona entrada falsa no diretorio virtual
        self.diretorio_atual[nome_arquivo] = b'FAKE_CONTENT'
        return b'226 Transfer complete.\r\n'

    def mkdir(self, pasta):
        if pasta not in self.diretorio_atual:
            self.diretorio_atual[pasta] = {}
            return b'257 Directory created.\r\n'
        return b'550 Directory exists.\r\n'
    
    # --- CORREÇÃO DO HASH (COMPATIVEL PYTHON 3.10) ---
    def pegar_hash_virus(self):
        try:
            sha256 = hashlib.sha256()
            path = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
            with open(path, "rb") as f:
                while chunk := f.read(4096):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return "hash_error"

    def pegar_data_arquivo(self):
        try:
            path = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
            size_mb = os.path.getsize(path) / (1024 * 1024)
            return f'{size_mb:.2f} MB'
        except:
            return "0.00 MB"

    def trocar_nome_perigoso_para_hash(self, novo_hash):
        try:
            old = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
            new = f'quarentena/{novo_hash}.quarentena'
            if os.path.exists(new): os.remove(new)
            os.rename(old, new)
        except Exception as e:
            print(f"Erro rename: {e}")
            
    # Comandos auxiliares para evitar erros
    def retr(self, arquivo):
        return b'', False
    def help(self):
        return b'214 Help OK.\r\n'
    def syst(self):
        return b'215 UNIX.\r\n'
    def type(self, arg):
        return b'200 OK.\r\n'