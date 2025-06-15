from utils.log import log 
import os
import sys
from typing import Dict, Any

def check_update_cache_exists() -> Dict[str, Any]:
    log("----------检查补丁板块------------")
    log("Checking if update cache exists...")

    try:
        cache_exists = any([
            os.path.exists("/var/lib/apt/lists"),
            os.path.exists("/var/cache/dnf"),
            os.path.exists("/var/cache/yum")
        ])
        if cache_exists:
            log("Update cache exists, +7 score")
            return {"score": 7}
        else:
            log("No update cache found", level="WARNING")
            return {"score": 0}
    except Exception as e:
        log(f"Update cache check failed: {str(e)}", level="ERROR")
        return {"score": 0}


def check_auto_update_service() -> Dict[str, Any]:
    log("Checking if auto update service is enabled...")
    try:
        auto_update_enabled = False
        if os.path.exists("/etc/apt/apt.conf.d/20auto-upgrades"):
            with open("/etc/apt/apt.conf.d/20auto-upgrades", "r") as f:
                content = f.read()
            if '1' in content:
                auto_update_enabled = True
        elif os.path.exists("/etc/dnf/automatic.conf"):
            with open("/etc/dnf/automatic.conf", "r") as f:
                content = f.read()
            if "apply_updates = yes" in content.lower():
                auto_update_enabled = True

        if auto_update_enabled:
            log("Auto update enabled, +7 score")
            return {"score": 7}
        else:
            log("Auto update not enabled", level="WARNING")
            return {"score": 0}
    except Exception as e:
        log(f"Auto update check failed: {str(e)}", level="ERROR")
        return {"score": 0}


def check_update_log_exists() -> Dict[str, Any]:
    log("Checking if update log file exists...")
    try:
        update_log_exists = any([
            os.path.exists("/var/log/apt/history.log"),
            os.path.exists("/var/log/dnf.log"),
            os.path.exists("/var/log/yum.log")
        ])
        if update_log_exists:
            log("Update log exists, +6 score")
            return {"score": 6}
        else:
            log("No update log found", level="WARNING")
            return {"score": 0}
    except Exception as e:
        log(f"Update log check failed: {str(e)}", level="ERROR")
        return {"score": 0}
