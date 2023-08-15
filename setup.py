from setuptools import setup, find_packages

with open('d2lbook/_version.py') as ver_file:
    exec(ver_file.read())

requirements = [
    'jupyter',
    'regex',
    'sphinx==5.1.1', # >=5.1.1 to enable pre_border-radius in code cells, 6.1.3 shows blank webpages
    'recommonmark',
    'sphinxcontrib-bibtex==2.4.2', # >=2.2 to enable citet and citep
    'pybtex-apa-style',
    'd2l-notedown',
    'mxtheme>=0.3.17',
    'sphinxcontrib-svg2pdfconverter',
    'numpydoc',
    'awscli',
    'gitpython',
    'sphinx_autodoc_typehints==1.19.2',
    'astor',
    'yapf',
    'fasteners',
    'isort'
]

setup(
    name='d2lbook',
    version=__version__,
    install_requires=requirements,
    python_requires='>=3.8',
    author='D2L Developers',
    author_email='d2l.devs@gmail.com',
    url='https://book.d2l.ai',
    description="Create an online book with Jupyter Notebooks and Sphinx",
    license='Apache-2.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={'d2lbook':['config_default.ini', 'upload_doc_s3.sh', 'upload_github.sh']},
    entry_points={
        'console_scripts': [
            'd2lbook = d2lbook.main:main',
        ]
    },
)
