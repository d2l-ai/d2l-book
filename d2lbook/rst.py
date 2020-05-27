"""utilities to handle rst files"""
import re
import logging
from typing import Dict
import nbconvert
import nbformat
from nbformat import notebooknode
from d2lbook import notebook
from d2lbook import common
from d2lbook import markdown

def convert_notebook(nb: notebooknode.NotebookNode, resources: Dict[str, str]):
    nb = _process_nb(nb)
    writer = nbconvert.RSTExporter()
    body, resources = writer.from_notebook_node(nb, resources)
    body = _process_rst(body)
    return body, resources

def _process_nb(nb):
    # add empty lines before and after a mark/fence
    new_cells = []
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            md_cells = markdown.split_markdown(cell.source)
            for i, md_cell in enumerate(md_cells):
                if i < len(md_cells) - 1 and md_cells[i+1]['type'] == 'code':
                    md_cells[i]['source'] += '\n'
                if md_cell['type'] == 'markdown':
                    lines = md_cells[i]['source'].split('\n')
                    for j, line in enumerate(lines):
                        m = common.md_mark_pattern.match(line)
                        if (m is not None
                            and m[1] not in ('ref', 'numref', 'eqref')
                            and m.end() == len(line)):
                            lines[j] = '\n'+line+'\n'
                    md_cells[i]['source'] = '\n'.join(lines)
            new_cells.append(nbformat.v4.new_markdown_cell(
                markdown.join_markdown_cells(md_cells)))
        else:
            new_cells.append(cell)
    # hide/show
    for cell in new_cells:
        if cell.cell_type == 'code':
            if '# hide outputs' in cell.source.lower():
                cell.outputs = []
            if '# hide code' in cell.source.lower():
                cell.source = ''
    return notebook.create_new_notebook(nb, new_cells)

