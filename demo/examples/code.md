# Code Cells

```{.python .input  n=1}
from IPython import display
from matplotlib import pyplot as plt
import numpy as np

display.set_matplotlib_formats('svg')

x = np.arange(0, 10, 0.1)
plt.plot(x, np.sin(x));
```
