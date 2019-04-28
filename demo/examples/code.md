# Code Cells
:label:`sec_code`

```{.python .input}
%matplotlib inline

1+2
```

```bash
ls .
```

```
1+2+3
```

```{.python .input}
%matplotlib inline

print(['test']*10)
1+2
```


```{.python .input  n=3}
from IPython import display
from matplotlib import pyplot as plt
import numpy as np

display.set_matplotlib_formats('svg')

x = np.arange(0, 10, 0.1)
plt.plot(x, np.sin(x))
plt.show()
```
