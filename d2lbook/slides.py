import argparse
import glob
import sys
from d2lbook import config, notebook
import logging
import glob
import nbformat
import pathlib

def slides():
    parser = argparse.ArgumentParser(description='Generate slides from markdown files.')
    parser.add_argument('filename', nargs='+', help='the source markdown files')
    parser.add_argument('--tab', default=None, help='the tab')
    args = parser.parse_args(sys.argv[2:])
    tab = args.tab
    cf = config.Config()
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
            nb = notebook.get_slides(nb, cf)
            if not nb.cells:
                logging.warning('No slides generated from '+md)
                continue
            nb['metadata'].update({'language_info':{'name':'python'}})
            output_fn = str(pathlib.Path(md).with_suffix(''))+('_'+tab if tab else '_')+'_slides.ipynb'
            with open(output_fn, 'w') as f:
                f.write(nbformat.writes(nb))
            logging.info('Write slides into '+output_fn)

