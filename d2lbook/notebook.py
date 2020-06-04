"""utilities to handle notebooks"""

from typing import Union, List, Optional

import os
import copy
import notedown
import nbformat
import nbconvert
from nbformat import notebooknode
from d2lbook import markdown
from d2lbook import common

def create_new_notebook(nb: notebooknode.NotebookNode,
                         cells: List[notebooknode.NotebookNode]
                         ) -> notebooknode.NotebookNode:
    """create an empty notebook by copying metadata from nb"""
    new_nb = copy.deepcopy(nb)
    new_nb.cells = cells
    return new_nb

def read(fname: str):
    if not os.path.exists(fname) or os.stat(fname).st_size == 0:
        return None
    with open(fname, 'r') as f:
        return nbformat.read(f, as_version=4)


def read_markdown(source: Union[str, List[str]]) -> notebooknode.NotebookNode:
    """Returns a notebook from markdown source"""
    if not isinstance(source, str):
        source = '\n'.join(source)
    reader = notedown.MarkdownReader(match='strict')
    return reader.reads(source)

def split_markdown_cell(nb: notebooknode.NotebookNode) -> notebooknode.NotebookNode:
    """split a markdown cell if it contains tab block.

    a new property `class` is added to the metadata for a tab cell.
    """
    # merge continous markdown cells
    grouped_cells = common.group_list(nb.cells,
                                      lambda cell, _: cell.cell_type=='markdown')
    new_cells = []
    for is_md, group in grouped_cells:
        if not is_md:
            new_cells.extend(group)
        else:
            src = '\n\n'.join(cell.source for cell in group)
            md_cells = markdown.split_markdown(src)
            is_tab_cell = lambda cell, _: cell['type']=='markdown' and 'class' in cell
            grouped_md_cells = common.group_list(md_cells, is_tab_cell)
            for is_tab, md_group in grouped_md_cells:
                new_cell = nbformat.v4.new_markdown_cell(
                    markdown.join_markdown_cells(md_group))
                if is_tab:
                    tab = md_group[0]['class']
                    assert tab.startswith('`') and tab.endswith('`'), tab
                    new_cell.metadata['tab'] = [tab[1:-1]]
                new_cells.append(new_cell)
    new_cells = [cell for cell in new_cells if cell.source]
    return create_new_notebook(nb, new_cells)

def _get_cell_tab(cell: notebooknode.NotebookNode, default_tab: str='') -> List[str]:
    """Get the cell tab"""
    if 'tab' in cell.metadata:
        return cell.metadata['tab']
    if cell.cell_type != 'code':
        return []
    match = common.source_tab_pattern.search(cell.source)
    if match:
        return [tab.strip() for tab in match[1].split(',')]
    return [default_tab,]

def get_tab_notebook(nb: notebooknode.NotebookNode, tab: str, default_tab: str
                     ) -> notebooknode.NotebookNode:
    """Returns a notebook with code/markdown cells that doesn't match tab
    removed.

    Return None if no cell matched the tab and nb contains code blocks.

    A `origin_pos` property is added to the metadata for each cell, which
    records its position in the original notebook `nb`.
    """
    matched_tab = False
    new_cells = []
    for i, cell in enumerate(nb.cells):
        new_cell = copy.deepcopy(cell)
        new_cell.metadata['origin_pos'] = i
        cell_tab = _get_cell_tab(new_cell, default_tab)
        if not cell_tab:
            new_cells.append(new_cell)
        else:
            if cell_tab == ['all'] or tab in cell_tab:
                new_cell.metadata['tab'] = 'all' if cell_tab == ['all'] else tab
                matched_tab = True
                # remove the tab from source
                lines = new_cell.source.split('\n')
                for j, line in enumerate(lines):
                    src_tab = common.source_tab_pattern.search(line)
                    text_tab = common.md_mark_pattern.search(line)
                    if src_tab or (text_tab and (
                            text_tab[1]=='begin_tab' or text_tab[1]=='end_tab')):
                        del lines[j]
                    new_cell.source = '\n'.join(lines)
                new_cells.append(new_cell)
    if not matched_tab and any([cell.cell_type=='code' for cell in nb.cells]):
        return None
    return create_new_notebook(nb, new_cells)

