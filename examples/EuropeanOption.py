from illuminaro import *


def eo_server(inputs, outputs):
    print(inputs)


eo_gui = SimplePage('European Option',
                    WellPanel(StaticHeader('European Option'),
                              Well(
                                  Slider('strike', 'Strike', minvalue=1, maxvalue=20, step_size=1, value=6),
                                  Slider('interest_rate', 'Interest Rate', minvalue=0.0, maxvalue=50.0, step_size=0.1),
                                  Slider('dividend_rate', 'Dividend Rate', minvalue=0.0, maxvalue=50.0, step_size=0.1),
                                  Slider('volatility', 'Volatility', minvalue=0.0, maxvalue=1.0, step_size=0.01),
                                  Slider('tte', 'Time to Expiry', minvalue=0.0, maxvalue=1.0, step_size=0.1)
                              ),
                              Well(
                                  RadioButtons('put_or_call', ['puts', 'calls'])
                              )
                    )
)
IlluminaroApp(eo_gui, eo_server).run()
