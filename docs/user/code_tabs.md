# Codes with Multi-tabs 

Implement $a+b$:

```{.python .input  n=4}
a = [1,1,1]
b = [2,2,2]
[ia+ib for ia, ib in zip(a,b)]
```

```{.python .input  n=4}
#@tab numpy
import numpy as np
a = np.ones(3)
b = np.ones(3)*2
a + b
```

```{.python .input  n=4}
#@tab cpython
# Just a place holder
print(1+2)
```

Next let's implement $a - b$

```{.python .input  n=4}
a = [1,1,1]
b = [2,2,2]
[ia-ib for ia, ib in zip(a,b)]
```

```{.python .input  n=4}
#@tab numpy
a = np.ones(3)
b = np.ones(3)*2
a - b
```

