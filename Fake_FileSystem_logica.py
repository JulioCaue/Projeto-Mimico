class Logica_de_arquivos():
    def __init__(self):
        import Fake_FileSystem_dados as filesystem
        self.filesystem=filesystem.dados
        #Coloca diretorio padrão de inicio como o diretorio root
        self.diretorio_atual=self.filesystem['/']
        self.caminho_atual=['/']

    #Funciona!
    def comando_list(self):
        lista_de_arquivos=[]
        for arquivo in self.diretorio_atual:
            lista_de_arquivos.append(arquivo)
        print (''.join(lista_de_arquivos))
        lista_de_arquivos=[]
        
    #Diretorio antigo é o diretorio atual -> diretorio atual vira diretorio antigo + diretorio novo.
    def comando_cd(self,diretorio_novo):
        if diretorio_novo=="/":
            self.diretorio_atual=self.filesystem['/']
        else:
            self.caminho_atual.append(diretorio_novo)
            diretorio_antigo=self.diretorio_atual
            self.diretorio_atual=([diretorio_antigo][0][diretorio_novo])
    
    def comando_pwd(self):
        print (''.join(self.caminho_atual))

teste=Logica_de_arquivos()


#apenas testes e todo a partir daqui!!!!

#Simulando input de diretorio novo para testes
diretorio_novo='etc'
diretorio2='shadow'
#diretorio3='shadow'
teste.comando_cd(diretorio_novo)
#teste.comando_list()
teste.comando_pwd()



        #To do:
            #criar uma forma de salvar estado do filesystem(???) em multiplas instancias simultaneas.
            #pensar em como diabos fazer o mkdir
            #adicionar o pwd - mostra caminho atual ✓
            #alguma forma de adicionar cd ... ao comando

            
        #Notas:
            #Cat provavelmente não é uma boa.