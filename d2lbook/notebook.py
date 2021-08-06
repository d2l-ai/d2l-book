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
from d2lbook import config

def create_new_notebook(
        nb: notebooknode.NotebookNode,
        cells: List[notebooknode.NotebookNode]) -> notebooknode.NotebookNode:
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

def split_markdown_cell(
        nb: notebooknode.NotebookNode) -> notebooknode.NotebookNode:
    """split a markdown cell if it contains tab block.

    a new property `class` is added to the metadata for a tab cell.
    """
    # merge continous markdown cells
    grouped_cells = common.group_list(
        nb.cells, lambda cell, _: cell.cell_type == 'markdown')
    new_cells = []
    for is_md, group in grouped_cells:
        if not is_md:
            new_cells.extend(group)
        else:
            src = '\n\n'.join(cell.source for cell in group)
            md_cells = markdown.split_markdown(src)
            is_tab_cell = lambda cell, _: cell['class'] if (cell[
                'type'] == 'markdown' and 'class' in cell) else 'not_tab_cell'
            grouped_md_cells = common.group_list(md_cells, is_tab_cell)
            for tab, md_group in grouped_md_cells:
                new_cell = nbformat.v4.new_markdown_cell(
                    markdown.join_markdown_cells(md_group))
                if tab != 'not_tab_cell':
                    assert tab.startswith('`') and tab.endswith('`'), tab
                    new_cell.metadata['tab'] = [
                        t.strip() for t in tab[1:-1].split(',')]
                new_cells.append(new_cell)
    new_cells = [cell for cell in new_cells if cell.source]
    return create_new_notebook(nb, new_cells)

def get_cell_tab(cell: notebooknode.NotebookNode,
                 default_tab: str = '') -> List[str]:
    """Get the cell tab"""
    if 'tab' in cell.metadata:
        tab = cell.metadata['tab']
        return [tab] if type(tab) == str else tab
    if cell.cell_type != 'code':
        return []
    match = (common.source_tab_pattern.search(cell.source) or
             common.source_tab_pattern_2.search(cell.source))
    if match:
        return [tab.strip() for tab in match[1].split(',')]
    return [default_tab,]

def get_tab_notebook(nb: notebooknode.NotebookNode, tab: str,
                     default_tab: str) -> notebooknode.NotebookNode:
    """Returns a notebook with code/markdown cells that doesn't match tab
    removed.

    Return None if no cell matched the tab and nb contains code blocks.

    A `origin_pos` property is added to the metadata for each cell, which
    records its position in the original notebook `nb`.
    """
    if tab != default_tab:
        has_tab = False
        for cell in nb.cells:
            if tab in get_cell_tab(cell):
                has_tab = True
                break
        if not has_tab and any(
            [cell.cell_type == 'code' for cell in nb.cells]):
            return None

    matched_tab = False
    new_cells = []
    for i, cell in enumerate(nb.cells):
        new_cell = copy.deepcopy(cell)
        new_cell.metadata['origin_pos'] = i
        cell_tab = get_cell_tab(new_cell, default_tab)
        if not cell_tab:
            new_cells.append(new_cell)
        else:
            if cell_tab == ['all'] or tab in cell_tab:
                # drop the cell contains `%load_ext d2lbook.tab`
                if '%load_ext d2lbook.tab' in new_cell.source:
                    continue
                new_cell.metadata['tab'] = [tab]
                matched_tab = True
                # remove the tab from source
                lines = new_cell.source.split('\n')
                for j, line in enumerate(lines):
                    src_tab = (common.source_tab_pattern.search(line) or
                               common.source_tab_pattern_2.search(line))
                    text_tab = common.md_mark_pattern.search(line)
                    if src_tab or (text_tab and (text_tab[1] == 'begin_tab' or
                                                 text_tab[1] == 'end_tab')):
                        del lines[j]

                    # TODO, also remove the tailing #@save
                    lines = _clean_if_branches(lines, tab)
                    new_cell.source = '\n'.join(lines)
                new_cells.append(new_cell)
    if not matched_tab and any([cell.cell_type == 'code'
                                for cell in nb.cells]):
        return None
    return create_new_notebook(nb, new_cells)

