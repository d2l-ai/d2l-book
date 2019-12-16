# Creating Your Project
:label:`sec_create`

Let's start with a simple project from scratch.

## Project From Scratch

First make a folder for our project.

```{.python .input  n=1}
!mkdir -p mybook
```

Then create two pages. The `index.md` is the index page which should contain the table of contents (TOC). In this case, there is only another `get_started.md`. Note that the TOC is defined in a code block with name `toc`. If you are familiar with Sphinx, you can find it's similar to the TOC definition in Sphinx. Please refer to :numref:`sec_markdown` for more extensions `d2lbook` added to markdown.

```{.python .input  n=2}
%%writefile mybook/index.md
# My Book

The starting page of my book with `d2lbook`.

````toc
get_started
````

```

```{.json .output n=2}
[
 {
  "name": "stdout",
  "output_type": "stream",
  "text": "Writing mybook/index.md\n"
 }
]
```

```{.python .input  n=3}
%%writefile mybook/get_started.md
# Getting Started

Please first install my favorite package `numpy`.
```

```{.json .output n=3}
[
 {
  "name": "stdout",
  "output_type": "stream",
  "text": "Writing mybook/get_started.md\n"
 }
]
```

Now let's build the HTML version.

```{.python .input  n=4}
!cd mybook && d2lbook build html
```

```{.json .output n=4}
[
 {
  "name": "stdout",
  "output_type": "stream",
  "text": "[d2lbook:build.py:L98] INFO   2 notebooks are outdated\n[d2lbook:build.py:L100] INFO   [1] ./get_started.md\n[d2lbook:build.py:L100] INFO   [2] ./index.md\n[d2lbook:build.py:L107] INFO   [1/2, 00:00:00] Evaluating ./get_started.md, save as _build/eval/get_started.ipynb\n[d2lbook:execute.py:L252] INFO   Executing notebook with kernel: python\n[d2lbook:build.py:L112] INFO   Finished in 00:00:01\n[d2lbook:build.py:L107] INFO   [2/2, 00:00:01] Evaluating ./index.md, save as _build/eval/index.ipynb\n[d2lbook:execute.py:L252] INFO   Executing notebook with kernel: python\n[d2lbook:build.py:L112] INFO   Finished in 00:00:01\n[d2lbook:build.py:L121] INFO   \"d2lbook build eval\" finished in 00:00:02\n[d2lbook:build.py:L177] INFO   2 rst files are outdated\n[d2lbook:build.py:L179] INFO   Convert _build/eval/get_started.ipynb to _build/rst/get_started.rst\n[d2lbook:build.py:L179] INFO   Convert _build/eval/index.ipynb to _build/rst/index.rst\n[d2lbook:utils.py:L124] INFO   Run \"sphinx-build _build/rst _build/html -b html -c _build/rst -j 4\"\n\u001b[01mRunning Sphinx v2.2.2\u001b[39;49;00m\n\u001b[01mmaking output directory... \u001b[39;49;00mdone\n\u001b[01mbuilding [mo]: \u001b[39;49;00mtargets for 0 po files that are out of date\n\u001b[01mbuilding [html]\u001b[39;49;00m: targets for 2 source files that are out of date\n\u001b[01mupdating environment: \u001b[39;49;00m[new config] 2 added, 0 changed, 0 removed\n\u001b[01mreading sources... \u001b[39;49;00m[100%] \u001b[35mindex\u001b[39;49;00m                                                 \n\u001b[01mlooking for now-outdated files... \u001b[39;49;00mnone found\n\u001b[01mpickling environment... \u001b[39;49;00mdone\n\u001b[01mchecking consistency... \u001b[39;49;00mdone\n\u001b[01mpreparing documents... \u001b[39;49;00mdone\n\u001b[01mwriting output... \u001b[39;49;00m[100%] \u001b[32mindex\u001b[39;49;00m                                                  \n\u001b[01mwaiting for workers...\u001b[39;49;00m\n\u001b[01mgenerating indices... \u001b[39;49;00m genindexdone\n\u001b[01mwriting additional pages... \u001b[39;49;00m searchdone\n\u001b[01mcopying static files... ... \u001b[39;49;00mdone\n\u001b[01mcopying extra files... \u001b[39;49;00mdone\n\u001b[01mdumping search index in English (code: en)... \u001b[39;49;00mdone\n\u001b[01mdumping object inventory... \u001b[39;49;00mdone\n\u001b[01mbuild succeeded.\u001b[39;49;00m\n\nThe HTML pages are in _build/html.\n[d2lbook:build.py:L204] INFO   \"d2lbook build html\" finished in 00:00:04\n"
 }
]
```

The index HTML page is then available at `mybook/_build/html/index.html`.

## Configuration

You can customize how your book is built and published through `config.ini`.

```{.python .input  n=5}
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

```{.json .output n=5}
[
 {
  "name": "stdout",
  "output_type": "stream",
  "text": "Writing mybook/config.ini\n"
 }
]
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
