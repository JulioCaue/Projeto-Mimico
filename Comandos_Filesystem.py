import socket
import os
import random
import hashlib
import Pastas_filesystem as filesystem

class LogicaArquivos:  # CORREÇÃO: Nome da classe em PascalCase
    def __init__(self):
        self.filesystem = filesystem.dados
        self.diretorio_atual = self.filesystem['/']
        self.caminho_atual = []
        self.nome_temporario_arquivo = 'nome_temporario'
        
        # Garante que a pasta existe na inicialização
        if not os.path.exists('quarentena'):
            os.makedirs('quarentena')

    def list(self):
        lista_de_arquivos = []
        for arquivo, conteudo in self.diretorio_atual.items():
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

        if not lista_de_arquivos: return None
        return '\r\n'.join(lista_de_arquivos)

    def cd(self, diretorio_novo):
        if diretorio_novo == '..':
            if not self.caminho_atual: return b'250 OK\r\n'
            self.caminho_atual.pop()
            self.diretorio_atual = self.filesystem['/']
            for pasta in self.caminho_atual:
                self.diretorio_atual = self.diretorio_atual[pasta]
            return b"250 Directory changed.\r\n"
        
        elif diretorio_novo == '/':
            self.caminho_atual = []
            self.diretorio_atual = self.filesystem['/']
            return b"250 Directory changed.\r\n"

        partes = diretorio_novo.strip('/').split('/')
        temp_dir = self.diretorio_atual
        
        try:
            for parte in partes:
                if not parte: continue
                if parte in temp_dir and isinstance(temp_dir[parte], dict):
                    temp_dir = temp_dir[parte]
                else:
                    return b'550 Not a directory.\r\n'
            
            self.diretorio_atual = temp_dir
            for parte in partes:
                if parte: self.caminho_atual.append(parte)
            return b"250 Directory changed.\r\n"
        except:
             return b'550 Not a directory.\r\n'

    def pwd(self):
        path = '/' + '/'.join(self.caminho_atual)
        if len(path) > 1 and path.endswith('/'): path = path[:-1]
        return path

    def stor(self, conexao_dados, nome_arquivo):
        # Reforço de segurança para garantir pasta
        if not os.path.exists('quarentena'):
            os.makedirs('quarentena')

        conexao_dados.settimeout(10.0) # Timeout maior para garantir recebimento
        caminho_temp = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
        
        try:
            with open(caminho_temp, 'wb') as f:
                bytes_recebidos = 0
                while True:
                    try:
                        data = conexao_dados.recv(4096)
                        if not data: break
                        f.write(data)
                        bytes_recebidos += len(data)
                    except socket.timeout:
                        break
            
            print(f"[DEBUG] STOR: Recebidos {bytes_recebidos} bytes.")
            self.diretorio_atual[nome_arquivo] = b'FAKE_CONTENT'
            return b'226 Transfer complete.\r\n'
            
        except Exception as e:
            print(f"[!] Erro ao gravar arquivo em disco: {e}")
            return b'451 Error writing file.\r\n'

    def mkdir(self, pasta):
        if pasta not in self.diretorio_atual:
            self.diretorio_atual[pasta] = {}
            return b'257 Directory created.\r\n'
        return b'550 Directory exists.\r\n'
    
    def pegar_hash_arquivo_temporario(self):
        try:
            sha256 = hashlib.sha256()
            path = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
            if not os.path.exists(path): return None # Retorna None explícito se falhar
            
            with open(path, "rb") as f:
                while chunk := f.read(4096):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return None

    def pegar_tamanho_arquivo(self, hash_do_arquivo):
        try:
            path = f'quarentena/{hash_do_arquivo}.quarentena'
            if not os.path.exists(path): return 0
            return os.path.getsize(path)
        except:
            return 0

    def renomear_arquivo_final(self, hash_final):
        try:
            old = f'quarentena/{self.nome_temporario_arquivo}.quarentena'
            new = f'quarentena/{hash_final}.quarentena'
            
            if not os.path.exists(old): return False
            
            if os.path.exists(new): os.remove(new) # Remove duplicata se já existir
            os.rename(old, new)
            return True
        except Exception as e:
            print(f"Erro rename: {e}")
            return False
            
    def retr(self, arquivo): return b'', False
    def help(self): return b'214 Help OK.\r\n'
    def syst(self): return b'215 UNIX.\r\n'
    def type(self, arg): return b'200 OK.\r\n'