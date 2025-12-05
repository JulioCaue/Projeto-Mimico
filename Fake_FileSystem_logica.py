class Logica_de_arquivos():
    def __init__(self):
        import Fake_FileSystem_dados as filesystem
        self.filesystem=filesystem.dados
        self.diretorio_atual=self.filesystem['/']

    def comando_list(self):
        lista_de_arquivos=[]
        for arquivos in self.diretorio_atual:
            lista_de_arquivos.append(arquivos)
        print (' '.join(lista_de_arquivos))
        lista_de_arquivos=[]


teste=Logica_de_arquivos()

teste.comando_list()