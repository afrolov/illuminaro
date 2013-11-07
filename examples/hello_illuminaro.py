from illuminaro import *

gui = SimplePage(
    'First Illuminaro app',
    TextOutput(id='text_output', text='Hello from Illuminaro')
)
IlluminaroApp(gui, None).run()
