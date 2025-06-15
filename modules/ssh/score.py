from utils.log import log
import os
import sys
from typing import Dict, Any

def check_ssh_root_login() -> Dict[str, Any]:
    log("----------检查ssh板块------------")
    log("Checking SSH root login...")
    try:
        with open("/etc/ssh/sshd_config", "r") as f:
            config = f.read().lower()

        if "permitrootlogin no" in config:
            log("Root login disabled, +8 score")
            return {"score": 8}
        else:
            log("Root login not disabled", level="WARNING")
            return {"score": 0}
    except Exception as e:
        log(f"SSH root login check failed: {str(e)}", level="ERROR")
        return {"score": 0}


def check_ssh_empty_password() -> Dict[str, Any]:
    log("Checking SSH empty passwords...")
    try:
        with open("/etc/ssh/sshd_config", "r") as f:
            config = f.read().lower()

        if "permitemptypasswords no" in config:
            log("Empty passwords disabled, +7 score")
            return {"score": 7}
        else:
            log("Empty passwords not disabled", level="WARNING")
            return {"score": 0}
    except Exception as e:
        log(f"SSH empty password check failed: {str(e)}", level="ERROR")
        return {"score": 0}


def check_ssh_max_auth_tries() -> Dict[str, Any]:
    log("Checking SSH MaxAuthTries...")
    try:
        max_auth = 6  # default fallback
        with open("/etc/ssh/sshd_config", "r") as f:
            for line in f:
                if line.strip().lower().startswith("maxauthtries"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        max_auth = int(parts[1])
                        break

        if max_auth <= 4:
            log("MaxAuthTries <= 4, +5 score")
            return {"score": 5}
        else:
            log("MaxAuthTries > 4, +0 score")
            return {"score": 0}
    except Exception as e:
        log(f"SSH MaxAuthTries check failed: {str(e)}", level="ERROR")
        return {"score": 0}
