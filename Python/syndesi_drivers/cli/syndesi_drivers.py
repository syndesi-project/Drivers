# cli.py
# 28.06.24
# Syndesi drivers CLI tool
import argparse
from enum import Enum
from .tools import list_drivers, print_drivers


class Subcommand(Enum):
    LIST = 'list'

def main():
    parser = argparse.ArgumentParser(
        prog='syndesi-drivers',
        description='Syndesi drivers helper tool'
    )

    parser.add_argument('subcommand', choices=[x.value for x in Subcommand])

    args = parser.parse_args()

    if args.subcommand == Subcommand.LIST.value:
        print_drivers()    
        


if __name__ == '__main__':
    main()