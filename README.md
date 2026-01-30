# MIMICO // FTP Honeypot Monitor

[ Ler em Português ](README.pt-br.md)

### Project Status
Functional / Prototype

### Description
Mimico is a medium-interaction Honeypot developed in Python. It emulates a vulnerable FTP server to capture, log, and analyze intrusion attempts.

Unlike simple port listeners (low interaction), Mimico simulates a complete virtual file system (Fake FS), allowing attackers to navigate directories, upload files, and execute commands. All activity is contained within the Python environment, isolated from the host operating system.

### Frontend and API Status
The Web Dashboard is in a transition phase. While the visual interface (HTML/CSS/JS) is a legacy version designed for the initial prototype, the Backend has been entirely refactored by to a modern FastAPI architecture.

### Key Features

**Backend & Core**
* **Custom FTP Protocol:** Server implementation using raw `socket` libraries and threading. No external FTP frameworks were used.
* **Virtual File System:** Emulates a Linux directory structure (/var, /etc, /home) using Python dictionaries. Attackers interact with fake data, ensuring the real OS remains untouched.
* **Concurrency Control:** Uses `threading.Lock` and a dedicated database manager to handle multiple simultaneous connections and SQLite writes without race conditions.
* **Malware Quarantine:** Intercepts `STOR` commands. Uploaded files are hashed (SHA-256), renamed, and safely isolated in a quarantine folder.
* **Threat Intelligence:** Automatic integration with VirusTotal API to scan captured payloads.

### Architecture

The project is structured into modular components:

1.  **honeypot.py:** The main server loop. Handles TCP connections, manages thread pools, and routes raw data to the command parsers.
2.  **gerenciar_banco_de_dados.py:** Centralizes all database operations (CRUD). Implements locking mechanisms to ensure thread safety during high-traffic attacks.
3.  **Comandos_Filesystem.py:** The logic engine that interprets FTP commands (CWD, LIST, RETR) and manipulates the virtual state.
4.  **Pastas_filesystem.py:** A static dictionary defining the fake file tree (Linux emulation).
5.  **site_backend.py:** A Flask server that exposes the SQLite data via JSON APIs for the dashboard.

### Security Warning
**READ BEFORE RUNNING:**
This software is designed to be attacked.
1.  **Isolation:** Ideally, run this in a Virtual Machine (VM) or a dedicated container.
2.  **Network Risk:** Exposing port 21 to the internet *will* attract real malware and automated botnets. Ensure you understand your network configuration before port forwarding.

### Setup & Usage (Localhost Testing)

To test the project safely without exposing your network:

1.  **Clone the repository:**
    `git clone https://github.com/JulioCaue/Projeto-Mimico.git`

2.  **Install dependencies:**
    `pip install -r requirements.txt`

3.  **Configuration (.env):**
    Create a `.env` file in the root directory. For safe local testing, set the IP to localhost:
    ```env
    HOST_PUBLIC_IP=127.0.0.1
    virus_total=YOUR_API_KEY_HERE
    ```

4.  **Run the Honeypot (Server):**
    `python honeypot.py`
    *Note: If you receive a "Permission denied" error, use `sudo` (Linux) or Run as Administrator (Windows) to bind port 21, or change the port in the code.*

5.  **Run the Dashboard (Visualizer):**
    `python site_backend.py`
    Access at: `http://localhost:5000`

6.  **Simulate an Attack:**
    Open a separate terminal or an FTP client (like FileZilla) and connect:
    `ftp 127.0.0.1`
