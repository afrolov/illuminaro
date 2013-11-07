from tornado import template
from jinja2 import Markup
import datetime
import uuid


#Style Guidelines for this module
#--------------------------------
# Each widget must have an identifier. The object field and positional argument are named 'id'.
#  This shadows Python built-in function 'id'. If you need to access it from methods, use
#  '__builtins__.id'. As 'id' is very frequently used, we consider that a reasonable trade-off
# Label may be either a string value or a boolean value. If it is True, label is derived from
#  identifier, by replacing underscores with spaces


def label_markup(for_what, label):
    """Create label markup with a given text for an element with specific identifier"""
    return Markup(
        '<label for="%s" class="control-label inline">%s</label>' % (for_what, label)) if label is not None else ''


class SelectInput():
    def __init__(self, id, choices, selected=None, label=None):
        """
        Initialize SelectInput object that presents a dropdown list of choices

        Parameters
        ----------
        id : string
            widget identifier
        choices : list
            list of choices
        selected: string, optional
            choice selected by default
        label : string, optional
            label for the widget
        """
        self.id = id
        self.choices = choices
        self.selected = selected
        self.label = label
        if self.selected is None:
            self.selected = self.choices[0]

    def markup(self):
        select_options = Markup('')
        for x in self.choices:
            selected_attribute = Markup(' selected="selected"') if x == self.selected else ''
            select_options += Markup('<option value="%s"%s>%s</option>') % (x, selected_attribute, x)
        return label_markup(self.id, self.label) + \
               (Markup('<select id="%s">%s</select>') % (self.id, select_options))


class DateInput():
    def __init__(self, id, value=None, label=None):
        self.id = id
        self.value = value
        self.format = "dd-mm-yyyy"
        self.label = label

    def markup(self):
        date_value_string = ''
        if self.value is None:
            date_value_string = datetime.date.today().strftime("%d-%m-%Y")
        elif isinstance(self.value, datetime.date):
            date_value_string = self.value.strftime("%d-%m-%Y")
        else:
            date_value_string = self.value
        s = label_markup(self.id, self.label)
        s += Markup('<div class="input-append date illuminaro-datepicker" id="%s" data-date="%s" data-date-format="%s">') \
            % (self.id, date_value_string, self.format)
        s += Markup('<input class="span2" size="100%%" type="text" value="%s">') % date_value_string
        s += Markup('<span class="add-on"><i class="icon-th"></i></span>')
        s += Markup('</div>')
        return s


class CheckboxInput:
    def __init__(self, id, checked=False, label=None):
        """Initialize Checkbox Input

        Parameters
        ----------
        id : string
            widget identifier
        checked : bool, optional
            whether checkbox is checked by default or not (False by default)
        label : string, optional
            label for the widget

        """

        self.id = id
        self.checked = checked
        self.label = label

    def markup(self):
        return Markup('<label class="checkbox">') + \
               (
                   Markup('<input id="%s" type="checkbox"%s/>') % (
                       self.id, ' checked="checked"' if self.checked else '')) + \
               self.label + Markup('</label>')


class TextInput:
    def __init__(self, id, value=None, label=None):
        """Initialize Text Input (single line)

        Parameters
        ----------
        id : string
            widget identifier
        value : string, optional
            Initial text, empty by default
        label : string, optional
            label for the widget
        """
        self.id = id
        self.value = value
        self.label = label

    def markup(self):
        m = Markup('<label>%s<label>') % self.label if self.label is not None else ''
        m += Markup('<input id="%s" type="text" value="%s"/>') % (self.id, self.value if self.value is not None else '')
        return m


class NumericInput:
    def __init__(self, id, value=0, label=None):
        self.id = id
        self.value = value
        self.label = label
        # TODO check value is numeric

    def markup(self):
        return label_markup(self.id, self.label) + \
               Markup('<input id="%s" type="number" value="%s"/>') % (self.id, self.value)


class JSlider:
    def __init__(self, id, label, minvalue, maxvalue, initial_value=None, step_size=None, steps=None):
        self.id = id
        self.label = label
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        if steps is None and step_size is None:
            if self.maxvalue > 1:
                self.steps = int(self.maxvalue)
            else:
                self.steps = 10  # just because, maybe be more smart about it
            self.step_size = float(self.maxvalue - self.minvalue) / self.steps
        elif steps is not None:
            self.step_size = float(self.maxvalue - self.minvalue) / self.steps
        elif step_size is not None:
            self.step_size = step_size
            self.steps = int((self.maxvalue - self.minvalue) / step_size)
        if initial_value is None:
            self.value = self.minvalue
        else:
            self.value = initial_value

    def markup(self):
        data_scale = ';'.join(['|'] * (self.steps + 1))
        return Markup('\n<input id="') + self.id + \
               Markup('" type="slider" name="') + self.id + ('" value="') + str(self.value) + Markup(
            '" class="jslider" data-from="') + \
               str(self.minvalue) + Markup('" data-to="') + str(self.maxvalue) + Markup('" data-step="') + \
               str(self.step_size) + Markup(
            '" data-skin="plastic" data-round="false" data-locale="us" data-format="#,##0.#####" data-scale="') + \
               data_scale + Markup('" data-smooth="false"/>\n')


