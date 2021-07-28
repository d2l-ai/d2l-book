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
import isort

HEADER = '#################   WARNING   ################\n'
def _write_header(f):
    f.write(HEADER)
    f.write('# The below part is generated automatically through:\n')
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
            f.write(
                f'# This file is generated from {str(nbfile)} automatically through:\n'
            )
            f.write('#    d2lbook build lib\n')
            f.write('# Don\'t edit it directly\n\n')
            for blk in saved:
                f.write(blk + '\n\n')
            logging.info(f'Found {len(saved)} blocks in {str(nbfile)}')

def save_mark(notebooks: List[str], lib_fname: str, save_mark: str):
    logging.info('Matching with the pattern: "%s"', save_mark)
    with open(lib_fname, 'w') as f:
        _write_header(f)
        lib_name = os.path.dirname(lib_fname)
        lib_name = lib_name.split('/')[-1]
        f.write('import sys\n' + lib_name + ' = sys.modules[__name__]\n\n')

        for nb in notebooks:
            _save_code(nb, f, save_mark=save_mark)
        logging.info('Saved into %s', lib_fname)

def save_tab(notebooks: List[str], lib_fname: str, tab: str, default_tab: str):
    logging.info(
        f'Matching with the pattern: "#@save", seaching for tab {tab}')
    custom_header = []
    if os.path.exists(lib_fname):
        with open(lib_fname, 'r') as f:
            lines = f.readlines()
        for i, l in enumerate(lines):
            if l.strip() == HEADER.strip():
                custom_header = lines[:i]
                break

    with open(lib_fname, 'w') as f:
        if custom_header:
            f.write(''.join(custom_header))            
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
            for j in range(i + 1, len(lines)):
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
    return format_code('\n'.join(block))

def _save_code(input_fn, output_fp, save_mark='@save', tab=None,
               default_tab=None):
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
            code = '# Defined in file: %s\n%s\n\n\n' % (input_fn, block)
            output_fp.write(code)

def _parse_mapping_config(config: str, split_line=True):
    """Parse config such as: numpy -> asnumpy, reshape, ...
    Return a list of string pairs
    """
    terms = []
    for line in config.splitlines():
        if split_line:
            terms.extend(line.split(','))
        else:
            terms.append(line)
    mapping = []
    for term in terms:
        term = term.strip()
        if not term:
            continue
        if len(term.split('->')) == 2:
            a, b = term.split('->')
            mapping.append((a.strip(), b.strip()))
        else:
            mapping.append((term, term))
    return mapping

def node_to_source(node):
    if isinstance(node, ast.Constant):
        return str(node.value)
    return astor.to_source(node).rstrip()

def save_alias(tab_lib):
    """Save alias into the library file"""
    alias = ''
    if 'alias' in tab_lib:
        alias += tab_lib['alias'].strip() + '\n'
    if 'lib_name' in tab_lib:
        lib_name = tab_lib["lib_name"]
        if 'simple_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['simple_alias'])
            for a, b in mapping:
                if a.endswith('('): a = a[:-1]
                if b.endswith('('): b = b[:-1]
                alias += f'\n{a} = {lib_name}.{b}'
        if 'fluent_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['fluent_alias'])
            alias += '\n' + '\n'.join([
                f'{a} = lambda x, *args, **kwargs: x.{b}(*args, **kwargs)'
                for a, b in mapping])
        if 'args_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['args_alias'], split_line=False)
            for a, b in mapping:
                alias += f'\ndef {a}:\n    return {b}'
    if alias:
        lib_file = tab_lib['lib_file']
        with open(lib_file, 'a') as f:
            logging.info(
                f'Wrote {len(alias.splitlines())} alias into {lib_file}')
            f.write('# Alias defined in config.ini\n')
            f.write(alias + '\n\n')

def replace_call(source: str, mapping, replace_fn):

    matched = False
    for a in mapping:
        if 'd2l.'+a in source:
            matched = True
    if not matched:
        return source
    lines = source.splitlines()
    if lines[0].startswith('%'):
        source = '\n'.join(lines[1:])
    for _ in range(100):  # 100 is a (random) big enough number
        replaced = False
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'd2l' and
                node.func.attr in mapping):
                new_node = replace_fn(node, mapping[node.func.attr])
                if new_node:
                    source = source.replace(
                        ast.get_source_segment(source, node),
                        new_node if isinstance(new_node, str) else node_to_source(new_node))
                    replaced = True
                    break
        if not replaced:
            break
    if lines[0].startswith('%'):
        source = lines[0] + '\n' + source
    return source


