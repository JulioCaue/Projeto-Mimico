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
        print (' '.join(lista_de_arquivos))
        lista_de_arquivos=[]
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    #'cd ' é removido antes de fazer operações com conteudo.
    def comando_cd(self,diretorio_novo):
        comando_separado=diretorio_novo.split()
        if len(comando_separado) < 2:
            return

        diretorio_do_comando=comando_separado[1:]
        diretorio_novo=''.join(diretorio_do_comando)

        if diretorio_novo == '..':
            if not self.caminho_atual:
                print ('erro')
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
                print('erro: é arquivo')
        else:
            print('erro: não existe')

    #Lista caminho atual
    def comando_pwd(self):
        print ('/' + '/'.join(self.caminho_atual))


teste=Logica_de_arquivos()








#apenas testes e todo a partir daqui!!!!

#Simulando input de diretorio novo para testes
'''diretorio_novo='etc'
diretorio2='shadow'''

while True:
    diretorio_novo=input('comando aqui: ')
    teste.comando_cd(diretorio_novo)
    teste.comando_list()


#diretorio3='shadow'
teste.comando_cd(diretorio_novo)
#teste.comando_list()
teste.comando_pwd()



        #To do:
            #criar uma forma de salvar estado do filesystem(???) em multiplas instancias simultaneas.
                #talvez irrelevante nesse arquivo. Deixar aqui por enquanto para se lembrar
            
            #fazer o mkdir (make directory) (cria pasta)
            
            #alguma forma de adicionar cd .. ao comando cd
                #Talvez criar uma nova função para esse comando seja melhor?
            
            #adicionar o retr (retrieve) (envia conteudo ao hacker)
            #adicionar o stor (store) (recebe conteudo do hacker)

            
        #Notas:
            #Cat provavelmente não é uma boa.