class Para:
    def __init__(self, id, text):
        self.id = id
        self.text = text

    def markup(self):
        return Markup('<p class="pull-left" id="%s">%s</p>') % (self.id, self.text)


class Span:
    def __init__(self, id, contents, classes=None):
        self.id = id
        self.contents = contents
        self.classes = classes

    def markup(self):
        classes_attribute = ' class="%s"' % self.classes if self.classes else ''
        return Markup('<span id="%s"%s>%s</span>') % (self.id, classes_attribute, self.contents)


class Div:
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.children = args

    def markup(self):
        s = Markup('<div class="%s">' % self.cls)
        for c in self.children:
           s += c.markup()
        s += Markup('</div>')
        return s


def render_markup(s):
    if isinstance(s, Markup):
        return s
    else:
        return str(s)


def strong(s):
    return Markup('<strong>') + render_markup(s) + Markup('</strong>')


class Table:
    def __init__(self, headers=None, rows=None):
        self.headers = headers
        self.rows = rows

    def markup(self):
        s = Markup('<table class="table table-bordered table-condensed">')
        if self.headers:
            s += Markup('<thead><tr>')
            for header in self.headers:
                s += Markup('<th>%s</th>') % render_markup(header)
            s += Markup('</tr></thead>')
        s += Markup('<tbody>')
        if self.rows:
            for row in self.rows:
                s += Markup('<tr>')
                for cell in row:
                    s += Markup("<td>%s</td>") % render_markup(cell)
                s += Markup('</tr>')
        s += Markup('</tbody>')
        s += Markup('</table>')
        return s

    def style(self):
        return None


class Well:
    def __init__(self, *args, **kwargs):
        self.div = Div('well', *args)

    def markup(self):
        return self.div.markup()


class CheckboxButtons:
    def __init__(self, id, texts, toggled=None, label=None):
        """Row of buttons where each one may be toggled separately

        Parameters
        ----------
        id : string
            widget identifier
        texts : list
            list of texts to appear on buttons
        toggled : list
            list of boolean values that control whether button at respective position is toggled
        """

        self.id = id
        self.texts = texts
        self.label = label
        self.toggled = toggled if toggled is not None else [False] * len(self.texts)

    def markup(self):
        label_markup(self.id, self.label)
        s = Markup('<div id="%s" class="control-group btn-group illuminaro-btn-group" data-toggle="illuminaro-buttons-checkbox">') % self.id
        for i, t in enumerate(self.texts):
            if i < len(self.toggled) and self.toggled[i]:
                toggled_class = " active"
            else:
                toggled_class = ""
            btn_id = "%s_%d" % (self.id, i)
            s += Markup('<button id="%s" type="button" class="illuminaro-btn btn' + toggled_class + '">%s</button>') % (
                btn_id, t)
        s += Markup('</div>')
        return s


class RadioButtons:
    def __init__(self, id, texts, toggled=None, label=None):
        """Row of buttons where no more than one may be toggled at each time

        Parameters
        ----------
        id : string
            widget identifier
        texts : list
            list of texts to appear on buttons
        toggled : integer
            number of a button that will be toggled (0 by default, meaning first button)
        """

        self.id = id
        self.texts = texts
        self.label = label
        self.toggled = toggled if toggled is not None else 0

    def markup(self):
        s = label_markup(self.id, self.label)
        s += Markup('<div id="%s" class="control-group btn-group illuminaro-btn-group" data-toggle="illuminaro-buttons-radio">') % self.id
        for i, t in enumerate(self.texts):
            if self.toggled == i:
                toggled_class = " active"
            else:
                toggled_class = ""
            btn_id = "%s_%d" % (self.id, i)
            s += Markup('<button id="%s" type="button" class="illuminaro-btn btn' + toggled_class + '">%s</button>') % (
                btn_id, t)
        s += Markup('</div>')
        return s