def _process_rst(body):

    def delete_lines(lines, deletes):
        return [line for i, line in enumerate(lines) if i not in deletes]
    def indented(line):
        return line.startswith('   ')

    def blank(line):
        return len(line.strip()) == 0

    def look_behind(i, cond, lines):
        indices = []
        while i < len(lines) and cond(lines[i]):
            indices.append(i)
            i = i + 1
        return indices

    lines = body.split('\n')
    # deletes: indices of lines to be deleted
    i, deletes = 0, []
    while i < len(lines):
        line = lines[i]
        # '.. code:: toc' -> '.. toctree::', then remove consecutive empty lines
        # after the current line
        if line.startswith('.. code:: toc'):
            # convert into rst's toc block
            lines[i] = '.. toctree::'
            blanks = look_behind(i+1, blank, lines)
            deletes.extend(blanks)
            i += len(blanks)
        # .. code:: eval_rst
        #
        #
        #    .. only:: html
        #
        #       References
        #       ==========
        # ->
        #
        #
        #
        # .. only:: html
        #
        #    References
        #    ==========
        elif line.startswith('.. code:: eval_rst'):
            # make it a rst block
            deletes.append(i)
            j = i + 1
            while j < len(lines):
                line_j = lines[j]
                if indented(line_j):
                    lines[j] = line_j[3:]
                    if lines[j].strip().startswith('.. '):
                        lines[j] = '\n'+lines[j].strip()
                elif not blank(line_j):
                    break
                j += 1
            i = j
        elif line.startswith('.. parsed-literal::'):
            # add a output class so we can add customized css
            lines[i] += '\n    :class: output'
            i += 1
        # .. figure:: ../img/jupyter.png
        #    :alt: Output after running Jupyter Notebook. The last row is the URL
        #    for port 8888.
        #
        #    Output after running Jupyter Notebook. The last row is the URL for
        #    port 8888.
        #
        # :width:``700px``
        #
        # :label:``fig_jupyter``
        #->
        # .. _fig_jupyter:
        #
        # .. figure:: ../img/jupyter.png
        #    :width: 700px
        #
        #    Output after running Jupyter Notebook. The last row is the URL for
        #    port 8888.
        elif indented(line) and ':alt:' in line:
            # Image caption, remove :alt: block, it cause trouble for long captions
            caps = look_behind(i, lambda l: indented(l) and not blank(l), lines)
            deletes.extend(caps)
            i += len(caps)
        # .. table:: Dataset versus computer memory and computational power
        #    +-...
        #    |
        #    +-...
        #
        # :label:``tab_intro_decade``
        # ->
        # .. _tab_intro_decade:
        #
        # .. table:: Dataset versus computer memory and computational power
        #
        #    +-...
        #    |
        #    +-...
        #
        elif line.startswith('.. table::'):
            # Add indent to table caption for long captions
            caps = look_behind(i+1, lambda l: not indented(l) and not blank(l),
                               lines)
            for j in caps:
                lines[j] = '   ' + lines[j]
            i += len(caps) + 1
        else:
            i += 1

    # change :label:my_label: into rst format
    lines = delete_lines(lines, deletes)
    deletes = []

    for i, line in enumerate(lines):
        pos, new_line = 0, ''
        while True:
            match = common.rst_mark_pattern.search(line, pos)
            if match is None or match[2] is None:
                new_line += line[pos:]
                break
            start, end = match.start(), match.end()
            # e.g., origin=':label:``fig_jupyter``', key='label', value='fig_jupyter'
            origin, key, value = match[0], match[1], match[2]
            assert value.startswith('``') and value.endswith('``'), value
            value = value[2:-2]
            new_line += line[pos:start]
            pos = end
            # assert key in ['label', 'eqlabel', 'ref', 'numref', 'eqref', 'width', 'height'], 'unknown key: ' + key
            if key == 'label':
                new_line += '.. _' + value + ':'
            elif key in ['ref', 'numref', 'cite']:
                new_line += ':'+key+':`'+value+'`'
            elif key == 'eqref':
                new_line += ':eq:`'+value+'`'
            elif key in ['class', 'func']:
                new_line += ':py:'+key+':`'+value+'`'
            # .. math:: f
            #
            # :eqlabel:``gd-taylor``
            # ->
            # .. math:: f
            #    :label: gd-taylor
            elif key == 'eqlabel':
                new_line += '   :label: '+value
                if blank(lines[i-1]):
                    deletes.append(i-1)
            elif key in ['width', 'height']:
                new_line += '   :'+key+': '+value
            elif key == 'bibliography':
                # a hard coded plain bibtex style...
                new_line += ('.. bibliography:: ' + value +
                             '\n   :style: apa')
                             # '\n   :style: apa\n   :all:') MM 20200104 removed ':all:' so only the cited references get printed
            else:
                logging.fatal(f'unknown key {key}')

        lines[i] = new_line
    lines = delete_lines(lines, deletes)

    def move(i, j): # move line i to line j
        lines.insert(j, lines[i])
        if i > j:
            del lines[i+1]
        else:
            del lines[i]

    # move :width: or :width: just below .. figure::
    for i, line in enumerate(lines):
        if line.startswith('.. figure::'):
            for j in range(i+1, len(lines)):
                line_j = lines[j]
                if not indented(line_j) and not blank(line_j):
                    break
                if line_j.startswith('   :width:') or line_j.startswith('   :height:'):
                    move(j, i+1)

    # move .. _label: before a image, a section, or a table
    lines.insert(0, '')
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('.. _'):
            for j in range(i-1, -1, -1):
                line_j = lines[j]
                if (line_j.startswith('.. table:')
                    or line_j.startswith('.. figure:')):
                    move(i, j-1)
                    lines.insert(j-1, '')
                    i += 1  # Due to insertion of a blank line
                    break
                if (len(set(line_j)) == 1
                    and line_j[0] in ['=','~','_', '-']):
                    k = max(j-2, 0)
                    move(i, k)
                    lines.insert(k, '')
                    i += 1  # Due to insertion of a blank line
                    break
        i += 1

    # change .. image:: to .. figure:: to they will be center aligned
    for i, line in enumerate(lines):
        if '.. image::' in line:
            lines[i] = line.replace('.. image::', '.. figure::')

    # sometimes the code results contains vt100 codes, widely used for
    # coloring, while it is not supported by latex.
    for i, l in enumerate(lines):
        lines[i] = re.sub(r'\x1b\[[\d;]*K', '',
                          re.sub(r'\x1b\[[\d;]*m', '', l))

    return '\n'.join(lines)
