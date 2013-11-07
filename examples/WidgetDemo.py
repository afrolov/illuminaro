from illuminaro import *


def eo_server(app, values, outputs, **kwargs):
    outputs.text_output = 'Hey, you chose ' + values.select_input + "\n" +\
            "Sum of sliders: " + str(int(values.slider_1) + int(values.slider_2))


eo_gui = PageWithSidebar(
    'Page title',
    WellPanel(StaticHeader('Header 1', 1),
        StaticHeader('Header 2', 2),
        StaticHeader('Header 3', 3),
        StaticHeader('Header 4', 4),
        StaticHeader('Header 5', 5),
        StaticHeader('Header 6', 6),
        Well(
            Slider('slider_1', 'Slider 1', minvalue=1, maxvalue=20, step_size=1, value=6),
            Slider('slider_2', 'Slider 2', minvalue=1, maxvalue=20, step_size=1, value=6),
        ),
        Well(
            RadioButtons('radio_buttons', ['Several', 'Radio', 'Buttons']),
            CheckboxButtons('checkbox_buttons', ['Several', 'Toggle', 'Buttons']),
            RadioInputs('radio_input', ['Radio Input 1', 'Radio Input 2'], ['ri1', 'ri2'], 1),
            CheckboxInput('checkbox_input_1', False, 'Unchecked checkbox'),
            CheckboxInput('checkbox_input_2', True, 'Checked checkbox')
        ),
        Well(
            SelectInput('select_input', ['Choice 1', 'Choice 2', 'Choice 3'], label='Drop-down Select:')
        )
    ),
    TabSet(
        TabPanel(
            'Slider report',
            TextOutput('text_output', '')
        ),
        TabPanel(
            'Another Tab',
            TextOutput('text_output_2', 'A static text')
        ),
        TabPanel(
            'Accordion',
            Accordion(
                AccordionPanel(
                    'Header 1',
                    TextOutput('acc1', 'Text 1'),
                ),
                AccordionPanel(
                    'Header 2',
                    TextOutput('acc2', 'Text 2'),
                ),
                AccordionPanel(
                    'Header 3',
                    TextOutput('acc3', 'Text 3'),
                ),
                AccordionPanel(
                    'Header 4',
                    TextOutput('acc4', 'Text 2'),
                )
            )
        )
    )
    #TabSet(
    #    TabPanel('Tab 1', TextOutput('text output 1')),
    #    TabPanel('Tab 2', TextOutput('text output 2')),
    #    TabPanel('Tab 3', TextOutput('text output 3'))
    #)
)

# debug=True enables live code reloading on save
IlluminaroApp(eo_gui, eo_server, debug=True).run()
