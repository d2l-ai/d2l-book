import notedown
import nbformat
import nbconvert


class Builder(object):
    def __init__(self, src_dir, tgt_dir):
        self.src_dir = src_dir
        self.tgt_dir = tgt_dir

    def get_output():
        """"""



def md2ipynb(input_fn, output_fn, run_cells, timeout=20*60, lang='python'):
    reader = notedown.MarkdownReader(match='strict')
    with open(input_fn, 'r') as f:
        notebook = reader.read(f)
    if run_cells:
        notedown.run(notebook, timeout)
    notebook['metadata'].update({'language_info':{'name':lang}})
    with open(output_fn, 'w') as f:
        f.write(nbformat.writes(notebook))


def ipynb2rst(input_fn, output_fn):
    with open(input_fn, 'r') as f:
        notebook = nbformat.reads(f)

    exporter = nbconvert.RSTExporter()
    body, resources = exporter.from_notebook_node(notebook)
    base = os.path.basename(output_fn)
    for fn in resources:
        with open(os.path.join(base, fn), 'w') as f:
            f.write(resources[fn])
    with open(output_fn, 'w') as f:
        f.write(body)

def build_output(src_dir, tgt_dir):
def build_ipynb(src_dir, tgt_dir):
    """found"""
