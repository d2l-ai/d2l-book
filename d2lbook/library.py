"""Save codes into library"""
from typing import List
from d2lbook import notebook
import logging
import os

def _write_header(f):
    f.write('# This file is generated automatically through:\n')
    f.write('#    d2lbook build lib\n')
    f.write('# Don\'t edit it directly\n\n')

def save_mark(notebooks: List[str], lib_fname: str, save_mark: str):
    logging.info('Matching with the pattern: "%s"', save_mark)
    with open(lib_fname, 'w') as f:
        _write_header(f)
        lib_name = os.path.dirname(lib_fname)
        lib_name = lib_name.split('/')[-1]
        f.write('import sys\n'+lib_name+' = sys.modules[__name__]\n\n')

        for nb in notebooks:
            _save_code(nb, f, save_mark=save_mark)
        logging.info('Saved into %s', lib_fname)

def save_tab(notebooks: List[str], lib_fname: str, tab: str, default_tab: str):
    logging.info(f'Matching with the pattern: "#@save", seaching for tab {tab}')
    with open(lib_fname, 'w') as f:
        _write_header(f)
        for nb in notebooks:
           _save_code(nb, f, tab=tab, default_tab=default_tab)
        logging.info('Saved into %s', lib_fname)

def _save_code(input_fn, output_fp, save_mark=None, tab=None, default_tab=None):
    """get the code blocks (import, class, def) that will be saved"""
    with open(input_fn, 'r') as f:
        nb = notebook.read_markdown(f.read())
    if tab:
        nb = notebook.get_tab_notebook(nb, tab, default_tab)
        if not nb:
            return
    saved = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            for i, l in enumerate(lines):
                if ((save_mark and l.strip().startswith('#') and save_mark in l) or
                    (tab and l.strip().endswith('@save') and '#'in l)):
                    if l.strip().startswith('#'):
                        block = [lines[i+1]]
                    else:
                        block = lines[i:i+2]
                    # For code block only containing import statements (e.g., in
                    # preface.md)
                    if lines[i+1].startswith('import') or lines[i+1].startswith('from'):
                        for j in range(i+2, len(lines)):
                            block.append(lines[j])
                    # For code blocks containing def or class
                    else:
                        for j in range(i+2, len(lines)):
                            l = lines[j]
                            if not l.startswith(' ') and len(l):
                                break
                            block.append(l)
                    if len(block[-1]) == 0:
                        del block[-1]
                    saved.append(block)

    if saved:
        logging.info('Found %d blocks in %s', len(saved), input_fn)
        for block in saved:
            logging.info(' --- %s', block[0])
            code = '# Defined in file: %s\n%s\n\n\n' %(input_fn, '\n'.join(block))
            output_fp.write(code)
