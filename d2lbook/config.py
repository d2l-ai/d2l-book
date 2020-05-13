import configparser
import os
import logging

class Config():
    def __init__(self, tab=None, config_fname='config.ini'):
        config = configparser.ConfigParser()
        default_config_name = os.path.join(
            os.path.dirname(__file__), 'config_default.ini')
        config.read(default_config_name)
        if os.path.exists(config_fname):
            logging.info('Load configure from %s', config_fname)
            config.read(config_fname)
        tabs = config['build']['tabs']
        self.tabs = [tab.strip() for tab in tabs.split(',')] if tabs else []
        self.tab = tab.lower() if tab else None
        if self.tab:
            assert self.tabs, 'No tabs is specified'
            if self.tab != 'all':
                assert self.tab in [tab.lower() for tab in self.tabs], \
                    self.tab + ' is not found in tabs, which are ' + tabs   
        self.build = config['build']
        self.deploy = config['deploy']
        self.project = config['project']
        self.html = config['html']
        self.pdf = config['pdf']
        self.library = config['library']
        self.colab = config['colab']
        self.sagemaker = config['sagemaker']

        # A bunch of directories
        tab_ext = '_'+tab if tab else ''
        self.src_dir = self.build['source_dir']
        self.tgt_dir = self.build['output_dir']
        self.eval_dir = os.path.join(self.tgt_dir, 'eval'+tab_ext)
        self.ipynb_dir = os.path.join(self.tgt_dir, 'ipynb'+tab_ext)
        self.rst_dir = os.path.join(self.tgt_dir, 'rst'+tab_ext)
        try:
            self.html_dir = self.build['html_dir']
        except KeyError:
            self.html_dir = os.path.join(self.tgt_dir, 'html')
        # MM20200104 changed to allow separate html_dir to be specified in config.ini, e.g. put 'html_dir = docs' in the [build] section
        self.pdf_dir = os.path.join(self.tgt_dir, 'pdf'+tab_ext)
        self.colab_dir = os.path.join(self.tgt_dir, 'colab'+tab_ext)
        self.sagemaker_dir = os.path.join(self.tgt_dir, 'sagemaker'+tab_ext)
        self.linkcheck_dir = os.path.join(self.tgt_dir, 'linkcheck'+tab_ext)

        # Some targets names.
        self.pdf_fname = os.path.join(self.pdf_dir, self.project['name']+'.pdf')
        self.tex_fname = os.path.join(self.pdf_dir, self.project['name']+'.tex')
        self.pkg_fname = os.path.join(self.tgt_dir, self.project['name']+'.zip')

        # The project must have an index page
        index_fname, ext = os.path.splitext(self.build['index'])
        if ext and ext != '.md':
            logging.info('Ignore the file extesion, %s, specified by index in %s',
                         ext, config_fname)
        index_fname = os.path.join(self.src_dir, index_fname+'.md')
        if not os.path.exists(index_fname):
            logging.fatal('Failed to find the index file: %s', index_fname)
            exit(-1)

        if not self.project['title']:
            # Infer the book title from the index page
            with open(index_fname, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if line.startswith('#'):
                            line = line[1:]
                        self.project['title'] = line.strip()
                        break

        # Sanity checks.
        self.sanity_check()

    def sanity_check(self):
        notebook_patterns = self.build['notebooks'].split()
        for p in notebook_patterns:
            assert p.endswith('md'), '`notebooks` patterns must end with `md`' \
                   ' in `config.init`. Examples: `notebooks = *.md */*.md`.'

        rst_patterns = self.build['rsts'].split()
        for p in rst_patterns:
            assert p.endswith('rst'), '`rsts` patterns must end with `rst`' \
                    ' in `config.init`. Examples: `rsts = index.rst' \
                    ' api/**/*.rst`.'
