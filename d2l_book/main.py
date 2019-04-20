import argparse

parser = argparse.ArgumentParser(description='D2L Book: Publish a book based on Jupyter notebooks.')
parser.add_argument('command', help="xxx, b, c, d")


def main():
    args = parser.parse_args()

if __name__ == "__main__":
    main()
