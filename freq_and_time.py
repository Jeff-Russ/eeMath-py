import sympy as sp
# import numpy as np
# import matplotlib.pyplot as plt


from eeMath.eeSymbols import R, C, f_Hz, tau1, n_tau, n_midi, p_cnt
from eeMath.units import getUnit, parseNum
from eeMath.math_helpers import evalF


#### TIME <> FREQUENCY CONVERSION ################################################################

def periodOfHz(hz): return 1/hz # period, in seconds, from hertz
sOfHz = periodOfHz

def hzOfPeriod(seconds): return 1/seconds
hzOfS = hzOfPeriod

def msOfHz(hz): return 1000/hz # period, in milliseconds, from hertz


#### RC CIRCUITS #################################################################################

tau1_of_RC_eq = sp.Eq(tau1, R * C) # tau1 means tau*1 so really just tau (in seconds)

p_cnt_after_n_tau_eq =  sp.Eq(p_cnt, 1 - sp.exp(-n_tau))

n_tau_of_p_cnt_eq = sp.Eq(n_tau, sp.log(-1/(p_cnt - 1)))


def valOfRCWithTau(R_or_C_val, tau_val, n_tau=1, exact=False): 
  R_or_C_val = parseNum(R_or_C_val)
  if n_tau != 1: tau_val /= n_tau
  
  sol = sp.solve(tau1_of_RC_eq.subs({R: R_or_C_val, tau1: tau_val}), C)
  if not sol: return sol
  if exact:
    if len(sol) == 1: return sol[0]
    else: return sol
  else:
    return sol[0].evalf()

f_Hz_of_RC_at_n_tau_eq = sp.Eq( f_Hz, 1/(R * C * n_tau) )

# C_val = sp.solve(eq.subs({f_Hz:8.175798915643707, n_tau:DCO_tc_span, R: max_R}) )[0].evalf()

def valOfRCWithHz(R_or_C_val, f_hz, n_taus=1, exact=False): 
  R_or_C_val = parseNum(R_or_C_val)
  sol = sp.solve(f_Hz_of_RC_at_n_tau_eq.subs({f_Hz:f_hz, R: R_or_C_val, n_tau: n_taus}), C)
  if not sol: return sol
  if len(sol) == 1: 
    if exact: return sol[0]
    else: return parseNum(sol[0])
  else: return sol

def hzOfRC(R_val, C_val, n_taus=1, exact=False):
  R_val = parseNum(R_val)
  C_val = parseNum(C_val)
  sol = sp.solve(f_Hz_of_RC_at_n_tau_eq.subs({R:R_val, C:C_val, n_tau: n_taus}), f_Hz)
  if not sol: return sol
  if len(sol) == 1: 
    if exact: return sol[0]
    else: return parseNum(sol[0])
  else: return sol

def infoOnRC(R_val, C_val, forTau=[1,3,5]):
  from math import pi
  from re import search
  R_val =  parseNum(R_val)
  C_val = parseNum(C_val)
  t_const = R_val * C_val
  f_cut = 1 / (2 * pi * t_const)
  ret = {'R':R_val, 'C':C_val, 't_const':t_const, 'f_cut':f_cut}
  for tc in forTau:
    ms = t_const * tc * 1000
    hz = 1 / (t_const * tc)
    ret[f'atTau{tc}'] = { 'ms':ms, 'hz':hz }
  return ret

#### MIDI NOTE FREQUENCY ##########################################################################


with sp.evaluate(False):
  f_Hz_of_n_midi_eq = sp.Eq(f_Hz, 440 * 2**((n_midi-69)/12))
  n_midi_of_f_Hz_eq = sp.Eq(n_midi, ((12 * sp.ln(f_Hz / 440)) / sp.ln(2)) + 69)


semitone_up_ratio = 2**(sp.Rational(1, 12))
semitone_down_ratio = 2**(sp.Rational(11, 12))/2

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


