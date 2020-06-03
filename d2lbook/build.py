import os
import sys
import notedown
import nbformat
import logging
import shutil
import datetime
import argparse
import re
import regex
import subprocess
import hashlib
from d2lbook.utils import *  # TODO(mli), don't report *
from d2lbook.sphinx import prepare_sphinx_env
from d2lbook.config import Config
from d2lbook import colab, sagemaker
from d2lbook import markdown
from d2lbook import library
from d2lbook import notebook
from d2lbook import rst as rst_lib

__all__  = ['build']

commands = ['eval', 'rst', 'html', 'pdf', 'pkg', 'linkcheck', 'ipynb',
            'outputcheck', 'lib', 'colab', 'sagemaker', 'all', 'merge']

def build():
    parser = argparse.ArgumentParser(description='Build the documents')
    parser.add_argument('commands', nargs='+', choices=commands)
    parser.add_argument('--tab', default=None, help='The tab to build, if multi-tab is enabled.')
    args = parser.parse_args(sys.argv[2:])
    config = Config(tab=args.tab)
    builder = Builder(config)
    for cmd in args.commands:
        getattr(builder, cmd)()

def _once(func):
    # An decorator that run a method only once
    def warp(self):
        name = func.__name__
        if self.config.tab:
            name += '_' + self.config.tab
        if name in self.done and self.done[name]:
            return
        full_name = 'd2lbook build ' + name
        tik = datetime.datetime.now()
        func(self)
        logging.info('=== Finished "%s" in %s', full_name,
                        get_time_diff(tik, datetime.datetime.now()))
        self.done[name] = True
    return warp

