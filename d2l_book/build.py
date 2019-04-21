import os
import sys
import glob
import notedown
import nbformat
import nbconvert
import pkg_resources
import logging
import shutil
import time
import configparser
import argparse


__all__  = ['build']

def build():
    parser = argparse.ArgumentParser(description='build')
    parser.add_argument('commands', nargs='+', help=' ')
    args = parser.parse_args(sys.argv[2:])
    config =  configparser.ConfigParser()
    config.read('config.ini')
    builder = Builder(config)
    commands = {'eval': builder.eval_output, 'rst':builder.get_rst}
    for cmd in args.commands:
        commands[cmd]()


def rm_ext(filename):
    return os.path.splitext(filename)[0]


def find_files(pattern, root):
    fnames = []
    patterns = pattern.split(' ')
    for p in patterns:
        if len(p) == 0:
            continue
        p = os.path.join(root, p)
        if os.path.isdir(p):
            p += '*'
        for fn in glob.glob(p):
            if not os.path.isfile(p):
                fnames.append(fn)
    return fnames

def get_mtimes(fnames):
    if isinstance(fnames, str):
        fnames = [fnames]
    return [os.path.getmtime(fn) for fn in fnames]

def get_updated_files(src_fnames, src_dir, tgt_dir, new_ext, deps_mtime=0):
    updated_fnames = []
    for src_fn in src_fnames:
        tgt_fn = os.path.join(tgt_dir, os.path.relpath(src_fn, src_dir))
        tgt_fn = rm_ext(tgt_fn) + '.' + new_ext
        if (not os.path.exists(tgt_fn) # new
            or os.path.getmtime(src_fn) > os.path.getmtime(tgt_fn) # target is old
            or os.path.getmtime(src_fn) < deps_mtime): # deps is updated
            updated_fnames.append((src_fn, tgt_fn))
    return updated_fnames

# can be run in parallel
def eval_notebook(input_fn, output_fn, run_cells, timeout=20*60, lang='python'):
    # read
    reader = notedown.MarkdownReader(match='strict')
    with open(input_fn, 'r') as f:
        notebook = reader.read(f)
    # evaluate
    if run_cells:
        notedown.run(notebook, timeout)
    # write
    notebook['metadata'].update({'language_info':{'name':lang}})
    with open(output_fn, 'w') as f:
        f.write(nbformat.writes(notebook))

def ipynb2rst(input_fn, output_fn):
    #os.system('jupyter nbconvert --to rst '+input_fn + ' --output '+
    #          os.path.relpath(output_fn, os.path.dirname(input_fn)))

    with open(input_fn, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
    writer = nbconvert.RSTExporter()
    image_dir = rm_ext(os.path.basename(output_fn))
    resources = {'output_files_dir':image_dir}
    (body, resources) = writer.from_notebook_node(notebook, resources)
    with open(output_fn, 'w') as f:
        f.write(body)
    base_dir = os.path.dirname(output_fn)
    outputs = resources['outputs']
    for fn in outputs:
        full_fn = os.path.join(base_dir, fn)
        mkdir(os.path.dirname(full_fn))
        with open(full_fn, 'wb') as f:
            f.write(outputs[fn])

def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)

# def md2ipynb(input_fn, outout_fn):

class Builder(object):
    def __init__(self, config):
        self.config = config
        self.src_dir = config['build'].get('source_dir', '.')
        self.tgt_dir = config['build'].get('output_dir', '_build')
        mkdir(self.tgt_dir)
        self.eval_dir = os.path.join(self.tgt_dir, 'eval')
        self.rst_dir = os.path.join(self.tgt_dir, 'rst')
        self.html_dir = os.path.join(self.tgt_dir, 'html')
        self.pdf_dir = os.path.join(self.tgt_dir, 'pdf')

    def _find_md_files(self):
        build = self.config['build']
        excluded_files = find_files(build.get('exclusions', ''), self.src_dir)
        pure_markdowns = find_files(build.get('non-notebooks', ''), self.src_dir)
        pure_markdowns = [fn for fn in pure_markdowns if fn not in excluded_files]

        notebooks = find_files(build.get('notebooks', ''), self.src_dir)
        notebooks = [fn for fn in notebooks if fn not in pure_markdowns and fn
                     not in pure_markdowns]
        depends = find_files(build.get('dependences', ''), self.src_dir)
        return notebooks, pure_markdowns, depends


    def eval_output(self):
        """Evaluate the notebooks and save them in a different folder"""
        notebooks, pure_markdowns, depends = self._find_md_files()
        depends_mtimes = get_mtimes(depends)
        latest_depend = max(depends_mtimes) if len(depends_mtimes) else 0
        updated_notebooks = get_updated_files(
            notebooks, self.src_dir, self.eval_dir, 'ipynb', latest_depend)
        updated_markdowns = get_updated_files(
            pure_markdowns, self.src_dir, self.eval_dir, 'md', latest_depend)
        logging.info('%d notedowns and %d markdowns are out dated',
                     len(updated_notebooks), len(updated_markdowns))
        for src, tgt in updated_notebooks:
            logging.info('Evaluating %s, save as %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            start = time.time()
            run_cells = self.config['build'].get('eval_notebook', 'True').lower()

            eval_notebook(src, tgt, run_cells=='true')
            logging.info('Finished in %.1f sec', time.time() - start)

        for src, tgt in updated_markdowns:
            logging.info('Copy %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            shutil.copyfile(src, tgt)

    def get_rst(self):
        notebooks = glob.glob(os.path.join(self.eval_dir, '**', '*.ipynb'), recursive=True)
        updated_notebooks = get_updated_files(
            notebooks, self.eval_dir, self.rst_dir, 'rst')
        logging.info('%d rst files are outdated', len(updated_notebooks))
        for src, tgt in updated_notebooks:
            logging.info('Convert %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            ipynb2rst(src, tgt)
