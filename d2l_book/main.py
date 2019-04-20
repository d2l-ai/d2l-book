import argparse
import .build

parser = argparse.ArgumentParser(description='D2L Book: Publish a book based on Jupyter notebooks.')
commands = ['ipynb', 'rst', 'html', 'pdf', 'publish']
parser.add_argument('command', help=' '.join(commands))






def main():

    args = parser.parse_args()

if __name__ == "__main__":
    main()
