# Group Code Blocks into Tabs

下面是一个例子，显示了如何将代码块分组为三个选修卡。

## 例子

让我们实现$a+b$。我们先展示说明，然后演示代码。

:begin_tab:`python`
你需要安装先 python

:end_tab:

:begin_tab:`numpy`
你可以通过以下命令安装 numpy
```bash
pip install numpy
```
:end_tab:

:begin_tab:`cpython`
请安装 cpython
:end_tab:


```{.python .input}
a = [1,1,1]
b = [2,2,2]
[ia+ib for ia, ib in zip(a,b)]
```

```{.python .input}
#@tab numpy
import numpy as np
a = np.ones(3)
b = np.ones(3)*2
a + b
```

```{.python .input}
#@tab cpython
# 只是一个占位符
print(1+2)
```

下一步让我们展示 $a - b$

```{.python .input}
a = [1,1,1]
b = [2,2,2]
[ia-ib for ia, ib in zip(a,b)]
```

```{.python .input}
#@tab numpy
a = np.ones(3)
b = np.ones(3)*2
a - b
```

```{.python .input}
#@tab cpython
# 只是一个占位符
print(1-2)
```

## 使用方法



要启用多选项卡，首先在 `config.ini` 文件中配置 `tabs` 条目。举个例子，这里我们配置选项为 `tabs = python, numpy, cpython`。 `python` 是默认选项卡。要指定不属于默认选项卡 （python） 的代码块，请在代码块的第一行添加 `#@tab` ，后跟选项卡名称（不区分大小写）。

有时这些代码块会相互冲突。我们可以一次激活一个选项卡，这样就只有属于该选项卡的代码块才能在 Jupyter 中进行评估。例如：

```bash
d2lbook activate default user/code_tabs.md  # activate the default tab
d2lbook activate numpy user/code_tabs.md    # activate the numpy tab
d2lbook activate all user/code_tabs.md      # activate all tabs
```
