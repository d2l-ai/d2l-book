# Markdown Cells

## Insert an image

```
![A nice image with a cat and a dog](../img/catdog.jpg)
```

.. _label:

![A nice image with a cat and a dog](../img/catdog.jpg)


Insert a SVG file

.. _lstm:

![A LSTM cell](../img/lstm.svg)

.. _mysec:

## Reference an image

```
{% ref catdog %}
```

Check :numref:`label`.
Check  for an image with a cat and a dog. You can refer it from
another page as well.

.. _myeq:

$$\sum_{i=1}^n a_i + b_i$$
