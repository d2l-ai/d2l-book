import argparse
import glob
import sys
import os
from d2lbook import config, markdown, utils
import logging

def translate():
    parser = argparse.ArgumentParser(description='Translate to another language')
    parser.add_argument('filename', nargs='+', help='the markdown files to activate')
    parser.add_argument('--commit', default='latest', help='the commit of the base repo')
    args = parser.parse_args(sys.argv[2:])

    cf = config.Config()
    trans = Translate(cf, args.commit)
    for fn in args.filename:
        trans.translate(fn)

class Translate(object):
    def __init__(self, cf: config.Config, commit: str):
        import git
        self.config = cf
        self.repo_dir = os.path.join(cf.tgt_dir, 'origin_repo')
        self.url = 'https://github.com/' + cf.build['origin_repo']
        if os.path.exists(self.repo_dir):
            self.repo = git.Repo(self.repo_dir)
            logging.info(f'Pulling from {self.url} into {self.repo_dir}')
            self.repo.remotes.origin.pull()
        else:
            logging.info(f'Clone {self.url} into {self.repo_dir}')
            self.repo = git.Repo.clone_from(self.url, self.repo_dir)
        if commit == 'latest':
            self.commit = str(self.repo.commit())[:7]
        else:
            self.repo.git.reset(commit, '--hard')
            self.commit = commit[:7]

    def translate(self, filename: str):
        src_fn = os.path.join(self.repo_dir, filename)
        tgt_fn = os.path.join(self.config.src_dir, filename)
        if not os.path.exists(tgt_fn):
            with open(tgt_fn, 'w') as f:
                logging.info(f'Create an empty file {tgt_fn}')

        assert filename.endswith('.md'), filename
        tgt_fn = os.path.join(self.config.src_dir,
                              filename[:-3]+'_origin.md')

        header = (f'---\nsource: {self.url}/blob/master/{filename}\n'
                  f'commit: {self.commit}\n---\n\n')

        logging.info(f'Write into {tgt_fn}')
        utils.mkdir(os.path.dirname(tgt_fn))
        with open(tgt_fn, 'w') as f:
            f.write(header)
            with open(src_fn, 'r') as f2:
                f.write(f2.read())



