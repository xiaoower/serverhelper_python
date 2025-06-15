from utils.log import log
import subprocess
import os
import grp
from utils.backup_rollback import backup_file

BACKUP_DIR = "backup/"

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Command failed: {' '.join(cmd)}\n{result.stderr}", level="ERROR")
        return False
    return True

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def group_exists(group_name):
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False

def fix_empty_password(users):
    ensure_backup_dir()
    shadow_file = "/etc/shadow"
    backup_path = os.path.join(BACKUP_DIR, "shadow.bak")
    if not backup_file(shadow_file, backup_path):
        log("Warning: Backup of /etc/shadow failed before fixing empty passwords", level="WARNING")

    for user in users:
        log(f"Locking user account: {user}")
        if not run_cmd(["passwd", "-l", user]):
            log(f"Failed to lock user {user}", level="ERROR")

def fix_uid0_users(users):
    ensure_backup_dir()
    passwd_file = "/etc/passwd"
    group_file = "/etc/group"
    passwd_backup = os.path.join(BACKUP_DIR, "passwd.bak")
    group_backup = os.path.join(BACKUP_DIR, "group.bak")

    if not backup_file(passwd_file, passwd_backup):
        log("Warning: Backup of /etc/passwd failed before fixing UID 0 users", level="WARNING")
    if not backup_file(group_file, group_backup):
        log("Warning: Backup of /etc/group failed before fixing UID 0 users", level="WARNING")

    new_uid_start = 1001
    for user in users:
        log(f"Changing UID of user {user} to {new_uid_start}")
        if not run_cmd(["usermod", "-u", str(new_uid_start), user]):
            log(f"Failed to change UID for user {user}", level="ERROR")
            continue

        # 注意：这里对全盘 chown，存在性能风险，建议你后续优化
        if not run_cmd(["find", "/", "-user", "0", "-exec", "chown", f"{user}", "{}", "+"]):
            log(f"Failed to change ownership for files of user {user}", level="ERROR")
        new_uid_start += 1

def fix_risky_sudoers(users):
    ensure_backup_dir()
    group_file = "/etc/group"
    backup_path = os.path.join(BACKUP_DIR, "group.bak")
    if not backup_file(group_file, backup_path):
        log("Warning: Backup of /etc/group failed before fixing risky sudoers", level="WARNING")

    privileged_groups = ["sudo", "wheel", "admin"]

    for user in users:
        for group in privileged_groups:
            if group_exists(group):
                log(f"Removing user {user} from group {group}")
                if not run_cmd(["gpasswd", "-d", user, group]):
                    log(f"Failed to remove user {user} from group {group}", level="ERROR")
            else:
                log(f"Group '{group}' does not exist, skipping", level="WARNING")
