dados = {
    "/": {
        "bin": {
            "bash": b"\x7fELF...\x00\x02\x01",
            "ls": b"\x7fELF...\xaa\x10\x91",
            "cp": b"\x7fELF...\x32\x88\x23",
            "mv": b"\x7fELF...\x44\x55\x66",
            "cat": b"\x7fELF...\x99\x77\x11",
            "grep": b"\x7fELF...\x21\x43\x65",
            "chmod": b"\x7fELF...\x13\x57\x9b"
        },

        "etc": {
"passwd": """root:x:0:0:root:/root:/bin/bash
ftp:x:1001:1001:FTP Service:/srv/ftp:/bin/false
backup:x:1002:1002:Backup Automation:/home/backup:/bin/bash
deploy:x:1003:1003:Deployment Service:/home/deploy:/bin/bash
j.smith:x:1101:1101:James Smith:/home/j.smith:/bin/bash
m.keller:x:1102:1101:Maria Keller:/home/m.keller:/bin/bash
t.murphy:x:1103:1102:Thomas Murphy:/home/t.murphy:/bin/bash
a.stevens:x:1104:1102:Alicia Stevens:/home/a.stevens:/bin/bash
devops:x:1201:2001:DevOps Automation:/srv/devops:/bin/bash
secscan:x:1202:2002:Security Scanner:/srv/secscan:/bin/bash
audit:x:1203:2003:Audit Daemon:/srv/audit:/bin/bash
itsupport:x:1301:3001:IT Support Bot:/srv/itsupport:/bin/false
""",

            "shadow": """root:$6$gQ1u4bFv$Xqf9k8Zpy9WdQWJ2z0P9qErF3Z2GiqV05zUptw7B1S3y00jIFy:w:19874:0:99999:7:::
ftp:*:19876:0:99999:7:::
backup:$6$Dk91UsQx$JL0Zq3p8nqMxYt4S/7WamkYzY6kZCwPzA9KePuJlldf2A6mQW.:19890:0:99999:7:::
deploy:$6$B91vz9GQ$k4gL3zJ1abFQ0vC9pgm7XGzcW4z3CwrlAt:S:19901:0:99999:7:::
j.smith:$6$M2qW4rG1$v91PzeKp12wzTtCzF6nPq1e2Ue5UwgG93pLq:19911:0:99999:7:::
m.keller:$6$Hp9bC7Fv$z7R2rH1kLn38TtqkA2zU9pA4qD0kRmU5R:s:19902:0:99999:7:::
t.murphy:$6$Zt0FeQv9$A0K9qN1pD13bWqE7z91MjQ0n2X9kAqK4QwN:19883:0:99999:7:::
a.stevens:$6$Pk13wD8s$hR9bP3UuQ1p9CzG7h2L3zv0Q8aRnS5xXQe:q:19895:0:99999:7:::
devops:$6$D0rv9GfT$U1XcP3oVsU19xB3lP3KtQn4Ew8eGf4KzL2y:19870:0:99999:7:::
secscan:$6$S21zCv8J$ha8G1zE0Ny5Uq1JkP1aB0cK7mU2wFePzE6n:19870:0:99999:7:::
audit:$6$Tt9LwA21$Kz1pF0eQc9YjW3uD82NfS4nG1hMqC7eQ3K0:19920:0:99999:7:::
itsupport:*:19876:0:99999:7:::
""",

            "hosts": """127.0.0.1   localhost
10.55.23.18 ftp.corpnet.internal ftp-server
10.55.23.20 ldap.corpnet.internal
10.55.23.25 updates.corpnet.internal
""",

            "motd": """Corporate File Transfer Node
All access is monitored and logged.
""",

            "security": {
                "policies.conf": """password_length=12
max_login_attempts=6
2fa_required=yes
audit_rotate_days=30
""",
                "enforce_list.txt": """j.smith
m.keller
devops
audit
"""
            },

            "ftp.conf": """listen=YES
anonymous_enable=NO
local_enable=YES
write_enable=YES
secure_chroot_dir=/var/secure
chroot_local_user=YES
idle_session_timeout=600
pam_service_name=vsftpd
""",
        },

        "srv": {
            "corp_data": {
                "finance": {
                    "reports": {
                        "audit_Q1_2025.xlsx": b"\x50\x4B\x03\x04...",
                        "revenue_breakdown_2024.pdf": b"%PDF-1.4...",
                    },
                    "budgets": {
                        "internal_budget_2025.txt": """Department Budgets 2025
-----------------------
Infrastructure: +12%
Security: +30%
R&D: +22%
Marketing: +5%
""",
                    }
                },
                "engineering": {
                    "designs": {
                        "system_arch_v3.png": b"\x89PNG\r\n\x1a\n...",
                        "api_flowchart.vsdx": b"\x50\x4B\x03\x04..."
                    },
                    "docs": {
                        "internal_api_guide.md": """# API Guide
Endpoints:
 - /auth/token
 - /data/push
 - /deploy/request
"""
                    }
                },
                "legal": {
                    "contracts": {
                        "nda_template.pdf": b"%PDF-1.7...",
                        "client_agreement_2024.pdf": b"%PDF-1.7..."
                    }
                }
            },

            "ftp": {
                "banners": {
                    "login.txt": "Corporate FTP Node - Authorized Personnel Only\n"
                },
                "sessions": {
                    "active.json": """{
    "current_sessions": [
        {"user": "j.smith", "ip": "10.55.34.11", "since": "2025-12-04T09:21:00"},
        {"user": "devops", "ip": "10.55.22.88", "since": "2025-12-04T09:50:00"},
        {"user": "backup", "ip": "10.55.20.33", "since": "2025-12-04T08:00:00"}
    ]
}"""
                }
            }
        },

        "var": {
            "log": {
                "auth.log": """Dec 04 08:02:11 ftp-server sshd[9281]: Accepted password for backup from 10.55.20.33 port 42214
Dec 04 08:11:55 ftp-server sshd[9341]: Failed password for unknown user 'sysadmin' from 185.212.18.90 port 51233
Dec 04 08:12:01 ftp-server sshd[9341]: Connection closed by 185.212.18.90
Dec 04 09:51:14 ftp-server sshd[10411]: Accepted password for devops from 10.55.22.88 port 44110
""",
                "ftp.log": """[INFO] 08:15 - User 'backup' downloaded /srv/corp_data/finance/reports/audit_Q1_2025.xlsx
[WARN] 09:33 - Repeated login failures from 185.212.18.90
[INFO] 09:52 - User 'devops' uploaded /srv/devops/deploy_queue/task_559.json
""",
                "audit.log": """[AUDIT] Unauthorized directory scan attempt detected (10.55.34.11).
Rule triggered: CORP-DIR-SCAN-002
"""
            },

            "secure": {
                "access_tokens": {
                    "cache.db": b"\xB1\x99\x03\x20...",
                },
                "reports": {
                    "security_status_2025-12-01.txt": """Security Status - Dec 2025
 - Vulnerability scans clean
 - Suspicious IP flagged: 185.212.18.90
"""
                }
            },

            "backups": {
                "daily": {
                    "etc_backup_2025-12-01.tar.gz": b"\x1f\x8b\x08\x00...",
                    "userdb_2025-12-01.sql": """-- Daily User DB Backup
INSERT INTO corp_users VALUES (...);
"""
                },
                "monthly": {
                    "snapshot_2025-11.tar.gz": b"\x1f\x8b\x08..."
                }
            }
        },

        "home": {
            "backup": {
                "scripts": {
                    "rotate.sh": """#!/bin/bash
rm -f /var/backups/daily/*_old
""",
                    "sync_finance.sh": """#!/bin/bash
rsync -avz /srv/corp_data/finance /var/backups/
"""
                },
                "notes.txt": """Backup retention:
- daily: 14d
- weekly: 90d
- monthly: 365d
"""
            },
            "deploy": {
                "queue": {
                    "task_559.json": """{
    "service": "payment-node",
    "version": "4.8.12",
    "approved_by": "a.stevens"
}"""
                }
            },
            "j.smith": {
                "inbox": {
                    "msg1.txt": """James, meeting moved to 3 PM. - Alicia"""
                },
                "projects": {
                    "network_plan_v2.txt": """Switches:
 - Core-1: online
 - Edge-3: firmware pending
"""
                }
            },
            "m.keller": {
                "reports": {
                    "q4_summary.txt": """Draft Summary:
Revenue stable. Security incidents down 12%.
"""
                }
            },
            "a.stevens": {
                "documents": {
                    "team_update.txt": """Deployment team notes:
 - Jenkins upgrade planned
 - Container registry optimization pending
"""
                }
            }
        },

        "srv_internal": {
            "security": {
                "scans": {
                    "scan_2025-12-03.xml": """<scan>
 <result severity="low"/>
 <result severity="none"/>
</scan>"""
                }
            },
            "devops": {
                "deploy_queue": {
                    "task_559.json": """{
    "service": "payment-node",
    "update_type": "patch"
}"""
                }
            }
        },

        "tmp": {
            "sess_3821.tmp": "cached data...",
            "upload_ch_19.bin": b"\x00\x01\x02\x10\x22",
            "patch_extract": {}
        },

        "root": {
            "admin.txt": """Root tasks:
 - Review shadow entries
 - Update mandatory rotation policy
 - Check logs for repeated IP 185.212.18.90
"""
        }
    }
}
