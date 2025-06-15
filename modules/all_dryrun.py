from modules.account.dryrun import (
    fix_empty_password,
    fix_uid0_users,
    fix_risky_sudoers,
    # 未来其他模块的 fix 函数继续导入
)
from modules.firewall.dryrun import fix_firewall

from modules.logaudit.dryrun import fix_audit_logrotate,fix_audit_rules,fix_auditd_install

from modules.patch.dryrun import fix_auto_update_service,fix_update_cache,fix_update_log_file

from modules.ssh.dryrun import fix_ssh_empty_password,fix_ssh_max_auth_tries,fix_ssh_root_login
from modules.portscan.dryrun import fix_ftp_disable,fix_telnet_disable,fix_ssh_bind


from utils.log import log
import json
import os

RESULT_FILE = "json/account.json"

# 模块注册表
DRYRUN_MODULES = [
    {
        "key": "empty_password",
        "fix_func": fix_empty_password,
        "desc": "Empty password check"
    },
    {
        "key": "uid0_users",
        "fix_func": fix_uid0_users,
        "desc": "UID 0 users check"
    },
    {
        "key": "risky_sudoers",
        "fix_func": fix_risky_sudoers,
        "desc": "Risky sudoers check"
    },
    {
        "key": "firewall",
        "fix_func": fix_firewall,
        "desc": "Firewall check"
    },
        {
        "key": "auditd_install",
        "fix_func": fix_auditd_install,
        "desc": "Auditd installation check"
    },
    {
        "key": "audit_rules",
        "fix_func":fix_audit_rules,
        "desc": "Audit rules check"
    },
    {
        "key": "audit_logrotate",
        "fix_func": fix_audit_logrotate,
        "desc": "Audit logrotate check"
    },
    {
        "key": "update_log_file",
        "fix_func": fix_update_log_file,
        "desc": "Audit update_log check"

    },
    {
        "key": "update_update_cache",
        "fix_func": fix_update_cache,
        "desc": "Audit update_cache check"
        
    },
    {
        "key": "update_update_service",
        "fix_func": fix_auto_update_service,
        "desc": "Audit update_service check"
        
    },
     {
        "key": "fix_ssh_bind",
        "fix_func": fix_ssh_bind,
        "desc": "Fix SSH bind address to localhost"
    },
    {
        "key": "fix_telnet_disable",
        "fix_func": fix_telnet_disable,
        "desc": "Disable and remove Telnet service"
    },
    {
        "key": "fix_ftp_disable",
        "fix_func": fix_ftp_disable,
        "desc": "Disable and remove FTP service"
    },
    {
        "key": "fix_root_login",
        "fix_func": fix_ssh_root_login,
        "desc": "Audit ssh_root check"
        
    },

    {
        "key": "fix_ssh_empty_password",
        "fix_func": fix_ssh_empty_password,
        "desc": "Audit ssh_passwd_check"
        
    },
    {
        "key": "fix_ssh_max_auth_tries",
        "fix_func": fix_ssh_max_auth_tries,
        "desc": "Audit ssh_max check"
        
    },

]

def all_dryrun():    
    if not os.path.exists(RESULT_FILE):
        log("JSON file not found", level="ERROR", console=True, file=True)
        return

    with open(RESULT_FILE, "r") as f:
        results = json.load(f)

    scan = results.get("scan_results", {})

    for module in DRYRUN_MODULES:
        key = module["key"]
        fix_func = module["fix_func"]
        desc = module["desc"]

        item = scan.get(key, {})

        if item.get("exists"):
            log(f"{desc}: 存在隐患，执行模拟修复")
            fix_func(item.get("users", []))
        else:
            log(f"{desc}: 没有检测到问题，跳过")
