# Books with Jupyter and Sphinx

`d2l-book` lets you build an online book with Jupyter notebooks saved in the
Markdown format. It evaluates all notebooks to obtain outputs, and then use
Sphinx to generate various output formats. It adds extra functionalities such as
image/table reference, bibtex citation and parallel executions to facilitate
building a book.

Check [Dive into Deep Learning](https://d2l.ai/) for an example built with
`d2l-book`.


## Getting Started

### Installation

Use `pip` to install the command-line interface.

```sh
pip install d2lbook
```


### Create a new book

Create a new book using the demo book content (the website that you’re viewing now) with this command:

```sh
d2lbook create mybook --demo
cd mybook
```


### Build the contents for your book

It will build both HTML and PDF formats

```sh
d2lbook build all
```


### Publish the contents online

```sh
d2l-book publish ipynb https://github.com/d2l-ai/notebooks
d2l-book publish html pdf s3://book.d2l.ai
```


## Table of Contents

```toc
:numbered:
:maxdepth: 2

examples/index
```


## Acknowledgments

This project starts with several scripts I wrote to build the documents sites for
several projects, including [Apache MXNet](http://mxnet.io),
[GluonCV](http://gluon-cv.mxnet.io),  [D2L](http://d2l.ai). Later on, inspired
by [Jupyter Book](https://jupyter.org/jupyter-book), I ensemble these scripts
into a project.
