Illuminaro
~~~~~~

Illuminaro is a package for building interactive rich web applications with Python.

Illuminaro Hello World
------------------
Once you installed illuminaro, save the following code into hello_illuminaro.py

    from illuminaro import *

    gui = SimplePage(
        'First Illuminaro app',
        TextOutput(id='text_output', text='Hello from Illuminaro')
    )
    IlluminaroApp(gui, None).run()
    
set ``PYTHONPATH=.`` or ``PYTHONPATH=/path/to/illuminaro`` so that python could find
illuminaro code and run it with ``python examples/hello_illuminaro.py`` then in your browser navigate to
http://localhost:5000/ You should see a simple text "Hello from Illuminaro"

Features
--------

Third party dependencies
------------------------
Illuminaro re-uses a lot of functionality from existing quality Python modules:

* Jinja2 - template engine and input sanitation
* Six - to maintain single source for both Python 2 and Python 3
* Tornado - web framework and asynchronous networking library