class RadioInputs:
    def __init__(self, name, texts, values=None, toggled=None):
        """Group of generic radio inputs

        Parameters
        ----------
        name : string
            name of the parameter
        texts : list
            list of texts to appear beside radio buttons
        toggled : integer
            number of a button that will be toggled (0 by default, meaning first button)
        """

        self.name = name
        self.texts = texts
        self.toggled = toggled if toggled is not None else 0
        self.values = texts if values is None else values

    def markup(self):
        s = Markup('')
        for i, t in enumerate(self.texts):
            s += Markup('<label class="radio"><input type="radio" name="%s" id="%s" value="%s"/>\n%s\n</label>') \
                 % (self.name, self.name + str(i), self.values[i], t)
        return s


class TabSet:
    def __init__(self, *args, **kwargs):
        self.children = args
        self.active = int(kwargs['active']) if 'active' in kwargs else 0
        self.id = 'autoid_' + str(uuid.uuid4())
        for i, child in enumerate(self.children):
            child.id = self.id + '_' + str(i)

    def markup(self):
        s = Markup('<div class="tabbable">')
        s += Markup('<ul class="nav nav-tabs">')
        for i, c in enumerate(self.children):
            s += Markup('<li%s>' % (' class="active"' if i == self.active else ''))
            s += Markup('<a href="#%s" data-toggle="tab">%s</a>') % (c.id, c.title)
            s += Markup('</li>')
        s += Markup('</ul>')
        s += Markup('</div>')
        s += Markup('<div class="tab-content">')
        for i, c in enumerate(self.children):
            if i == self.active:
                c.active = True
            s += c.markup()
        s += Markup('</div>')
        return s


class TabPanel:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.active = False
        self.id = ''

    def markup(self):
        active_class = ' active' if self.active else ''
        s = Markup('<div class="tab-pane%s" title="%s" id="%s">') % (active_class, self.title, self.id)
        s += self.content.markup()
        s += Markup('</div>')
        return s


class Accordion:
    def __init__(self, *args, **kwargs):
        self.children = args
        self.active = int(kwargs['active']) if 'active' in kwargs else 0
        self.id = 'autoid_' + str(uuid.uuid4())
        for i, child in enumerate(self.children):
            child.id = self.id + '_' + str(i)

    def markup(self):
        s = Markup('<div class="accordion" id="%s">' % self.id)
        for i, c in enumerate(self.children):
            s += Markup('<div class="accordion-group">')
            s += Markup('<div class="accordion-heading">')
            if  self.active:
                collapsed_attr = ''
                in_attr = ' in'
            else:
                collapsed_attr = ' collapsed'
                in_attr = ''
            s += Markup('<a href="#%s" class="accordion-toggle%s" data-toggle="collapse" data-parent="#%s">%s</a>')\
                    % (c.id, collapsed_attr, self.id, c.title)
            s += Markup('</div>')  # accordion-heading
            s += Markup('<div id="%s" class="accordion-body%s collapse">' % (c.id, in_attr))
            s += Markup('<div class="accordion-inner">')
            s += c.markup()
            s += Markup('</div>')  # accordion-inner
            s += Markup('</div>')  # accordion-body
            s += Markup('</div>')  # accordion-group

        s += Markup('</div>')  # accordion
        return s


class AccordionPanel:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.active = False
        self.id = ''

    def markup(self):
        return self.content.markup()


class Slider:
    def __init__(self, id, label, minvalue, maxvalue, value=None, step_size=None, steps=None):
        self.id = id
        self.label = label
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        if steps is None and step_size is None:
            if self.maxvalue > 1:
                self.steps = int(self.maxvalue)
            else:
                self.steps = 10  # just because, maybe be more smart about it
            self.step_size = float(self.maxvalue - self.minvalue) / self.steps
        elif steps is not None:
            self.step_size = float(self.maxvalue - self.minvalue) / self.steps
        elif step_size is not None:
            self.step_size = step_size
            self.steps = int((self.maxvalue - self.minvalue) / step_size)
        if value is None:
            self.value = self.minvalue
        else:
            self.value = value

    def markup(self):
        value_id = self.id + '_para'
        onchange_script = Markup(' oninput="jQuery(\'#%s\').text(String(this.value));"') % value_id
        return Markup('<div class="control-group row-fluid margin-bottom">') + label_markup(self.id, self.label) + \
               (Markup('<input id="%s" type="range" value="%s" min="%s" max="%s" step="%s" %s/>') %
                (self.id, self.value, self.minvalue, self.maxvalue, self.step_size, onchange_script)) + \
               Span(value_id, str(self.value)).markup() + Markup('</div>')


