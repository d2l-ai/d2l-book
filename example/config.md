```{.python .input}
b
```

```{.python .input  n=1}
import configparser
```

```{.python .input  n=33}
config =  configparser.ConfigParser()
config.read('build/config.ini')
```

```{.json .output n=33}
[
 {
  "data": {
   "text/plain": "['build/config.ini']"
  },
  "execution_count": 33,
  "metadata": {},
  "output_type": "execute_result"
 }
]
```

```{.python .input  n=34}
for sec in config.sections():
    for key in config[sec]:
        print(config[sec][key])
```

```{.json .output n=34}
[
 {
  "name": "stdout",
  "output_type": "stream",
  "text": "d2l-en\nDive into Deep Learning\nJenson A. Smith, Alex Zhang\n0.9\n2019, All developers. CC-4.0 license\nd2l-build-en\nbuild/env.yml\n\n\nBerkeley Course 2019,\nhttps://courses.d2l.ai/berkeley-stat-157/index.html,\nfas fa-user-graduate,\nPDF,\nhttps://en.d2l.ai/d2l-en.pdf\nfas fa-file-pdf\nUA-96378503-12\ns3://test.d2l.ai\n"
 }
]
```

```{.python .input  n=35}
x = config['publish']['header_links']
```

```{.python .input  n=37}
x.replace('\n', '').split(',')
```

```{.json .output n=37}
[
 {
  "data": {
   "text/plain": "['Berkeley Course 2019',\n 'https://courses.d2l.ai/berkeley-stat-157/index.html',\n 'fas fa-user-graduate',\n 'PDF',\n 'https://en.d2l.ai/d2l-en.pdffas fa-file-pdf']"
  },
  "execution_count": 37,
  "metadata": {},
  "output_type": "execute_result"
 }
]
```
