import argparse
import glob
import sys
import os
from d2lbook import config, markdown, utils, common
import logging
import re

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
        # init the original repo
        import git
        self.config = cf
        self.repo_dir = os.path.join(cf.tgt_dir, 'origin_repo')
        assert cf.translation['origin_repo'], 'much provide the origin repo'
        self.url = 'https://github.com/' + cf.translation['origin_repo']
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
        basename, ext = os.path.splitext(filename)
        tgt_fn = os.path.join(self.config.src_dir,
                              basename+'_origin'+ext)
        header = (f'---\nsource: {self.url}/blob/master/{filename}\n'
                  f'commit: {self.commit}\n---\n\n')

        logging.info(f'Write original text into {tgt_fn}')
        utils.mkdir(os.path.dirname(tgt_fn))
        with open(tgt_fn, 'w') as f:
            f.write(header)
            with open(src_fn, 'r') as f2:
                f.write(f2.read())

        tgt_fn = os.path.join(self.config.src_dir, filename)
        if self.translator:
            self.translator.translate_markdown(src_fn, tgt_fn)
            logging.info(f'Write translated results into {tgt_fn}')
        else:
            if not os.path.exists(tgt_fn):
                with open(tgt_fn, 'w') as f:
                    logging.info(f'Create an empty file {tgt_fn}')

# token = r'[\ \*-\/\\\._\w\d]+'
token = r'[\:\^\(\)\{\}\[\]\ \*-\/\\\.,_=\w\d]+'

class MarkdownText(object):
    def __init__(self):
        self.mapping = []

    def _encode_pattern(self, pattern, text):
        matched = set(re.findall(pattern, text))
        for m in matched:
            # another solution is use some special tokens and put them in
            # the terminology. unfortuanly it doesn't work for amazon transcribe.
            # So use a number instead, hope it will not be translated.
            token = '73214_'+str(len(self.mapping))
            text = text.replace(m, token)
            self.mapping.append((m, token))
        return text

    def encode(self, text:str) -> str:
        patterns = [rf'(`{token}`)', rf'(:{token}:`{token}`)',
                    rf'(\${token}\$)']
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

    def _translate_markdown_paragraph(self, paragraph):
        groups = common.group_list(
            paragraph.splitlines(),
            lambda a, _: a.strip().startswith(':') and a.strip().endswith('`'))
        results = []
        markdown_text = MarkdownText()
        for mark, item in groups:
            text = '\n'.join(item)
            if not mark:
                text = markdown_text.decode(self.translate(
                    markdown_text.encode(text)))
            results.append(text)
        return '\n'.join(results)

    def translate_markdown(self, src_fn: str, tgt_fn: str):
        with open(src_fn, 'r') as f:
            cells = markdown.split_markdown(f.read())
        for cell in cells:
            if cell['type'] == 'markdown':
                translated_text = '\n\n'.join([
                    self._translate_markdown_paragraph(p)
                    for p in markdown.split_paragraphs(cell['source'])])
                cell['source'] = translated_text
        with open(tgt_fn, 'w') as f:
            f.write(markdown.join_markdown_cells(cells))

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


