class Logica_de_arquivos():
    def __init__(self):
        import Pastas_filesystem as filesystem
        self.filesystem=filesystem.dados
        #Coloca diretorio padrão de inicio como o diretorio root
        self.diretorio_atual=self.filesystem['/']
        self.caminho_atual=[]
        self.retirar_comando=('')

    #Lista arquivos no diretorio atual. Simples
    def comando_list(self):
        lista_de_arquivos=[]
        for arquivo in self.diretorio_atual:
            lista_de_arquivos.append(arquivo)
        return (' '.join(lista_de_arquivos))
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    #'cd ' é removido antes de fazer operações com conteudo.
    def comando_cd(self,diretorio_novo):
        comando_separado=diretorio_novo.split()
        if len(comando_separado) < 2:
            return

        diretorio_do_comando=comando_separado[1:]
        diretorio_novo=' '.join(diretorio_do_comando)

        if diretorio_novo == '..':
            if not self.caminho_atual:
                return ('erro')
            else:
                self.caminho_atual.pop()
                self.diretorio_atual=self.filesystem['/']
                for pasta in self.caminho_atual:
                    self.diretorio_atual=self.diretorio_atual[pasta]

        elif diretorio_novo in self.diretorio_atual:
            conteudo = self.diretorio_atual[diretorio_novo]
            if isinstance(conteudo, dict):
                self.diretorio_atual=conteudo
                self.caminho_atual.append(diretorio_novo)
            else:
                print ('erro: é arquivo')
        else:
            return ('erro: não existe')

    #Lista caminho atual
    def comando_pwd(self):
        return ('/' + '/'.join(self.caminho_atual))

    
    #Envia arquivo ao cliente
    def comando_RETR(self, arquivo_requisitado):
        #retira o RETR do comando
        comando_separado=arquivo_requisitado.split('',1)
        if len(comando_separado) < 2:
            return ('erro: falta nome do arquivo')
        arquivo_do_comando=comando_separado[1:]
        arquivo_requisitado=''.join(arquivo_do_comando)

        #verifica se o arquivo está na pasta. Se estiver, envia o conteudo. Se não, da erro.
        if arquivo_requisitado in self.diretorio_atual:
            conteudo_do_arquivo=self.diretorio_atual[arquivo_requisitado]
            if isinstance(conteudo_do_arquivo,dict):
                return ('erro: Não é arquivo')
            else:
                return conteudo_do_arquivo
        else:
            return ('erro: arquivo não encontrado.')
    

    def logica_comando_STOR(self,nome_virus_recebido,bytes_virus_recebido):
        self.diretorio_atual[nome_virus_recebido]=bytes_virus_recebido
        pass




    #cria um diretorio novo (vazio)
    def comando_mkdir(self,nome_pasta_nova):
        comando_separado=nome_pasta_nova.split()

        nome_pasta_nova=comando_separado[1:]
        nova_pasta=' '.join(nome_pasta_nova)
        self.diretorio_atual[nova_pasta]={}








#apenas testes e todo a partir daqui!!!!

#Simulando input de diretorio novo para testes
'''diretorio_novo='etc'
diretorio2='shadow'''

teste=Logica_de_arquivos()

while True:
    teste.comando_list()
    diretorio_novo=input('comando aqui: ')
    if diretorio_novo.startswith('mkdir'):
        nome_pasta_nova=diretorio_novo
        teste.comando_mkdir(nome_pasta_nova)
    else:
        teste.comando_cd(diretorio_novo)
    print (teste.comando_list())


#diretorio3='shadow'
teste.comando_cd(diretorio_novo)
#teste.comando_list()
teste.comando_pwd()



        #To do:
            #criar uma forma de salvar estado do filesystem(???) em multiplas instancias simultaneas.
                #talvez irrelevante nesse arquivo. Deixar aqui por enquanto para se lembrar
                #parece que não vai ser um problema, e isso já funciona. Terei que ver no teste real.
            
            #adicionar o stor (store) 
                # (recebe conteudo do hacker [trabalho do arquivo principal],
                # grava nome e bytes em uma chave no dicionario)

            
        #Notas:
            #Cat provavelmente não é uma boa.