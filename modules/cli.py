import argparse

from modules.operation import run_scan, dryrun,show_log #run_fix,rollback


import argparse

def setup_parser(): 
    parser = argparse.ArgumentParser( 
        description="系统安全扫描工具：检测并修复系统问题",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--scan",
        action="store_true",
        help="执行完整系统扫描"
    )

    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="仅模拟扫描，不进行实际修改"
    )

    parser.add_argument(
        "--log",
        action="store_true",
        help="显示详细日志信息"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="自动修复已发现的问题"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="回滚所有已执行的修复操作"
    )

    return parser


def handle_commands(args):
    if args.dryrun:
        dryrun()
        return True
    elif args.scan:
        run_scan()
        return True
    elif args.log:
        show_log()
        return True
    # elif args.fix:
    #     run_fix()
    #     return True
    # elif args.rollback:
    #     rollback()
    #     return True
    else:
        return None  # Signal "no valid command"

