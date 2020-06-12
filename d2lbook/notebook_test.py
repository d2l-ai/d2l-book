from d2lbook import notebook
from d2lbook import build
from d2lbook import common
import unittest
import nbconvert

# 8 blocks:
# 0: markdown
# 1: markdown python2
# 2: markdown
# 3: markdown python2
# 4: markdown python3
# 5: code default
# 6: code python2
# 7: markdown 
_markdown_src = r'''# Test

first para

:begin_tab:`python2`
python is good
:end_tab:

another para

This is :eqref:`sec_1`

:begin_tab:`python2`
```python2
1+2+3
```
:end_tab:

:begin_tab:`python3`
python3 is better

- here
- haha

:end_tab:

```{.input .python}
1+2+3
```

```{.input .python}
#@tab python2
1+2+3
```

```bash
````
$ ls
````
```
'''

_multi_tab_cell = r'''# Test

```{.input .python}
#@tab python2, python3
1+2
```

The end
'''

_all_tab_cell = r'''# Test

```{.input .python}
#@tab all
1+2
```

Split

```{.input .python}
#@tab python2,python4
1122
```

:begin_tab:`python2,python3`
Here
:end_tab:
'''

class TestNotebook(unittest.TestCase):

    def test_split_markdown_cell(self):
        nb = notebook.read_markdown(_markdown_src)
        new_nb = notebook.split_markdown_cell(nb)
        cells = new_nb.cells
        self.assertEqual(len(cells), 8)
        self.assertEqual(cells[0].cell_type, 'markdown')
        self.assertEqual(cells[1].cell_type, 'markdown')
        self.assertEqual(cells[1].metadata['tab'], ['python2'])
        self.assertEqual(cells[2].cell_type, 'markdown')
        self.assertEqual('tab' in cells[2].metadata, False)
        self.assertEqual(cells[3].metadata['tab'], ['python2'])
        self.assertEqual(cells[4].metadata['tab'], ['python3'])
        self.assertEqual(cells[5].cell_type, 'code')
        self.assertEqual(cells[6].cell_type, 'code')

    def test_get_tab_notebook(self):
        nb = notebook.split_markdown_cell(notebook.read_markdown(_markdown_src))
        new_nb = notebook.get_tab_notebook(nb, tab='python2', default_tab='python3')
        cells = new_nb.cells
        self.assertEqual(cells[0].cell_type, 'markdown')
        self.assertEqual(cells[1].cell_type, 'markdown')
        self.assertEqual(cells[1].metadata['tab'], ['python2'])
        self.assertEqual(cells[2].cell_type, 'markdown')
        self.assertEqual('tab' in cells[2].metadata, False)
        self.assertEqual(cells[3].metadata['tab'], ['python2'])
        self.assertEqual(cells[4].cell_type, 'code')
        self.assertEqual(cells[4].metadata['tab'], ['python2'])
        self.assertEqual(len(cells), 6)

        new_nb = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3')
        cells = new_nb.cells
        self.assertEqual(cells[3].metadata['tab'], ['python3'])
        self.assertEqual(len(cells), 5)

        nb = notebook.read_markdown(_multi_tab_cell)
        cells = notebook.get_tab_notebook(nb, tab='python2', default_tab='python3').cells
        self.assertEqual(len(cells), 3)
        self.assertEqual(cells[1].metadata['tab'], ['python2'])

        cells = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3').cells
        self.assertEqual(len(cells), 3)
        self.assertEqual(cells[1].metadata['tab'], ['python3'])

    def _split_and_merge(self, nb, tabs):        
        split_nb = [notebook.get_tab_notebook(nb, tab, tabs[0]) for tab in tabs]
        merged_nb = notebook.merge_tab_notebooks(split_nb)
        return split_nb, merged_nb

    def test_merge_tab_notebooks(self):
        nb = notebook.split_markdown_cell(notebook.read_markdown(_markdown_src))
        _, new_nb = self._split_and_merge(nb, ['python3', 'python2'])
        self.assertEqual(len(nb.cells), len(new_nb.cells))
        for cell, new_cell in zip(nb.cells, new_nb.cells):
            if new_cell.source != cell.source:
                self.assertTrue(new_cell.source in cell.source)

    def test_add_html_tab(self):
        nb = notebook.split_markdown_cell(notebook.read_markdown(_markdown_src))
        _, new_nb = self._split_and_merge(nb, ['python3', 'python2'])
        new_nb = notebook.add_html_tab(new_nb, tabs=['python3', 'python2'])
        cells = new_nb.cells
        self.assertEqual(len(cells), 18)
        self.assertRegex(cells[1].source, 'mdl-js-tabs')
        self.assertRegex(cells[2].source, 'mdl-tabs__panel.*python2')
        self.assertRegex(cells[4].source, '</div>')
        self.assertRegex(cells[5].source, '</div>')
        self.assertRegex(cells[8].source, 'mdl-tabs__panel.*python3')
        self.assertRegex(cells[12].source, 'mdl-tabs__panel.*python2')

        nb = notebook.split_markdown_cell(notebook.read_markdown(_all_tab_cell))        
        _, new_nb = self._split_and_merge(nb, ['python3', 'python2', 'python4']) 
        cells = new_nb.cells
        self.assertEqual(len(cells), 5)
        self.assertEqual(cells[4].metadata['tab'], ['python3', 'python2'])

        new_nb = notebook.add_html_tab(new_nb, tabs=['python3', 'python2', 'python4'])
        cells = new_nb.cells
        self.assertEqual(len(cells), 15)
        self.assertRegex(cells[3].source, 'mdl-js-tabs')
        self.assertRegex(cells[4].source, 'mdl-tabs__panel.*python3')
        self.assertRegex(cells[7].source, 'mdl-tabs__panel.*python2')
        self.assertRegex(cells[11].source, 'mdl-tabs__panel.*python4')
        

if __name__ == '__main__':
    unittest.main()
