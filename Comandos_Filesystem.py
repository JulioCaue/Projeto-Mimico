import socket
import os # Necessário para verificar pastas
import random
import hashlib

class Logica_de_arquivos():
    def __init__(self):
        import Pastas_filesystem as filesystem
        self.filesystem=filesystem.dados
        #Coloca diretorio padrão de inicio como o diretorio root
        self.diretorio_atual=self.filesystem['/']
        self.caminho_atual=[]
        self.retirar_comando=('')
        self.caracteres_proibidos = "'\"><,:?*/|\\"
        self.diretorio_anterior=self.filesystem['/']
        #verifica se o usuario está na pasta raiz atualmente. False se saiu de lá.

    #Lista arquivos no diretorio atual. Simples
    def list(self):
        lista_de_arquivos=[]
        for arquivo,conteudo in self.diretorio_atual.items():
            random.seed(arquivo)
            lista_de_meses=['Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            mes_aleatorio=random.choice(lista_de_meses)

            dia_aleatorio=random.randint(1, 28)
            if dia_aleatorio<10:
                dia_aleatorio=str(f'0{dia_aleatorio}')

            hora_aleatoria=(random.randint(0, 23))
            if hora_aleatoria<10:
                hora_aleatoria=str(f'0{hora_aleatoria}')
            minuto_aleatorio=random.randint(1, 59)
            if minuto_aleatorio<10:
                minuto_aleatorio=str(f'0{minuto_aleatorio}')
            hora_fake=(f'{hora_aleatoria}:{minuto_aleatorio}')

            data=(f'{mes_aleatorio} {dia_aleatorio} {hora_fake}')

            if isinstance(conteudo,dict):
                linha_formatada = f"drwxr-xr-x 1 root root 4096 {data} {arquivo}"
            else:
                tamanho=len(conteudo)
                linha_formatada = f"-rw-r--r-- 1 root root {tamanho} {data} {arquivo}"
            
            
            lista_de_arquivos.append(linha_formatada)

        if not lista_de_arquivos:
            return None
        else: return ('\r\n'.join(lista_de_arquivos))
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    #'cd ' é removido antes de fazer operações com conteudo.
    def cd(self,diretorio_novo):
        #verifica se está voltando ou avançando.
        if diretorio_novo=='..':
            if self.diretorio_atual==['/']:
                return (b'550 Directory not found.\r\n')
            else:
                self.diretorio_atual=self.filesystem['/']
                try:
                    self.caminho_atual.pop(-1)
                except:
                    return (b'550 Directory not found.\r\n')
                for pasta in self.caminho_atual:
                    self.diretorio_atual=self.diretorio_atual[pasta]
                return (b"250 Directory successfully changed.\r\n")
        
        elif diretorio_novo=='/':
            self.caminho_atual=[]
            self.diretorio_atual=self.filesystem['/']
            return (b"250 Directory successfully changed.\r\n")
            
        caminho_temp=diretorio_novo.strip('/')
        partes=caminho_temp.split('/')
        navegação_temp=self.diretorio_atual

        caminho_absoluto=diretorio_novo.startswith('/')

        if caminho_absoluto:
            navegação_temp=self.filesystem['/']

        for parte in partes:
            if parte in navegação_temp:
                conteudo=navegação_temp[parte]
                if isinstance(conteudo,dict):
                    navegação_temp=conteudo
                else:
                    return (b'550 Not a directory.\r\n')
            else:
                return (b'550 File or directory not found.\r\n')
            
        if caminho_absoluto:
            self.caminho_atual=partes
            self.diretorio_atual=navegação_temp
        
        else:
            for parte in partes:
                self.caminho_atual.append(parte)
            self.diretorio_atual=navegação_temp
        return (b"250 Directory successfully changed.\r\n")

    #Lista caminho atual
    def pwd(self):
        return ('/' + '/'.join(self.caminho_atual))

    
    #Envia arquivo ao cliente
    def retr(self, arquivo_requisitado):
        #verifica se o arquivo está na pasta. Se estiver, envia o conteudo. Se não, da erro.
        if arquivo_requisitado in self.diretorio_atual:
            conteudo_do_arquivo=self.diretorio_atual[arquivo_requisitado]
            estado_do_arquivo=True
            return conteudo_do_arquivo,estado_do_arquivo
        else:
            conteudo_do_arquivo=None
            estado_do_arquivo=False
            return conteudo_do_arquivo,estado_do_arquivo
    
    #grava arquivo no dicionario como nomes.
    def stor(self,conexao_dados,comando_recebido):
        #pega nome do virus
        nome_virus_recebido=comando_recebido

        if nome_virus_recebido in self.diretorio_atual:
            return (b'550 Requested action not taken\r\n')
        
        bytes_virus_recebido=bytearray()
        terminado=False
        
        # Cria a pasta quarentena se não existir (evita erro de FileNotFoundError)
        if not os.path.exists('quarentena'):
            os.makedirs('quarentena')

        # CORREÇÃO CRÍTICA: Timeout para evitar loop infinito
        conexao_dados.settimeout(1.0) 
        
        try:
            while terminado==False:
                try:
                    data=conexao_dados.recv(1024)
                    if not data:
                        terminado=True
                    else:
                        bytes_virus_recebido+=data
                except socket.timeout:
                    terminado=True # Sai do loop se não vier mais nada
        finally:
            conexao_dados.settimeout(None) # Remove timeout para o loop principal voltar ao normal

        with open(f'quarentena/{nome_virus_recebido}.quarentena','wb') as arquivo:
            arquivo.write(bytes_virus_recebido)
            arquivo.close()

        self.diretorio_atual[nome_virus_recebido]=bytes_virus_recebido
        return (b'226 Closing data connection. Requested file action successful.\r\n')


    #cria um diretorio novo
    def mkdir(self,nova_pasta):
        for caractere in nova_pasta:
            if caractere in self.caracteres_proibidos or caractere == (' ',''):
                return (b'553 File name not allowed.\r\n')
            
        for caractere in nova_pasta:
            if caractere in [".",'..','']:
                return (b'553 File name not allowed.\r\n')
        if nova_pasta in self.diretorio_atual:
            return (b'550 Directory already exists.\r\n')
        elif nova_pasta in self.diretorio_atual:
            return (b'550 Directory already exists.\r\n')
        else:
            #adiciona nova key (vazia) ao filesystem (AKA nova pasta).
            self.diretorio_atual[nova_pasta]={}
            return (b'257 Directory created.\r\n')


    #Envia os comandos disponiveis atualmente
    def help(self):
        return (b'''214 The following commands are recognized <* =>'s unimplemented>:
CWD      XCWD*   CDUP*   XCUP*   SMNT*   QUIT    PORT*   PASV*
EPRT*    EPSV*   ALLO*   RNFR*   RNTO*   DELE*   MDTM*   RMD*
XRMD*    MKD     XMKD*   PWD     XPWD*   SIZE*   SYST    HELP
NOOP*    FEAT*   OPTS*   AUTH*   CCC*    CONF*   ENC*    MIC*
APPE*    REST*   ABOR*   STRU*   MODE*   RETR    STOR    STOU*
LIST     NLIST*  STAT*   SITE*   TYPE\r\n''')
    

    def syst(self):
        return (b'215 UNKNOWN Type: L8\r\n')
    
    def type(self,comando_recebido):
        return (f'200 Type set to {comando_recebido}\r\n')
    
    def pegar_data_arquivo(self,nome_virus_recebido):
        tamanho_do_virus=os.path.getsize(f'quarentena/{nome_virus_recebido}')
        tamanho_do_virus=(tamanho_do_virus/1048576)
        tamanho_do_virus=f'{tamanho_do_virus:.2f}'
        return tamanho_do_virus

    def pegar_hash_virus(self,nome_virus_recebido,algorithm="sha256"):
        try:
            with open(f'quarentena/{nome_virus_recebido}.quarentena', "rb") as f:
                digest = hashlib.file_digest(f, algorithm)
            return digest.hexdigest()
        except FileNotFoundError:
            return "Error: File not found"
        except ValueError as e:
            return (f"Error: {e}")