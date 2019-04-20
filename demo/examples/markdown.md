# Markdown Cells

## Insert an image

```markdown
{% label catdog %}
![A nice image with a cat and a dog](../img/catdog.jpg)
```

{= label catdog =}
![A nice image with a cat and a dog](../img/catdog.jpg)


Insert a SVG file

label lstm
![A LSTM cell](../img/lstm.svg)

## Reference an image

```markdown
{% ref catdog %}
```

Check {% ref catdog %} for an image with a cat and a dog. You can refer it from
another page as well.
