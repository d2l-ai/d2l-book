FROM ubuntu:20.04

RUN apt update && apt dist-upgrade -y && DEBIAN_FRONTEND=noninteractive apt install -y python3-pip pandoc librsvg2-bin git latexmk texlive-xetex texlive-fonts-extra && apt clean

RUN pip3 install git+https://github.com/d2l-ai/d2l-book

WORKDIR /book

CMD ["d2lbook", "--help"]