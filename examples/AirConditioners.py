from illuminaro import *

aircon_gui = SimplePage(
    "Air conditioner chooser web app",
    StaticHeader('Choose an air conditioner'),
    Well(
        StaticHeader('Room Properties', 3),
        Well(
            NumericInput('area',  100, 'Area (sq. ft)'),
            NumericInput('height',  10, 'Height (ft)'),
            RadioButtons('orientation', ['North', 'West', 'South', 'East'],
                         label='Room Orientation'),
            RadioButtons('insulation', ['Poor', 'Good', 'Excellent'],
                         label='Insulation Quality'),
        ),
        StaticHeader('Result', 3),
        MarkupOutput('result_btu', ''),
    )
)


def aircon_server(app, values, outputs, **kwargs):
    if values.insulation == 'Good':
        insulation_factor = 5
    elif values.insulation == 'Excellent':
        insulation_factor = 6
    else:
        insulation_factor = 4

    if values.orientation == 'East':
        sunlight_level = 17
    elif values.orientation == 'North':
        sunlight_level = 16
    elif values.orientation == 'South':
        sunlight_level = 18
    elif values.orientation == 'West':
        sunlight_level = 20

    btu = values.area * values.height * sunlight_level / insulation_factor
    outputs.result_btu = '<p>You will need at least <strong>' \
            + str(btu) + '</strong> BTU</p>'
    pass

IlluminaroApp(aircon_gui, aircon_server, port=5000, debug=True).run()