def replace_fluent_alias(source, fluent_mapping):
    def _replace(node, b):
        return ast.Call(
            ast.Attribute(value=node.args[0], attr=b),
            node.args[1:], node.keywords)
    return replace_call(source, fluent_mapping, _replace)

def replace_args_alias(source, args_mapping):
    def _replace(node, b):
        a_args, b = b
        a_kwargs = {a: b for a, b in a_args if not a.startswith('a_')}
        a_args = [a for a, _  in a_args if a.startswith('a_')]
        if len(node.args) != len(a_args):
            return None
        key_value = {a : node_to_source(arg) for arg, a in zip(node.args, a_args)}
        for kw in node.keywords:
            assert kw.arg in a_kwargs, (kw.arg, a_kwargs)
            key_value['='+kw.arg] = '='+node_to_source(kw.value)
        # remove not appeared keywords
        b_call = ast.parse(b).body[0].value
        if isinstance(b_call, ast.Call):
            new_keywords = [kw for kw in b_call.keywords if '='+kw.value.id in key_value]
            b_call.keywords = new_keywords
            b = node_to_source(b_call)
        for k, v in key_value.items():
            b = b.replace(k, v)
        return b
    return replace_call(source, dict(args_mapping), _replace)

def call_args(call_str):
    call = ast.parse(call_str).body[0].value
    assert isinstance(call, ast.Call), call_str
    name = call.func.id
    args = [(a.id,None) for a in call.args] + [(k.arg, k.value) for k in call.keywords]
    return name, args

def replace_alias(nb, tab_lib):
    nb = copy.deepcopy(nb)
    patterns = []
    fluent_mapping = {}
    args_mapping = {}
    if 'reverse_alias' in tab_lib:
        patterns += _parse_mapping_config(tab_lib['reverse_alias'], split_line=False)
    if 'lib_name' in tab_lib:
        lib_name = tab_lib["lib_name"]
        if 'simple_alias' in tab_lib:
            mapping = _parse_mapping_config(tab_lib['simple_alias'])
            patterns += [(f'd2l.{a}', f'{lib_name}.{b}') for a, b in mapping]
        if 'fluent_alias' in tab_lib:
            fluent_mapping = dict(_parse_mapping_config(tab_lib['fluent_alias']))
        if 'args_alias' in tab_lib:
            for a, b in _parse_mapping_config(tab_lib['args_alias'], split_line=False):
                name, args = call_args(a)
                args_mapping[name] = (args, b)

    for cell in nb.cells:
        if cell.cell_type == 'code':
            for p, r in patterns:
                cell.source = cell.source.replace(p, r)
            if fluent_mapping:
                cell.source = replace_fluent_alias(cell.source, fluent_mapping)
            if args_mapping:
                cell.source = replace_args_alias(cell.source, args_mapping)
    return nb

def format_code(source: str):
    if 'import ' in source:
        config = isort.settings.Config(no_lines_before=[
            isort.settings.FUTURE, isort.settings.STDLIB, isort.settings.
            THIRDPARTY, isort.settings.FIRSTPARTY, isort.settings.LOCALFOLDER])

        source = isort.code(source, config=config)

    # fix the bug that yapf cannot handle jupyter magic
    for l in source.splitlines():
        if l.startswith('%') or l.startswith('!'):
            return source

    # fix the bug that yapf remove the tailling ;
    has_tailling_semicolon = source.rstrip().endswith(';')

    style = {
        'DISABLE_ENDING_COMMA_HEURISTIC': True,
        'SPACE_BETWEEN_ENDING_COMMA_AND_CLOSING_BRACKET': False,
        'SPLIT_BEFORE_CLOSING_BRACKET': False,
        'SPLIT_BEFORE_DICT_SET_GENERATOR': False,
        'SPLIT_BEFORE_LOGICAL_OPERATOR': False,
        'SPLIT_BEFORE_NAMED_ASSIGNS': False,
        'COLUMN_LIMIT': 78,
        'BLANK_LINES_AROUND_TOP_LEVEL_DEFINITION': 1,}
    source = FormatCode(source, style_config=style)[0].strip()
    if has_tailling_semicolon: source += ';'
    return source

def format_code_nb(nb):
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.source = format_code(cell.source)
    return nb
