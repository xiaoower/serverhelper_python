import shutil
import grp
import os

def group_exists(name):
    try:
        grp.getgrnam(name)
        return True
    except KeyError:
        return False

def command_exists(cmd):
    return shutil.which(cmd) is not None

def detect_os_family():
    os_release_path = "/etc/os-release"
    if not os.path.isfile(os_release_path):
        return "unknown"
    
    os_info = {}
    with open(os_release_path) as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                os_info[key] = val.strip('"')
    
    if "ID_LIKE" in os_info:
        return os_info["ID_LIKE"]
    elif "ID" in os_info:
        return os_info["ID"]
    else:
        return "unknown"

def detect_environment():
    return {
        "commands": {
            "sudo": command_exists("sudo"),
            "passwd": command_exists("passwd"),
            "usermod": command_exists("usermod"),
            "gpasswd": command_exists("gpasswd"),
        },
        "groups": {
            "sudo": group_exists("sudo"),
            "wheel": group_exists("wheel"),
            "admin": group_exists("admin"),
        },
        "os_family": detect_os_family()
    }
