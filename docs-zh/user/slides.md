# 创建幻灯片


我们可以标记一个笔记本，然后从该笔记本中创建幻灯片。例如，这里是从 markdown 的 [源文件](https://github.com/d2l-ai/d2l-en/blob/master/chapter_preliminaries/ndarray.md) 中生成的 [幻灯片](https://nbviewer.jupyter.org/format/slides/github/d2l-ai/d2l-pytorch-slides/blob/main/chapter_preliminaries/ndarray.ipynb#/) 。让我们通过下面的例子来解释如何做到这一点。这是一个带有标记的 markdown 文件，用来生成幻灯片。

````md
# Data Manipulation

## Getting Started

To start, we can use `arange` to create a row vector `x`
containing the first 12 integers starting with 0,
though they are created as floats by default.

(**A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.**)


```{.python .input}
import numpy as np

x = np.arange(12)
x
```

[**Many**] more (**operations can be applied elementwise,**)
including unary operators like exponentiation.
(~~e.g. `exp`~~)

```{.python .input}
np.exp(x)
```

(**Even when shapes differ, we can still perform elementwise operations**)
by invoking the *broadcasting mechanism*.


```{.python .input}
a = np.arange(3).reshape(3, 1)
b = np.arange(2).reshape(1, 2)
a, b
```

````

上面的代码块将生成 2 张幻灯片。第一张幻灯片包含以下内容：

````md
# Data Manipulation

A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.

```{.python .input}
import numpy as np

x = np.arange(12)
x
```
````

您可以看到我们自动复制了一级标题和代码块。
此外，我们复制了 `(**` 和 `**)` 之间的文本，而删除了所有其他的文本。

第二张幻灯片包含以下内容：

````md
Many operations can be applied elementwise,
e.g. `exp`

```{.python .input}
np.exp(x)
```

Even when shapes differ, we can still perform elementwise operations

```{.python .input}
a = np.arange(3).reshape(3, 1)
b = np.arange(2).reshape(1, 2)
a, b
```
````

首先，你可以看到 
(`[**`, `**]`)，
(`(**`, `**)`) 和
(`(~~`, `~~)`) 这三个部分之间的所有文本被保留了。
在这里， `[` 表示开始一张新幻灯片，而 `(` 表示继续当前幻灯片。
一级标题 (`[**`, `**]`) 内的文本将开始一张新幻灯片，因此我们在上一个块中使用了`(` 来连接两段标题的文本 。
另外，`~~` 表示文本只会出现在幻灯片中，不会在普通 notebook 、html 或 pdf 中出现。

其次，我们没有在最后一个代码块之前开始新的幻灯片，没有一级标题，也没有 (`[**`, `**]`) 对，所以最后两个代码块合并到同一张幻灯片。
