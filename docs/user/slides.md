# Creating Slides

We can mark a notebook and then create slides from that notebook. For example, here is the generate [slides](https://nbviewer.jupyter.org/format/slides/github/d2l-ai/d2l-pytorch-slides/blob/main/chapter_preliminaries/ndarray.ipynb#/) from the markdown [source file](https://github.com/d2l-ai/d2l-en/blob/master/chapter_preliminaries/ndarray.md).
Let explain how to do it by the following example. It's a markdown file with marks to
generate slides.

````md
# Data Manipulation

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

````

The above code block will generate 2 slides. The first slide contains the following contents:

````md
# Data Manipulation

A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.

```{.python .input}
import numpy as np

x = np.arange(12)
x
```
````

You can see that we automatically copied the level-1 heading and the code block.
In addition, we copied the text between `(**` and `**)`, while dropped all others.

The second slide contains the following:

````md
Many operations can be applied elementwise,
e.g. `exp`

```{.python .input}
np.exp(x)
```

Even when shapes differ, we can still perform elementwise operations

```{.python .input}
a = np.arange(3).reshape(3, 1)
b = np.arange(2).reshape(1, 2)
a, b
```
````

First you can see is that all text between these three paris
(`[**`, `**]`),
(`(**`, `**)`), and
(`(~~`, `~~)`) are kept.
Here `[` means starting a new slide, while `(` means continuing the current slide.
(Level-1 heading will start a new slide, so we used `(` in the previous block).
In addition, `~~` means the text will only appear in slides,
why not in the normal notebooks, htmls or pdfs.

Second, we didn't start a new slide before the last code block, i.e. there is no
level-1 heading and no (`[**`, `**]`) pair, so the last two code blocks are merged
into the same slide.
