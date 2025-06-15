from utils.log import log 

def fix_ssh_root_login():
    
    log("[dryrun]禁止 root 账户登录")

def fix_ssh_empty_password():
   
    log("[dryrun]禁止空密码登录")

def fix_ssh_max_auth_tries():
   
    log("[dryrun]限制认证尝试次数最大为4")

