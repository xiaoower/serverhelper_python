from utils.log import log 
import subprocess
import os
from typing import Dict, Any

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()

def check_ssh_bind_public() -> Dict[str, Any]:
    log("----------检查端口扫描板块------------")
    log("Checking if SSH is bound to 0.0.0.0")
    try:
        retcode, output = run_cmd(["ss", "-ltnp"])
        if retcode != 0:
            raise Exception("Failed to run ss")

        bound_public = False
        for line in output.splitlines():
            if "0.0.0.0:22" in line or "[::]:22" in line:
                bound_public = True
                break

        if bound_public:
            log("SSH bound to public interface, score 0")
            return {"exists": True, "score": 0}
        else:
            log("SSH not bound to public, score 4")
            return {"exists": False, "score": 4}
    except Exception as e:
        log(f"SSH bind check failed: {e}", level="ERROR")
        return {"exists": True, "score": 0}

def check_telnet_enabled() -> Dict[str, Any]:
    log("Checking if Telnet service exists")
    try:
        retcode, _ = run_cmd(["systemctl", "is-enabled", "telnet.socket"])
        if retcode == 0:
            log("Telnet enabled, score 0")
            return {"exists": True, "score": 0}
        else:
            log("Telnet not enabled, score 4")
            return {"exists": False, "score": 4}
    except:
        log("Telnet service not found, score 4")
        return {"exists": False, "score": 4}

def check_ftp_enabled() -> Dict[str, Any]:
    log("Checking if FTP service installed")
    try:
        retcode, output = run_cmd(["which", "vsftpd"])
        if output:
            log("FTP service installed, score 0")
            return {"exists": True, "score": 0}
        else:
            log("FTP not installed, score 4")
            return {"exists": False, "score": 4}
    except:
        log("FTP not found, score 4")
        return {"exists": False, "score": 4}
