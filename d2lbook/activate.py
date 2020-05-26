import argparse
from d2lbook import markdown
import glob
import re
import sys

__all__  = ['activate']

commands = ['tab']

def activate():
    parser = argparse.ArgumentParser(description='Activate tabs')
    parser.add_argument('tab', default='all', help='the tab to activate')
    parser.add_argument('filename', help='the markdown files to activate')
    args = parser.parse_args(sys.argv[2:])

    for fn in glob.glob(args.filename):
        _activate_tab(fn, args.tab)

_tab_re = re.compile('# *@tab +([\w]+)')

def _get_cell_tab(cell):
    if cell['type'] != 'code':
        return None
    if not '.input' in cell['class'] and not 'python' in cell['class']:
        return None
    match = _tab_re.search(cell['source'])
    if match:
        return match[1]
    return 'default'

def _activate_tab(filename, tab):
    with open(filename, 'r') as f:
        src = f.read()
    cells = markdown.split_markdown(src)
    for cell in cells:
        cell_tab = _get_cell_tab(cell)
        if not cell_tab:
            continue
        if tab == 'all' or cell_tab == 'all' or cell_tab == tab:
            # activate
            cell['class'] = '{.python .input}'
        else: # disactivate
            cell['class'] = 'python'
    src = markdown.join_markdown_cells(cells)
    with open(filename, 'w') as f:
        f.write(src)
