# D2L-Book: A Toolkit for Hands-on Books

The D2L Book (`d2lbook`) package helps you build and publish **a book
with Python code blocks**, or **Python package documents with tutorials**. You can
check [Dive into Deep Learning](https://d2l.ai/) for a book
example and [AutoGluon](https://autogluon.mxnet.io/) for a package document site
example.

`d2lbook` is designed to meet the following two requirements:

- Your book may contain **a large amount of Python code** and you
  expect your readers to run them. Or your package documents have **multiple
  tutorials** to walk readers through your package usage through examples.
  The code should be runnable and maintainable.

- You would like to publish **both a HTML website and a printable PDF
  version**. You expect the website should be modern, searchable and mobile
  friendly, and the PDF version should be at the same quality as written using LaTeX.


To achieve the above goals, `d2lbook` combines
[Jupyter Notebook](https://jupyter.org/), the widely used interactive
environment in Python, and [Sphinx](http://www.sphinx-doc.org/en/master/), the
de facto document building system for Python packages. In particular, its main
features include:

- Using [markdown](https://daringfireball.net/projects/markdown/) for your contents.
- A minimal configuration file to customize the building so you can focus on the
  contents.
- Evaluating all code blocks to obtain their output before publishing to validate the
  correctness. By default, `d2lbook` only evaluates the updated code blocks to save cost.
- Being able to reference sections, figure, tables, equations, function, and
  class.
- Pipelines to publish your website through Github or AWS.

If `d2lbook` does not fit your requirements, you may check the following tools:

- [Jupyter Book](https://jupyterbook.org): A similar tool for building books 
  from computational material with Jupyter Notebooks and MyST Markdown.
- [gitbook](https://www.gitbook.com/): very convenient to push a book written
  with markdown if you don't need to run them as Jupyter notebooks.
- [sphinx-gallery](https://sphinx-gallery.github.io/stable/index.html), a Sphinx
  plugin to evaluate and publish your tutorials. It requires you to know how
  to use Sphinx and write your tutorials in `.py` format with the `rst` style.

```eval_rst
.. only:: html

   Table of Contents
   -----------------
```


```toc
:numbered:
:maxdepth: 2

install
user/index
develop/index
```

