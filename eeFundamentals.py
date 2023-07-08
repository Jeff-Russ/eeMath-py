import sympy as sp
# import numpy as np
# import matplotlib.pyplot as plt
# from numbers import Number


from eeMath.eeSymbols import V, I, R

ohmslaw_V_eq = sp.Eq(V, I*R)
ohmslaw_I_eq = sp.Eq(I, sp.solve(ohmslaw_V_eq, I)[0])
ohmslaw_R_eq = sp.Eq(R, sp.solve(ohmslaw_V_eq, R)[0])


def resistorJunctionVoltage(*Vn_Rn_tuples, exact=False, evaluate=False):
  # Each arg is a 2-tuple of voltage and resistance, 
  # where either can be a number, a symbol or a string of a symbol
  # DEMO: https://tinyurl.com/2e6aa5o5
  # https://electronics.stackexchange.com/a/140278
  # https://electronics.stackexchange.com/questions/631663/how-can-i-calculate-what-voltage-i-have-in-the-middle-of-2-series-resistors-in-a
  # TODO: prevent division to evaluation of division irrationals: I tried sp.Rational but you can't use that with sp.parse_expr
  #  UPDATE: Workaround: place the assignment using `sp.parse_expr` inside a `with sp.evaluate(False):` block.
  # TODO: maybe return newly created symbols?
  numerator=[]   # each is Vn/Rn, which will all be added to form the numerator
  denominator=[] # each is 1/Rn, which will all be added to form the denominator
  new_symbols={}
  for Vn, Rn in Vn_Rn_tuples:
    if Vn.__class__.__name__ == 'Symbol': v = Vn.name
    else:
      V=Vn
      if isinstance(Vn, str): new_symbols[Vn] = sp.symbols(Vn, real=True, finite=True)
    if Rn.__class__.__name__ == 'Symbol' : R = Rn.name
    else:
      R=Rn
      if isinstance(Rn, str): new_symbols[Rn] = sp.symbols(Rn, real=True, nonnegative=True)
    numerator.append( f'{V} / {R}' )
    denominator.append( f'1 / {R}' )
  numerator   = ' + '.join(numerator)
  denominator = ' + '.join(denominator)
  if evaluate: V_expression = sp.parse_expr(f'( {numerator} ) / ( {denominator} ) ')
  else:
    with sp.evaluate(False):
      V_expression = sp.parse_expr(f'( {numerator} ) / ( {denominator} ) ')
    
  solution = V_expression.evalf()
  if not exact and solution.is_number : 
    return solution, new_symbols
  else:
    return V_expression, new_symbols


def parallelR(*R_tuple):
  if len(R_tuple) == 2: 
    with sp.evaluate(False):
      return (R_tuple[0] * R_tuple[1])/(R_tuple[0] + R_tuple[1])
  with sp.evaluate(False):
    denom = 1 / R_tuple[0]
    for R_item in R_tuple[1:]: denom += 1 / R_item
    return 1 / denom

llR=parallelR # an alias for easier typing

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


