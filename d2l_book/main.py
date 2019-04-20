import argparse
import sys
from .build import build
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-6s [%(filename)s:L%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

commands = {'build': build}
parser = argparse.ArgumentParser(description='D2L Book: Publish a book based on Jupyter notebooks.')
parser.add_argument('command', help=' '.join(commands.keys()))

def main():
    args = parser.parse_args(sys.argv[1:2])
    commands[args.command]()


if __name__ == "__main__":
    main()
