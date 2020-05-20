# Group Code Blocks into Tabs

Here is an example showing grouping code blocks into three tabs.

## Example

Let's implement $a+b$. We first show instructions, then demonstrate the codes.

:begin_tab:`python`
You need to have python installed

:end_tab:

:begin_tab:`numpy`
You can install numpy by
```bash
pip install numpy
```
:end_tab:

:begin_tab:`cpython`
Please install cpython
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
# Just a place holder
print(1+2)
```

Next let's implement $a - b$

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

## Usages

To enable multi-tabs, first configure the `tabs` entry in the `config.ini` file. For example, here we use `tabs = python, numpy, cpython`. `python` is the default tab. To specify a code block that doesn't belong to the default tab, add `#@tab`, followed by the tab name (case insensitive), in the first line of the code block.

Sometimes these codes blocks conflict with each others. We can activate one tab at a time, so only code blocks belong to this tab can be evaluated in Jupyter. For example

```bash
d2lbook activate default user/code_tabs.md  # activate the default tab
d2lbook activate numpy user/code_tabs.md    # activate the numpy tab
d2lbook activate all user/code_tabs.md      # activate all tabs
```
