import argparse
import sys
from d2lbook.build import build
from d2lbook.deploy import deploy
import logging

logging.basicConfig(format='[d2lbook:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s')

logging.getLogger().setLevel(logging.INFO)

commands = {'build': build, 'deploy':deploy}
parser = argparse.ArgumentParser(description='D2L Book: Publish a book based on Jupyter notebooks.')
parser.add_argument('command', help=' '.join(commands.keys()))

def main():
    args = parser.parse_args(sys.argv[1:2])
    commands[args.command]()


if __name__ == "__main__":
    main()
