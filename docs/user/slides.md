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

(((A tensor represents a (possibly multi-dimensional) array of numerical values. We can access a tensor's *shape*.
)))

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
````

You can see that we automatically copied the level-1 heading and the code block.
In addition, we copied the sentence between `(((` and `)))`, while dropped all other texts.

The second slide contains the following:

````md
Many operations can be applied elementwise,
e.g. `exp`

```{.python .input}
np.exp(x)
```
````


Besides the code block, it copied the contents between these three paris
(`[**`, `**]`),
(`(**`, `**)`), and
(`(~~`, `~~)`).
Here `[` means starting a new slide, while `(` means continuing the current slide.
(Level-1 heading will start a new slide, so we used `(` in the previous block).
And `**` slices a part from a line, why by repeating `[` or `(` three times means
copying multiple lines.  In addition, `~~` means the text will only appear in slides,
why not in the normal notebooks, htmls or pdfs.

One noticeable thing in the third slide is that, if we want to keep a non level-1
heading, we don't need to put `##` within the mark, as markdown reader will not
recognize it.

````
## Broadcasting Mechanism

Even when shapes differ, we can still perform elementwise operations

```{.python .input}
a = np.arange(3).reshape(3, 1)
b = np.arange(2).reshape(1, 2)
a, b
```
````
