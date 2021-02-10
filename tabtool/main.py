import argparse
import sys
from tabtool.build import build
from tabtool.deploy import deploy
from tabtool.clear import clear
from tabtool.activate import activate
from tabtool.translate import translate
from tabtool.slides import slides
import logging

logging.basicConfig(format='[tabtool:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s')
logging.getLogger().setLevel(logging.INFO)


def main():
    commands = {'build': build, 'deploy':deploy, 'clear':clear,
                'activate':activate, 'translate':translate, 'slides':slides}
    parser = argparse.ArgumentParser(description='''
D2L Book: Publish a book based on Jupyter notebooks.

Run tabtool command -h to get the help message for each command.
''')
    parser.add_argument('command', nargs=1, choices=commands.keys())
    args = parser.parse_args(sys.argv[1:2])
    commands[args.command[0]]()

if __name__ == "__main__":
    main()
