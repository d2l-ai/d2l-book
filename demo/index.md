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

```
pip install d2l-book
```

### Create a new book

Create a new book using the demo book content (the website that you’re viewing now) with this command:

```
d2l-book create mybook --demo
cd mybook
```

### Build the contents for your book


```
d2l-book build html pdf
```

### Publish the contents online

```
d2l-book publish html pdf s3://book.d2l.ai
```

## Table of Contents

{% toc
:numbered:
:maxdepth: 2

guide/index
examples/index

%}

## Acknowledgements

This project starts with several scripts I wrote to build the documents sites for
several projects, including [Apache MXNet](http://mxnet.io),
[GluonCV](http://gluon-cv.mxnet.io),  [D2L](http://d2l.ai). Later on, inspired
by [Jupyter Book](https://jupyter.org/jupyter-book), I ensemble these scripts
into a project.
