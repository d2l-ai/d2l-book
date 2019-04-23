import configparser
import os

class Config():
    def __init__(self, config_fname):
        if not os.path.exists(config_fname):
            logging.fatal('Failed to find the config', config_fname)
            logging.fatal('You can use "d2lbook create ." to create a default config')
            exit(-1)
        config = configparser.ConfigParser()
        default_config_name = os.path.join(
            os.path.dirname(__file__), 'config_default.ini')
        config.read(default_config_name)
        config.read(config_fname)
        self.build = config['build']
        self.deploy = config['deploy']
        self.project = config['project']

        # a bunch of directories
        self.src_dir = self.build['source_dir']
        self.tgt_dir = self.build['output_dir']
        self.eval_dir = os.path.join(self.tgt_dir, 'eval')
        self.rst_dir = os.path.join(self.tgt_dir, 'rst')
        self.html_dir = os.path.join(self.tgt_dir, 'html')
        self.pdf_dir = os.path.join(self.tgt_dir, 'pdf')
