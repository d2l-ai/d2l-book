# D2L-Book： “动手做” 书籍的工具箱

The D2L Book (`d2lbook`)软件包可以帮助你构建和发布**一本带有Python代码的书，**或者是**带有教程的Python软件包文档**。你可以查看书的例子 [Dive into Deep Learning](https://d2l.ai/) ，或者是 python 软件包文档的例子 [AutoGluon](https://autogluon.mxnet.io/) 。

`d2lbook` 旨在满足以下两个要求：

- 您的书中可能包含有**大量的 Python 代码**，并且您希望您的读者能够运行它们。或者您的软件包文档中有**多个实例教程**，并希望通过这些示例引导读者了解您的软件包的使用方法。这些代码应该是可运行和可维护的。

- 您希望同时发布 **HTML 网站和可打印的 PDF 版本** 两个版本。您希望网站应该是现代的、可搜索的和对移动端友好的，并且 PDF 版本应该与使用 LaTeX 编写的质量相同。


为了实现上述目标， `d2lbook` 结合了 Python 中广泛使用的交互式环境 [Jupyter Notebook](https://jupyter.org/) 和 Python 软件包中事实上的通用文档构建系统 [Sphinx](http://www.sphinx-doc.org/en/master/) 。具体来说，它的主要特点包括

- 使用 [markdown](https://daringfireball.net/projects/markdown/) 编写您的内容
- 一个最小的配置文件，用于自定义构建目标，以便您可以专注于内容。
- 在发布之前会自动评估所有代码并获得其输出，以验证其正确性。我们只评估更新过的代码来节省成本。
- 能够参考引用章节、图、表、方程式、函数和类别。
- 通过 Github 或 AWS 发布您的网站的管道。

如果 `d2lbook` 不符合您的要求，您可以查看以下工具：

- [Jupyter book](https://jupyterbook.org/intro)：与 `d2lbook` 非常相似，用于发布 Jupyter 笔记本。两个主要的设计差异是：1) `d2lbook` 鼓励你使用 markdown 文件格式，并在保存笔记本前删除所有代码输出。2) `d2lbook` 使用 Sphinx 而不是 Jupyter book 采用的 Jekyll 来构建文档。  Jekyll 更容易定制主题，而 Sphinx 对 PDF 和分析 Python 代码有更好的支持。注：目前 `Jupyter book` 也使用了 Sphinx 来构建文档。
- [gitbook](https://www.gitbook.com/)：如果您不需要将它们作为 Jupyter 笔记本运行，那么使用这个来推送用 markdown 编写的书非常方便。
- [sphinx-gallery](https://sphinx-gallery.github.io/stable/index.html)：这是一个Sphinx插件，用来评估和发布你的教程。它要求你知道如何使用 Sphinx 并以 `.py` 格式和 `rst` 风格编写你的教程。

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

