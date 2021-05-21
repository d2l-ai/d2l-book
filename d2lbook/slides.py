import argparse
import glob
import sys
from d2lbook import config, notebook, common, utils
import logging
import glob
import nbformat
import pathlib
import os
from nbformat import notebooknode
from typing import Optional
import re

def slides():
    parser = argparse.ArgumentParser(
        description='Generate slides from markdown files.')
    parser.add_argument('filename', nargs='+',
                        help='the source markdown files')
    parser.add_argument('--tab', default=None, help='the tab')
    args = parser.parse_args(sys.argv[2:])
    tab = args.tab
    cf = config.Config()
    sd = Slides(cf)
    for fn in args.filename:
        fns = glob.glob(fn)
        if not len(fns):
            logging.warning('Not found ' + fn)
            return
        for md in fns:
            with open(md, 'r') as f:
                nb = notebook.read_markdown(f.read())
            if tab:
                nb = notebook.split_markdown_cell(nb)
                nb = notebook.get_tab_notebook(nb, tab, cf.default_tab)
            output_fn = str(pathlib.Path(md).with_suffix('')) + (
                '_' + tab if tab else '_') + '_slides.ipynb'
            sd.generate(nb, output_fn)

class Slides():
    def __init__(self, config):
        self._valid = config.slides and config.slides['github_repo']
        if not self._valid:
            return
        self.config = config
        repo = utils.split_config_str(self.config.slides['github_repo'], 2)
        self._repo = {r[0]: r[1] for r in repo}

    def deploy(self):
        if not self._valid:
            return
        repo = self._repo.get(self.config.tab, '')
        if not repo:
            return
        bash_fname = os.path.join(os.path.dirname(__file__),
                                  'upload_github.sh')
        utils.run_cmd([
            'bash', bash_fname, self.config.slides_dir, repo,
            self.config.project['release']])

    def generate_readme(self):
        repo = self._repo.get(self.config.tab, '')
        if not self._valid or not repo: return

        root = os.path.join(self.config.src_dir,
                            self.config.build['index'] + '.md')
        notebooks = notebook.get_toc(root)
        items = []
        for nb in notebooks:
            p = (self.config.slides_dir /
                 pathlib.Path(nb)).with_suffix('.ipynb')
            if p.exists():
                p = str(p.relative_to(self.config.slides_dir))
                base = 'https://nbviewer.jupyter.org/format/slides/github'
                items.append(f' - [{p}]({base}/{repo}/blob/main/{p})')

        with open(os.path.join(self.config.slides_dir, 'README.md'), 'w') as f:
            f.write(f'# {repo}\n')
            f.write('''
This repo contains generated notebook slides. To open it locally, we suggest you to install the [rise](https://rise.readthedocs.io/en/stable/) extension.

You can also preview them in nbviwer:
''')
            f.write('\n'.join(items))

    def generate(self, nb: notebooknode.NotebookNode, output_fn: str):
        """Get all slide blocks and write to file."""
        nb = _generate_slides(nb)
        if not nb: return

        nb['metadata'].update({
            'language_info': {
                'name': 'python'},
            'celltoolbar': 'Slideshow',
            'rise': {
                "autolaunch":
                True,
                "enable_chalkboard":
                True,
                "overlay":
                f"<div class='my-top-right'>{self.config.slides['top_right']}</div><div class='my-top-left'>{self.config.slides['top_left']}</div>",
                "scroll": 
                True
            }})
        dirname = os.path.dirname(output_fn)
        utils.mkdir(dirname)
        with open(output_fn, 'w') as f:
            f.write(nbformat.writes(nb))
        logging.info('Write slides into ' + output_fn)

        with open(dirname + '/rise.css', 'w') as f:
            f.write('''
div.text_cell_render.rendered_html {
    padding: 0.35em 0.1em;
}

div.code_cell {
    font-size: 120%;
}

div.my-top-right {
    position: absolute;
    right: 5%;
    top: 1em;
    font-size: 2em;
}

div.my-top-left {
    position: absolute;
    left: 5%;
    top: 1em;
    font-size: 2em;
}
''')

