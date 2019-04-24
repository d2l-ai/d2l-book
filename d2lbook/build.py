import os
import sys
import notedown
import nbformat
import nbconvert
import pkg_resources
import logging
import shutil
import time
import argparse
import re
from d2lbook import template
from d2lbook.utils import *

__all__  = ['build']

mark_re = re.compile(':([-\/\\._\w\d]+):([-\/\\\._\w\d]+):')

def build(config):
    parser = argparse.ArgumentParser(description='build')
    parser.add_argument('commands', nargs='+', help=' ')
    args = parser.parse_args(sys.argv[2:])
    builder = Builder(config)
    commands = {
        'eval' : builder.eval_output,
        'rst' : builder.build_rst,
        'html' : builder.build_html,
        'pdf' : builder.build_pdf,
        'all' : builder.build_all,
    }
    for cmd in args.commands:
        commands[cmd]()


def eval_notebook(input_fn, output_fn, run_cells, timeout=20*60, lang='python'):
    # process: add empty lines before and after a mark, otherwise it confuses
    # the rst parser...
    with open(input_fn, 'r') as f:
        md = f.read()
    lines = md.split('\n')
    in_code = False
    for i, line in enumerate(lines):
        if line.startswith('```'):
            in_code ^= True
        m = mark_re.match(line)
        if m is not None and not in_code and m.end() == len(line):
            lines[i] = '\n'+line+'\n'
    reader = notedown.MarkdownReader(match='strict')
    notebook= reader.reads('\n'.join(lines))
    # evaluate
    if run_cells:
        notedown.run(notebook, timeout)
    # write
    notebook['metadata'].update({'language_info':{'name':lang}})
    with open(output_fn, 'w') as f:
        f.write(nbformat.writes(notebook))

def delete_lines(lines, deletes):
    return [line for i, line in enumerate(lines) if i not in deletes]

def process_rst(body):
    def indented(line):
        return line.startswith('   ')
    def in_code(line, pos):
        return indented(line) or (line[0:pos].count('``') % 2) == 1
    def blank(line):
        return len(line.strip()) == 0

    def look_behind(i, cond):
        indices = []
        while i < n and cond(lines[i]):
            indices.append(i)
            i = i + 1
        return indices
    lines = body.split('\n')
    i, n, deletes = 0, len(lines), []
    while i < n:
        line = lines[i]
        if line.startswith('.. code:: toc'):
            # convert into rst's toc block
            lines[i] = '.. toctree::'
            blanks = look_behind(i+1, blank)
            deletes.extend(blanks)
            i += len(blanks)
        elif indented(line) and ':alt:' in line:
            # Image caption, remove :alt: block, it cause trouble for long captions
            caps = look_behind(i, lambda l: indented(l) and not blank(l))
            deletes.extend(caps)
            i += len(caps)
        elif line.startswith('.. table::'):
            # Add indent to table caption for long captions
            caps = look_behind(i+1, lambda l: not indented(l) and not blank(l))
            for j in caps:
                lines[j] = '   ' + lines[j]
            i += len(caps) + 1
        else:
            i += 1

    # process references, first change :label:my_label: into rst format
    lines = delete_lines(lines, deletes)
    deletes = []

    for i, line in enumerate(lines):
        pos, new_line = 0, ''
        while True:
            match = mark_re.search(line, pos)
            if match is None:
                new_line += line[pos:]
                break
            start, end = match.start(), match.end()
            origin, key, value = match[0], match[1], match[2]
            new_line += line[pos:start]
            pos = end
            if in_code(line, start):
                new_line += origin # no change if in code
            else:
               # assert key in ['label', 'eqlabel', 'ref', 'numref', 'eqref', 'width', 'height'], 'unknown key: ' + key
                if key == 'label':
                    new_line += '.. _' + value + ':'
                elif key in ['ref', 'numref', 'cite']:
                    new_line += ':'+key+':`'+value+'`'
                elif key == 'eqref':
                    new_line += ':eq:`'+value+'`'
                elif key == 'eqlabel':
                    new_line += '   :label: '+value
                    if blank(lines[i-1]):
                        deletes.append(i-1)
                elif key in ['width', 'height']:
                    new_line += '   :'+key+': '+value
                elif key == 'bibliography':
                    new_line += '.. bibliography:: ' + value
                else:
                    logging.fatal('unknown key', key)

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
                if line_j.startswith('   :'):
                    move(j, i+1)

    # move .. _label: before a image, a section, or a table
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
                    i += 1
                    break
                if (len(set(line_j)) == 1
                    and line_j[0] in ['=','~','_', '-']):
                    move(i, j-2)
                    lines.insert(j-2, '')
                    i += 1
                    break
        i += 1

    return '\n'.join(lines)

