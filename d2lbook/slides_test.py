from d2lbook import slides
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

(((A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.
)))

[**this is not a slide mark**](https://d2l.ai)

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

## [**Broadcasting Mechanism**]

(**Even when shapes differ, we can still perform elementwise operations**)
by invoking the *broadcasting mechanism*.


```{.python .input}
a = np.arange(3).reshape(3, 1)
b = np.arange(2).reshape(1, 2)
a, b
```

````

The above code block will generate 3 slides. The first slide contains the following contents:

````md
# Data Manipulation

A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.

```{.python .input}
import numpy as np

x = np.arange(12)
x
```
'''

class TestSlides(unittest.TestCase):
    def test_match_pairs(self):
        self.assertEqual(slides._match_slide_marks(
            _md
        ), [((
            '(((', ')))'
        ), "A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.\n"
             ), (('[**', '**]'), 'Many'),
            (('(**', '**)'), 'operations can be applied elementwise,'),
            (('(~~', '~~)'), 'e.g. `exp`'),
            (('[**', '**]'), 'Broadcasting Mechanism'),
            (('(**', '**)'),
             'Even when shapes differ, we can still perform elementwise operations'
             )])

if __name__ == '__main__':
    unittest.main()
