# MIMICO // Monitor de Honeypot FTP

[ Read in English ](README.md)

### Status do Projeto
Funcional / Protótipo

### Descrição
O Mimico é um Honeypot de média interatividade desenvolvido em Python. Ele emula um servidor FTP vulnerável para capturar, registrar e analisar tentativas de intrusão.

Diferente de listeners simples (baixa interatividade), o Mimico simula um sistema de arquivos virtual completo (Fake FS), permitindo que atacantes naveguem por diretórios, enviem arquivos e executem comandos. Toda a atividade é contida dentro do ambiente Python, isolada do sistema operacional real.

### Status do Frontend e API
O Dashboard Web está em fase de transição. Enquanto a interface visual (HTML/CSS/JS) é uma versão legada do protótipo inicial, o Backend foi integralmente refatorado para uma arquitetura moderna em FastAPI. Por esse motivo, a visualização do Dashboard não está disponível no momento.

### Funcionalidades Principais

**Backend e Core**
* **Protocolo FTP Customizado:** Implementação do servidor usando bibliotecas `socket` puras e threading. Nenhum framework FTP externo foi utilizado.
* **Sistema de Arquivos Virtual:** Emula uma estrutura de diretórios Linux (/var, /etc, /home) usando dicionários Python. O atacante interage com dados falsos, garantindo a integridade do OS real.
* **Controle de Concorrência:** Utiliza `threading.Lock` e um gerenciador de banco de dados dedicado para lidar com múltiplas conexões simultâneas e escritas no SQLite sem condições de corrida (race conditions).
* **Quarentena de Malware:** Intercepta comandos `STOR`. Arquivos enviados são processados via Hash (SHA-256), renomeados e isolados com segurança na pasta de quarentena.
* **Inteligência de Ameaças:** Integração automática com a API do VirusTotal para escanear payloads capturados.

### Arquitetura

O projeto é estruturado em componentes modulares:

1.  **honeypot.py:** O loop principal do servidor. Gerencia conexões TCP, administra as threads e roteia dados brutos para os interpretadores de comando.
2.  **gerenciar_banco_de_dados.py:** Centraliza todas as operações de banco de dados (CRUD). Implementa mecanismos de trava (locks) para garantir a segurança das threads durante ataques de alto tráfego.
3.  **Comandos_Filesystem.py:** O motor lógico que interpreta comandos FTP (CWD, LIST, RETR) e manipula o estado virtual.
4.  **Pastas_filesystem.py:** Um dicionário estático que define a árvore de arquivos falsa (emulação Linux).
5.  **site_backend.py:** Servidor Flask que expõe os dados do SQLite via APIs JSON para o dashboard.

### Aviso de Segurança
**LEIA ANTES DE EXECUTAR:**
Este software foi projetado para ser atacado.
1.  **Isolamento:** Idealmente, execute este projeto em uma Máquina Virtual (VM) ou container dedicado.
2.  **Risco de Rede:** Expor a porta 21 para a internet *irá* atrair malwares reais e botnets. Certifique-se de entender a configuração da sua rede antes de realizar redirecionamento de portas (port forwarding).

### Instalação e Uso (Teste Local)

Para testar o projeto com segurança sem expor sua rede:

1.  **Clone o repositório:**
    `git clone https://github.com/JulioCaue/Projeto-Mimico.git`

2.  **Instale as dependências:**
    `pip install -r requirements.txt`

3.  **Configuração (.env):**
    Crie um arquivo `.env` na raiz do projeto. Para testes locais seguros, defina o IP como localhost:
    ```env
    HOST_PUBLIC_IP=127.0.0.1
    virus_total=SUA_API_KEY_AQUI
    app_porta=SUA_PORTA_DESEJADA_AQUI
    ```

4.  **Execute o Honeypot (Servidor):**
    `python honeypot.py`
    *Nota: Se receber erro de permissão, use `sudo` (Linux) ou execute como Administrador (Windows) para liberar a porta 21, ou altere a porta no código.*

5.  **Execute o Dashboard (Visualizador):**
    `python site_backend.py`
    Acesse em: `http://localhost:5000`

6.  **Simule um Ataque:**
    Abra um terminal separado ou um cliente FTP (como FileZilla) e conecte-se:
    `ftp 127.0.0.1`
