from illuminaro import *

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

code = open('examples/showmethecode.py').read()
hl = highlight(code, PythonLexer(), HtmlFormatter())

gui = SimplePage(
    'Code Highlighter',
    MarkupOutput(id='code_output', content=CodeHighlighter(code))
)
IlluminaroApp(gui, None).run()
