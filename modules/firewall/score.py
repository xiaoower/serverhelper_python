from utils.log import log
import subprocess
import sys
import os
from typing import Dict, Any
from utils.detect_os import detect_environment
import json

def run_cmd_output(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()

def install_package(package_name):
    if os.path.exists("/usr/bin/apt"):
        subprocess.run(["apt", "install", "-y", package_name])
    elif os.path.exists("/usr/bin/dnf"):
        subprocess.run(["dnf", "install", "-y", package_name])
    elif os.path.exists("/usr/bin/yum"):
        subprocess.run(["yum", "install", "-y", package_name])
    else:
        log("Package manager not supported, install manually", level="ERROR")

def detect_os_family() -> str:
    try:
        if os.path.exists("/etc/redhat-release"):
            return "redhat"
        elif os.path.exists("/etc/debian_version"):
            return "debian"
        else:
            # 尝试通过 /etc/os-release 识别
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    if "red hat" in content or "centos" in content or "fedora" in content:
                        return "redhat"
                    elif "debian" in content or "ubuntu" in content:
                        return "debian"
    except Exception as e:
        log(f"OS detection failed: {str(e)}", level="ERROR")
    return ""

def check_firewall() -> Dict[str, Any]:
    log("----------检查防火墙板块------------")

    # 加入环境探测
    try:
        result = detect_environment()

        json_dir = "json/"
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, "detect_result.json")

        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)

        log(f"Environment detection completed and saved to {json_path}")
    except Exception as e:
        log(f"Environment detection failed: {str(e)}", level="ERROR")

    if os.geteuid() != 0:
        log("This check requires sudo privileges", level="ERROR")
        sys.exit("Fatal: Please run again with sudo privilege")

    score = 0
    details = {}

    os_family = detect_os_family()

    try:
        if os_family == "redhat":
            ret, _ = run_cmd_output(["rpm", "-q", "firewalld"])
            if ret != 0:
                log("firewalld not installed, installing...", level="WARNING")
                install_package("firewalld")

            ret, _ = run_cmd_output(["systemctl", "is-active", "firewalld"])
            if ret == 0:
                score += 8
                details["firewalld_active"] = True
                log("firewalld active: success, score +8")
            else:
                details["firewalld_active"] = False
                log("firewalld active: failed, score +0", level="ERROR")

            ret, output = run_cmd_output(["firewall-cmd", "--get-default-zone"])
            if ret == 0 and output.strip() in ["drop", "block"]:
                score += 8
                details["default_zone"] = output.strip()
                log(f"default zone '{output.strip()}': secure, score +8")
            else:
                details["default_zone"] = output.strip()
                log(f"default zone '{output.strip()}': insecure, score +0", level="ERROR")

            ret, output = run_cmd_output(["firewall-cmd", "--get-log-denied"])
            if ret == 0 and output.strip() != "off":
                score += 4
                details["logging"] = output.strip()
                log(f"firewall logging '{output.strip()}': enabled, score +4")
            else:
                details["logging"] = "off"
                log("firewall logging: disabled, score +0", level="ERROR")

            return {"exists": True, "score": score, "details": details}

        elif os_family == "debian":
            ret, _ = run_cmd_output(["dpkg", "-s", "ufw"])
            if ret != 0:
                log("ufw not installed, installing...", level="WARNING")
                install_package("ufw")

            ret, output = run_cmd_output(["ufw", "status"])
            if "Status: active" in output:
                score += 8
                details["ufw_active"] = True
                log("ufw active: success, score +8")
            else:
                details["ufw_active"] = False
                log("ufw active: failed, score +0", level="ERROR")

            ret, output = run_cmd_output(["ufw", "status", "verbose"])
            if "Default: deny" in output:
                score += 8
                details["default_policy"] = "deny"
                log("ufw default policy deny: success, score +8")
            else:
                details["default_policy"] = output
                log("ufw default policy deny: failed, score +0", level="ERROR")

            ret, output = run_cmd_output(["ufw", "status", "verbose"])
            if "Logging: on" in output:
                score += 4
                details["logging"] = "on"
                log("ufw logging on: enabled, score +4")
            else:
                details["logging"] = "off"
                log("ufw logging: disabled, score +0", level="ERROR")

            return {"exists": True, "score": score, "details": details}

        else:
            log("Unsupported OS family for firewall check", level="WARNING")
            return {"exists": False, "score": 0, "details": {"reason": "unsupported_os"}}

    except Exception as e:
        log(f"Firewall check failed: {str(e)}", level="ERROR")
        return {"exists": False, "score": 0, "details": {"error": str(e)}}