class Builder(object):
    def __init__(self, config):
        self.config = config
        mkdir(self.config.tgt_dir)
        self.sphinx_opts = '-j 4'
        if config.build['warning_is_error'].lower() == 'true':
            self.sphinx_opts += ' -W'
        self.done = {}
        self._colab = colab.Colab(config)
        self._sagemaker = sagemaker.Sagemaker(config)

    def _find_md_files(self):
        build = self.config.build
        src_dir = self.config.src_dir
        notebooks = find_files(build['notebooks'], src_dir,
                               build['exclusions']+' '+build['non-notebooks'])
        pure_markdowns = find_files(build['non-notebooks'], src_dir,
                                    build['exclusions'])
        depends = find_files(build['dependencies'], src_dir)
        return sorted(notebooks), sorted(pure_markdowns), sorted(depends)

    def _get_updated_md_files(self):
        notebooks, pure_markdowns, depends = self._find_md_files()
        depends_mtimes = get_mtimes(depends)
        latest_depend = max(depends_mtimes) if len(depends_mtimes) else 0
        updated_notebooks = get_updated_files(
            notebooks, self.config.src_dir, self.config.eval_dir, 'md', 'ipynb', latest_depend)
        updated_markdowns = get_updated_files(
            pure_markdowns, self.config.src_dir, self.config.eval_dir, 'md', 'md', latest_depend)
        return updated_notebooks, updated_markdowns

    def outputcheck(self):
        notebooks, _, _ = self._find_md_files()
        reader = notedown.MarkdownReader()
        error = False
        for fn in notebooks:
            with open(fn, 'r') as f:
                notebook= reader.read(f)
            for c in notebook.cells:
                if 'outputs' in c and len(c['outputs']):
                    logging.error("Found execution outputs in %s", fn)
                    error = True
        if error:
            exit(-1)

    @_once
    def eval(self):
        """Evaluate the notebooks and save them in a different folder"""
        # TODO(mli) if tabs is enabled, and a .md doesn't have the default tab,
        # then the current implementation will not run the eval.
        eval_tik = datetime.datetime.now()
        notebooks, pure_markdowns, depends = self._find_md_files()
        depends_mtimes = get_mtimes(depends)
        latest_depend = max(depends_mtimes) if len(depends_mtimes) else 0
        updated_notebooks = get_updated_files(
            notebooks, self.config.src_dir, self.config.eval_dir, 'md', 'ipynb', latest_depend)
        updated_markdowns = get_updated_files(
            pure_markdowns, self.config.src_dir, self.config.eval_dir, 'md', 'md', latest_depend)
        num_updated_notebooks = len(updated_notebooks)
        num_updated_markdowns = len(updated_markdowns)
        logging.info('%d notebooks are outdated', num_updated_notebooks)
        for i, nb in enumerate(updated_notebooks):
            logging.info('[%d] %s', i + 1, nb[0])
        self._copy_resources(self.config.src_dir, self.config.eval_dir)

        for i, (src, tgt) in enumerate(updated_notebooks):
            tik = datetime.datetime.now()
            logging.info('[%d/%d, %s] Evaluating %s, save as %s',
                         i+1, num_updated_notebooks,
                         get_time_diff(eval_tik, tik), src, tgt)
            mkdir(os.path.dirname(tgt))
            run_cells = self.config.build['eval_notebook'].lower()=='true'
            process_and_eval_notebook(src, tgt, run_cells, tab=self.config.tab,
                                      default_tab=self.config.default_tab)
            tok = datetime.datetime.now()
            logging.info('Finished in %s', get_time_diff(tik, tok))

        for src, tgt in updated_markdowns:
            logging.info('Copying %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            shutil.copyfile(src, tgt)
        self._rm_tgt_files('md', 'ipynb', self.config.eval_dir)

    # Remove target files (e.g., eval and rst) based on removed files under src
    def _rm_tgt_files(self, src_ext, tgt_ext, tgt_dir, must_incls=None):
        notebooks_to_rm = get_files_to_rm(
                self.config.build['notebooks'], self.config.src_dir, tgt_dir,
                src_ext, tgt_ext)

        non_notebooks_pattern = (self.config.build['non-notebooks'] + ' '
                + self.config.build['resources'])
        non_notebooks_to_rm = get_files_to_rm(non_notebooks_pattern,
                self.config.src_dir, tgt_dir)

        if must_incls:
            must_incls = set(must_incls)
        tgt_files_to_rm = [f for f in notebooks_to_rm + non_notebooks_to_rm
                           if not must_incls or f not in must_incls]
        if tgt_files_to_rm:
            tgt_files_to_rm_concise = hide_individual_data_files(tgt_files_to_rm)
            logging.info('Cleaning target files whose corresponding source '
                'files are removed (individual data files are hidden, '
                'e.g., _build/eval/data/VOC/A/B/C -> _build/eval/data/VOC')
            for fn in tgt_files_to_rm_concise:
                logging.info('Cleaning target files: %s' % fn)
            for fn in tgt_files_to_rm:
                os.remove(fn)
            rmed_empty_dirs = []  # To display more concisely
            rm_empty_dir(tgt_dir, rmed_empty_dirs)
            rmed_empty_dirs_concise = hide_individual_data_files(rmed_empty_dirs)
            for fn in rmed_empty_dirs_concise:
                logging.info('Cleaned empty directories: %s' % fn)

    def _copy_resources(self, src_dir, tgt_dir):
        resources = self.config.build['resources']
        if resources:
            logging.info('Copying resources "%s" from %s to %s',
                         ' '.join(resources.split()), src_dir, tgt_dir)
        for res in resources.split():
            src = os.path.join(src_dir, res)
            updated = get_updated_files(find_files(src), src_dir, tgt_dir)
            for src, tgt in updated:
                if os.path.isdir(src):
                    continue
                mkdir(os.path.dirname(tgt))
                shutil.copyfile(src, tgt)

    def _copy_rst(self):
        rst_files = find_files(self.config.build['rsts'], self.config.src_dir)
        updated_rst = get_updated_files(rst_files, self.config.src_dir, self.config.rst_dir)
        if len(updated_rst):
            logging.info('Copy %d updated RST files to %s',
                         len(updated_rst), self.config.rst_dir)
        for src, tgt in updated_rst:
            copy(src, tgt)
        return rst_files

    @_once
    def merge(self):
        assert self.config.tab == 'all'
        assert self.config.eval_dir.endswith('_all')
        assert len(self.config.tabs) > 1, self.config.tabs
        default_eval_dir = self.config.eval_dir[:-4]
        notebooks = find_files(os.path.join(default_eval_dir, '**', '*.ipynb'))
        # TODO(mli) if no default tab, then will not trigger merge
        updated_notebooks = get_updated_files(
            notebooks, default_eval_dir, self.config.eval_dir, 'ipynb', 'ipynb')
        tab_dirs = [default_eval_dir+'_'+tab for tab in self.config.tabs[1:]]
        for default, merged in updated_notebooks:
            src_notebooks = [default]
            for tab_dir in tab_dirs:
                fname = os.path.join(tab_dir,
                    os.path.relpath(default, default_eval_dir))
                if os.path.exists(fname) and os.stat(fname).st_size > 0:
                    src_notebooks.append(fname)
            logging.info(f'merge {src_notebooks} into {merged}')
            src_nbs = [nbformat.read(open(fn, 'r'), as_version=4)
                       for fn in src_notebooks]
            if len(src_nbs) > 1:
                dst_nb = notebook.merge_tab_notebooks(src_nbs)
                dst_nb = notebook.add_html_tab(dst_nb, self.config.default_tab)
            else:
                dst_nb = src_nbs[0]
            mkdir(os.path.dirname(merged))
            with open(merged, 'w') as f:
                nbformat.write(dst_nb, f)
        self._copy_resources(default_eval_dir, self.config.eval_dir)

    @_once
    def rst(self):
        if self.config.tab == 'all':
            self.merge()
        else:
            self.eval()
        notebooks = find_files(os.path.join(self.config.eval_dir, '**', '*.ipynb'))
        updated_notebooks = get_updated_files(
            notebooks, self.config.eval_dir, self.config.rst_dir, 'ipynb', 'rst')
        logging.info('%d rst files are outdated', len(updated_notebooks))
        for src, tgt in updated_notebooks:
            logging.info('Convert %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            ipynb2rst(src, tgt)
        # Generate conf.py under rst folder
        prepare_sphinx_env(self.config)
        self._copy_rst()
        self._copy_resources(self.config.src_dir, self.config.rst_dir)

        must_incl_rst_files = get_tgt_files_from_src_pattern(
                self.config.build['rsts'], self.config.rst_dir, 'rst', 'rst')
        self._rm_tgt_files('md', 'rst', self.config.rst_dir,
                           must_incl_rst_files)

    @_once
    def html(self):
        self.rst()
        self.colab()
        self.sagemaker()
        run_cmd(['sphinx-build', self.config.rst_dir, self.config.html_dir,
                 '-b html -c', self.config.rst_dir, self.sphinx_opts])
        self._colab.add_button(self.config.html_dir)

    def _default_tab_dir(self, dirname):
        tokens = dirname.split('/')
        if self.config.tabs and '_' in tokens[-1]:
            tokens[-1] =  '_'.join(tokens[-1].split('_')[:-1])
            return '/'.join(tokens)
        return dirname

    @_once
    def ipynb(self):
        self.eval()
        run_cmd(['rm -rf', self.config.ipynb_dir, '; cp -r ',
                 self.config.eval_dir, self.config.ipynb_dir])
        update_ipynb_toc(self.config.ipynb_dir)

    @_once
    def colab(self):
        def _run():
            self.ipynb()
            self._colab.generate_notebooks(self.config.ipynb_dir,
                                           self.config.colab_dir, self.config.tab)
        self.config.iter_tab(_run)

    @_once
    def sagemaker(self):
        def _run():
            self.ipynb()
            self._sagemaker.generate_notebooks(self.config.ipynb_dir,
                                               self.config.sagemaker_dir, self.config.tab)
        self.config.iter_tab(_run)

    @_once
    def linkcheck(self):
        self.rst()
        run_cmd(['sphinx-build', self.config.rst_dir, self.config.linkcheck_dir,
                 '-b linkcheck -c', self.config.rst_dir, self.sphinx_opts])

    @_once
    def pdf(self):
        self.rst()
        run_cmd(['sphinx-build ', self.config.rst_dir, self.config.pdf_dir,
                 '-b latex -c', self.config.rst_dir, self.sphinx_opts])

        script = self.config.pdf['post_latex']
        process_latex(self.config.tex_fname, script)
        run_cmd(['cd', self.config.pdf_dir, '&& make'])

    @_once
    def pkg(self):
        zip_fname = 'out.zip'
        if not self.config.tabs:
            self.ipynb()
            run_cmd(['cd', self.config.ipynb_dir, '&& zip -r',
                     zip_fname, '*'])
            shutil.move(os.path.join(self.config.ipynb_dir, zip_fname),
                        self.config.pkg_fname)
        else:
            origin_tab = self.config.tab
            for tab in self.config.tabs:
                self.config.set_tab(tab)
                self.ipynb()
                run_cmd(['rm -rf', tab])
                run_cmd(['cp -r', self.config.ipynb_dir, tab])
            run_cmd(['zip -r', zip_fname]+self.config.tabs)
            shutil.move(zip_fname, self.config.pkg_fname)
            self.config.set_tab(origin_tab)

    @_once
    def lib(self):
        root = os.path.join(self.config.src_dir, self.config.build['index'] + '.md')
        notebooks = get_toc(root)
        notebooks_enabled, _, _ = self._find_md_files()
        notebooks = [nb for nb in notebooks if nb in notebooks_enabled]

        save_patterns = self.config.library['save_patterns']
        if save_patterns:
            items = split_config_str(save_patterns, num_items_per_line=2)
            for lib_fname, tab in items:
               library.save_tab(notebooks, lib_fname, tab, self.config.default_tab)

        save_mark = self.config.library['save_mark']
        lib_fname = self.config.library['save_filename']
        if save_mark and lib_fname:
            library.save_mark(notebooks, lib_fname, save_mark)

        version = self.config.library['version']
        version_fn = self.config.library['version_file']
        if version and version_fn:
            with open(version_fn, 'r') as f:
                lines = f.read().split('\n')
            for i, l in enumerate(lines):
                if '__version__' in l:
                    lines[i] = f'__version__ = "{version}"'
                    logging.info(f'save {lines[i]} into {version_fn}')
            with open(version_fn, 'w') as f:
                f.write('\n'.join(lines))

    def all(self):
        self.eval()
        self.rst()
        self.html()
        self.pdf()
        self.pkg()

def update_ipynb_toc(root):
    """Change the toc code block into a list of clickable links"""
    notebooks = find_files('**/*.ipynb', root)
    for fn in notebooks:
        nb = notebook.read(fn)
        if not nb:
            continue
        for cell in nb.cells:
            if (cell.cell_type == 'markdown' and '```toc' in cell.source):
                md_cells = markdown.split_markdown(cell.source)
                for c in md_cells:
                    if c['type'] == 'code' and c['class'] == 'toc':
                        toc = []
                        for l in c['source'].split('\n'):
                            if l and not l.startswith(':'):
                                toc.append(' - [%s](%s.ipynb)'%(l,l))
                        c['source'] = '\n'.join(toc)
                        c['type'] = 'markdown'
                cell.source = markdown.join_markdown_cells(md_cells)
        with open(fn, 'w') as f:
            f.write(nbformat.writes(nb))

def get_toc(root):
    """return a list of files in the order defined by TOC"""
    subpages = get_subpages(root)
    res = [root]
    for fn in subpages:
        res.extend(get_toc(fn))
    return res

def get_subpages(input_fn):
    """read toc in input_fn, returns what it contains"""
    subpages = []
    reader = notedown.MarkdownReader()
    with open(input_fn, 'r') as f:
        nb = reader.read(f)
    for cell in nb.cells:
        if (cell.cell_type == 'code' and
            'attributes' in cell.metadata and
            'toc' in cell.metadata.attributes['classes']):
            for l in cell.source.split('\n'):
                l = l.strip()
                if not l.startswith(':'):
                    fn = os.path.join(os.path.dirname(input_fn), l + '.md')
                    if os.path.exists(fn):
                        subpages.append(fn)
    return subpages

def process_and_eval_notebook(input_fn, output_fn, run_cells, timeout=20*60,
                              lang='python', tab=None, default_tab=None):
    with open(input_fn, 'r') as f:
        md = f.read()
    nb = notebook.read_markdown(md)
    if tab:
        # get the tab
        nb = notebook.split_markdown_cell(nb)
        nb = notebook.get_tab_notebook(nb, tab, default_tab)
        if not nb:
            logging.info(f"Skip to eval tab {tab} for {input_fn}")
            # write an emtpy file to track the dependencies
            open(output_fn, 'w')
            return
    # evaluate
    if run_cells:
        # change to the notebook directory to resolve the relpaths properly
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd, os.path.dirname(output_fn)))
        notedown.run(nb, timeout)
        os.chdir(cwd)
    # write
    nb['metadata'].update({'language_info':{'name':lang}})
    with open(output_fn, 'w') as f:
        f.write(nbformat.writes(nb))


