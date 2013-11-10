from illuminaro import *
import numpy as np
import matplotlib.pyplot as plt

def eo_server(app, values, outputs, **kwargs):
    xs = np.arange(-3, +3, 0.05)
    ys = float(values.amp_1) * np.sin((xs + float(values.phase_1))*float(values.freq_1)) + \
        float(values.amp_2) * np.sin((xs + float(values.phase_2))*float(values.freq_2))

    pix_x = values.illuminaroout_waves_width
    pix_y = values.illuminaroout_waves_height
    plt.figure()
    fig = plt.gcf()
    dpi = fig.get_dpi()
    default_aspect_ratio = float(3) / 2
    if True or not pix_y: # bizarre behaviour of height
        pix_y = int(pix_x / default_aspect_ratio)
    inches_x = pix_x / dpi
    inches_y = pix_y / dpi
    fig.set_size_inches(inches_x, inches_y)
    plt.grid(values.show_grid)
    plt.plot(xs, ys)

    outputs.waves = render_plot(fig)

eo_gui = PageWithSidebar(
    'Two waves',
    WellPanel(StaticHeader('Parameters', 1),
        Well(
            Slider('amp_1', 'Amplitude 1', minvalue=1, maxvalue=10, step_size=1, value=6),
            Slider('amp_2', 'Amplitude 2', minvalue=1, maxvalue=10, step_size=1, value=2),
            Slider('freq_1', 'Frequency 1', minvalue=1, maxvalue=20, step_size=1, value=6),
            Slider('freq_2', 'Frequency 2', minvalue=1, maxvalue=20, step_size=1, value=6),
            Slider('phase_1', 'Phase 1', minvalue=-90, maxvalue=90, step_size=1, value=0),
            Slider('phase_2', 'Phase 2', minvalue=-90, maxvalue=90, step_size=1, value=90),
            CheckboxInput('show_grid', True, 'Show grid')
        ),
    ),
    Well(
        PlotOutput('waves')
    )
)

# debug=True enables live code reloading on save
IlluminaroApp(eo_gui, eo_server, debug=True).run()