def ipynb2rst(input_fn, output_fn):
    #os.system('jupyter nbconvert --to rst '+input_fn + ' --output '+
    #          os.path.relpath(output_fn, os.path.dirname(input_fn)))

    with open(input_fn, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
    writer = nbconvert.RSTExporter()
    image_dir = rm_ext(os.path.basename(output_fn))
    resources = {'output_files_dir':image_dir}
    (body, resources) = writer.from_notebook_node(notebook, resources)

    body = process_rst(body)

    with open(output_fn, 'w') as f:
        f.write(body)
    base_dir = os.path.dirname(output_fn)
    outputs = resources['outputs']
    for fn in outputs:
        full_fn = os.path.join(base_dir, fn)
        mkdir(os.path.dirname(full_fn))
        with open(full_fn, 'wb') as f:
            f.write(outputs[fn])

def convert_header_links(header_links):
    items = header_links.replace('\n','').split(',')
    assert len(items) % 3 == 0, header_links
    header_links = ''
    for i in range(0, len(items), 3):
        header_links += "('%s', '%s', True, '%s')," % (
            items[i], items[i+1], items[i+2])
    return header_links

def write_sphinx_conf(config):
    pyconf = template.sphinx_conf
    config.project['header_links'] = convert_header_links(
        config.project['header_links'])
    for key in config.project:
        pyconf = pyconf.replace(key.upper(), config.project[key])

    with open(os.path.join(config.rst_dir, 'conf.py'), 'w') as f:
        f.write(pyconf)

def write_sphinx_static(config):
    g_id = 'google_analytics_tracking_id'
    d2l_js = template.shorten_sec_num
    if g_id in config.deploy:
        d2l_js += template.google_tracker.replace(g_id.upper(), config.deploy[g_id])
    static_dirname = os.path.join(config.rst_dir, '_static')
    mkdir(static_dirname)
    with open(os.path.join(static_dirname, 'd2l.js'), 'w') as f:
        f.write(d2l_js)

class Builder(object):
    def __init__(self, config):
        self.config = config
        mkdir(self.config.tgt_dir)
        self.sphinx_opts = '-j 4'
        if config.build['warning_is_error'].lower() == 'true':
            self.sphinx_opts += ' -W'
        self.done = {'eval':False, 'html':False, 'rst':False, 'pdf':False}

    def _find_md_files(self):
        build = self.config.build
        src_dir = self.config.src_dir
        excluded_files = find_files(build['exclusions'], src_dir)
        pure_markdowns = find_files(build['non-notebooks'], src_dir)
        pure_markdowns = [fn for fn in pure_markdowns if fn not in excluded_files]
        notebooks = find_files(build['notebooks'], src_dir)
        notebooks = [fn for fn in notebooks if fn not in pure_markdowns and fn
                     not in pure_markdowns and fn not in excluded_files]
        depends = find_files(build['dependencies'], src_dir)
        return notebooks, pure_markdowns, depends

    def eval_output(self):
        """Evaluate the notebooks and save them in a different folder"""
        if self.done['eval']:
            return
        self.done['eval'] = True
        notebooks, pure_markdowns, depends = self._find_md_files()
        depends_mtimes = get_mtimes(depends)
        latest_depend = max(depends_mtimes) if len(depends_mtimes) else 0
        updated_notebooks = get_updated_files(
            notebooks, self.config.src_dir, self.config.eval_dir, 'ipynb', latest_depend)
        updated_markdowns = get_updated_files(
            pure_markdowns, self.config.src_dir, self.config.eval_dir, 'md', latest_depend)
        logging.info('%d notedowns and %d markdowns are out dated',
                     len(updated_notebooks), len(updated_markdowns))
        for src, tgt in updated_notebooks:
            logging.info('Evaluating %s, save as %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            start = time.time()
            run_cells = self.config.build['eval_notebook'].lower()
            eval_notebook(src, tgt, run_cells=='true')
            logging.info('Finished in %.1f sec', time.time() - start)

        for src, tgt in updated_markdowns:
            logging.info('Copy %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            shutil.copyfile(src, tgt)


    def _prepare_sphinx_env(self):
        write_sphinx_conf(self.config)
        write_sphinx_static(self.config)
        for res in self.config.build['resources'].split():
            src = os.path.join(self.config.src_dir, res)
            updated = get_updated_files(find_files(src),
                                        self.config.src_dir, self.config.rst_dir)
            for src, tgt in updated:
                if os.path.isdir(src):
                    continue
                logging.info('Copy %s to %s', src, tgt)
                mkdir(os.path.dirname(tgt))
                shutil.copyfile(src, tgt)

    def build_rst(self):
        if self.done['rst']:
            return
        self.done['rst'] = True
        self.eval_output()
        notebooks = find_files(os.path.join(self.config.eval_dir, '**', '*.ipynb'))
        updated_notebooks = get_updated_files(
            notebooks, self.config.eval_dir, self.config.rst_dir, 'rst')
        logging.info('%d rst files are outdated', len(updated_notebooks))
        for src, tgt in updated_notebooks:
            logging.info('Convert %s to %s', src, tgt)
            mkdir(os.path.dirname(tgt))
            ipynb2rst(src, tgt)

        self._prepare_sphinx_env()

    def build_html(self):
        if self.done['html']:
            return
        self.done['html'] = True
        self.build_rst()
        run_cmd(['sphinx-build', self.config.rst_dir, self.config.html_dir,
                 '-b html -c', self.config.rst_dir, self.sphinx_opts])

    def build_pdf(self):
        if self.done['pdf']:
            return
        self.done['pdf'] = True
        self.build_rst()
        run_cmd(['sphinx-build ', self.config.rst_dir, self.config.pdf_dir,
                 '-b latex -c', self.config.rst_dir, self.sphinx_opts])
        run_cmd(['cd', self.config.pdf_dir, '&& make'])

    def build_all(self):
        self.eval_output()
        self.build_rst()
        self.build_html()
        self.build_pdf()
