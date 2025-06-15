from utils.log import log
import subprocess
import os
import sys
import json
from typing import Dict, Any
from glob import glob

def check_auditd_installed() -> Dict[str, Any]:
    log("----------检查日志审计板块------------")
    log("Checking if auditd is installed...")
    if os.geteuid() != 0:
        log("This check requires sudo privileges", level="ERROR")
        sys.exit("Fatal: Please run again with sudo privilege")

    try:
        result = subprocess.run(["which", "auditd"], capture_output=True, text=True)
        if result.returncode == 0:
            log("auditd installed, +4 score")
            return {"installed": True, "score": 4}
        else:
            log("auditd not installed, attempting installation...")
            with open("json/detect_result.json", "r") as f:
                detect_result = json.load(f)
            os_family = detect_result.get("os_family", "").lower()
            if os_family == "debian":
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", "auditd"], check=True)
            elif os_family == "redhat":
                subprocess.run(["yum", "install", "-y", "audit"], check=True)
            else:
                log(f"Unsupported OS family: {os_family}", level="ERROR")
                return {"installed": False, "score": 0}

            result = subprocess.run(["which", "auditd"], capture_output=True, text=True)
            if result.returncode == 0:
                log("auditd installed after auto install, +4 score")
                return {"installed": True, "score": 4}
            else:
                log("Failed to install auditd", level="ERROR")
                return {"installed": False, "score": 0}

    except Exception as e:
        log(f"Auditd install check failed: {str(e)}", level="ERROR")
        return {"installed": False, "score": 0}


def check_audit_rules_passwd_shadow_secure() -> Dict[str, Any]:
    log("Checking audit rules for passwd, shadow, secure...")
    required_rules = ["/etc/passwd", "/etc/shadow", "/var/log/secure"]
    rules_files = glob("/etc/audit/rules.d/*.rules")

    try:
        all_rules = set()
        for rf in rules_files:
            with open(rf, "r") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                all_rules.add(line)

        missing_rules = []
        for rule in required_rules:
            matched = any(rule in r for r in all_rules)
            if not matched:
                log(f"Audit rule for {rule} missing", level="WARNING")
                missing_rules.append(rule)

        if not missing_rules:
            log("All required audit rules found, +3 score")
            return {"exists": True, "score": 3}
        else:
            log("Not all required audit rules found, +0 score", level="WARNING")
            return {"exists": False, "score": 0}

    except Exception as e:
        log(f"Audit rules check failed: {str(e)}", level="ERROR")
        return {"exists": False, "score": 0}


def check_audit_logrotate() -> Dict[str, Any]:
    log("Checking logrotate for audit logs...")
    try:
        for root, dirs, files in os.walk("/etc/logrotate.d/"):
            for file in files:
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    content = f.read()
                if "/var/log/audit/audit.log" in content:
                    log("Logrotate config found for audit logs, +3 score")
                    return {"exists": True, "score": 3}
        log("No logrotate config found for audit logs", level="WARNING")
        return {"exists": False, "score": 0}
    except Exception as e:
        log(f"Audit logrotate check failed: {str(e)}", level="ERROR")
        return {"exists": False, "score": 0}
