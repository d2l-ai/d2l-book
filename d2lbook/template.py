
sphinx_conf = """
project = "NAME"
copyright = "COPYRIGHT"
author = "AUHTOR"
release = "RELEASE"

extensions = [
    'recommonmark',
    'sphinxcontrib.bibtex',
    'sphinxcontrib.rsvgconverter',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
master_doc = 'INDEX'
numfig = True
numfig_secnum_depth = 2
math_numfig = True
math_number_all = True

html_theme = 'mxtheme'
html_theme_options = {
    'primary_color': 'blue',
    'accent_color': 'deep_orange',
    'header_links': [
        HEADER_LINKS
    ],
    'show_footer': False
}
html_static_path = ['_static']


# latex_documents = [
#     (master_doc, "NAME.tex", "TITLE",
#      author, 'manual'),
# ]


def setup(app):
    app.add_javascript('d2l.js')
"""


google_tracker = """
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'GOOGLE_ANALYTICS_TRACKING_ID', 'auto');
  ga('send', 'pageview');
"""

shorten_sec_num = """
$(document).ready(function () {
    $('.localtoc').each(function(){
        $(this).find('a').each(function(){
            $(this).html($(this).html().replace(/^\d+\.\d+\./, ''))
        });
    });
});
"""
