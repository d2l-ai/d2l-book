# Books with Jupyter Notebooks

The `d2lbook` package helps you build and publish a book consists with
multiple Jupyter notebooks. It assumes all notebooks are saved in the Markdown
format with outputs striped in favor of editing and reviewing. It then evaluates
notebooks to obtain code cell outputs and build them to various formats,
including Jupyter notebook, HTML and PDF.

In addition, it provides extra functionalities such as:

1. Reference sections, figures, and tables with labels.
1. Cite references with bibtex.
1. Evaluate notebooks in parallel with GPU supports (under developing).

Check [Dive into Deep Learning](https://d2l.ai/) for an example built with
`d2lbook`.


## Getting Started

### Installation

Use `pip` to install the command-line interface.

```sh
pip install git+https://github.com/d2l-ai/d2l-book
```

In addition, you also need to install `pandoc`, e.g. `conda install pandoc`.


### Create a new book (under developing)

Create a new book into the directory `mybook` with a default configuration
file.

```sh
d2lbook create mybook
```

Or create a new book using the demo book content (the website that you’re viewing
now).

```sh
d2lbook create mybook --demo
```

Edit the `config.ini` by updating the book title,  authors, and others.

### Build the contents for your book

First enter your book directory

```sh
cd mybook
```

The following command will evaluate all notebooks and generate outputs in
`ipynb`, `html` and `pdf` format.

```sh
d2lbook build all
```

Once finished, you can check the results in the `_build` folder.

Or you can only build HTML outputs

```
d2lbook build html
```

### Deploy the contents online

Publish both HTML and PDF into a s3 bucket, which allows to setup a static
website hosting easily (you need to configure the `s3_bucket` in `config.ini`).

```sh
d2l-book deploy html pdf
```

Or push all notebooks in the `ipynb` format into a github repo (you need
configure `github_repo` in `config.ini`) (under developing).

```sh
d2l-book deploy ipynb
```

## Table of Contents

```toc
:numbered:
:maxdepth: 2

examples/index
develop/index
```


## History

This project starts with several scripts wrote to build the documents sites for
several projects, including [Apache MXNet](http://mxnet.io),
[GluonCV](http://gluon-cv.mxnet.io),  [D2L](http://d2l.ai). Later on, heavily inspired
by [Jupyter Book](https://jupyter.org/jupyter-book), we refactored these scripts
into a package.