def remove_slide_marks(
        nb: notebooknode.NotebookNode) -> notebooknode.NotebookNode:
    """Remove all slide blocks and return."""
    new_cells = []
    for cell in nb.cells:
        if cell.cell_type != 'markdown':
            new_cells.append(cell)
        else:
            src = cell.source
            matches = _match_slide_marks(cell.source)
            for pair, text in matches:
                old = pair[0] + text + pair[1]
                new = '' if pair[0].endswith('~~') else text
                src = src.replace(old, new)
            new_cells.append(nbformat.v4.new_markdown_cell(src))
    return notebook.create_new_notebook(nb, new_cells)

def _generate_slides(
        nb: notebooknode.NotebookNode) -> Optional[notebooknode.NotebookNode]:
    new_cells = []
    has_slides = False
    for cell in nb.cells:
        if cell.cell_type != 'markdown':
            # remove comments
            lines = cell.source.splitlines()
            new_lines = []
            for l in lines:
                new_l = re.sub(r'\#\ .*', '', l)
                if new_l != l and not new_l.rstrip(): 
                    continue
                new_lines.append(new_l.rstrip())
            cell.source = '\n'.join(new_lines)
            new_cells.append(cell)
        else:
            slide_type = '-'
            src = []
            matches = _match_slide_marks(cell.source)
            if matches:
                has_slides = True
            for pair, text in matches:
                if pair[0].startswith('['):
                    slide_type = 'slide'
                src.append(text)
            src = '\n'.join(src)
            if src:
                # cannot simply use . as it could be in code such as `a.text()`
                for m in ('.\n', '. '):
                    sentences = [s.strip() for s in src.split(m)]
                    src = m.join([s[0].upper() + s[1:] for s in sentences])
                src = src.replace('.$$', '$$').replace(',$$', '$$')
                src = src.rstrip(',. \n:，。：')
            # find level-1 head
            for l in cell.source.splitlines():
                if l.strip().startswith('# '):
                    src = l + '\n\n' + src
                    break
            if not src: continue
            new_cells.append(
                nbformat.v4.new_markdown_cell(
                    src, metadata={"slideshow": {
                        "slide_type": slide_type}}))
    if not has_slides:
        return None

    # merge code cell in the same slide if they don't have output
    md_code_group = common.group_list(new_cells,
                                      lambda cell, _: cell.cell_type == 'code')
    merged_code_cell = []
    for is_code, group in md_code_group:
        if not is_code:
            merged_code_cell.extend(group)
        else:
            src = []
            for i, cell in enumerate(group):
                src.append(cell.source)
                if i == len(group) - 1 or 'outputs' in cell and len(
                        cell['outputs']):
                    cell.source = '\n\n'.join(src)
                    src = []
                    merged_code_cell.append(cell)
    # clean #@save
    for cell in merged_code_cell:
        if cell.cell_type == 'code':
            cell.source = cell.source.replace( \
                '\n#@save\n', '\n').replace('#@save', '').strip()
    return notebook.create_new_notebook(nb, merged_code_cell)

def _match_slide_marks(text: str):
    """return the texts in a pair. cannot be recursive"""
    # the pair marks to generate slides
    pairs = (('[**', '**]'), ('(**', '**)'), ('[~~', '~~]'), ('(~~', '~~)'))
    matches = []
    for p in pairs:
        assert len(p) == 2, f'not a valid pair: {p}'
        start = [i for i in range(len(text)) if text.startswith(p[0], i)]
        end = [i for i in range(len(text)) if text.startswith(p[1], i)]
        assert len(start) == len(end), f'some {p} are not enclosed in {text}'
        for i, (s, e) in enumerate(zip(start, end)):
            s += len(p[0])
            assert s <= e, f'some {p} are overlapped'
            if i < len(start) - 1:
                assert e < start[i + 1], f'some {p} are overlapped'
            # handle if it's a markdown link such as [**a**](https://xx)
            if p[1].endswith(']') and text.startswith(p[1] + '(', e):
                continue
            matches.append((p, s, e))
    matches.sort(key=lambda x: x[1])
    for i in range(len(matches) - 1):
        assert matches[i][1] < matches[i+1][1], \
                f'some {matches[i][0]} and {matches[i+1][0]} are overlapped'
    return [(p, text[s:e]) for p, s, e in matches]
