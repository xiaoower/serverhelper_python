from utils.log import log


def fix_empty_password(users):
    log("----------开始账户修复流程------------")
    log("[dryrun] 锁定账户: {}".format(users))

def fix_uid0_users(users):
    log("[dryrun] 将非 root 用户 UID 改为普通 UID, 同步修改其文件所属者: {}".format(users))

def fix_risky_sudoers(users):
    log("[dryrun] 从 sudo, wheel, admin 组移除无关成员: {}".format(users))
