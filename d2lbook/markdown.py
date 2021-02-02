"""utilities to handle markdown
"""
import re
from d2lbook import common
from typing import List, Dict
import logging

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
                cells.append({
                    'type': 'code',
                    'fence': cur_code_mark,
                    'class': cur_tag,
                    'source': src})
            else:
                if not src and not cur_tag:
                    return
                cells.append({'type': 'markdown', 'source': src})
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
                if cell_src[-1].endswith('\n'):
                    cell_src[-1] = cell_src[-1][:-1]
                cell_src.append(':end_tab:')
        else:
            cell_src += [c['fence'] + c['class'], c['source'], c['fence']]
        src.append('\n'.join(cell_src).strip())
    return '\n\n'.join(src) + '\n'

basic_token = r'[\ \*-\/\\\._\w\d\:/]+'
token = r'[\|\'\:\;\<\>\^\(\)\{\}\[\]\ \*-\/\\\.,_=\w\d]+'

def _is_mark(lines):
    if isinstance(lines, str):
        lines = [lines]
    for l in lines:
        l = l.strip()
        if l:
            m = re.match(rf':{token}:(`{token}`)?', l)
            if m is None or m.span() != (0, len(l)):
                return False
    return True

def _list(line, prev_prefix):
    m = re.match(r' *[-\*\+] *', line) or re.match(r' *[\d]+\. *', line)
    if m:
        if prev_prefix is not None and len(prev_prefix.split('__')) == 2:
            p = int(prev_prefix.split('__')[1]) + 1
        else:
            p = 0
        return m[0] + '__' + str(p)
    if prev_prefix == '':
        return ''
    if prev_prefix is not None and len(re.match(r' *', line)[0]) > len(
            re.match(r' *', prev_prefix)[0]):
        return prev_prefix
    return ''

def split_text(text: str) -> List[Dict[str, str]]:
    """Split text into a list of paragraphs

    1. type: text, list, image, title, equation, table
    1. source:
    1. prefix:
    1. mark:
    """
    # split into paragraphs
    lines = text.splitlines()
    groups = common.group_list(lines, lambda a, _: a.strip() == '')
    paras = ['\n'.join(item) for empty_line, item in groups if not empty_line]

    def _fallback(p, type):
        logging.warn(f'Wrong {type} format:\n' + p)
        cells.append({'type': 'text', 'source': p})

    cells = []
    for p in paras:
        lines = p.splitlines() + ['']
        p += '\n'
        if p.startswith('#'):
            # parse title
            if not _is_mark(lines[1:]):
                _fallback(p, 'title')
            else:
                m = re.match(r'#+ *', lines[0])
                cells.append({
                    'type': 'title',
                    'prefix': m[0],
                    'source': lines[0][m.span()[1]:],
                    'mark': '\n'.join(lines[1:])})
        elif p.startswith('$$'):
            # parse equations
            m = re.findall(r'\$\$', p)
            if len(m) != 2:
                _fallback(p, 'equation')
            else:
                cells.append({'type': 'equation', 'source': p})
        elif p.startswith('!['):
            # parse images
            if not lines[0].strip().endswith(')') or not _is_mark(lines[1:]):
                _fallback(p, 'image')
            else:
                cells.append({'type': 'image', 'source': p})
        elif p.startswith('|'):
            # parse table
            for i, l in enumerate(lines):
                if not l.startswith('|'):
                    break
            if not _is_mark(lines[i:]):
                _fallback(p, 'equation')
            else:
                cells.append({'type': 'table', 'source': p})
        else:
            groups = common.group_list(lines, _list)
            for prefix, item in groups:
                if len(prefix.split('__')) == 2:
                    prefix = prefix.split('__')[0]
                source = '\n'.join(item)[len(prefix):]
                if prefix == '':
                    cells.append({'type': 'text', 'source': source})
                else:
                    cells.append({
                        'type': 'list',
                        'prefix': prefix,
                        'source': source})
    return cells

def join_text(cells) -> str:
    paras = []
    for cell in cells:
        l = cell['source']
        if 'prefix' in cell:
            l = cell['prefix'] + l
        if 'mark' in cell:
            l += '\n' + cell['mark']
        paras.append(l)
    return '\n'.join(paras)