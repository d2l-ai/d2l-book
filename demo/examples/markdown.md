# Markdown Cells

The `d2lbook` provide additional features beyond the normal markdown supports in
Jupyter.

## Table of Contents

You can use a `toc` code block to specify the table of contents.
Here `:maxdepth: 2` means display two levels of files, and `:numbered:` means
adding number to each section (default is not enabled). Also note that you don't
need to specify the file extension.

`````
```toc
:maxdepth: 2
:numbered:

index
guide/index
```
`````

## Images


We can specify the image caption in `[]`. In addition, we can use
`:width:value:` for the image width, similar `:height:` for height.

```
![Estimating the length of a footg](../img/koebel.jpg)
:width:300px:
```

![Estimating the length of a footg](../img/koebel.jpg)
:width:300px:


### SVG Images

We recommend you to use SVG images as much as you can. It is sharp and its size
is small. But since Latex doesn't support SVG images, if you want to build a PDF
output, you need to install `rsvg-convert`. On Macos, you can simply
`brew install librsvg` or `sudo apt-get install librsvg2-bin` for Ubuntu.

![A LSTM cell in SVG](../img/lstm.svg)


## Cross Reference


We often want to reference sections, figures, tables and equations in a book.

### Section
:label:my.sec0:


We can put a label immediately after the section title. The label format is
`:label:TEXT:`, you can replace `TEXT` with any string contains char in
`a-zA-Z0-9._-`. For example

```
### Section
:label:my.sec0:
```

Then we can ref to it through `:ref:TEXT:`, e.g. :ref:my.sec0:. We can cross
reference label from other files as well, e.g. :ref:sec.code:.

### Image


Similarly we can have a `:label:TEXT:` after the image. Then it can be
referenced through `:numref:TEXT:`. The difference between `ref` to `numref` is
that the former will have a the section title as link text while the later is
the figure number such as `Fig 1.1`. .

```
![A nice image with a cat and a dog](../img/catdog.jpg)
:width:300px:
:label:img.catdog:
```


![A nice image with a cat and a dog](../img/catdog.jpg)
:width:300px:
:label:img.catdog:

As can be seen from :numref:img.catdog:, there is a cat and a dog.

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

## Citation

First put your bib file at somewhere. All references will be displayed on the HTML page it
inserted, but them will be put at the end in the PDF always.

```
:bibliography:../refs.bib:
```

Then we can cite a paper through `:cite:BIB_KEY:`. For example:

The breakthrough of deep learning origins from :cite:krizhevsky2012imagenet: for
computer vision, there is a rich of following up works, such as
:cite:he2016deep:. NLP is catching up as well, the recent work
:cite:devlin2018bert: shows significant improvements.

## References

:bibliography:../refs.bib:
