from tabtool import notebook
from tabtool import rst
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

$x=1$, :numref:`sec_2`
'''

class TestRst(unittest.TestCase):

    # TODO(mli) add some asserts
    def test_convert_notebook(self):
        nb = notebook.read_markdown(_markdown_src)
        body, _ = rst.convert_notebook(nb, {})
        lines = body.split('\n')

        for l in lines:
            if l.startswith(':math:`x=1`'):
                self.assertEqual(l, ':math:`x=1`, :numref:`sec_2`')

