import os
import sys
import logging
import argparse
from d2lbook.utils import *

__all__  = ['deploy']

def deploy(config):
    parser = argparse.ArgumentParser(description='deploy')
    parser.add_argument('commands', nargs='+', help=' ')
    args = parser.parse_args(sys.argv[2:])
    deployer = Deployer(config)
    commands = {
        'html' : deployer.deploy_html,
        'pdf' : deployer.deploy_pdf,
    }
    for cmd in args.commands:
        commands[cmd]()

class Deployer(object):
    def __init__(self, config):
        self.config = config

    def deploy_html(self):
        assert self.config.deploy['s3_bucket'] is not '', 'empty target URL'
        bash_fname = os.path.join(os.path.dirname(__file__), 'upload_doc_s3.sh')
        run_cmd(['bash', bash_fname, self.config.html_dir, self.config.deploy['s3_bucket']])

    def deploy_pdf(self):
        assert self.config.deploy['s3_bucket'] is not '', 'empty target URL'
        url = self.config.deploy['s3_bucket']
        pdf_fname = os.path.join(self.config.pdf_dir, self.config.project['name']+'.pdf')
        logging.info('cp %s to %s', pdf_fname, url)
        run_cmd(['aws s3 cp', pdf_fname, url, "--acl 'public-read'"])
