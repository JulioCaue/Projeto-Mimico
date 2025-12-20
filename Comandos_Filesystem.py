import socket
import os # Necessário para verificar pastas

class Logica_de_arquivos():
    def __init__(self):
        import Pastas_filesystem as filesystem
        self.filesystem=filesystem.dados
        #Coloca diretorio padrão de inicio como o diretorio root
        self.diretorio_atual=self.filesystem['/']
        self.caminho_atual=[]
        self.retirar_comando=('')
        self.caracteres_proibidos = "'\"><,:?*/|\\"

    #Lista arquivos no diretorio atual. Simples
    def list(self):
        lista_de_arquivos=[]
        for arquivo in self.diretorio_atual:
            lista_de_arquivos.append(arquivo)
        if not lista_de_arquivos:
            return None
        else: return (' '.join(lista_de_arquivos))
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    #'cd ' é removido antes de fazer operações com conteudo.
    def cd(self,diretorio_novo):
        #verifica se está voltando ou avançando.
        if diretorio_novo == '..':
            #volta para pasta anterior
            if not self.caminho_atual:
                return (b'erro')
            else:
                self.caminho_atual.pop()
                self.diretorio_atual=self.filesystem['/']
                for pasta in self.caminho_atual:
                    self.diretorio_atual=self.diretorio_atual[pasta]
                return (b"250 Directory successfully changed.\r\n")

        #avança para a proxima pasta se for uma pasta e não arquivo
        elif diretorio_novo in self.diretorio_atual:
            conteudo = self.diretorio_atual[diretorio_novo]
            if isinstance(conteudo, dict):
                self.diretorio_atual=conteudo
                self.caminho_atual.append(diretorio_novo)
                return (b"250 Directory successfully changed.\r\n")
            else:
                return (b'550 Not a directory.\r\n')
        else:
            return (b'550 File or directory not found.\r\n')

    #Lista caminho atual
    def pwd(self):
        return ('/' + '/'.join(self.caminho_atual))

    
    #Envia arquivo ao cliente
    def retr(self, arquivo_requisitado):
        #verifica se o arquivo está na pasta. Se estiver, envia o conteudo. Se não, da erro.
        if arquivo_requisitado in self.diretorio_atual:
            conteudo_do_arquivo=self.diretorio_atual[arquivo_requisitado]
            if isinstance(conteudo_do_arquivo,dict):
                return (b'550 File or directory not found.\r\n')
            else:
                return conteudo_do_arquivo
        else:
            return (b'550 File or directory not found.\r\n')
    
    #grava arquivo no dicionario como nomes.
    def stor(self,socket_comunicação,comando_recebido):
        #pega nome do virus
        nome_virus_recebido=comando_recebido

        if nome_virus_recebido in self.diretorio_atual:
            return (b'550 Requested action not taken')
        
        bytes_virus_recebido=bytearray()
        terminado=False
        
        # Cria a pasta quarentena se não existir (evita erro de FileNotFoundError)
        if not os.path.exists('quarentena'):
            os.makedirs('quarentena')

        # CORREÇÃO CRÍTICA: Timeout para evitar loop infinito
        socket_comunicação.settimeout(1.0) 
        
        try:
            while terminado==False:
                try:
                    data=socket_comunicação.recv(1024)
                    if not data:
                        terminado=True
                    else:
                        bytes_virus_recebido+=data
                except socket.timeout:
                    terminado=True # Sai do loop se não vier mais nada
        finally:
            socket_comunicação.settimeout(None) # Remove timeout para o loop principal voltar ao normal

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
        elif not nova_pasta:
            #adiciona nova key (vazia) ao filesystem (AKA nova pasta).
            self.diretorio_atual[nova_pasta]={}
            return (b'257 Directory created.\r\n')