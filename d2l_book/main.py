import argparse
import sys
from .build import build

commands = {'build': build}
parser = argparse.ArgumentParser(description='D2L Book: Publish a book based on Jupyter notebooks.')
parser.add_argument('command', help=' '.join(commands.keys()))

def main():
    args = parser.parse_args(sys.argv[1:2])
    commands[args.command]()


if __name__ == "__main__":
    main()
