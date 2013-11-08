try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO as BytesIO

try:
    from urllib2 import quote
except ImportError:
    from urllib.parse import quote

import base64


def render_plot(fig, format=None):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    if not fig or fig is None:
        return ''
    if format is None or not format:
        format = 'png'
    canvas = FigureCanvasAgg(fig)
    buf = BytesIO()
    canvas.print_figure(buf, format=format)
    image_data = buf.getvalue()
    return 'data:image/%s;base64,%s' % (quote(format), quote(base64.b64encode(image_data)))


def render_plot_2(fig, format=None):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    """
    Render a matplotlib figure into an inline string to display on HTML page
    """
    if not fig or fig is None:
        return ''
    if format is None or not format:
        format = 'png'
    image_data = BytesIO()
    fig.savefig(image_data, format=format)
    image_data.seek(0)
    return 'data:image/png;base64,' + quote(base64.b64encode(image_data.buf))
