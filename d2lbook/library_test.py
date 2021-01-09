from d2lbook import library
import unittest

from collections import namedtuple

class Cell:
    def __init__(self, cell_type, source):
        self.cell_type = cell_type
        self.source = source
class Nb:
    def __init__(self, cells):
        self.cells = cells

class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.nb = Nb([Cell('code', '')])
        self.tab_lib = {
            'lib_name':'torch',
            'simple_alias': 'ones, zeros, tensor, arange, meshgrid, sin, sinh, cos, cosh, tanh, linspace, exp, log, normal, rand, matmul, int32, float32, concat -> cat, stack, abs, eye',
            'fluent_alias': 'numpy -> detach().numpy, reshape, size -> numel, to, reduce_sum -> sum, argmax, astype -> type, transpose -> t',
            'alias':'',
            'reverse_alias':'',}

    def test_replace_alias(self):
        # Test https://github.com/d2l-ai/d2l-book/issues/14
        pairs = [('X = d2l.reshape(d2l.arange(10),(2,3))',
                  'X = torch.arange(10).reshape((2,3))'),
                  ('d2l.numpy(a)', 'a.detach().numpy()'),
                  ('d2l.transpose(a)', 'a.t()'),
                  ('metric.add(l * d2l.size(y), d2l.size(y))',
                   'metric.add(l * y.numel(), y.numel())',
                  ),
                  ('float(d2l.reduce_sum(cmp.astype(y.dtype)))',
                   'float(cmp.astype(y.dtype).sum())',
                   )
        ]
        for a, b in pairs:
            self.nb.cells[0].source = a
            nb = library.replace_alias(self.nb, self.tab_lib)
            self.assertEqual(nb.cells[0].source, b)


