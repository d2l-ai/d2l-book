from setuptools import setup, find_packages
from d2lbook import __version__

requirements = [
    'jupyter',
    'sphinx>=1.7',
    'recommonmark',
    'sphinxcontrib-bibtex',
    'mu-notedown',
    'mxtheme',
    'sphinxcontrib-svg2pdfconverter'
]

setup(
    name='d2lbook',
    version=__version__,
    install_requires=requirements,
    python_requires='>=3.5',
    author='D2L Developers',
    author_email='d2l.devs@google.com',
    url='https://book.d2l.ai',
    description="Create an online book with Jupyter Notebooks and Sphinx",
    license='Apache-2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'd2lbook = d2lbook.main:main',
        ]
    },
)
