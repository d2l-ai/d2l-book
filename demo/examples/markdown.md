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

guide/index
```
`````

## Images


We can put the image caption in `[]`. In addition, we can use
`:width:value:` to specify the image width, similar `:height:value:` for height.

```
![Estimating the length of a foot](../img/koebel.jpg)
:width:400px:
```

![Estimating the length of a foot](../img/koebel.jpg)
:width:400px:


### SVG Images

We recommend you to use SVG images as much as you can. It is sharp and its size
is small. But since Latex doesn't support SVG images, if you want to build a PDF
output, you need to install `rsvg-convert`. On Macos, you can simply
`brew install librsvg` or `sudo apt-get install librsvg2-bin` for Ubuntu.

![A LSTM cell in SVG](../img/lstm.svg)

## Tables

You can insert table caption before the table by starting it with a `:`. Note
that you need to leave an empty line between the caption and the table itself.

```
: The number is computed by $z_{ij} = \sum_{k}x_{ik}y_{kj}$.

| Year | Number | Comment |
| ---  | --- | --- |
| 2018 | 100 | Good year |
| 2019 | 200 | Even better |
```

: The number is computed by $z_{ij} = \sum_{k}x_{ik}y_{kj}$.

| Year | Number | Comment |
| ---  | --- | --- |
| 2018 | 100 | Good year |
| 2019 | 200 | Even better |

## Cross References

We often want to reference sections, figures, tables and equations in a book.

### Referencing Sections
:label:my-sec3:

We can put a label immediately after the section title to allow this section to
be referenced by its label. The label format is
`:label:TEXT:`, you can replace `TEXT` with any string contains chars in
`a-zA-Z0-9._-`. For example, we create a label called `my-sec3` for this section.

```
### Referencing Sections
:label:my-sec3:
```

Then we can reference this section through `:ref:my-sec3:`, i.e. :ref:my-sec3:,
which will display the referenced section title with a clickable link. We can
also use a numbered version by `:numref:my-sec3:`, i.e. :numref:my-sec3:.

If the label is incorrect, say we put `my-sec2` here, the build log will
contains a warning such as

```
WARNING: undefined label: my-sec2
```

You can turn it into error by setting `warning_is_error = True` in
`config.ini`.

Besides, we can cross
reference label from other files as well, e.g. :numref:sec.code:. This applies
to figures, tables and equations as well.


### Referencing Images

Similarly we can have a `:label:TEXT:` after the image. Then it can be
referenced through `:numref:TEXT:`. For example,

```
![A nice image with a cat and a dog.](../img/catdog.jpg)
:width:300px:
:label:img.catdog:
```


![A nice image with a cat and a dog.](../img/catdog.jpg)
:width:300px:
:label:img.catdog:

As can be seen from :numref:img.catdog:, there is a cat and a dog. We can also
use `:ref:img.catdog:`(e.g. :ref:img.catdog:) to replace the figure ID with its
caption.

### Referencing Tables

We can also put a `:label:TEXT:` after the table to cite it later.

```
:This a is very long table caption. It will breaks into several lines. And
contains a math equation as well. $z_{ij} = \sum_{k}x_{ik}y_{kj}$.

| Year | Number | Comment |
| ---  | --- | --- |
| 2018 | 100 | Good year |
:label:table:

```


:This a is very long table caption. It will breaks into several lines. And
contains a math equation as well. $z_{ij} = \sum_{k}x_{ik}y_{kj}$.

| Year | Number | Comment |
| ---  | --- | --- |
| 2018 | 100 | Good year |
:label:table:

Cite it :numref:table:.

### Referencing Equations

The difference here is that we need to use `eqlabel` instead of `label`. For
example

```
$$\hat{\mathbf{y}}=\mathbf X \mathbf{w}+b$$
:eqlabel:linear:
```

$$\hat{\mathbf{y}}=\mathbf X \mathbf{w}+b$$
:eqlabel:linear:

Then use `:eqref:linear:` to refer this equation. For example,
In :eqref:linear:, we define the linear model.


## Citations

First put your bib file at somewhere. All references will be displayed on the
place it inserted in HTML. But in PDF, all references will be moved to end of
the document.

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
