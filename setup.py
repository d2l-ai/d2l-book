from setuptools import setup, find_packages
from d2lbook import __version__

requirements = [
    'jupyter',
    'regex',
    'sphinx>=2.2.1',
    'recommonmark',
    'nbformat<=5.0.7',  # there is an issue with 5.1.2
    'nbconvert<=5.6.1',  # there is an issue with the newest 6.0.0a1
    'sphinxcontrib-bibtex<2.0.0',
    'pybtex-apa-style',
    'mu-notedown',
    'mxtheme>=0.3.11',
    'sphinxcontrib-svg2pdfconverter',
    'numpydoc',
    'awscli',
    'gitpython',
    'sphinx_autodoc_typehints',
    'astor',
    'yapf',
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
