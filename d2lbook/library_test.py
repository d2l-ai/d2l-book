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
            'lib_name': 'torch',
            'simple_alias':
            'ones, zeros, tensor, arange, meshgrid, sin, sinh, cos, cosh, tanh, linspace, exp, log, normal, rand(, matmul, int32, float32, concat -> cat, stack, abs, eye',
            'fluent_alias':
            'numpy -> detach().numpy, reshape, size -> numel, to, reduce_sum -> sum, argmax, astype -> type, transpose -> t',
            'alias': '',
            'reverse_alias': '',
            'args_alias': 'randn(size, device=None) -> np.random.randn(size=size, ctx=device)'
            }

    def test_replace_alias(self):
        # Test https://github.com/d2l-ai/d2l-book/issues/14
        pairs = [  # before, after
            ('X = d2l.reshape(d2l.arange(10,20),(2,3))',
             'X = torch.arange(10, 20).reshape((2, 3))'),
            ('d2l.numpy(a)', 'a.detach().numpy()'),
            ('d2l.transpose(a)', 'a.t()'),
            ('metric.add(l * d2l.size(y), d2l.size(y))',
             'metric.add(l * y.numel(), y.numel())'),
            ('float(d2l.reduce_sum(cmp.astype(y.dtype)))',
             'float(cmp.astype(y.dtype).sum())'),
            ('d2l.numpy(nn.LeakyReLU(alpha)(x))',
             'nn.LeakyReLU(alpha)(x).detach().numpy()'),
            ('d2l.reshape(X_tile(1 - d2l.eye(n_train)).astype(\'bool\'), (1,2))',
             'X_tile(1 - torch.eye(n_train)).astype(\'bool\').reshape((1, 2))'
             ),
            ('float(d2l.reduce_sum(d2l.astype(cmp, y.dtype)))',
             'float(cmp.type(y.dtype).sum())'),
            ('\nenc_attention_weights = d2l.reshape(\n    d2l.concat(net.encoder.attention_weights, 0),\n    (num_layers, num_heads, -1, num_steps))\nenc_attention_weights.shape = 2\n',
             'enc_attention_weights = torch.cat(net.encoder.attention_weights, 0).reshape(\n    (num_layers, num_heads, -1, num_steps))\nenc_attention_weights.shape = 2'
             ),
            ('float(d2l.reduce_sum(d2l.abs(Y1 - Y2))) < 1e-6',
             'float(torch.abs(Y1 - Y2).sum()) < 1e-6'),
            ('d2l.plt.scatter(d2l.numpy(features[:, a + b]), d2l.numpy(labels), 1);',
             'd2l.plt.scatter(features[:, a + b].detach().numpy(),labels.detach().numpy(), 1);'
             ),
            ('d2l.reshape(multistep_preds[i - tau: i], (1, -1))',
             'multistep_preds[i - tau:i].reshape((1, -1))'),
            ('X = d2l.reshape(d2l.arange(16, dtype=d2l.float32), (1, 1, 4, 4))',
             'X = torch.arange(16, dtype=torch.float32).reshape((1, 1, 4, 4))'
             ),
            ('# comments\nX = d2l.reshape(a)', '# comments\nX = a.reshape()'),
            ('X = d2l.reshape(a)  # comments', 'X = a.reshape()  # comments'),
            ('Y[i, j] = d2l.reduce_sum((X[i: i + h, j: j + w] * K))',
             'Y[i, j] = (X[i:i + h, j:j + w] * K).sum()'),
            ('d2l.randn(size=(1,2)) * 0.01',
             'np.random.randn(size=(1,2)) * 0.01'),
             ('d2l.randn(size=(1,2), device=d2l.try_gpu()) * 0.01',
             'np.random.randn(size=(1,2), ctx=d2l.try_gpu()) * 0.01'
             ),
             
             ]

        for a, b in pairs:
            self.nb.cells[0].source = a
            nb = library.replace_alias(self.nb, self.tab_lib)
            compact = lambda x: x.replace('\n', '').replace(' ', '')
            self.assertEqual(compact(nb.cells[0].source), compact(b))
