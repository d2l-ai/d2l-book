# 编辑源文件

无论是纯文本文件还是 Jupyter notebook，我们都建议您将其保存为 markdown 文件。如果是 Jupyter notebook ，可以在保存前清空输出，方便代码审查和版本控制。

您可以使用自己喜欢的 markdown 编辑器，例如[Typora](https://www.typora.io/)，用来直接编辑 markdown 文件。我们扩展了 markdown 以支持附加功能，例如图像/表格标题和引用参考文献，请参阅 :numref:`sec_markdown` 了解更多详细信息。对于 Jupyter notebook 来说，一个 Jupyter 源代码块会被放置在一个带有 `{.python .input}` 标签的 markdown 代码块中，例如，

````
```{.python .input}
print('this is a Jupyter code cell')
```
````

我们另一种推荐的做法是直接使用 Jupyter 编辑 markdown 文件，尤其是它包含代码块的时候。 Jupyter 默认的文件格式是 ipynb ，我们可以使用 notedown 插件让 Jupyter 打开并保存 markdown 文件。

你可以通过以下命令安装它： 

```bash
pip install mu-notedown
```

（`mu-notedown` 是 [notedown](https://github.com/aaren/notedown) 的一个分支，与源文件存在几个修改。安装之前，你可能需要先卸载原来的 `notedown`。）

如果要在运行 Jupyter Notebook 时默认打开 “notedown” 插件，请执行以下操作：首先，生成一个 Jupyter Notebook 配置文件（如果已经生成，则可以跳过此步骤）。

```bash
jupyter notebook --generate-config
```

然后，在 Jupyter 笔记本电脑配置文件的末尾添加以下行（对于Linux/macOS，通常位于路径 `~/.Jupyter/Jupyter_Notebook_config.py` ）：

```bash
c.NotebookApp.contents_manager_class = 'notedown.NotedownContentsManager'
```

接下来重新启动 Jupyter，您现在应该可以在 Jupyter 中将这些 markdown 作为 Jupyter notebook 打开。

![Use Jupyter to edit :numref:`sec_create`](../img/jupyter.png)
:width:`500px`
