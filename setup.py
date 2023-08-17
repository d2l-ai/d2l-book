from setuptools import setup, find_packages

with open('d2lbook/_version.py') as ver_file:
    exec(ver_file.read())

requirements = [
    'jupyter==1.0.0',
    'regex==2022.7.25',
    'sphinx==5.3.0', # >=5.1.1 to enable pre_border-radius in code cells, 6.1.3 shows blank webpages
    'recommonmark==0.7.1',
    'sphinxcontrib-bibtex==2.4.2', # >=2.2 to enable citet and citep
    'pybtex-apa-style==1.3',
    'd2l-notedown==2.1.0',
    'mxtheme==0.3.17',
    'sphinxcontrib-svg2pdfconverter==1.2.0',
    'numpydoc==1.4.0',
    'awscli==1.25.44',
    'gitpython==3.1.32',
    'sphinx_autodoc_typehints==1.19.1',
    'astor==0.8.1',
    'yapf==0.32.0',
    'fasteners==0.17.3',
    'isort==5.10.1'
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
