from utils.log import log
import json
import subprocess
import getpass
import os
from typing import Dict, Any
import sys 


def check_empty_password() -> Dict[str, Any]:
    log("----------检查账户板块------------")
    log("hecking for users with empty passwords...")

    if os.geteuid() != 0:
        log("This check requires sudo privileges", level="ERROR")
        sys.exit("Fatal: Please run again with sudo privilege")

    try:
        result = subprocess.run(
            ["awk", '-F:', '($2 == "") {print $1}', "/etc/shadow"],
            capture_output=True,
            text=True
        )
        users = result.stdout.splitlines()

        if users:
            log(f"Empty password users found: {users}, score 0")
            return {"exists": True, "users": users, "score": 0}
        else:
            log("No empty password users found, success, score 8")
            return {"exists": False, "users": [], "score": 8}

    except Exception as e:
        log(f"Password check failed: {str(e)}", level="ERROR")
        sys.exit(f"Fatal: Unexpected error in password check: {e}")


def check_uid0_users() -> Dict[str, Any]:
    log("Checking for non-root UID 0 users...")
    try:
        result = subprocess.run(
            ["awk", '-F:', '($3 == 0 && $1 != "root") {print $1}', "/etc/passwd"],
            capture_output=True,
            text=True
        )
        users = result.stdout.splitlines()

        if users:
            log(f"Non-root UID 0 users found: {users}, score 0")
            return {"exists": True, "users": users, "score": 0}
        else:
            log("No non-root UID 0 users found, success, score 6")
            return {"exists": False, "users": [], "score": 6}

    except Exception as e:
        log(f"UID check failed: {str(e)}", level="ERROR")
        return {"exists": False, "users": [], "score": 0}


def check_risky_sudoers() -> Dict[str, Any]:
    log("Checking for risky sudoers...")
    current_user = getpass.getuser()
    privileged_groups = ["sudo", "wheel", "admin"]
    risky_users = []
    skipped_users = []

    try:
        for group in privileged_groups:
            result = subprocess.run(
                ["getent", "group", group],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(":")
                if len(parts) >= 4:
                    members = parts[3].split(",")
                    for user in members:
                        user = user.strip()
                        if not user:
                            continue
                        if user == current_user:
                            skipped_users.append(user)
                        else:
                            risky_users.append(user)

        risky_users = list(set(risky_users))
        skipped_users = list(set(skipped_users))

        if skipped_users:
            log(f"Skipped current user(s) in risky sudoers check: {skipped_users}", level="WARNING")

        if risky_users:
            log(f"Risky sudoers found (excluding current user): {risky_users}, score 0",
                level="ERROR")
            return {
                "exists": True,
                "users": risky_users,
                "skipped": skipped_users,
                "score": 0
            }
        else:
            log("No risky sudoers found, success, score 6")
            return {
                "exists": False,
                "users": [],
                "skipped": skipped_users,
                "score": 6
            }

    except Exception as e:
        log(f"Sudoers check failed: {e}", level="ERROR")
        return {
            "exists": False,
            "users": [],
            "skipped": [],
            "score": 0,
            "error": str(e)
        }
