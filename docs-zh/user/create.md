# 创建你的项目
:label:`sec_create`

让我们以来自 scratch 的一个简单项目开始.

## Scratch 的羡慕

首先我们为我们的项目创建一个文件夹。

```{.python .input  n=1}
!mkdir -p mybook
```

然后创建两个页面。 `index.md` 是包含目录 (table of content，TOC) 的索引页，其中包含其他页 `get_started.md` 。请注意，TOC 是在带有标签 “toc” 的代码块中定义的。如果您熟悉 Sphinx，您会发现它类似于 Sphinx 中的 TOC 定义。请参考 :numref:`sec_markdown` 来了解更多 `d2lbook` 添加到 markdown 中的扩展 。另外请注意，我们使用内置魔法命令 `writefile` 将代码块保存到 [Jupyter] (https://ipython.readthedocs.io/en/stable/interactive/magics.html) 提供的文件中。

```{.python .input  n=2}
%%writefile mybook/index.md
# My Book

以 `d2lbook` 构建的项目—— mybook 的起始页。

````toc
get_started
````
```

```{.python .input  n=3}
%%writefile mybook/get_started.md
# Getting Started

Please first install my favorite package `numpy`.
```

现在让我们构建 html 版本。

```{.python .input  n=4}
!cd mybook && d2lbook build html
```

HTML 索引页 可以在 `mybook/_build/html/index.html` 目录中找到.

## 构造配置

你可以通过根文件夹上的 `config.ini` 来自定义构建结果和发布方式。

```{.python .input  n=5}
%%writefile mybook/config.ini

[project]
# Specify the PDF filename to mybook.pdf
name = mybook  
# Specify the authors names in PDF
author = Adam Smith, Alex Li  

[html]
# Add two links on the navbar. A link consists of three
# items: name, URL, and a fontawesome icon. Items are separated by commas.
header_links = PDF, https://book.d2l.ai/d2l-book.pdf, fas fa-file-pdf,
               Github, https://github.com/d2l-ai/d2l-book, fab fa-github
```

让我们清除并重新构建。

```{.python .input}
!cd mybook && rm -rf _build && d2lbook build html
```

如果再次打开 `index.html`，你将在导航栏上看到两个链接。

让我们构建 PDF 输出，您会在输出日志中找到 `Outputwritten on mybook.pdf (7 pages).`。

```{.python .input}
!cd mybook && d2lbook build pdf
```

我们将在以下部分介绍更多配置选项。您可以查看 [default_config.ini](https://github.com/d2l-ai/d2l-book/blob/master/d2lbook/config_default.ini) 了解所有配置选项及其默认值。还可以查看这些示例的 `config.ini`

- [This website](https://github.com/d2l-ai/d2l-book/blob/master/docs/config.ini)
- [Dive into Deep Learning](https://github.com/d2l-ai/d2l-en/blob/master/config.ini)

最后，让我们清理一下我们的工作区。

```{.python .input}
!rm -rf mybook
```
