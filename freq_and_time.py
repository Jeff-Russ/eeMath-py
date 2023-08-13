import sympy as sp
# import numpy as np
# import matplotlib.pyplot as plt


from eeMath.eeSymbols import R, C, n_midi, f_Hz
from eeMath.units import getUnit

with sp.evaluate(False):
  f_Hz_of_n_midi_eq = sp.Eq(f_Hz, 440 * 2**((n_midi-69)/12))
  n_midi_of_f_Hz_eq = sp.Eq(n_midi, ((12 * sp.ln(f_Hz / 440)) / sp.ln(2)) + 69)


def hzOfMidi(note, exact=False): 
  if exact:
    sol = sp.solve(f_Hz_of_n_midi_eq.subs({n_midi: note}), f_Hz)
    if len(sol) == 1: return sol[0]
    else: return sol
  else:
    return 440 * 2**((note-69)/12)
  

def midiOfHz(hz, exact=False): 
  if exact:
    sol = sp.solve(n_midi_of_f_Hz_eq.subs({f_Hz: hz}), n_midi)
    if len(sol) == 1: return sol[0]
    else: return sol
  else:
    from math import log as ln
    return ((12 * ln(hz / 440)) / ln(2)) + 69

def msOfHz(hz): return 1000/hz # period, in milliseconds, from hertz

def periodOfHz(hz): return 1/hz # period, in seconds, from hertz

# def hzOfPeriod(seconds): return 1/seconds

# def msOfms(ms): return 1000/ms

sOfHz = periodOfHz

def periodOfMidi(note, exact=False, unit='s'):
  if unit == 's': unit = 1
  else: unit = getUnit(unit)

  hz = hzOfMidi(note, exact)

  if hasattr(hz, '__len__') :
    for i in range(len(hz)):
      hz[i] = 1 / hz[i] / unit
    return hz
  else:
    return 1 / hz / unit

# 8-bit MIDI: my invention, where lower "notes" are added, which are actually for LFOs/Envelopes
# in this 8-bit, notes 128 to 255 result in what notes 0 to 127 result in with 7-bit.

midi8def440 = 197
