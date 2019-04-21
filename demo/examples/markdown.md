# Markdown Cells

## Insert an image

```markdown
![A nice image with a cat and a dog](../img/catdog.jpg)
```

.. _label:

![A nice image with a cat and a dog](../img/catdog.jpg)


Insert a SVG file

.. _label:

![A LSTM cell](../img/lstm.svg)

## Reference an image

```markdown
{% ref catdog %}
```

Check :numref:`label`.
Check  for an image with a cat and a dog. You can refer it from
another page as well.
