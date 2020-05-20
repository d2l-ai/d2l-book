from d2lbook import markdown
import unittest

_markdown_src = r'''
# Test

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

class TestMarkdown(unittest.TestCase):

    def test_split(self):
        cells = markdown.split_markdown(_markdown_src)
        self.assertEqual(len(cells), 7)
        self.assertEqual(cells[0]['type'], 'markdown')
        self.assertEqual(cells[1]['type'], 'markdown')
        self.assertEqual(cells[1]['class'], '`python2`')
        self.assertEqual(cells[3]['class'], '`python 3`')
        self.assertEqual(cells[5]['class'], 'bash')

    def test_merge(self):
        cells = markdown.split_markdown(_markdown_src)
        src = markdown.join_markdown_cells(cells)
        self.assertEqual(_markdown_src, src)

if __name__ == '__main__':
    unittest.main()
