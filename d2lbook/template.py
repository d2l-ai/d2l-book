
sphinx_conf = """
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')

project = "TITLE"
copyright = "COPYRIGHT"
author = "AUTHOR"
release = "RELEASE"

extensions = [
    'recommonmark',
    'sphinxcontrib.bibtex',
    'sphinxcontrib.rsvgconverter',
    'sphinx.ext.autodoc',
    # 'IPython.sphinxext.ipython_console_highlighting',
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


latex_documents = [
    (master_doc, "NAME.tex", "TITLE",
     author, 'manual'),
]

latex_engine = 'xelatex' # for utf-8 supports
latex_show_pagerefs = True
latex_show_urls = 'footnote'


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

# Replace the QR code with an embeded discussion thread. TODO, make the URL replaciable
replace_qr = """
$(document).ready(function () {
    var discuss_str = 'Discuss'
    $('h2').each(function(){
        if ($(this).text().indexOf("Scan the QR Code") != -1) {
            var url = $(this).find('a').attr('href');
            var tokens = url.split('/');
            var topic_id = tokens[tokens.length-1];
            $(this).html('<h2>'.concat(discuss_str).concat('</h2>'));
            $(this).parent().append('<div id="discourse-comments"></div>');

            $('a').each(function(){
                if ($(this).text().indexOf("Scan the QR Code to Discuss") != -1) {
                    $(this).text(discuss_str);
                }
            });

            $('img').each(function(){
                if ($(this).attr('src').indexOf("qr_") != -1) {
                    $(this).hide();
                }
            });

            DiscourseEmbed = { discourseUrl: 'https://discuss.mxnet.io/', topicId: topic_id };
            (function() {
                var d = document.createElement('script'); d.type = 'text/javascript';
                d.async = true;
                d.src = DiscourseEmbed.discourseUrl + 'javascripts/embed.js';
                (document.getElementsByTagName('head')[0] ||
                 document.getElementsByTagName('body')[0]).appendChild(d);
            })();
        }
    });

    var replaced = $('body').html().replace(/Scan-the-QR-Code-to-Discuss/g, discuss_str);
    $('body').html(replaced);
});
"""
