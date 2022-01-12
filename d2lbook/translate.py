import argparse
import glob
import sys
import os
from d2lbook import config, markdown, utils, common
import logging
import re
import glob

def translate():
    parser = argparse.ArgumentParser(description='Translate to another language')
    # Example usage: d2lbook translate --commit 35a64ab chapter_optimization chapter_computer-vision/anchor.md
    parser.add_argument('source', nargs='+', help='chapter directories or markdown files to activate')
    parser.add_argument('--commit', default='latest', help='the commit of the base repo')
    args = parser.parse_args(sys.argv[2:])

    cf = config.Config()
    trans = Translate(cf, args.commit)
    for source in args.source:
        # Check if source is a file or a chapter dir
        if not source.endswith(".md"):
            chap_dir = os.path.join(trans.repo_dir, source)
            if os.path.isdir(chap_dir):
                logging.info(f'Translating all sections of {source}')
                all_chap_secs = os.listdir(chap_dir)
                for sec_name in all_chap_secs:
                    if sec_name.endswith(".md"):
                        trans.translate(os.path.join(source, sec_name))
            else:
                logging.error(f'Invalid directory {source}: Please provide'
                              'a valid chapter name for translation')
        else:
            trans.translate(source)

class Translate(object):
    def __init__(self, cf: config.Config, commit: str):
        # init the original repo
        import git
        self.config = cf
        self.repo_dir = os.path.join(cf.tgt_dir, 'origin_repo')
        assert cf.translation['origin_repo'], 'much provide the origin repo'
        self.url = 'https://github.com/' + cf.translation['origin_repo']
        if os.path.exists(self.repo_dir):
            self.repo = git.Repo(self.repo_dir)
            logging.info(f'Pulling from {self.url} into {self.repo_dir}')
            # Reset to origin/master before pulling updates
            self.repo.git.reset('--hard', self.repo.remotes.origin.name + '/' + self.repo.active_branch.name)
            self.repo.remotes.origin.pull()
        else:
            logging.info(f'Clone {self.url} into {self.repo_dir}')
            self.repo = git.Repo.clone_from(self.url, self.repo_dir)
        if commit == 'latest':
            self.commit = str(self.repo.commit())[:7]
        else:
            self.repo.git.reset(commit, '--hard')
            self.commit = commit[:7]
        # init the translator
        self.translator = None
        if cf.translation['translator']:
            if cf.translation['translator'] == 'aws':
                assert cf.project['lang']
                assert cf.translation['origin_lang']
                self.translator = AWS(cf.translation['origin_lang'], cf.project['lang'], cf.translation['terminology'])
            else:
                logging.error(f'Unknown translator: {cf.translation["translator"]}')

    def translate(self, filename: str):
        src_fn = os.path.join(self.repo_dir, filename)
        fns = glob.glob(src_fn)
        if not len(fns):
            logging.warn('Not found '+src_fn)
            return
        if len(fns) > 1:
            for fn in fns:
                self.translate(os.path.relpath(fn, self.repo_dir))
            return
        src_fn = fns[0]
        filename = os.path.relpath(src_fn, self.repo_dir)
        basename, ext = os.path.splitext(filename)
        origin_tgt_fn = os.path.join(self.config.src_dir,
                              basename+'_origin'+ext)
        tgt_fn = os.path.join(self.config.src_dir, filename)
        if os.path.exists(tgt_fn):
            logging.warn(f'File {tgt_fn} already exists, skip translation.')
            return
        logging.info(f'Write original text into {origin_tgt_fn}')
        utils.mkdir(os.path.dirname(origin_tgt_fn))
        with open(origin_tgt_fn, 'w') as f:
            with open(src_fn, 'r') as f2:
                f.write(f2.read())

        if self.translator and ext == '.md':
            self.translator.translate_markdown(src_fn, tgt_fn)
            logging.info(f'Write translated results into {tgt_fn}')
        else:
            if not os.path.exists(tgt_fn):
                with open(tgt_fn, 'w') as f:
                    logging.info(f'Create an empty file {tgt_fn}')


class MarkdownText(object):
    def __init__(self):
        self.mapping = []

    def _encode_pattern(self, pattern, text):
        matched = set(re.findall(pattern, text))
        for m in matched:
            # another solution is use some special tokens and put them in
            # the terminology. unfortuanly it doesn't work for amazon transcribe.
            # So use a number instead, hope it will not be translated.
            token = str(732293614+len(self.mapping))
            text = text.replace(m, token)
            self.mapping.append((m, token))
        return text

    def encode(self, text:str) -> str:
        patterns = [rf'(:{markdown.token}:`{markdown.token}`)', # mark
                    rf'(`{markdown.token}`)',  # code
                    rf'(\${markdown.token}\$)', # inline match
                    rf'(\[{markdown.basic_token}\]\({markdown.basic_token}\))', # link
                    ]
        for p in patterns:
            text = self._encode_pattern(p, text)
        return text

    def decode(self, text:str) -> str:
        for key, value in self.mapping:
            text = text.replace(value, key)
        text = text.replace('] (', '](')
        return text

class Translator(object):
    def translate(self, text: str):
        raise NotImplemented()

    def _translate_markdown(self, text):
        cells = markdown.split_markdown(text)
        for cell in cells:
            if cell['type'] == 'markdown':
                if 'class' in cell and cell['class']:
                    # it may have nested code blocks
                    cell['source'] = self._translate_markdown(cell['source'])
                else:
                    text_cells = markdown.split_text(cell['source'])
                    for t_cell in text_cells:
                        if t_cell['source'] and (
                            t_cell['type'] in ['text', 'list', 'title']):
                            text = t_cell['source']
                            markdown_text = MarkdownText()
                            t_cell['source'] = markdown_text.decode(self.translate(
                                markdown_text.encode(text)))
                            if text.endswith('\n'):
                                t_cell['source'] += '\n'
                    cell['source'] = markdown.join_text(text_cells)
        return markdown.join_markdown_cells(cells)

    def translate_markdown(self, src_fn: str, tgt_fn: str):
        with open(src_fn, 'r') as r:
            with open(tgt_fn, 'w') as w:
                w.write(self._translate_markdown(r.read()))

class AWS(Translator):
    """Use Amazon Translate"""
    def __init__(self, src_lang, target_lang, terminology=None):
        import boto3
        self.client = boto3.client('translate')
        self.terminology = [terminology] if terminology else []
        self.src_lang = src_lang
        self.tgt_lang = target_lang
        logging.info(f'Amazon Translate {src_lang} -> {target_lang}, terminology {self.terminology}')

    def translate(self, text: str):
        text = text.replace('\n', ' ')
        print(text)
        resp = self.client.translate_text(
            Text=text, TerminologyNames=self.terminology,
            SourceLanguageCode=self.src_lang, TargetLanguageCode=self.tgt_lang)
        return resp['TranslatedText']

if __name__ == "__main__":
    logging.basicConfig(format='[d2lbook:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    if len(sys.argv) == 5:
        _, src_fn, src_lang, tgt_fn, tgt_lang = sys.argv
        terminology = None
    elif len(sys.argv) == 6:
        _, src_fn, src_lang, tgt_fn, tgt_lang, terminology = sys.argv
    else:
        exit(-1)
    translator = AWS(src_lang, tgt_lang, terminology)
    translator.translate_markdown(src_fn, tgt_fn)


