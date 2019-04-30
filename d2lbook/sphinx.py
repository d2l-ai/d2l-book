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
        for key in self.config.project:
            self._update_pyconf(key, self.config.project[key])
        self._update_pyconf('index', self.config.build['index'])
        fname = os.path.join(self.config.rst_dir, 'conf.py')
        logging.info('write into %s', fname)
        with open(fname, 'w') as f:
            f.write(self.pyconf)

    def _update_pyconf(self, key, value):
        self.pyconf = self.pyconf.replace(key.upper(), value)

    def _copy_static_files(self):
        static_keys = ['favicon']
        for key in static_keys:
            fname = self.config.html[key]
            if not fname:
                continue
            sphinx_fname = os.path.join(self.config.rst_dir, '_static',
                                        os.path.basename(fname))
            print(fname, sphinx_fname)
            utils.copy(fname, sphinx_fname)
            self._update_pyconf(key, os.path.join(
                '_static', os.path.basename(fname)))

    def _update_header_links(self):
        header_links = self.config.html['header_links']
        items = header_links.replace('\n','').split(',')
        assert len(items) % 3 == 0, header_links
        sphinx_links = ''
        for i in range(0, len(items), 3):
            sphinx_links += "('%s', '%s', True, '%s')," % (
                items[i], items[i+1], items[i+2])
        self._update_pyconf('header_links', sphinx_links)

    def _write_js(self):
        d2l_js = template.shorten_sec_num + template.replace_qr
        g_id = 'google_analytics_tracking_id'
        if g_id in self.config.deploy:
            d2l_js += template.google_tracker.replace(
                g_id.upper(), self.config.deploy[g_id])
        fname = os.path.join(self.config.rst_dir, '_static', 'd2l.js')
        logging.info('write into %s', fname)
        with open(fname, 'w') as f:
            f.write(d2l_js)
