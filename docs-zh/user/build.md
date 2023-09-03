# 构建 

本节我们将解释构建项目的各种选项。这些选项可分为四类：

1. 完整性检查
   - `d2lbook build linkcheck` 将检查是否所有内部和外部链接都可以访问。  
   - `d2lbook build outputcheck` 将检查是否没有 notebook 将包含代码输出
1. 构建结果
   - `d2lbook build html`: 将构建 HTML 版本到 `_build/html`
   - `d2lbook build pdf`: 将构建 PDF 版本到 `_build/pdf`
   - `d2lbook build pkg`: 构建一个包含所有 `.ipynb` 格式 Jupyter notebook 的 zip 文件
1. 附加功能   
   - `d2lbook build colab`: 将所有 notebook 转换为可以在 Google Colab 上运行的文件并保存到 `_build/colab`。更多信息请参见 :numref:`sec_colab`
   - `d2lbook build lib`: 构建一个 Python 包，以便我们可以在其他笔记本中重用代码。更多信息请参见 XXX 。
1. 内部阶段，通常是自动触发的。
   - `d2lbook build eval`: 评估所有笔记本并将它们作为 `.ipynb` 笔记本保存到`_build/eval`
   - `d2lbook build rst`: 将所有笔记本转换为 `rst` 文件并在 `_build/rst` 中创建一个 Sphinx 项目
   

## 构建时的缓存

我们鼓励您使用内置的自动化评估您的笔记本以获得代码单元结果，而不是将这些结果保存在源文件中，原因有两个：
   1. 这些结果使代码审查变得困难，尤其是当它们由于数值精度或随机数生成器而具有随机性时。 

   1. 一段时间未评估的笔记本可能因升级包而损坏。 

但是评估会在构建过程中产生额外的开销。因此，我们建议将每个笔记本的运行时间限制在几分钟内。并且 `d2lbook` 将重用之前构建的并且只评估修改后的笔记本。

例如，由于训练神经网络，[Dive into Deep Learning](https://d2l.ai) 中的笔记本（部分）在 GPU 机器上的平均运行时间约为 2 分钟。它包含 100 多个笔记本，这使得总运行时间多达 2-3 小时。但是，实际上，每次代码更改只会修改其中几个笔记本，因此 [构建时间](http://ci.d2l.ai/blue/organizations/jenkins/d2l-en/activity) 通常不到 10 分钟。

让我们看看它是如何工作的。首先我们像这一节创建一个项目 :numref:`sec_create`. 

```{.python .input}
!mkdir -p cache
```

```{.python .input}
%%writefile cache/index.md
# My Book

通过 `d2lbook`创建 my book 的起始页

````toc
get_started
````
```

```{.python .input}
%%writefile cache/get_started.md
# 开始

首先请安装我最喜欢的包 `numpy`。
```

```{.python .input}
!cd cache; d2lbook build html
```

你可以看到 `index.md` 被评估了。 （虽然它不包含代码，但可以将其作为 Jupyter notebook 评估。）如果再次构建，我们将看到不会评估任何 notebook 。

```{.python .input}
!cd cache; d2lbook build html
```

现在让我们修改 `get_started.md` ，你会看到它会被重新评估，但不包括 `index.md` 。

```{.python .input}
%%writefile cache/get_started.md
# 开始写入的内容

首先请安装我最喜欢的包 `numpy>=1.18`.
```

```{.python .input}
!cd cache; d2lbook build html
```

触发从头开始重新构建的一种方法是删除 `_build/eval` 中保存的 notebook ，或者直接删除 `_build` 。另一种方法是重新指定一些依赖项。例如，在下面的单元格中，我们将 `config.ini` 添加到依赖项中。每次修改 config.ini 都会使所有 notebook 的缓存失效，并触发从头开始重新构建。


```{.python .input}
%%writefile cache/config.ini

[build]
dependencies = config.ini
```

```{.python .input}
!cd cache; d2lbook build html
```

最后，让我们清理一下我们的工作区。

```{.python .input}
!rm -rf cache
```
