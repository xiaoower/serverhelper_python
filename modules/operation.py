
from utils.log import log
#from modules.all_fix import all_fix
from modules.all_scan import all_scan
from modules.all_dryrun import all_dryrun
#from modules.all_rollback import all_rollback



def run_scan():
    log("---------------------开始扫描-----------------------")
    all_scan()
    log("--------- All scanning completed successfully-----------------")


def dryrun():
    log("-----------------开始模拟修复----------------")
    all_dryrun()
    log("-----All simulated fixes completed successfully-----")



# def run_fix():
#     log("-------------------Starting true fixes ---------------------")
#     all_fix()
#     log("----------All fixes completed successfully------------------")


# def rollback():
#     log("----------------------Starting the rollback------------------------------")
#     all_rollback()
#     log("----------All rollback operations completed successfully------------------")

def show_log():
    print("--show the log--") 