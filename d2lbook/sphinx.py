import os
import logging
from d2lbook import sphinx_template as template
from d2lbook import utils

__all__ = ['prepare_sphinx_env']

def prepare_sphinx_env(config):
    env = SphinxEnv(config)
    env.prepare_env()

class SphinxEnv(object):
    def __init__(self, config):
        self.config = config
        self.pyconf = template.sphinx_conf

    def prepare_env(self):
        self._copy_static_files()
        self._update_header_links()
        self._write_js()
        self._write_css()
        for key in self.config.project:
            self._update_pyconf(key, self.config.project[key])
        self._update_pyconf('index', self.config.build['index'])
        self._update_pyconf('sphinx_configs', self.config.build['sphinx_configs'])
        extensions = ['recommonmark', 'sphinxcontrib.bibtex',
                      'sphinxcontrib.rsvgconverter', 'sphinx.ext.autodoc',
                      'jupyter_sphinx.execute']
        extensions.extend(self.config.build['sphinx_extensions'].split())
        self._update_pyconf('extensions', ','.join('"'+ext+'"' for ext in extensions))
        fname = os.path.join(self.config.rst_dir, 'conf.py')
        logging.info('write into %s', fname)
        with open(fname, 'w') as f:
            f.write(self.pyconf)

    def _update_pyconf(self, key, value):
        self.pyconf = self.pyconf.replace(key.upper(), value)

    def _copy_static_files(self):
        static_keys = ['favicon', 'logo']
        for key in static_keys:
            fname = self.config.html[key]
            if not fname:
                self._update_pyconf(key, '')
                continue
            sphinx_fname = os.path.join(self.config.rst_dir, '_static',
                                        os.path.basename(fname))
            utils.copy(fname, sphinx_fname)
            self._update_pyconf(key, os.path.join(
                '_static', os.path.basename(fname)))

    def _update_header_links(self):
        items = utils.split_config_str(self.config.html['header_links'], 3)
        sphinx_links = ''
        for tk in items:
            sphinx_links += "('%s', '%s', True, '%s')," % (tk[0], tk[1], tk[2])
        self._update_pyconf('header_links', sphinx_links)

    def _write_js(self):
        d2l_js = (template.shorten_sec_num + template.replace_qr
                  + template.copybutton_js)
        g_id = 'google_analytics_tracking_id'
        if g_id in self.config.deploy:
            d2l_js += template.google_tracker.replace(
                g_id.upper(), self.config.deploy[g_id])

        os.makedirs(os.path.join(self.config.rst_dir, '_static'), exist_ok=True)
        fname = os.path.join(self.config.rst_dir, '_static', 'd2l.js')
        logging.info('write into %s', fname)
        with open(fname, 'w') as f:
            f.write(d2l_js)
            for fname in utils.find_files(self.config.html['include_js'], self.config.src_dir):
                with open (fname, 'r') as fin:
                    f.write(fin.read())

    def _write_css(self):
        fname = os.path.join(self.config.rst_dir, '_static', 'd2l.css')
        d2l_css = template.hide_bibkey_css + template.copybutton_css
        with open(fname, 'w') as f:
            f.write(d2l_css)
            for fname in utils.find_files(self.config.html['include_css'], self.config.src_dir):
                with open (fname, 'r') as fin:
                    f.write(fin.read())
