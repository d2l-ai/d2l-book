"""utilities to handle markdown
"""
import re

def split_markdown(source):
    """Split markdown into a list of text and code blocks"""
    cells = []
    in_code = False
    in_tab = False
    cur_code_mark = None
    cur_tag = None
    cur_src = []
    code_mark = re.compile('(```+) *(.*)')
    tab_begin_mark = re.compile(':tab_begin:`([ \*-\/\\\._\w\d]+)`')
    tab_end_mark = re.compile(':tab_end:')
    def _add_cell():
        if cur_src:
            src = '\n'.join(cur_src)
            if in_code:
                cells.append({'type':'code', 'class':cur_tag, 'source':src})
            else:
                cells.append({'type':'markdown', 'source':src})
                if cur_tag:
                    cells[-1]['class'] = cur_tag

    for l in source.split('\n'):
        code = code_mark.match(l)
        tab_begin = tab_begin_mark.match(l)
        tab_end = tab_end_mark.match(l)
        if any([code, tab_begin, tab_end]):
            # code can be nested
            if in_code and ((code and code.groups()[0] != cur_code_mark) or tab_begin or tab_end):
                cur_src.append(l)
                continue
            # tab cannot be nested
            if in_tab and code:
                cur_src.append(l)
                continue
            _add_cell()
            cur_src = []
            if code:
                cur_code_mark, cur_tag = code.groups()
                in_code ^= True
            elif tab_begin:
                cur_tag, = tab_begin.groups()
                in_tab = True
            else:
                cur_tag = None
                in_tab = False
        else:
            cur_src.append(l)
    _add_cell()
    return cells

def join_markdown_cells(cells):
    src = []
    print(cells)
    for c in cells:
        if c['type'] == 'markdown':
            if 'class' in c:
                print('xxx')
                src.append(f':tab_begin:`{c["class"]}`')
            src.append(c['source'])
            if 'class' in c:
                print('yy')
                src.append(':tab_end:')
        else:
            src += ['```'+c['class'], c['source'], '```']
    return '\n'.join(src)
