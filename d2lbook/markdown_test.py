from d2lbook import markdown, common
import unittest

_markdown_src = r'''# Test

first para

:begin_tab:`python2`
python is good
:end_tab:

another para

:eqref:`sec_1`

:begin_tab:`python 3`
python3 is better

```python 3
print(3)
```
:end_tab:

````bash
```bash
$ ls
```
````
'''

_markdown_text_src = r'''# Test
:label:`sec`

THis is good. A paragraph.

![Image](../a.png)
:label:`a.png`

Assume A

$$
X^{(N)} = \sum_{i=1}^N X_i.
$$
:label:`adsf`

and

$$\|\boldsymbol{x}\|_2 = \sqrt{\sum_{i=1}^n x_i^2}.$$

Here is a list
- sadf
  wer
  - asdf sadf
    sd sdf
- asdf

1. wer asdf
  asdf asdf

1. Run the code in this section. Change the conditional statement `x == y` in this section to `x < y` or `x > y`, and then see what kind of tensor you can get.
1. Replace the two tensors that operate by element in the broadcasting mechanism with other shapes, e.g., 3-dimensional tensors. Is the result the same as expected?
'''

class TestMarkdown(unittest.TestCase):

    def test_split(self):
        cells = markdown.split_markdown(_markdown_src)
        self.assertEqual(len(cells), 5)
        self.assertEqual(cells[0]['type'], 'markdown')
        self.assertEqual(cells[1]['type'], 'markdown')
        self.assertEqual(cells[1]['class'], '`python2`')
        self.assertEqual(cells[3]['class'], '`python 3`')
        self.assertEqual(cells[4]['class'], 'bash')

    def test_merge(self):
        cells = markdown.split_markdown(_markdown_src)
        src = markdown.join_markdown_cells(cells)
        self.assertEqual(_markdown_src, src)

    def test_split_text(self):
        cells = markdown.split_text(_markdown_text_src)
        common.print_list(cells)

    def test_join_text(self):
        cells = markdown.split_text(_markdown_text_src)
        src = markdown.join_text(cells)
        self.assertEqual(_markdown_text_src, src)


if __name__ == '__main__':
    unittest.main()
