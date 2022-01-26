# 构建本网站

您可能会发现建立这个网站是您项目的一个很好的起点。该网站的源代码可在以下位置获得 [demo/](https://github.com/d2l-ai/d2l-book/tree/master/demo).

请确保你安装了`git`（可以通过 `conda install git` 安装）、`numpy` 和 `matplotlib` （可以通过 `pip install numpy matplotlib` 安装）。以下命令将下载源代码、评估所有笔记本并生成 `ipynb` 、 `html` 和 `pdf` 格式的输出。

```sh
git clone https://github.com/d2l-ai/d2l-book
cd d2l-book/demo
d2lbook build all
```

完成后，您可以在 `_build` 文件夹中检查结果。例如，现在这个页面会在 `_build/html/index.html`，PDF版本会在 `_build/pdf/d2l-book.pdf`，所有评估的笔记本都会在 `_build/eval/` 下。
你可以单独生成以下特定的格式：

```sh
d2lbook build eval  # 评估笔记本并以 .ipynb 格式保存
d2lbook build html  # 构建 html 版本
d2lbook build pdf   # 构建 pdf 版本
```
