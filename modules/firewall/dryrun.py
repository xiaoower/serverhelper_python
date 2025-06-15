import os
import json
from utils.log import log


def fix_firewall(_=None):
    json_path = "json/detect_result.json"
    if not os.path.exists(json_path):
        log(f"[dryrun] 错误：未找到文件 {json_path}，无法检测操作系统类型", level="ERROR")
        return

    try:
            with open(json_path, "r") as f:
                detect_result = json.load(f)
            os_family = detect_result.get("os_family", "")
    except Exception as e:
            log(f"[dryrun] 读取文件 {json_path} 失败，错误信息：{str(e)}", level="ERROR")
            return

    if os_family == "redhat":
            log("[dryrun] 将检查并配置 firewalld")
            log("[dryrun] firewalld 服务将被启用并设置为开机自启")
            log("[dryrun] 默认区域将设置为 'drop'")
            log("[dryrun] 防火墙日志将被启用")
    elif os_family == "debian":
            log("[dryrun] 将检查并配置 ufw")
            log("[dryrun] ufw 服务将被启用并设置为开机自启")
            log("[dryrun] 默认策略将设置为拒绝")
            log("[dryrun] ufw 日志将被启用")
    else:
            log("[dryrun] 不支持的操作系统类型，无法模拟防火墙修复操作")
    return

    