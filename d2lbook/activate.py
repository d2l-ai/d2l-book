import argparse
from d2lbook import markdown, common, config
import glob
import re
import sys

__all__  = ['activate']

commands = ['tab']

def activate():
    parser = argparse.ArgumentParser(description='Activate tabs')
    parser.add_argument('tab', default='all', help='the tab to activate')
    parser.add_argument('filename', nargs='+', help='the markdown files to activate')
    args = parser.parse_args(sys.argv[2:])

    cf = config.Config()
    for fn in args.filename:
        for f in glob.glob(fn):
            _activate_tab(f, args.tab, cf.default_tab)

_tab_re = re.compile('# *@tab +([\w]+)')

def _get_cell_tab(cell, default_tab):
    if cell['type'] != 'code':
        return []
    if not '.input' in cell['class'] and not 'python' in cell['class']:
        return []
    match = common.source_tab_pattern.search(cell['source'])
    if match:
        return [tab.strip() for tab in match[1].split(',')]
    return [default_tab]

def _activate_tab(filename, tab, default_tab):
    if tab == 'default':
        tab = default_tab
    with open(filename, 'r') as f:
        src = f.read()
    cells = markdown.split_markdown(src)
    for cell in cells:
        cell_tab = _get_cell_tab(cell, default_tab)
        if not cell_tab:
            continue
        if tab == 'all' or cell_tab == ['all'] or tab in cell_tab:
            # activate
            cell['class'] = '{.python .input}'
        else: # disactivate
            cell['class'] = 'python'
    src = markdown.join_markdown_cells(cells)
    with open(filename, 'w') as f:
        f.write(src)