def ipynb2rst(input_fn, output_fn):
    with open(input_fn, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    sig = hashlib.sha1(input_fn.encode()).hexdigest()[:6]
    resources = {'unique_key':
                 'output_'+rm_ext(os.path.basename(output_fn))+'_'+sig}
    body, resources = rst_lib.convert_notebook(nb, resources)
    with open(output_fn, 'w') as f:
        f.write(body)
    outputs = resources['outputs']
    base_dir = os.path.dirname(output_fn)
    for fn in outputs:
        full_fn = os.path.join(base_dir, fn)
        with open(full_fn, 'wb') as f:
            f.write(outputs[fn])

def process_latex(fname, script):
    with open(fname, 'r') as f:
        lines = f.read().split('\n')

    _combine_citations(lines)
    _center_graphics(lines)

    with open(fname, 'w') as f:
        f.write('\n'.join(lines))
    # Execute custom process_latex script
    if script:
        cmd = "python " + script + " " + fname
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error('%s', stderr.decode())
            exit(-1)

def _combine_citations(lines):
    # convert \sphinxcite{A}\sphinxcite{B} to \sphinxcite{A,B}
    for i, l in enumerate(lines):
        if '}\sphinxcite{' in l:
            lines[i] = l.replace('}\sphinxcite{', ',')

# E.g., tag = 'begin{figure}'
def _tag_in_line(tag, line):
    assert '\\' not in set(tag)
    return any([elem.startswith(tag) for elem in line.split('\\')])

def _center_graphics(lines):
    tabulary_cnt = 0
    figure_cnt = 0
    in_doc = False
    for i, l in enumerate(lines):
        if _tag_in_line('begin{tabulary}', l):
            tabulary_cnt += 1
        elif _tag_in_line('end{tabulary}', l):
            tabulary_cnt -= 1
        elif _tag_in_line('begin{figure}', l):
            figure_cnt += 1
        elif _tag_in_line('end{figure}', l):
            figure_cnt -= 1
        elif _tag_in_line('begin{document}', l):
            in_doc = True

        # 'tabulary' and 'figure' blocks do include '\centering', so only center
        # '\sphinxincludegraphics{}' by enclosing it with '\begin{center}'
        # '\end{center}'. Logo should not be centered and it is not in_doc.
        if tabulary_cnt == 0 and figure_cnt == 0 and in_doc:
            sigs_greedy = re.findall('\\\\sphinxincludegraphics\\{.*\\}', l)
            if len(sigs_greedy) > 0:
                longest_balanced_braces = regex.findall('\{(?>[^{}]|(?R))*\}',
                                                        sigs_greedy[0])
                sig_with_balanced_braces = ('\\sphinxincludegraphics'
                                            + longest_balanced_braces[0])
                lines[i] = l.replace(sig_with_balanced_braces,
                                     ('\\begin{center}'
                                      + sig_with_balanced_braces
                                      + '\\end{center}'))
