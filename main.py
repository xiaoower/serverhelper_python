from utils.log import log
from modules.cli import setup_parser ,handle_commands# Import the CLI parser


import sys

def main():
  
    parser = setup_parser()
    args = parser.parse_args()
    
    if not handle_commands(args):  # Returns True/False
        log("No arguments provided,Please enter at least one arguments",
            level="ERROR",
            console=True,
            file=False)
        sys.exit(1)

if __name__ == "__main__":
    main()

