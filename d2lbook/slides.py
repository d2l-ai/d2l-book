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

def slides():
    parser = argparse.ArgumentParser(description='Generate slides from markdown files.')
    parser.add_argument('filename', nargs='+', help='the source markdown files')
    parser.add_argument('--tab', default=None, help='the tab')
    args = parser.parse_args(sys.argv[2:])
    tab = args.tab
    cf = config.Config()
    sd = Slides(cf)
    for fn in args.filename:
        fns = glob.glob(fn)
        if not len(fns):
            logging.warning('Not found '+fn)
            return
        for md in fns:
            with open(md, 'r') as f:
                nb = notebook.read_markdown(f.read())
            if tab:
                nb = notebook.split_markdown_cell(nb)
                nb = notebook.get_tab_notebook(nb, tab, cf.default_tab)
            output_fn = str(pathlib.Path(md).with_suffix(''))+('_'+tab if tab else '_')+'_slides.ipynb'
            sd.generate(nb, output_fn)

class Slides():
    def __init__(self, config):
        self._valid = config.slides and config.slides['github_repo']
        if not self._valid:
            return
        self.config = config
        repo = utils.split_config_str(self.config.slides['github_repo'], 2)
        self._repo = {r[0]:r[1] for r in repo}

    def deploy(self):
        if not self._valid:
            return
        repo = self._repo.get(self.config.tab, '')
        if not repo:
            return
        bash_fname = os.path.join(os.path.dirname(__file__), 'upload_github.sh')
        utils.run_cmd(['bash', bash_fname, self.config.slides_dir, repo,
                      self.config.project['release']])

    def _generate(self, nb: notebooknode.NotebookNode) -> notebooknode.NotebookNode:
        """Get all slide blocks and return."""
        new_cells = []
        has_slides = False
        for cell in nb.cells:
            if cell.cell_type=='markdown':
                lines = cell.source.splitlines()
                blk = []
                in_blk = False
                for l in lines:
                    mark = common.md_mark_pattern.match(l)
                    begin = mark and mark.groups()[0] == 'begin_slide'
                    end = mark and mark.groups()[0] == 'end_slide'
                    if begin:
                        in_blk = True
                        has_slides = True
                        typ = [a.strip().replace('`','') for a in mark.groups()[1].split(',')] if mark.groups()[1] else []
                        slide_type = "slide"
                        if 'cont' in typ:
                            slide_type = '-'
                    elif end:
                        if blk:
                            new_cells.append(nbformat.v4.new_markdown_cell('\n'.join(blk),
                                metadata={"slideshow": {"slide_type": slide_type}}))
                            blk = []
                            in_blk = False
                    elif in_blk:
                        if l.startswith('# '):
                            l = '### ' + l[2:]
                        blk.append(l)
            else:
                new_cells.append(cell)
        slide = notebook.create_new_notebook(nb, new_cells if has_slides else [])
        slide['metadata'].update({
            'language_info':{'name':'python'},
            'celltoolbar':'Slideshow',
            'rise': {
                "autolaunch": True,
                "enable_chalkboard": True,
                "overlay": f"<div class='my-top-right'>{self.config.slides['top_right']}</div><div class='my-top-left'>{self.config.slides['top_left']}</div>"
            }})
        return slide

    def generate(self, nb: notebooknode.NotebookNode, output_fn: str):
        """Get all slide blocks and write to file."""
        nb = self._generate(nb)
        if not nb.cells:
            return
        dirname = os.path.dirname(output_fn)
        utils.mkdir(dirname)
        with open(output_fn, 'w') as f:
            f.write(nbformat.writes(nb))
        logging.info('Write slides into '+output_fn)

        with open(dirname + '/rise.css', 'w') as f:
            f.write('''
div.text_cell_render.rendered_html {
    padding: 0 0.5em;
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

