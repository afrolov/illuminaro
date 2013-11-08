#!/usr/bin/env python

# Inspired by http://demonstrations.wolfram.com/DiceProbabilities/

from illuminaro import *
from sympy import *


def multi_dice(n_dies, n_sides):
    x = symbols('x')
    f = 0
    for i in range(1, n_sides + 1):
        f += x ** i
    return Poly((f ** n_dies).expand()).all_coeffs()


def calculator(app, values, outputs, **kwargs):  # TODO do we really need to require kwargs?
    n_sides = int(values.number_of_sides[0])  # TODO FIXME - only one value or None
    n_dies = int(values.number_of_dice)
    chances = multi_dice(n_dies, n_sides)
    rows = []
    for n in range(len(chances)):
        number_of_chances = chances[len(chances) - n - 1]
        if number_of_chances:
            rows.append([n, number_of_chances])
    table = Table(['roll', 'chances'], rows)
    outputs.result_table = table.markup()  # TODO assign without explicit markup call


gui = SimplePage(
    "Dice Probabilities",
    Well(
        Slider('number_of_dice', 'number of dice', minvalue=1, maxvalue=10, step_size=1),
        RadioButtons('number_of_sides', ['2', '4', '6', '8', '10', '12', '20'], label='number of sides'),
        MarkupOutput('result_table')
    )
)

app = IlluminaroApp(gui, calculator, debug=True)
app.run()
