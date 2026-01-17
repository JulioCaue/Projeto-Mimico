# SISTEMA DE ARQUIVOS OTIMIZADO PARA CAPTURA DE MALWARE (HIGH INTERACTION SIMULATION)
# Estrutura focada em: LAMP Stack (Linux, Apache, MySQL, PHP), WordPress e Diretórios Temporários.

dados = {
    "/": {
        "bin": {
            "bash": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "ls": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "cp": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "sh": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "cat": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "curl": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "wget": b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        },

        "etc": {
            "passwd": """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
minecraft:x:1000:1000:Minecraft Server:/opt/minecraft:/bin/bash
deploy:x:1001:1001:Deploy User:/home/deploy:/bin/bash
""",
            "shadow": """root:$6$hJ8.kL9$W/qF9k8Zpy9WdQWJ2z0P9qErF3Z2GiqV05zUptw7B1S3y00jIFy:18982:0:99999:7:::
www-data:*:18982:0:99999:7:::
minecraft:$6$Kl9.mN2$z7R2rH1kLn38TtqkA2zU9pA4qD0kRmU5R:18982:0:99999:7:::
deploy:$6$Ab3.xY1$k4gL3zJ1abFQ0vC9pgm7XGzcW4z3CwrlAt:18982:0:99999:7:::
""",
            "hosts": """127.0.0.1 localhost
127.0.1.1 prod-server-01
""",
            "hostname": "prod-server-01\n",
            "issue": "Ubuntu 22.04.3 LTS \\n \\l\n",
            "ssh": {
                "sshd_config": """Port 22
PermitRootLogin prohibit-password
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
"""
            }
        },

        "var": {
            # --- ISCA PRINCIPAL: SERVIDOR WEB ---
            "www": {
                "html": {
                    # Arquivos falsos de WordPress para atrair bots de plugins
                    "index.php": b"<?php // Silence is golden. ?>",
                    "xmlrpc.php": b"<?php // XML-RPC API ?>",
                    "wp-config.php": """<?php
define( 'DB_NAME', 'wp_production' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'Store#2024!Secure' );
define( 'DB_HOST', 'localhost' );
$table_prefix = 'wp_';
define( 'WP_DEBUG', false );
?>""",
                    "wp-content": {
                        "plugins": {
                            "contact-form-7": {},
                            "woocommerce": {},
                            "elementor": {}
                        },
                        "themes": {
                            "twentytwentythree": {},
                            "astra": {}
                        },
                        # AQUI É ONDE O BOT VAI TENTAR ESCREVER O MALWARE
                        # Um dicionário vazio indica uma pasta vazia pronta para receber arquivos
                        "uploads": {
                            "2024": {},
                            "2025": {},
                            "cache": {}
                        },
                        "cache": {
                            "w3-total-cache": {}
                        }
                    },
                    "wp-admin": {
                        "admin-ajax.php": b"<?php ... ?>",
                        "css": {},
                        "js": {}
                    },
                    "wp-includes": {
                        "version.php": b"<?php $wp_version = '6.4.2'; ?>"
                    }
                }
            },
            
            # --- ISCA SECUNDÁRIA: LOGS E BACKUPS ---
            "log": {
                "syslog": "Mar 10 06:25:01 prod-server-01 CRON[1234]: (root) CMD (cd / && run-parts --report /etc/cron.hourly)\n",
                "auth.log": "Mar 10 12:00:01 prod-server-01 sshd[5555]: Failed password for invalid user admin from 192.168.1.50 port 4422\n",
                "apache2": {
                    "access.log": '10.0.0.5 - - [10/Mar/2025:06:25:01 +0000] "GET /wp-login.php HTTP/1.1" 200 4521\n',
                    "error.log": '[Mon Mar 10 06:25:01 2025] [error] [client 10.0.0.5] File does not exist: /var/www/html/favicon.ico\n'
                }
            },
            "backups": {
                "db_backup_2024.sql.gz": b"\x1f\x8b\x08\x00\x00\x00\x00\x00",
                "site_backup.tar.gz": b"\x1f\x8b\x08\x00\x00\x00\x00\x00"
            },
            
            # --- TERRENO FÉRTIL PARA MINERADORES ---
            "tmp": {
                # Pastas temporárias comuns que bots usam para compilar código
                ".X11-unix": {},
                ".ICE-unix": {},
                "systemd-private-xyz": {},
                "php-sessions": {}
            }
        },

        "tmp": {
            # O diretório /tmp na raiz é o lugar favorito para baixar scripts (wget)
            "vmware-root": {},
            "snap.lxd": {},
            ".XIM-unix": {}
        },

        "home": {
            "deploy": {
                ".ssh": {
                    "authorized_keys": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...",
                    "id_rsa": """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEHs...
-----END OPENSSH PRIVATE KEY-----
"""
                },
                "scripts": {
                    "deploy.sh": "#!/bin/bash\ngit pull origin main\nservice apache2 reload",
                    ".env": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                }
            },
            "minecraft": {
                "server": {
                    "server.properties": "server-port=25565\ngamemode=survival\n",
                    "eula.txt": "eula=true\n",
                    "logs": {
                        "latest.log": "[10:00:00] [Server thread/INFO]: Starting minecraft server version 1.20.1\n"
                    }
                }
            }
        },

        "usr": {
            "bin": {
                "perl": b"\x7fELF...",
                "python": b"\x7fELF...",
                "python3": b"\x7fELF...",
                "gcc": b"\x7fELF...",
                "make": b"\x7fELF..."
            },
            "local": {
                "bin": {}
            }
        },

        "proc": {
            "cpuinfo": """processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 85
model name	: Intel(R) Xeon(R) CPU @ 2.20GHz
stepping	: 7
microcode	: 0x5003003
cpu MHz		: 2200.000
cache size	: 39424 KB
physical id	: 0
siblings	: 2
core id		: 0
cpu cores	: 1
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
""",
            "meminfo": """MemTotal:        8174532 kB
MemFree:         1024320 kB
MemAvailable:    6543210 kB
Buffers:          123456 kB
Cached:          2345678 kB
"""
        },

        "root": {
            ".bash_history": "ls -la\ncd /var/www/html\nnano wp-config.php\nservice apache2 restart\n",
            ".ssh": {
                "authorized_keys": "ssh-rsa AAAAB3Nza..."
            }
        }
    }
}