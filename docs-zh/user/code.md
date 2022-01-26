# 代码单元格
:label:`sec_code`

## 最大行长（maximum line length）

我们建议您将代码的最大行长限制在 78 内以避免 PDF 中的自动换行。您可以在 [nbextensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions) 中启用标尺扩展，以便在编写代码时在 Jupyter 中添加可视垂直线。

```{.python .input}
'-' * 78
```

## 隐藏源代码和输出

我们可以通过在单元格中添加注释行 `# Hide code` 来隐藏代码单元格的源代码。我们还可以使用 `# Hide outputs` 隐藏代码单元格的输出

举个例子，这里是正常的代码单元:

```{.python .input}
1+2+3
```

让我们把源代码隐藏起来

```{.python .input}
# Hide code
1+2+3
```

还可以尝试一下隐藏输出

```{.python .input}
# Hide outputs
1+2+3
```

## 绘图
我们建议您使用 `svg` 格式来绘制图形。比如下面的代码调用了 `matplotlib` 来绘图

```{.python .input  n=3}
%matplotlib inline
from IPython import display
from matplotlib import pyplot as plt
import numpy as np

display.set_matplotlib_formats('svg')

x = np.arange(0, 10, 0.1)
plt.plot(x, np.sin(x));
```
