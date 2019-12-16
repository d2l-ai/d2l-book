# Editing the Source Files

We recommend you to save your Jupyter notebooks as markdown files, and clearing output before saving, to make code review and version control easier. 

You can use your favorite markdown editors to edits these files directly. A markdown code block with a `{.python .input}` tag will be treated as a code cell in the notebook, for example, 

````
```{.python .input}
print('this is a Jupyter code cell')
```
````

The rest will be grouped into markdown cells in the notebook. 

Another way is installing a Jupyter extension called `mu-notedown` by `pip install mu-notedown`, to ask Jupyter to open and save markdown files as notebooks directly. `mu-notedown` is a fork of [notedown](https://github.com/aaren/notedown) with several modifications. You may need to uninstall the original `notedown` first. 

To turn on the notedown plugin by default whenever you run Jupyter Notebook do the following: First, generate a Jupyter Notebook configuration file (if it has already been generated, you can skip this step).

```bash
jupyter notebook --generate-config
```

Then, add the following line to the end of the Jupyter Notebook configuration file (for Linux/macOS, usually in the path `~/.jupyter/jupyter_notebook_config.py`):

```bash
c.NotebookApp.contents_manager_class = 'notedown.NotedownContentsManager'
```

Next restart your Jupyter, you should be able to open these markdowns in Jupyter as notebooks now.
