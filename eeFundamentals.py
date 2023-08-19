import sympy as sp
# import numpy as np
# import matplotlib.pyplot as plt
# from numbers import Number

from sympy.parsing.latex import parse_latex
from eeMath.math_helpers import lambdifier
from eeMath.discrete import bitmaskList


from eeMath.eeSymbols import V, I, R, Rll, R_IN, R_GND,v_in, v_out, V_pull, R_pull

ohmslaw_V_eq = sp.Eq(V, I*R)
ohmslaw_I_eq = sp.Eq(I, sp.solve(ohmslaw_V_eq, I)[0])
ohmslaw_R_eq = sp.Eq(R, sp.solve(ohmslaw_V_eq, R)[0])


with sp.evaluate(False):
  vdiv_out_eq = sp.Eq(v_out, v_in * (R_GND/(R_IN + R_GND)))

vdiv_R_IN_eq = sp.Eq(R_IN, sp.solve(vdiv_out_eq, R_IN)[0])
vdiv_v_in_eq = sp.Eq(v_in, sp.solve(vdiv_out_eq, v_in)[0])
vdiv_R_GND_eq = sp.Eq(R_GND, sp.solve(vdiv_out_eq, R_GND)[0])

# this could/should be made generic: a lambdifier option that does the pre-solve for you
def mkfuncVDivSolver(solve_for, *required_symbol_args, **symbol_with_defaults):
  '''examples:
    vdivRin = mkfuncVDivSolver(R_IN, v_out, v_in=5, R_GND=10000)
  vdivRin is then equivalent to:
    def vdivRin(Vout, Vin=5, R2=10000): return ( ( Vin - Vout ) * R2 ) / Vout
    
  '''
  expr = sp.solve(vdiv_out_eq, solve_for)[0]
  return lambdifier(expr, *required_symbol_args, **symbol_with_defaults)

# def vdivRin(Vout, Vin=5, R2=10000): return ( ( Vin - Vout ) * R2 ) / Vout


def resistorJunctionVoltage(*Vn_Rn_tuples, exact=False, evaluate=False):
  # test: resistorJunctionVoltage((v_out, 33*kΩ),(0, 27*kΩ),(5,27*kΩ))
  # Each arg is a 2-tuple of voltage and resistance, 
  # where either can be a number, a symbol or a string of a symbol
  # DEMO: https://tinyurl.com/2e6aa5o5
  # https://electronics.stackexchange.com/a/140278
  # https://electronics.stackexchange.com/questions/631663/how-can-i-calculate-what-voltage-i-have-in-the-middle-of-2-series-resistors-in-a
  # TODO: prevent division to evaluation of division irrationals: I tried sp.Rational but you can't use that with sp.parse_expr
  #  UPDATE: Workaround: place the assignment using `sp.parse_expr` inside a `with sp.evaluate(False):` block.
  # TODO: maybe return newly created symbols?
  numerator = 0   # sum of each Vn/Rn
  denominator = 0 # sum of each 1/Rn
  new_symbols={}
  for Vn, Rn in Vn_Rn_tuples:
    # if isinstance(Vn, sp.Basic): V = Vn
    if isinstance(Vn, str): new_symbols[Vn] = Vn = sp.symbols(Vn, real=True, finite=True)
    if isinstance(Rn, str): new_symbols[Rn] = Rn = sp.symbols(Rn, real=True, finite=True)


    if isinstance(Rn, sp.Basic):
      numerator += Vn / Rn
      denominator += 1 / Rn
    elif isinstance(Vn, sp.Basic):
      numerator += Vn / Rn
      denominator += sp.Rational(1, Rn)
    else:
      numerator += sp.Rational(Vn, Rn)
      denominator += sp.Rational(1, Rn)

  if evaluate:
    V_expression = numerator / denominator
  else:
    with sp.evaluate(False):
      V_expression = numerator / denominator
    
  solution = V_expression.evalf()
  if not exact and solution.is_number : 
    if new_symbols: return solution, new_symbols
    else: return solution
  else:
    if new_symbols: return V_expression, new_symbols
    else: return solution

RJunctV = resistorJunctionVoltage

def parallelR(*R_tuple):
  if len(R_tuple) == 2: 
    with sp.evaluate(False):
      return (R_tuple[0] * R_tuple[1])/(R_tuple[0] + R_tuple[1])
  with sp.evaluate(False):
    denom = 1 / R_tuple[0]
    for R_item in R_tuple[1:]: denom += 1 / R_item
    return 1 / denom

llR=parallelR # an alias for easier typing

def get_Rll_eq(Rll_sym_or_val, *R_tuple):
  '''examples:
  get_Rll_eq(Rll, R1, R2) # returns Eq(Rll, (R1*R2)/(R_1+R_2) )
  solve(get_Rll_eq(500, 1_000, R2), R2)[0].evalf() # returns 1000'''
  with sp.evaluate(False):
    return sp.Eq(Rll_sym_or_val, parallelR(*R_tuple))

# def IParallelR(*R_lst):
#   subs = []
#   # R_tpl = sp.symbols( f'R0:{len(R_lst)}', real=True, nonnegative=True)
#   for i, R_val in enumerate(R_lst):
#     if isinstance(R_val, numbers.Number):
#       subs
  
#   for R_ in Rn:
#     if R_ is not None:
#       subs.append( (y, )) )
#     product *= number
#   return product

def parallelRPermutations(resistor_values, always_parallel_R=None, lsb_last=False, inv=False):
  '''Output is list of all permutations of parallel resistances from any
  (or all) of the resistor_values list. The output list size is: 
    2**len(resistor_values) - 1  elements
    (minus 1 because the state with no resistors is skipped)
  always_parallel_R (2nd arg), if provided, specifies a resistance that is always in
  in parallel with the circuit no matter what state (permutation).
  lsb_last (default=False) (3rd arg) If this is set to 
    True, the first resistance in the return all resistances
    in parallel, if False, it only one resistor. 
  inv (default=False) (4th arg) Set this to True if resistor outputs
    are active-LOW (enbled by LOW rather than HIGH)
  '''
  results = []
  for bint in range(1, 2**len(resistor_values)):
    active_parallel_resitors = bitmaskList(bint, resistor_values, lsb_last, inv)
    if active_parallel_resitors:
      if always_parallel_R:
        results.append(llR(*active_parallel_resitors, always_parallel_R))
      else:
        results.append(llR(*active_parallel_resitors))
    # results.append(active_parallel_resitors)
  return results
