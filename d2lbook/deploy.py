import os
import pathlib
import sys
import logging
import argparse
import shutil
from d2lbook.utils import *
from d2lbook.config import Config
from d2lbook import colab
from d2lbook import sagemaker
from d2lbook import slides
import glob

__all__  = ['deploy']

commands = ['html', 'pdf', 'pkg', 'colab', 'sagemaker', 'all', 'slides']

def deploy():
    parser = argparse.ArgumentParser(description='Deploy documents')
    parser.add_argument('commands', nargs='+', choices=commands)
    parser.add_argument('--s3', help='s3 bucket')
    args = parser.parse_args(sys.argv[2:])
    config = Config()
    if args.s3:
        config.deploy['s3_bucket'] = args.s3
    if config.deploy['s3_bucket']:
        deployer = S3Deployer(config)
    elif config.deploy['github_repo']:
        deployer = GithubDeployer(config)
    else:
        deployer = Deployer(config)
    for cmd in args.commands:
        getattr(deployer, cmd)()

class Deployer(object):
    def __init__(self, config):
        self.config = config

    def colab(self):
        _colab = colab.Colab(self.config)
        if not _colab.valid():
            return
        def _run():
            repo = _colab.git_repo(self.config.tab)
            bash_fname = os.path.join(os.path.dirname(__file__), 'upload_github.sh')
            run_cmd(['bash', bash_fname, self.config.colab_dir, repo,
                     self.config.project['release']])
        tab = self.config.tab
        self.config.set_tab('all')
        self.config.iter_tab(_run)
        self.config.set_tab(tab)

    def sagemaker(self):
        _sagemaker = sagemaker.Sagemaker(self.config)
        if not _sagemaker.valid():
            return
        def _run():
            repo = _sagemaker.git_repo(self.config.tab)
            bash_fname = os.path.join(os.path.dirname(__file__), 'upload_github.sh')
            run_cmd(['bash', bash_fname, self.config.sagemaker_dir, repo,
                     self.config.project['release']])
        tab = self.config.tab
        self.config.set_tab('all')
        self.config.iter_tab(_run)
        self.config.set_tab(tab)

    def slides(self):
        tab = self.config.tab
        self.config.set_tab('all')
        self.config.iter_tab(lambda: slides.Slides(self.config).deploy())
        self.config.set_tab(tab)

    def _get_pdfs(self):        
        # get all generated pdfs
        pdfs = list(glob.glob(self.config.tgt_dir+'/pdf*/'+self.config.project['name']+'*.pdf'))
        rets = []
        for p in pdfs:
            p = pathlib.Path(p)
            tks = p.parent.name.split('_')
            if len(tks) > 1:
                tab = tks[1]
                if p.with_suffix('').name.split('-')[-1] != tab:
                    continue
            rets.append(str(p))
        return rets
        
class GithubDeployer(Deployer):
    def __init__(self, config):
        super(GithubDeployer, self).__init__(config)
        self.git_dir = os.path.join(self.config.tgt_dir, 'github_deploy')
        shutil.rmtree(self.git_dir, ignore_errors=True)
        mkdir(self.git_dir)

    def html(self):
        run_cmd(['cp -r', os.path.join(self.config.html_dir, '*'), self.git_dir])

    def pdf(self):
        for pdf in self._get_pdfs():
            shutil.copy(pdf, self.git_dir)

    def pkg(self):
        shutil.copy(self.config.pkg_fname, self.git_dir)

    def __del__(self):
        bash_fname = os.path.join(os.path.dirname(__file__), 'upload_github.sh')
        run_cmd(['bash', bash_fname, self.git_dir, self.config.deploy['github_repo'], self.config.project['release']])

class S3Deployer(Deployer):
    def __init__(self, config):
        super(S3Deployer, self).__init__(config)

    def html(self):
        bash_fname = os.path.join(os.path.dirname(__file__), 'upload_doc_s3.sh')
        run_cmd(['bash', bash_fname, self.config.html_dir, self.config.deploy['s3_bucket']])

    def pdf(self):
        url = self.config.deploy['s3_bucket']
        if not url.endswith('/'):
            url += '/'
        for pdf in self._get_pdfs():
            logging.info('cp %s to %s', pdf, url)
            run_cmd(['aws s3 cp', pdf, url, "--acl 'public-read' --quiet"])

    def _deploy_other_files(self, tgt_url):
        other_urls = self.config.deploy['other_file_s3urls'].split()
        for other_url in other_urls:
            logging.info('cp %s to %s', other_url, tgt_url)
            run_cmd(['aws s3 cp', other_url, tgt_url, "--acl 'public-read' --quiet"])

    def pkg(self):
        url = self.config.deploy['s3_bucket']
        if not url.endswith('/'):
            url += '/'
        logging.info('cp %s to %s', self.config.pkg_fname, url)
        run_cmd(['aws s3 cp', self.config.pkg_fname, url, "--acl 'public-read' --quiet"])
        self._deploy_other_files(url)

    def all(self):
        self.html()
        self.pdf()
        self.pkg()
