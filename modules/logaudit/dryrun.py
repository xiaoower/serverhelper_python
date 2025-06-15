from utils.log import log 


def fix_auditd_install(os_family):
    log("[dryrun]根据传入的系统参数，分别调用 apt 或 yum 进行安装")
    

def fix_audit_rules(required_rules):
    
        log("[dryrun]将每个 required_rule 写入 hardening.rules 文件；执行 augenrules 生成最终规则并重启 auditd 服务。")


def fix_audit_logrotate():
    
    log("[dryrun]写入新的 logrotate 配置内容。")
