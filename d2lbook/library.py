"""Save codes into library"""
from typing import List
from d2lbook import notebook
import logging
import os
import copy
import re
import pathlib
import ast
import astor
from yapf.yapflib.yapf_api import FormatCode

def _write_header(f):
    f.write('# This file is generated automatically through:\n')
    f.write('#    d2lbook build lib\n')
    f.write('# Don\'t edit it directly\n\n')

def save_file(root_dir: str, nbfile: str):
    nbfile = pathlib.Path(nbfile)
    pyfile = root_dir / nbfile.with_suffix('.py')

    with nbfile.open('r') as f:
        nb = notebook.read_markdown(f.read())

    saved = []
    save_all = False
    for cell in nb.cells:
        if cell.cell_type == 'code':
            src = cell.source.lstrip()
            if re.search('# *@save_all', src):
                save_all = True
            if save_all or re.search('# *@save_cell', src):
                saved.append(src)
            else:
                blk = _save_block(src, '@save')
                if blk:
                    saved.append(blk)
    if saved:
        with pyfile.open('w') as f:
            f.write(f'# This file is generated from {str(nbfile)} automatically through:\n')
            f.write('#    d2lbook build lib\n')
            f.write('# Don\'t edit it directly\n\n')
            for blk in saved:
                f.write(blk+'\n\n')
            logging.info(f'Found {len(saved)} blocks in {str(nbfile)}')

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

def save_version(version: str, version_fn: str):
    if version and version_fn:
        with open(version_fn, 'r', encoding='UTF-8') as f:
            lines = f.read().split('\n')
        for i, l in enumerate(lines):
            if '__version__' in l:
                lines[i] = f'__version__ = "{version}"'
                logging.info(f'save {lines[i]} into {version_fn}')
        with open(version_fn, 'w') as f:
            f.write('\n'.join(lines))

def _save_block(source: str, save_mark: str):
    if not save_mark: return ''
    lines = source.splitlines()
    block = []
    for i, l in enumerate(lines):
        m = re.search(f'# *{save_mark}', l)
        if m:
            l = l[:m.span()[0]].rstrip()
            if l: block.append(l)
            for j in range(i+1, len(lines)):
                l = lines[j]
                if not l.startswith(' ') and len(l):
                    block.append(lines[j])
                else:
                    for k in range(j, len(lines)):
                        if lines[k].startswith(' ') or not len(lines[k]):
                            block.append(lines[k])
                        else:
                            break
                    break
    return format_code('\n'.join(block)).strip()

def _save_code(input_fn, output_fp, save_mark='@save', tab=None, default_tab=None):
    """get the code blocks (import, class, def) that will be saved"""
    with open(input_fn, 'r', encoding='UTF-8') as f:
        nb = notebook.read_markdown(f.read())
    if tab:
        nb = notebook.get_tab_notebook(nb, tab, default_tab)
        if not nb:
            return
    saved = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            block = _save_block(cell.source, save_mark)
            if block: saved.append(block)
    if saved:
        logging.info('Found %d blocks in %s', len(saved), input_fn)
        for block in saved:
            code = '# Defined in file: %s\n%s\n\n\n' %(input_fn, block)
            output_fp.write(code)

def _parse_mapping_config(config: str):
    """Parse config such as: numpy -> asnumpy, reshape, ...
    Return a list of string pairs
    """
    mapping = []
    for line in config.splitlines():
        for term in line.split(','):
            term = term.strip()
            if not term:
                continue
            if len(term.split('->')) == 2:
                a, b = term.split('->')
                mapping.append((a.strip(), b.strip()))
            else:
                mapping.append((term, term))
    return mapping

def save_alias(tab_lib):
    """Save alias into the library file"""
    alias = ''
    if 'alias' in tab_lib:
        alias += tab_lib['alias'].strip()+'\n'
    if 'lib_name' in tab_lib:
        lib_name = tab_lib["lib_name"]
        if 'simple_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['simple_alias'])
            alias += '\n'+'\n'.join([f'{a} = {lib_name}.{b}' for a, b in mapping])
        if 'fluent_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['fluent_alias'])
            alias += '\n'+'\n'.join([f'{a} = lambda x, *args, **kwargs: x.{b}(*args, **kwargs)'
                                for a, b in mapping])
    if alias:
        lib_file = tab_lib['lib_file']
        with open(lib_file, 'a') as f:
            logging.info(f'Wrote {len(alias.splitlines())} alias into {lib_file}')
            f.write('# Alias defined in config.ini\n')
            f.write(alias+'\n\n')

def replace_fluent_alias(source, fluent_mapping):
    fluent_mapping = {a:b for a, b in fluent_mapping}
    new_src = source
    for _ in range(100):  # 100 is a (random) big enough number
        replaced = False
        tree = ast.parse(new_src)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'd2l' and
                node.func.attr in fluent_mapping):
                new_node = ast.Call(
                    ast.Attribute(value=node.args[0],
                                  attr=fluent_mapping[node.func.attr]),
                    node.args[1:], node.keywords)
                new_src = new_src.replace(
                    ast.get_source_segment(new_src, node),
                    astor.to_source(new_node).rstrip())
                replaced = True
                break
        if not replaced:
            break
    return new_src

def replace_alias(nb, tab_lib):
    nb = copy.deepcopy(nb)
    patterns = []
    fluent_mapping = []
    if 'reverse_alias' in tab_lib:
        patterns += _parse_mapping_config(tab_lib['reverse_alias'])
    if 'lib_name' in tab_lib:
        lib_name = tab_lib["lib_name"]
        if 'simple_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['simple_alias'])
            patterns += [(f'd2l.{a}', f'{lib_name}.{b}') for a, b in mapping]
        if 'fluent_alias' in tab_lib:
            fluent_mapping = _parse_mapping_config(tab_lib['fluent_alias'])

    for cell in nb.cells:
        if cell.cell_type == 'code':
            for p, r in patterns:
                cell.source = re.sub(p, r, cell.source)
            if fluent_mapping:
                for a, _ in fluent_mapping:
                    if 'd2l.'+a in cell.source:
                        cell.source = replace_fluent_alias(cell.source, fluent_mapping)
                        break
    return nb

def format_code(source: str):
    style = {
        'DISABLE_ENDING_COMMA_HEURISTIC':True,
        'SPACE_BETWEEN_ENDING_COMMA_AND_CLOSING_BRACKET':False,
        'SPLIT_BEFORE_CLOSING_BRACKET':False,
        'SPLIT_BEFORE_DICT_SET_GENERATOR':False,
        'SPLIT_BEFORE_LOGICAL_OPERATOR':False,
        'SPLIT_BEFORE_NAMED_ASSIGNS':False,
        'COLUMN_LIMIT':78,
    }
    return FormatCode(source, style_config=style)[0]

def format_code_nb(nb):
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.source = format_code(cell.source)
    return nb
