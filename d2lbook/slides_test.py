from d2lbook import slides, notebook, common
import unittest
import time
import logging
import os

# from docs/user/slides.md

_md = '''# Data Manipulation

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
'''

class TestSlides(unittest.TestCase):
    def test_match_pairs(self):
        matched = slides._match_slide_marks(_md)
        common.print_list(matched)
        self.assertEqual(len(matched), 5)

    def test_generate_slides(self):
        nb = notebook.read_markdown(_md)
        nb = slides._generate_slides(nb)
        common.print_list(nb.cells)
        self.assertEqual(len(nb.cells), 6)

    def test_remove_slide_marks(self):
        nb = notebook.read_markdown(_md)
        nb = slides.remove_slide_marks(nb)
        common.print_list(nb.cells)

if __name__ == '__main__':
    unittest.main()
