from IPython.core.magic import Magics, magics_class, cell_magic
import os
import sys

_TAB = None
_LOG = sys.stderr.write

# the tab selected last time
_LAST_TAB = None
_LAST_TAB_FILE = '/tmp/d2lbook_last_selected_tab'
if os.path.exists(_LAST_TAB_FILE):
    with open(_LAST_TAB_FILE) as f:
        _LAST_TAB = f.read().strip()

def select_tab(tab=_LAST_TAB):
    _LOG(f'Selected tab "{tab}", all other code cells not marked as "{tab}" will be ignored in execution.\n')
    _LOG(f'This code block will be deleted during build.')
    sys.modules[__name__]._TAB = tab
    if tab:
        with open(_LAST_TAB_FILE, 'w') as f:
            f.write(tab+'\n')

def interact_select(*tabs):
    if len(tabs) == 1 and isinstance(tabs[0], (list, tuple)):
        tabs = tabs[0]
    from ipywidgets import interact
    interact(select_tab, tab=list(tabs))

def selected(*tabs):
    if len(tabs) == 1 and isinstance(tabs[0], (list, tuple)):
        tabs = tabs[0]
    return _TAB in tabs

@magics_class
class Tab(Magics):
    @cell_magic
    def tab(self, line, cell):
        tabs = [tab.strip() for tab in line.strip().split(',')]
        if _TAB in tabs or 'all' in tabs:
            self.shell.run_cell(cell)
        else:
            _LOG(f'Ignored to run as it is not marked as a "{_TAB}" cell.')


def load_ipython_extension(ipython):
    ipython.run_cell('from d2lbook import tab')
    ipython.register_magics(Tab)
