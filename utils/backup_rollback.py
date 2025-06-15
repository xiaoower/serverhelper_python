import os
import shutil
from utils.log import log

def backup_file(src_path: str, backup_path: str) -> bool:
    """
    备份指定文件到指定路径。
    如果源文件不存在或备份目录不存在，返回False。
    """
    if not os.path.isfile(src_path):
        log(f"备份跳过，源文件不存在: {src_path}", level="WARNING")
        return False

    backup_dir = os.path.dirname(backup_path)
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
        except Exception as e:
            log(f"备份失败，无法创建备份目录: {backup_dir}, 错误: {e}", level="ERROR")
            return False

    try:
        shutil.copy2(src_path, backup_path)
        log(f"备份成功: {src_path} -> {backup_path}")
        return True
    except Exception as e:
        log(f"备份失败: {src_path}, 错误: {e}", level="ERROR")
        return False

def rollback_file(backup_path: str, target_path: str) -> bool:
    """
    从备份文件恢复到指定目标路径，返回是否成功
    """
    if not os.path.isfile(backup_path):
        log(f"回滚失败，备份文件不存在: {backup_path}", level="ERROR")
        return False
    try:
        shutil.copy2(backup_path, target_path)
        log(f"回滚成功: {backup_path} -> {target_path}")
        return True
    except Exception as e:
        log(f"回滚失败: {target_path}, 错误: {e}", level="ERROR")
        return False
