import sympy as sp
# import numpy as np
# import matplotlib.pyplot as plt


from eeMath.eeSymbols import n_midi, f_Hz

with sp.evaluate(False):
  f_Hz_of_note = sp.Eq(f_Hz, 440 * 2**((n_midi-69)/12))
  # f_Hz_note_0expr = 440 * 2**((n_midi-69)/12) - f_Hz
  f_Hz_note_expr = 440 * 2**((n_midi-69)/12)