def _clean_if_branches(lines, tab):
    """Handle special if branchs
    """
    #TODO make it more general purpose
    mark = 'tab.selected'
    if not any([mark in l for l in lines]):
        return _clean_if_branches_old(lines, tab)
    # 1 means in a matched if branch,
    # 2 means in a not matched if branch
    # 0 means others
    mode = 0
    indent = 0
    _leading_spaces = lambda l: len(l) - len(l.lstrip())
    new_lines = []
    for i, l in enumerate(lines):
        assert '\t' not in l, 'please use space in ' + l
        if 'if' in l and mark in l:
            mode = 1 if (f'"{tab}"' in l or f"'{tab}'" in l) else 2
            indent = _leading_spaces(l)
            continue
        if mode != 0 and l.strip() != '' and _leading_spaces(l) <= indent:
            # out of the if branch
            mode = 0
        if mode == 0:
            new_lines.append(l)
        if mode == 1:
            new_lines.append(l[4:])
    return new_lines

def _clean_if_branches_old(lines, tab):
    """Handle speciall if branchs
    """
    #TODO make it more general purpose
    mark = 'd2l.USE_'
    matched = False
    for l in lines:
        if mark in l:
            matched = True
            break
    if not matched:
        return lines
    # 1 means in a matched if branch,
    # 2 means in a not matched if branch
    # 0 means others
    mode = 0
    indent = 0
    _leading_spaces = lambda l: len(l) - len(l.lstrip())
    new_lines = []
    for i, l in enumerate(lines):
        assert '\t' not in l, 'please use space in ' + l
        if 'if' in l and mark in l:
            mode = 1 if mark+tab.upper() in l else 2
            indent = _leading_spaces(l)
            continue
        if mode != 0 and l.strip() != '' and _leading_spaces(l) <= indent:
            # out of the if branch
            mode = 0
        if mode == 0:
            new_lines.append(l)
        if mode == 1:
            new_lines.append(l[4:])
    return new_lines

def _has_output(cell):
    """Return if a cell has output"""
    return 'outputs' in cell and len(cell['outputs'])

def merge_tab_notebooks(
    src_notebooks: List[notebooknode.NotebookNode]
) -> notebooknode.NotebookNode:
    """Merge the tab notebooks into a single one.

    The reserved function of get_tab_notebook.
    """
    n = max([
        max([cell.metadata['origin_pos'] for cell in nb.cells])
        for nb in src_notebooks])
    new_cells = [[] for _ in range(n + 1)]  # type: ignore

    # for compatability
    tab_list = lambda tab: [tab] if type(tab) == str else tab
    for nb in src_notebooks:
        for cell in nb.cells:
            cell = copy.deepcopy(cell)
            p = cell.metadata['origin_pos']
            if len(new_cells[p]):
                if _has_output(new_cells[p][-1]) or _has_output(
                        cell) or new_cells[p][-1].source != cell.source:
                    new_cells[p].append(cell)
                else:
                    if 'tab' in cell.metadata:
                        tab = tab_list(new_cells[p][-1].metadata['tab'])
                        tab.extend(tab_list(cell.metadata['tab']))
                        new_cells[p][-1].metadata['tab'] = tab
            else:
                new_cells[p].append(cell)
    expanded_cells = []
    for cell in new_cells:
        expanded_cells.extend(cell)
    return create_new_notebook(src_notebooks[0], expanded_cells)

def _get_tab_bar(tabs, tab_id, default_tab, div_class=''):
    code = f"```eval_rst\n\n.. raw:: html\n\n    <div class=\"mdl-tabs mdl-js-tabs mdl-js-ripple-effect\"><div class=\"mdl-tabs__tab-bar {div_class}\">"
    for i, tab in enumerate(tabs):
        active = 'is-active' if tab == default_tab else ''
        code += f'<a href="#{tab}-{tab_id}-{i}" onclick="tagClick(\'{tab}\'); return false;" class="mdl-tabs__tab {active}">{tab}</a>'
    code += "</div>\n```"
    return nbformat.v4.new_markdown_cell(code)

def _get_tab_panel(cells, tab, tab_id, default_tab):
    active = 'is-active' if tab == default_tab else ''
    tab_panel_begin = nbformat.v4.new_markdown_cell(
        f"```eval_rst\n.. raw:: html\n\n    <div class=\"mdl-tabs__panel {active}\" id=\"{tab}-{tab_id}\">\n```"
    )
    tab_panel_end = nbformat.v4.new_markdown_cell(
        "```eval_rst\n.. raw:: html\n\n    </div>\n```")
    return [tab_panel_begin, *cells, tab_panel_end]

