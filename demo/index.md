# Building Hands-on Books

The D2L book (`d2lbook`) package helps you build and publish **a book consists with Python codes**, or **a Python package document site with tutorials**. For example, Please check [Dive into Deep Learning](https://d2l.ai/) for a book example and [AutoGluon](https://autogluon.mxnet.io/) for a package document site example. 

We designed `d2lbook` for the following three requirements:

- Your book contains **a large amount of codes**, and your readers may run them on Jupyter. In particular,
  - Some chapters may take a while to run, such as running for 10 minutes on a GPU. But you would like to re-evaluate every modified chapters before publication to guarantee correctness. 
  - You may want to reuse codes in other chapters to reduce redundancy.  
- Your Python package documents have **multiple tutorials** that can be run on Jupyter. In particular,
  - As before, you want to evaluate every modified tutorial before publishing as part of your [CI](Continuous_integration) jobs (e.g Jenkins).
  - You want to build API documents as well.  
- You would like to publish **both a website for the book and a printable PDF version**. In particular, 
  - You can reference sections, figure, tables, equations, function, and class.
  - The HTML version should be modern, searchable, and mobile readable.
  - The PDF version should be at the same quality as written by Latex.

This tool combines [Jupyter Notebook](https://jupyter.org/), the widely used interactive environment in Python, and [Sphinx](http://www.sphinx-doc.org/en/master/), the de facto document building system for Python packages, to meet our requirements. 

Please also note there are multiple similar tools we recommend you to check, for example:

- [Jupyter book](https://jupyterbook.org/intro): very similar to `d2lbook` for publishing Jupyter notebooks. Two main design differences are 1) `d2lbook` encourage you to use markdown file format and remove all code outputs when saving notebooks. And all modified notebooks will be re-evaluated during building for code quality. 2) Jupyter book uses Jekyll to build the document, that is easy to use and customizable, but lacking the support for PDF and Python API documents. 
- [gitbook](https://www.gitbook.com/): very convenient to push a book written with markdown but cannot evaluate your codes.
- [sphinx-gallery](https://sphinx-gallery.github.io/stable/index.html), a Sphinx plugin to evaluate and publish your tutorials. But it requires you to know how to use sphinx and write your tutorials in `.py` format with `rst` style.  


## Getting Started

### Installation

Use `pip` to install the command-line interface.

```sh
pip install git+https://github.com/d2l-ai/d2l-book
```

In addition, you also need to install [pandoc](https://pandoc.org/) to build the HTML version, e.g. `conda install pandoc`. Building the PDF version requires [LibRsvg](https://wiki.gnome.org/Projects/LibRsvg) to convert your SVG images (our recommend format), e.g. `conda install librsvg`,  and installing three fonts (click the links to download): [Inconsolata](https://www.fontsquirrel.com/fonts/download/Inconsolata), [Source Serif Pro]( https://www.fontsquirrel.com/fonts/download/source-serif-pro), and [Source Sans Pro](https://www.fontsquirrel.com/fonts/download/source-sans-pro). 

## Building this Website

You may find building this website is a good starting point for your project. The source codes of this site is available under [demo/](https://github.com/d2l-ai/d2l-book/tree/master/demo). 

The following command will download the source codes, evaluate all notebooks and generate outputs in
`ipynb`, `html` and `pdf` format.

```sh
git clone https://github.com/d2l-ai/d2l-book
cd d2l-book/demo
d2lbook build all
```

Once finished, you can check the results in the `_build` folder. For example, this page is in `_build/html/index.html`, the PDF version is at `_build/pdf/d2l-book.pdf`, all evaluated notebooks are under `_build/eval/`.

You can build a particular format:

```sh
d2lbook build eval  # evaluate noteboks and save in .ipynb formats
d2lbook build html  # build the HTML version
d2lbook build pdf   # build the PDF version
```

## Table of Contents

```toc
:numbered:
:maxdepth: 2

examples/index
develop/index
```