class StaticHeader:
    """
    Header of a given level
    """
    def __init__(self, text, level=3):
        """
        Header of a given level
        """
        self.level = int(level)
        if self.level < 1:
            self.level = 1
        if self.level > 6:
            self.level = 6
        self.text = text

    def markup(self):
        return (Markup('<h%d>') % self.level) + self.text + Markup('</h%d>' % self.level)


class WellPanel:
    def __init__(self, *args, **kwargs):
        self.elements = args

    def markup(self):
        mu = Markup('<form class="well">\n')
        for e in self.elements:
            mu += e.markup()
        mu += Markup("</form>")
        return mu


class SubmitButton:
    def __init__(self, *args, **kwargs):
        self.value = 'Submit'
        if len(args) > 0:
            self.value = args[0]

    def markup(self):
        # TODO FIXME hardcode
        return Markup('<input type="button" onclick="foobar(); return false;" value="' + self.value + '"/>')


class TextOutput:
    def __init__(self, id, text=None):
        self.id = id
        self.text = text if text is not None else ''

    def setText(self, text):
        self.text = text

    def markup(self):
        return Markup('<p id="') + self.id + Markup('" class="illuminaro-text-output">') + self.text + Markup('</p>')


class CodeHighlighter:
    def __init__(self, code):
        self.id = id
        self.code = code

    def markup(self):
        try:
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter

            return Markup(highlight(self.code, PythonLexer(), HtmlFormatter()))
        except ImportError:
            return self.code

    def style(self):
        try:
            from pygments.formatters import HtmlFormatter
            return HtmlFormatter().get_style_defs('.highlight')
        except ImportError:
            return None


class MarkupOutput:
    def __init__(self, id, content=None):
        self.id = id
        self.content = content

    def markup(self):
        content = ''
        if self.content is None:
            content = ''
        elif hasattr(self.content, 'markup'):
            content = self.content.markup()
        else:
            content = Markup(self.content)

        return Markup('<div id="%s" class="illuminaro-html-output">') % self.id + \
               content + Markup('</div>')

    def style(self):
        return self.content.style()


def optional_attribute(attribute_name, attribute_value):
    if not attribute_value or attribute_value is None:
        return ''
    else:
        return ' %s="%s"' % (attribute_name, attribute_value)

class PlotOutput:
    def __init__(self, id, text=None):
        self.id = id
        self.text = text

    def markup(self):
        alt_attribute = optional_attribute("alt", self.text)
        return Markup('<div id="') + self.id + Markup('" class="illuminaro-plot-output"><img %s src=""/></div>' % alt_attribute)


class VerbatimTextOutput:
    def __init__(self, id, text=None):
        self.id = id
        self.text = text

    def markup(self):
        text = self.text if self.text else ''
        return Markup('<pre id="') + self.id + Markup('">') + text + Markup("</pre>")


class SelectableList:
    def __init__(self, id, choices):
        self.id = id
        self.choices = choices

    def markup(self):
        markup = Markup('<select multiple>')
        for t in self.choices:
            markup += Markup('<option value="') + str(t) + Markup('">') + t + Markup('</option>')
        markup += Markup('</select>')
        return markup


class NavigationList:
    def __init__(self, id, items):
        self.id = id
        self.items = items

    def markup(self):
        markup = Markup('<ul class="nav nav-list">')
        for t in self.items:
            markup += Markup('<li><a href="#">') + str(t) + Markup('</a></li>')
        markup += Markup('</ul>')
        return markup


class PageWithSidebar:
    def __init__(self, title, sidebar, mainPanel):
        self.title = title
        self.sidebar = sidebar
        self.mainPanel = mainPanel

    def render(self):
        contents = Div('container-fluid',
                       Div('row-fluid',
                           Div('span12', StaticHeader(self.title, 1))
                       ),
                       Div('row-fluid',
                           Div('span4', self.sidebar),
                           Div('span8', self.mainPanel),
                       )
        ).markup()
        styles = ''
        if hasattr(self.sidebar, 'style'):
            styles += self.sidebar.style()
        if hasattr(self.mainPanel, 'style'):
            styles += self.mainPanel.style()

        loader = template.Loader("templates")
        return loader.load('IlluminaroPage.html')\
                .generate(title=self.title, styles=styles, contents=contents)


class SimplePage:
    def __init__(self, title, *args, **kwargs):
        self.children = args
        self.title = title if title else ''

    def render(self):
        contents = ''
        styles = ''
        for c in self.children:
            contents += c.markup()
            if hasattr(c, 'style'):
                styles += c.style()

        loader = template.Loader("templates")
        return loader.load('IlluminaroPage.html').generate(title=self.title, styles=styles, contents=contents)
