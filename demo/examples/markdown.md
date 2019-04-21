# Markdown Cells


## Images

![A nice image with a cat and a dog](../img/catdog.jpg)
:width:400px:


### SVG Images

Need to install `rsvg-convert` to build latex. On macos, you can
`brew install librsvg`.

![A LSTM cell](../img/lstm.svg)

## Reference

### Section
:label:my_sec:

```
### Section
:label:my_sec:
```


We learn from :ref:my_sec: that we can reference a section through `:ref:`.


### Image

```
![Estimating the length of a footg](../img/koebel.jpg)
:label:koebel:
:width:400px:
```

![Estimating the length of a footg](../img/koebel.jpg)
:label:koebel:
:width:400px:


Now we can refer this image throuh `:numref:koebel:`: as we can seen from
:numref:koebel:, we saw people in a line.

### Table


:label:table:
:This a is very long table caption. It will breaks into several lines. And
contains a math equation as well. $z_{ij} = \sum_{k}x_{ik}y_{kj}$.

| Year | Number | Comment |
| ---  | --- | --- |
| 2018 | 100 | Good year |
| 2019 | 200 | Even better |

Cite :numref:table:

### Equations

We define the linear model in :eqref:linear:.

$$\hat{\mathbf{y}}=\mathbf X \mathbf{w}+b$$
:eqlabel:linear:
