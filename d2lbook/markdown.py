"""utilities to handle markdown
"""
from d2lbook import common
from typing import List, Dict

def split_markdown(source: str) -> List[Dict[str, str]]:
    """Split markdown into a list of text and code cells.

    A cell has three fields:
    1. type: either code or markdown
    2. class: code class or tab class
    3. source: single string for the source
    """
    cells: List[Dict] = []
    in_code = False
    in_tab = False
    cur_code_mark = None
    cur_tag = None
    cur_src = []
    def _add_cell(cur_src: List[str], cells: List[Dict]):
        if cur_src:
            src = '\n'.join(cur_src).strip()
            if in_code:
                cells.append({'type':'code', 'fence':cur_code_mark, 'class':cur_tag, 'source':src})
            else:
                if not src and not cur_tag:
                    return
                cells.append({'type':'markdown', 'source':src})
                if cur_tag:
                    cells[-1]['class'] = cur_tag

    for l in source.splitlines():
        code = common.md_code_fence.match(l)
        tab = common.md_mark_pattern.match(l)
        if code:
            # code can be nested
            if in_tab or (in_code and code.groups()[0] != cur_code_mark):
                cur_src.append(l)
            else:
                _add_cell(cur_src, cells)
                cur_src = []
                cur_code_mark, cur_tag = code.groups()
                in_code ^= True
        elif tab:
            begin = tab.groups()[0] == 'begin_tab'
            end = tab.groups()[0] == 'end_tab'
            if in_code or (not begin and not end):
                cur_src.append(l)
            else:
                _add_cell(cur_src, cells)
                cur_src = []
                if begin:
                    cur_tag = tab.groups()[1]
                else:
                    cur_tag = None
                in_tab = begin
        else:
            cur_src.append(l)
    _add_cell(cur_src, cells)
    return cells

def join_markdown_cells(cells: List[Dict]) -> str:
    """Join a list of cells into a markdown string"""
    src = []
    for c in cells:
        cell_src = []
        if c['type'] == 'markdown':
            if 'class' in c:
                cell_src.append(f':begin_tab:{c["class"]}')
            cell_src.append(c['source'])
            if 'class' in c:
                cell_src.append(':end_tab:')
        else:
            cell_src += [c['fence']+c['class'], c['source'], c['fence']]
        src.append('\n'.join(cell_src))
    return '\n\n'.join(src)+'\n'

def split_paragraphs(text: str) -> List[str]:
    """Split text into a list of paragraphs"""
    lines = text.splitlines()
    groups = common.group_list(lines, lambda a, _: a.strip()=='')
    return ['\n'.join(item) for empty_line, item in groups if not empty_line]

