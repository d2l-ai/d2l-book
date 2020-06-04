"""Integration with Colab notebooks"""
import os
import re
import nbformat
import logging
from d2lbook import notebook
from d2lbook import utils

def parse_repo_lib(repo_str, lib_str, version):
    repo = utils.split_config_str(repo_str)
    if len(repo) == 1 and len(repo[0]) == 1:
        repos = {None:repo[0]}
        libs = {None:utils.split_config_str(lib_str, 2)}
    else:
        repo = utils.split_config_str(repo_str, 2)
        repos = {r[0]:r[1] for r in repo}
        libs_list = utils.split_config_str(lib_str, 3)
        libs = {}
        for tab, pkg, install in libs_list:
            if tab in libs:
                libs[tab].append([pkg, install])
            else:
                libs[tab] = [[pkg, install]]
    for tab in libs:
        for i, l in enumerate(libs[tab]):
            if '==version' in l[1]:
                libs[tab][i][1] = l[1].replace('==version', f'=={version}')
    return repos, libs


class Colab():
    def __init__(self, config):
        self._valid = config.colab and config.colab['github_repo']
        if not self._valid:
            return
        self.tabs = config.tabs
        self.config = config.colab
        self._repo, self._libs = parse_repo_lib(
            self.config['github_repo'], self.config['libs'], config.library["version"])

    def valid(self):
        return self._valid

    def git_repo(self, tab):
        return self._repo[tab]

    def generate_notebooks(self, eval_dir, colab_dir, tab):
        if not self._valid:
            return
        # copy notebook fron eval_dir to colab_dir
        utils.run_cmd(['rm -rf', colab_dir])
        utils.run_cmd(['cp -r', eval_dir, colab_dir])
        notebooks = utils.find_files('**/*.ipynb', colab_dir)
        for fn in notebooks:
            nb = notebook.read(fn)
            if not nb:
                continue
            # Use Python3 as the kernel
            update_notebook_kernel(nb, "python3", "Python 3")
            # Check if GPU is needed
            use_gpu = False
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    if self.config['gpu_pattern'] in cell.source:
                        use_gpu = True
                        break
            if use_gpu:
                nb['metadata'].update({"accelerator": "GPU"})
                logging.info('Use GPU for '+fn)
            # Update SVG image URLs
            if self.config['replace_svg_url']:
                _update_svg_urls(nb, self.config['replace_svg_url'], fn, colab_dir)
            insert_additional_installation(nb, self._libs[tab], self.config['libs_header'])
            with open(fn, 'w') as f:
                f.write(nbformat.writes(nb))

    def add_button(self, html_dir):
        """Add an open colab button in HTML"""
        if not self._valid:
            return
        files = utils.find_files('**/*.html', html_dir, self.config['exclusions'])
        for fn in files:
            with open(fn, 'r') as f:
                html = f.read()
            if 'id="Colab' in html:
                continue
            url = os.path.relpath(fn, html_dir).replace('.html', '.ipynb')
            if self.tabs:
                colab_html = ''
                for tab in self.tabs:
                    colab_tab = _get_colab_html(self._repo[tab], url, f'Colab [{tab}]')
                    colab_html += f'<div class="d2l-tabs__tab">{colab_tab}</div>'
                colab_html = f'<div class="d2l-tabs" style="float:right">{colab_html}</div>'
            else:
                colab_html = _get_colab_html(self._repo[None], url, f'Colab')
            html = html.replace('</h1>', colab_html+'</h1>')
            with open(fn, 'w') as f:
                f.write(html)

def _get_colab_html(repo, url, text):
    id = text.replace(" ", "_")
    colab_link = f'https://colab.research.google.com/github/{repo}/blob/master/{url}'
    colab_html = f'<a href="{colab_link}" onclick="captureOutboundLink(\'{colab_link}\'); return false;"> <button style="float:right", id="{id}" class="mdl-button mdl-js-button mdl-button--primary mdl-js-ripple-effect"> <i class=" fas fa-external-link-alt"></i> {text} </button></a><div class="mdl-tooltip" data-mdl-for="{id}"> Open the notebook in Colab</div>'
    return colab_html

def insert_additional_installation(notebook, lib, lib_header):
    if lib:
        cell = _get_installation_cell(notebook, lib)
        if cell:
            notebook.cells.insert(0, cell)
            if lib_header:
                notebook.cells.insert(
                    0, nbformat.v4.new_markdown_cell(source=lib_header))

def update_notebook_kernel(notebook, name, display_name=None):
    if not display_name:
        display_name = name
    notebook['metadata'].update({"kernelspec": {
        "name": name,
        "display_name": display_name
    }})


def _update_svg_urls(notebook, pattern, filename, root_dir):
    orgin_url, new_url = utils.split_config_str(pattern, 2)[0]
    svg_re = re.compile('!\[.*\]\(([\.-_\w\d]+\.svg)\)')
    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            lines = cell.source.split('\n')
            for i, l in enumerate(lines):
                m = svg_re.search(l)
                if not m:
                    continue
                path = os.path.relpath(os.path.realpath(os.path.join(
                    root_dir, os.path.basename(filename), m[1])), root_dir)
                if not path.startswith(orgin_url):
                    logging.warning("%s in %s does not start with %s"
                                    "specified by replace_svg_url"%(
                                        path, filename, orgin_url))
                else:
                    url = new_url + path[len(orgin_url):]
                    lines[i] = l.replace(m[1], url)
            cell.source = '\n'.join(lines)

def _get_installation_cell(notebook, libs):
    """Return a cell for installing the additional libs"""
    lib_dict = dict(libs)
    lib1_re = re.compile('from ([_\w\d]+) import')
    lib2_re = re.compile('import ([_\w\d]+)')
    find_libs = []
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            for l in lines:
                if l.strip().startswith('#'): # it's a comment
                    continue
                m = lib1_re.search(l)
                if not m:
                    m = lib2_re.search(l)
                if m and m[1] in lib_dict:
                    find_libs.append(m[1])
    if not find_libs:
        return None
    install_str = ''
    for lib in set(find_libs):
        install_str += '!pip install ' + lib_dict[lib] + '\n'
    return nbformat.v4.new_code_cell(source=install_str)