def merge_tab_notebooks(src_notebooks: List[notebooknode.NotebookNode]
                        ) -> notebooknode.NotebookNode:
    """Merge the tab notebooks into a single one.

    The reserved function of get_tab_notebook.
    """
    n = max([max([cell.metadata['origin_pos'] for cell in nb.cells])
             for nb in src_notebooks])
    new_cells = [None] * (n+1)
    for nb in src_notebooks:
        for cell in nb.cells:
            new_cells[cell.metadata['origin_pos']] = copy.deepcopy(cell)
    return create_new_notebook(src_notebooks[0], new_cells)

def _get_tab_bar(tabs, tab_id, default_tab, div_class=''):
    code = f"```eval_rst\n\n.. raw:: html\n\n    <div class=\"mdl-tabs mdl-js-tabs mdl-js-ripple-effect\"><div class=\"mdl-tabs__tab-bar {div_class}\">"
    for i, tab in enumerate(tabs):
        active = 'is-active' if tab == default_tab else ''
        code +=f'<a href="#{tab}-{tab_id}-{i}" onclick="tagClick(\'{tab}\'); return false;" class="mdl-tabs__tab {active}">{tab}</a>'
    code += "</div>\n```"
    return nbformat.v4.new_markdown_cell(code)

def _get_tab_panel(cells, tab, tab_id, default_tab):
    active = 'is-active' if tab == default_tab else ''
    tab_panel_begin = nbformat.v4.new_markdown_cell(
        f"```eval_rst\n.. raw:: html\n\n    <div class=\"mdl-tabs__panel {active}\" id=\"{tab}-{tab_id}\">\n```")
    tab_panel_end = nbformat.v4.new_markdown_cell(
        "```eval_rst\n.. raw:: html\n\n    </div>\n```")
    return [tab_panel_begin, *cells, tab_panel_end]


def _merge_tabs(nb: notebooknode.NotebookNode):
    """merge side-by-side tabs into a single one"""
    def _tab_status(cell, status):
        tab = _get_cell_tab(cell)
        if tab:
            if cell.cell_type == 'markdown':
                return 1
            if tab == 'all':
                return 0
            return 2
        return 0
    cell_groups = common.group_list(nb.cells, _tab_status)
    meta = [(in_tab, [cell.metadata['tab'] for cell in group] if in_tab else None
             ) for in_tab, group in cell_groups]
    new_cells = []
    i = 0
    while i < len(meta):
        in_tab, tabs = meta[i]
        if not in_tab:
            new_cells.append((False, cell_groups[i][1]))
            i += 1
        else:
            j = i + 1
            while j < len(meta):
                if meta[j][1] != tabs:
                    break
                j += 1
            groups = [group for _, group in cell_groups[i:j]]
            new_cells.append((True, [x for x in zip(*groups)]))
            i = j

    return new_cells

def add_html_tab(nb: notebooknode.NotebookNode, default_tab: str) -> notebooknode.NotebookNode:
    """Add html codes for the tabs"""
    cell_groups = _merge_tabs(nb)
    tabs = [len(group) for in_tab, group in cell_groups if in_tab]
    if not tabs or max(tabs) <= 1:
        return nb
    new_cells = []
    for i, (in_tab, group) in enumerate(cell_groups):
        if not in_tab:
            new_cells.extend(group)
        else:
            tabs = [cells[0].metadata['tab'] for cells in group]
            div_class = "code" if group[0][0].cell_type == 'code' == 2 else "text"
            new_cells.append(_get_tab_bar(tabs, i, default_tab, div_class))
            for j, (tab, cells) in enumerate(zip(tabs, group)):
                new_cells.extend(_get_tab_panel(cells, tab, f'{i}-{j}', default_tab))
            new_cells.append(nbformat.v4.new_markdown_cell(
                "```eval_rst\n.. raw:: html\n\n    </div>\n```"))
    return create_new_notebook(nb, new_cells)
