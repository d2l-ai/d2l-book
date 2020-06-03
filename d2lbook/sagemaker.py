"""Integration with Sagemaker"""
import nbformat
from d2lbook import utils
from d2lbook import colab
from d2lbook import notebook

class Sagemaker(colab.Colab):
    def __init__(self, config):
        self._valid = config.sagemaker and config.sagemaker['github_repo']
        self.config = config.sagemaker
        self._repo, self._libs = colab.parse_repo_lib(
            self.config['github_repo'], self.config['libs'], config.library["version"])

    def generate_notebooks(self, eval_dir, sagemaker_dir, tab):
        if not self._valid:
            return
        utils.run_cmd(['rm -rf', sagemaker_dir])
        utils.run_cmd(['cp -r', eval_dir, sagemaker_dir])
        notebooks = utils.find_files('**/*.ipynb', sagemaker_dir)
        for fn in notebooks:
            nb = notebook.read(fn)
            if not nb:
                continue
            colab.update_notebook_kernel(nb, self.config['kernel'])
            colab.insert_additional_installation(nb, self._libs[tab], self.config['libs_header'])
            with open(fn, 'w') as f:
                f.write(nbformat.writes(nb))
