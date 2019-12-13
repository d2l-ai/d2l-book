# Creating Your Project

Let's start with a simple project from scratch.

## Project From Scratch

First make a folder for our project.

```{.python .input}
!mkdir -p mybook
```

Then create two pages. The `index.md` is the index page which should contain the table of contents (TOC). In this case, there is only another `get_started.md`. Note that the TOC is defined in a code block with name `toc`. If you are familiar with Sphinx, you can find it's similar to the TOC definition in Sphinx. Please refer to :numref:`sec_markdown` for more extensions `d2lbook` added to markdown.

```{.python .input}
%%writefile mybook/index.md
# My Book

The starting page of my book with `d2lbook`.

```toc
get_started
```
```

```{.python .input}
%%writefile mybook/get_started.md
# Getting Started

Please first install my favorite package `numpy`.
```

Now let's build the HTML version.

```{.python .input}
!cd mybook && d2lbook build html
```

The index HTML page is then available at `mybook/_build/html/index.html`.

## Configuration

You can customize how your book is built and published through `config.ini`.

```{.python .input}
%%writefile mybook/config.ini

[project]
name = mybook  # Specify the PDF filename to mybook.pdf
author = Adam Smith, Alex Li  # Specify the authors names in PDF

[html]
# Add two links on the navbar. A link consists of three
# items: name, URL, and a fontawesome icon. Items are separated by commas.
header_links = PDF, https://book.d2l.ai/d2l-book.pdf, fas fa-file-pdf,
               Github, https://github.com/d2l-ai/d2l-book, fab fa-github

[build]
# Don't evaluate the code blocks in notebooks to save time. But you
# will not see code outputs in your results.
eval_notebook = False

[deploy]
# Add a Google Analytics ID in each HTML page.
google_analytics_tracking_id = UA-96378503-1
```

Let's clean and build again.

```{.python .input}
!cd mybook && rm -rf _build && d2lbook build html
```

You can check [default_config.ini](https://github.com/d2l-ai/d2l-book/blob/master/d2lbook/config_default.ini) for more configuration options and their default values. Also check these examples `config.ini`:
- [This website](https://github.com/d2l-ai/d2l-book/blob/master/demo/config.ini)
- [Dive into Deep Learning](https://github.com/d2l-ai/d2l-en/blob/master/config.ini)

Last, let's remove our example.

```{.python .input}
!rm -rf mybook
```
