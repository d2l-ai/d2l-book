from d2lbook import notebook
from d2lbook import build
import unittest
import nbconvert


_markdown_src = r'''
# Test

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

_multi_tab_cell = r'''
# Test

```{.input .python}
#@tab python2, python3
1+2
```

The end
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
        self.assertEqual(cells[1].metadata['tab'], 'python2')
        self.assertEqual(cells[2].cell_type, 'markdown')
        self.assertEqual('tab' in cells[2].metadata, False)
        self.assertEqual(cells[3].metadata['tab'], 'python2')
        self.assertEqual(cells[4].cell_type, 'code')
        self.assertEqual(cells[4].metadata['tab'], 'python2')
        self.assertEqual(len(cells), 6)

        new_nb = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3')
        cells = new_nb.cells
        self.assertEqual(cells[3].metadata['tab'], 'python3')
        self.assertEqual(len(cells), 5)

        nb = notebook.read_markdown(_multi_tab_cell)
        cells = notebook.get_tab_notebook(nb, tab='python2', default_tab='python3').cells
        self.assertEqual(len(cells), 3)
        self.assertEqual(cells[1].metadata['tab'], 'python2')

        cells = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3').cells
        self.assertEqual(len(cells), 3)
        self.assertEqual(cells[1].metadata['tab'], 'python3')

    def test_merge_tab_notebooks(self):
        nb = notebook.split_markdown_cell(notebook.read_markdown(_markdown_src))
        nb2 = notebook.get_tab_notebook(nb, tab='python2', default_tab='python3')
        nb3 = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3')
        new_nb = notebook.merge_tab_notebooks([nb2, nb3])
        self.assertEqual(len(nb.cells), len(new_nb.cells))
        for cell, new_cell in zip(nb.cells, new_nb.cells):
            if new_cell.source != cell.source:
                self.assertTrue(new_cell.source in cell.source)

    def test_add_html_tab(self):
        nb = notebook.split_markdown_cell(notebook.read_markdown(_markdown_src))
        nb2 = notebook.get_tab_notebook(nb, tab='python2', default_tab='python3')
        nb3 = notebook.get_tab_notebook(nb, tab='python3', default_tab='python3')
        nb4 = notebook.merge_tab_notebooks([nb2, nb3])
        new_nb = notebook.add_html_tab(nb4, default_tab='python3')

        writer = nbconvert.RSTExporter()
        body, _ = writer.from_notebook_node(new_nb)
        # TODO(mli) add some asserts
        # print(build.process_rst(body))



if __name__ == '__main__':
    unittest.main()
