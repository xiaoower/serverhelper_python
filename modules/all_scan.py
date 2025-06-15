from modules.account.score import (
    check_empty_password,
    check_uid0_users,
    check_risky_sudoers,
    
)
from modules.firewall.score import check_firewall

from modules.logaudit.score import (
    check_audit_logrotate,
    check_audit_rules_passwd_shadow_secure,
    check_auditd_installed
)
from modules.patch.score import (
    check_auto_update_service,
    check_update_cache_exists,
    check_update_log_exists
)

from modules.portscan.score import (
    check_ftp_enabled,
    check_ssh_bind_public,
    check_telnet_enabled
)

from modules.ssh.score import (
    check_ssh_empty_password,
    check_ssh_max_auth_tries,
    check_ssh_root_login
)
from typing import Dict, Any
import json
from pathlib import Path
from utils.log import log

RESULT_FILE = Path("json/account.json")

# 扫描模块注册表
SCAN_MODULES = [
    {
        "key": "empty_password",
        "check_func": check_empty_password,
        "desc": "Empty password check",
        "user_prompt": True,  # 是否需要用户确认执行
    },
    {
        "key": "uid0_users",
        "check_func": check_uid0_users,
        "desc": "UID 0 users check",
        "user_prompt": False,
    },
    {
        "key": "risky_sudoers",
        "check_func": check_risky_sudoers,
        "desc": "Risky sudoers check",
        "user_prompt": False,
    },
    {
        "key": "firewall",
        "check_func": check_firewall,
        "desc": "Firewall status check",
        "user_prompt": True,
    },
    {
        "key": "auditd_installed",
        "check_func": check_auditd_installed,
        "desc": "Auditd installation check",
        "user_prompt": True,
    },
    {
        "key": "audit_rules",
        "check_func": check_audit_rules_passwd_shadow_secure,
        "desc": "Audit rules check",
        "user_prompt": True,
    },
    {
        "key": "audit_logrotate",
        "check_func": check_audit_logrotate,
        "desc": "Audit logrotate check",
        "user_prompt": False,
    },
    {
        "key": "update_cache",
        "check_func": check_update_cache_exists,
        "desc": "Update cache existence check",
        "user_prompt": False,
    },
    {
        "key": "auto_update",
        "check_func": check_auto_update_service,
        "desc": "Auto update service check",
        "user_prompt": False,
    },
    {   
        "key": "update_log",
        "check_func": check_update_log_exists,
        "desc": "Update log existence check",
        "user_prompt": False,
    },
    {
        "key": "ssh_bind_public",
        "check_func": check_ssh_bind_public,
        "desc": "Check if SSH is bound to public interfaces",
        "user_prompt": True,
    },
    {
        "key": "telnet_enabled",
        "check_func": check_telnet_enabled,
        "desc": "Check if Telnet service is enabled",
        "user_prompt": False,
    },
    {
        "key": "ftp_installed",
        "check_func": check_ftp_enabled,
        "desc": "Check if FTP service (vsftpd) is installed",
        "user_prompt": False,
    },

    {
        "key": "ssh_root_login",
        "check_func": check_ssh_root_login,
        "desc": "SSH root login check",
        "user_prompt": True,
    },
    {
        "key": "ssh_empty_password",
        "check_func": check_ssh_empty_password,
        "desc": "SSH empty password check",
        "user_prompt": True,
    },
    {
        "key": "ssh_max_auth_tries",
        "check_func": check_ssh_max_auth_tries,
        "desc": "SSH MaxAuthTries check",
        "user_prompt": True,
    },
]

def write_result_to_json(key: str, result: Dict[str, Any]):
    result_copy = result.copy()
    result_copy.pop("score", None)
    data = {key: result_copy}
    with open(RESULT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def all_scan():
    results = {}
    for module in SCAN_MODULES:
        key = module["key"]
        func = module["check_func"]
        desc = module["desc"]
        prompt_needed = module.get("user_prompt", False)

        if prompt_needed:
            user_input = input(f"运行{desc} (requires sudo)? (y/n): ").strip().lower()
            if user_input != 'y':
                results[key] = {"exists": False, "score": 0}
                continue

        try:
            result = func()
        except SystemExit as e:
            log(f"{desc} check aborted due to insufficient permissions or fatal error.", level="WARNING")
            raise  # 关键：重新抛出异常，程序终止

        results[key] = result

    results["total_score"] = sum(v.get("score", 0) for v in results.values())
    log(f"Account security audit completed. Total score: {results['total_score']} (总分为100分)")

    write_result_to_json("scan_results", results)
    return results
