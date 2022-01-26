# Installation

 `d2lbook` 包已经在 macOS 和 Linux 平台上通过了测试。  (欢迎你为 windows 平台上的发行版本做出贡献).

首先确保你有可用的 [pip](https://pip.pypa.io/en/stable/) 。 在选项中，我们建议使用 [conda](https://docs.conda.io/en/latest/miniconda.html) 安装 `pip` 不支持的库。

现在开始安装命令行界面

```sh
pip install git+https://github.com/d2l-ai/d2l-book
```

这就成功安装了 [d2lbook pip package](https://pypi.org/project/d2lbook/)， 但我们建议您直接安装在 Github 上的最新版本，因为它正在快速开发中。

为了构建 HTML 版本, 我们需要 [pandoc](https://pandoc.org/)。 你可以通过 `conda install pandoc` 安装它。

构建 PDF 版本需要[LibRsvg](https://wiki.gnome.org/Projects/LibRsvg) 去转换你的 SVG 格式图片(我们推荐的格式)，你可以通过 `conda install librsvg` 安装。当然，你你还需要有一个LaTeX发行版，例如 [Tex Live](https://www.tug.org/texlive/)，可用。
