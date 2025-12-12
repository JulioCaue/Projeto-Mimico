class Logica_de_arquivos():
    def __init__(self):
        import Pastas_filesystem as filesystem
        self.filesystem=filesystem.dados
        #Coloca diretorio padrão de inicio como o diretorio root
        self.diretorio_atual=self.filesystem['/']
        self.caminho_atual=['/']
        self.retirar_comando=('')

    #Lista arquivos no diretorio atual. Simples
    def comando_list(self):
        lista_de_arquivos=[]
        for arquivo in self.diretorio_atual:
            lista_de_arquivos.append(arquivo)
        print (' '.join(lista_de_arquivos))
        lista_de_arquivos=[]
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    def comando_cd(self,diretorio_novo):
        comando_separado=diretorio_novo.split()
        diretorio_do_comando=comando_separado[1:]
        diretorio_novo=''.join(diretorio_do_comando)

        if diretorio_novo=="/":
            self.diretorio_atual=self.filesystem['/']
            self.caminho_atual=[]
        elif diretorio_novo.endswith('..'):
            del self.caminho_atual[-1]
        else:
            if self.caminho_atual==['/']:
                self.caminho_atual.append(diretorio_novo)
            else:
                self.caminho_atual.append('/'+diretorio_novo)
            diretorio_antigo=self.diretorio_atual
            self.diretorio_atual=([diretorio_antigo][0][diretorio_novo])
    
    #Lista caminho atual
    def comando_pwd(self):
        print (''.join(self.caminho_atual))

teste=Logica_de_arquivos()








#apenas testes e todo a partir daqui!!!!

#Simulando input de diretorio novo para testes
'''diretorio_novo='etc'
diretorio2='shadow'''

while True:
    diretorio_novo=input('comando aqui: ')
    if diretorio_novo=='1':
        break
    else:
        teste.comando_cd(diretorio_novo)
        teste.comando_list()


#diretorio3='shadow'
teste.comando_cd(diretorio_novo)
#teste.comando_list()
teste.comando_pwd()



        #To do:
            #criar uma forma de salvar estado do filesystem(???) em multiplas instancias simultaneas.
            #pensar em como diabos fazer o mkdir
            #alguma forma de adicionar cd ... ao comando
                #Talvez criar uma nova função para esse comando seja melhor?

            
        #Notas:
            #Cat provavelmente não é uma boa.