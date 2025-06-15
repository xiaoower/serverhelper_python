from utils.log import log 




def fix_ssh_bind():
   
    log("[dryrun]把 SSH 监听地址强制修改为 127.0.0.1，避免绑定公网接口")

def fix_telnet_disable():
    log("[dryrun]彻底禁用并移除 telnet 服务，避免暴露风险服务端口")
   
def fix_ftp_disable():
    log("[dryrun]移除 FTP 服务，防止明文传输敏感数据")
  