def _merge_tabs(nb: notebooknode.NotebookNode, tabs: List[str]):
    """merge side-by-side tabs into a single one.

    Returns a list of item, an item can be (False, a list of not-in-tab-cell) or
    (True, a list of (tab_name, a list of cell-in-this-tab))
    """
    tab_status = lambda cell, _: 1 if get_cell_tab(cell) else 0
    cell_groups = common.group_list(nb.cells, tab_status)
    new_groups = []
    for in_tab, cells in cell_groups:
        if not in_tab:
            new_groups.append((False, cells))
            continue
        # a special case that we can merge into non-tab cells
        mergable = True
        for cell in cells:
            if set(cell.metadata['tab']) != set(tabs):
                mergable = False
                break
        if mergable:
            new_groups.append((False, cells))
            continue
        # the general case
        group_dict = {tab: [] for tab in tabs}  # type: ignore
        for cell in cells:
            for tab in cell.metadata['tab']:
                group_dict[tab].append(cell)
        group = [
            (tab, group_dict[tab]) for tab in tabs if len(group_dict[tab])]
        new_groups.append((True, group))
    # merge two consecutive code blocks. The first
    # code should not contain output
    for is_tab, group in new_groups:
        if not is_tab:
            continue
        for i, (tab, tab_cell) in enumerate(group):
            new_tab_cell = []
            for cell in tab_cell:
                if (len(new_tab_cell) > 0 and
                        new_tab_cell[-1].cell_type == 'code' and
                        cell.cell_type == 'code' and
                        not _has_output(new_tab_cell[-1])):
                    cell = copy.deepcopy(cell)
                    cell.source = new_tab_cell[-1].source + '\n\n' + cell.source
                    new_tab_cell[-1] = cell
                else:
                    new_tab_cell.append(cell)
            group[i] = (tab, new_tab_cell)
    return new_groups

def add_html_tab(nb: notebooknode.NotebookNode,
                 tabs: List[str]) -> notebooknode.NotebookNode:
    """Add html codes for the tabs"""
    cell_groups = _merge_tabs(nb, tabs)
    all_tabs = common.flatten([[tab for tab, _ in group]
                               for in_tab, group in cell_groups if in_tab])
    # If there is only one tab, assume it's the default tab.
    if len(set(all_tabs)) <= 1:
        return nb
    new_cells = []
    for i, (in_tab, group) in enumerate(cell_groups):
        if not in_tab:
            new_cells.extend(group)
        else:
            cur_tabs = [tab for tab, _ in group]
            div_class = "code"
            for _, cells in group:
                if cells[0].cell_type != "code":
                    div_class = "text"
            new_cells.append(_get_tab_bar(cur_tabs, i, tabs[0], div_class))
            for j, (tab, cells) in enumerate(group):
                new_cells.extend(
                    _get_tab_panel(cells, tab, f'{i}-{j}', tabs[0]))
            new_cells.append(
                nbformat.v4.new_markdown_cell(
                    "```eval_rst\n.. raw:: html\n\n    </div>\n```"))
    return create_new_notebook(nb, new_cells)

def get_toc(root, flat=True):
    """return a list of files in the order defined by TOC"""
    subpages = _get_subpages(root)
    res = [root]
    for fn in subpages:
        if flat:
            res.extend(get_toc(fn))
        else:
            res.append(get_toc(fn))
    return res

def _get_subpages(input_fn):
    """read toc in input_fn, returns what it contains"""
    subpages = []
    reader = notedown.MarkdownReader()
    with open(input_fn, 'r', encoding='UTF-8') as f:
        nb = reader.read(f)
    for cell in nb.cells:
        if (cell.cell_type == 'code' and 'attributes' in cell.metadata and
                'toc' in cell.metadata.attributes['classes']):
            for l in cell.source.split('\n'):
                l = l.strip()
                if not l.startswith(':'):
                    fn = os.path.join(os.path.dirname(input_fn), l + '.md')
                    if os.path.exists(fn):
                        subpages.append(fn)
    return subpages
