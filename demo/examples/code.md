# Code Cells
:label:`sec_code`

```{.python .input}

1+2
```

```{.python .input}
!ls .
```

## Hide Source and Outputs

We can hide the source of a code cell by adding a comment line `# Hide
code` in the cell. We can also hide the code cell outputs using `# Hide outputs`

For example, here is the normal code cell:

```{.python .input}
1+2+3
```

Let's hide the source codes
```{.python .input}
# Hide code
1+2+3
```

Also try hiding the outputs
```{.python .input}
# Hide outputs
1+2+3
```

## Plot

```{.python .input  n=3}
%matplotlib inline
from IPython import display
from matplotlib import pyplot as plt
import numpy as np

display.set_matplotlib_formats('svg')

x = np.arange(0, 10, 0.1)
plt.plot(x, np.sin(x));
```
