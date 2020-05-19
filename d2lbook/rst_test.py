from d2lbook import notebook
from d2lbook import rst
import unittest
import nbconvert

_markdown_src = r'''
# Test
:label:`test`

first para

python is good

another para

This is :eqref:`sec_1`

```python2
1+2+3
```

python3 is better

- here
- haha


```{.input .python}
1+2+3
```

```{.input .python}
#@tab python2
1+2+3
```

```bash
````
aa
````
```

## Section 2
:label:`sec_2`

```eval_rst
.. only:: html

   Table of Contents
   -----------------
```

```toc
:numbered:
:maxdepth: 2

install
user/index
develop/index
```

![Estimating the length of a foot](../img/koebel.jpg)
:width:`400px`
'''


class TestRst(unittest.TestCase):

    # TODO(mli) add some asserts
    def test_convert_notebook(self):
        nb = notebook.read_markdown(_markdown_src)
        body, _ = rst.convert_notebook(nb, {})
        # print(body)
