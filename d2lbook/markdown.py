"""utilities to handle markdown
"""
import re

def split_markdown(source):
    """Split markdown into a list of text and code blocks"""
    cells = []
    in_code = False
    cur_code_mark = None
    cur_code_class = None
    cur_src = []
    code_mark = re.compile('(```+) *(.*)')
    def _add_cell():
        if cur_src:
            if in_code:
                cells.append({'type':'code', 'class':cur_code_class,
                            'source':'\n'.join(cur_src)})
            else:
                cells.append({'type':'markdown', 'source':'\n'.join(cur_src)})
    for l in source.split('\n'):
        ret = code_mark.match(l)
        if ret:
            if not in_code:
                _add_cell()
                cur_code_mark, cur_code_class = ret.groups()
                cur_src = []
                in_code = True
            else:
                if ret.groups()[0] == cur_code_mark:
                    _add_cell()
                    cur_src = []
                    in_code = False
                else:
                    cur_src.append(l)
        else:
            cur_src.append(l)
    _add_cell()
    return cells

def join_markdown_cells(cells):
    src = []
    for c in cells:
        if c['type'] == 'markdown':
            src.append(c['source'])
        else:
            src += ['```'+c['class'], c['source'], '```']
    return '\n'.join(src)
