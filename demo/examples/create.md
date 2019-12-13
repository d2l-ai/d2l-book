# Create Your Project 

Let's start with a simple project from scratch. 

## Project From Scratch

First make a folder for our project. 

```{.python .input}
!rm -rf mybook; mkdir mybook
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


