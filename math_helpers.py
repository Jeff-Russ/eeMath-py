import sympy as sp
# import numpy as np
# from sympy import symbols, Eq, evaluate, sympify, parse_expr, init_printing, Rational, solve, simplify
# import matplotlib.pyplot as plt

###### MATH HELPERS ###############################################################################

from eeMath.eeSymbols import symbs


def subs(expr_or_eq=None, subs={}, persist=False):
  '''1) Normal mode of operation:
    subs(expr_or_eq)            # returns expr_or_eq.subs(symbs.subs)
    subs(expr_or_eq, subs_dict) # returns expr_or_eq.subs({**symbs.subs, **subs_dict})
    subs(expr_or_eq, subs_dict, persist=True) # same, but sets symbs.subs = {**symbs.subs, **subs_dict}
  
  2) Modes to set/get symbol subs defaults (all return symbs.subs or some subset of it)
    subs()                            # returns entire dictionary of symbols, whether set to a default or to self (no default)
    subs(set_of_symbols)              # returns dictionary, but only entires whose key is in set_of_symbols. Intended usage:
                                      # subs(expr_or_eq.free_symbols)
    subs('defaults')                  # return default dict (symbs.subs that define substitutions with defaults)
    subs('defaults', set_of_symbols)  # returns defaults dict but only entries with keys in set_of_symbols. Intended usage:
                                      # subs('get', expr_or_eq.free_symbols)
    subs('set', subs_dict)            # adds (persists) subs_dict entries to subs.default before returning it 
    subs('clear')                     # disables subsitutions for all symbols by setting each in symbs.subs to itself.
    subs('clear', subs_dict)          # same but also adds new subs entries
    subs('clear', set_of_symbols)     # the same as previous, but only for symbols in set_of_symbols. Intended usage:
                                      # subs('clear', expr_or_eq.free_symbols)
  '''
  global symbs

  if   expr_or_eq is None: return symbs.subs
  elif isinstance(expr_or_eq, (set, list, tuple)):
    return { k:v for (k,v) in symbs.subs.items() if k in expr_or_eq } 

  if isinstance(expr_or_eq, str):
    # also_include = []
    if expr_or_eq == 'clear':
      if subs:
        if isinstance(subs, dict):                 # clear, then set
          symbs.subs = {**{symb:symb for symb in symbs.subs}, **subs}
          # also_include = subs.keys() # we'll return those with defaults + those set

        elif isinstance(subs, (set, list, tuple)): # clear specified only
          for symb in subs: symbs.subs[symb] = symb
          # also_include = subs # we'll return those with defaults + those specified

        else: print(f'Warning: cannot clear defaults with {type(subs)} object provided as second argument')
      else:
        symbs.subs = { symb:symb for symb in symbs.subs }
      
    elif expr_or_eq == 'set':
      if subs:
        if isinstance(subs, dict):              # set
          symbs.subs = {**symbs.subs, **subs}
          # also_include = subs.keys() # we'll return those with defaults + those specified

        else: print(f'Warning: cannot set defaults using {type(subs)} object')
      else:
        print(f'Warning: cannot set defaults without second argument!')

    elif expr_or_eq == 'defaults':
      if subs and isinstance(subs, (set, list, tuple)): # show defaults for specified
        return { k:v for (k,v) in symbs.subs.items() if k != v and k in subs } 
    
    else: print(f'Warning: unknown option {expr_or_eq} to subs()')
    
    # return a copy of symbs.subs only containing entries whose keys do not equal values;
    # return { k:v for (k,v) in symbs.subs.items() if k != v or k in also_include} 
    return { k:v for (k,v) in symbs.subs.items() if k != v} 
  
  unidentified_keys = subs.keys() - expr_or_eq.free_symbols
  if unidentified_keys: 
    raise ValueError(f'The following subsitutions are for unknown symbols: {unidentified_keys}')
  
  merged_subs = {**symbs.subs, **subs} 
  result = expr_or_eq.subs(merged_subs)

  if persist:
    symbs.subs = {**symbs.subs, **subs}
  return result

#....... Boolean functions ...................................................

def equalExprs(*exprs):
  expr0 = sp.simplify(exprs[0])
  for i in range(1, len(exprs)):
    if expr0 - sp.simplify(exprs[i]) != 0: return False
  return True

#....... solve, calc ..........................................................

def solveFor(eq, solve_for, multiple_solutions='allow'):
  # multiple_solution ='first'|'fail'|'expect'|'allow' which mean:
  # return first (never array) | fail (never return array) | always return array | return array if multiple
  # in all cases, an empty array is returned if there are no solutions
  solutions = sp.solve(eq, solve_for)
  if   len(solutions) == 1:
    if multiple_solutions == 'expect': return [sp.Eq(solve_for, solutions[0])]
    else: return sp.Eq(solve_for, solutions[0])
  elif len(solutions) > 1:
    if multiple_solutions == 'first': return sp.Eq(solve_for, solutions[0])
    elif multiple_solutions == 'fail': raise Exception("multiple_solutions prevented")
    else:
      for i, solution in enumerate(solutions): solutions[i] = sp.Eq(solve_for, solutions[i])
      return solutions
  else:
    return []
  

def solveSys(eqs_or_exprs, *symbs, **flags):
  # TODO: merge this function with solveFor
  # normally sp.solve would return a dict of symbol values but this function 
  # will return a tuple of those values in the order they were passed to 
  # symbs. If there is than one solution, the return is a list of these tuples
  # Also, unlike sp.solve, evalf=True can be passed

  '''example with one solution:
  from sympy.abc import x, y, z
  equalities = [ Eq(x + y + z, 25), 5*x + 3*y + 2*z, Eq(6, y - z) ] # equalities[0]==0
  # solution is x = -131/5, y = 113/5, z = 143/5
  solveSys(equalities, [x,y,z])

  example with four solutions:
  solveSys([Eq(x**2 + y, 5),Eq(x**2 + y**2, 7)], x, y)

  '''
  try_eval = False
  if 'evalf' in flags:
    try_eval = flags['evalf']
    del flags['evalf']

  from collections.abc import Iterable
  if not isinstance(eqs_or_exprs, Iterable): eqs_or_exprs = [eqs_or_exprs]

  if len(symbs) == 1:
    symbs = symbs[0] if isinstance(symbs[0], Iterable) else [symbs[0]]

  sol = sp.solve(eqs_or_exprs, symbs)

  if isinstance(sol, dict):
    if try_eval: return tuple([evalF(sol[symb]) for symb in symbs])
    else: return tuple([sol[symb] for symb in symbs])
  elif isinstance(sol, list):
    if try_eval:
      return [ tuple(evalF(val) for val in tup) for tup in sol ]
    else: return sol
  else:
    return sol


def evalF(anything, exact=True, try_mixed=False, max_decimals=10):
  # TODO: maybe see if there is precision loss and avoid it by not .evalf in that case
  # UPDATE: DONE.
  # from sympy import Number
  # if isinstance(anything, Number): return anything
  try:
    flt = anything.evalf() 
    if flt == int(flt): return int(flt)
    if try_mixed and flt > 1 or flt < -1:
      int_part = sp.Integer(flt)
      frac_part = anything - int_part
      with sp.evaluate(False): return int_part + frac_part
    if (not exact) or (floatDecimalPlaces(flt) <= max_decimals): return flt
    else: return anything
  except: return anything

def spPrint(anything, *more, delim=''):
  # we can keep adding conditions for sympy type as we need them.
  # to see the supported ones, type `sp.StrPrinter._print_` and hit tab
  def _spPrint(anything):
    if type(anything) == sp.Add:
      print(sp.StrPrinter({'order':'none'})._print_Add(anything), end='')
    elif type(anything) == sp.Mul:
      print(sp.StrPrinter({'order':'none'})._print_Mul(anything), end='')
    elif type(anything) == sp.Rational:
      print(sp.StrPrinter({'order':'none'})._print_Rational(anything), end='')
    else:
      print(sp.StrPrinter({'order':'none'})._print(anything), end='')
  _spPrint(anything)
  if len(more) == 0 : print()
  else:
    for thing in more:
      print(delim, end='')
      _spPrint(thing)


def spStr(*anything, delim=''):
  # we can keep adding conditions for sympy type as we need them.
  # to see the supported ones, type `sp.StrPrinter._print_` and hit tab


  def _spStr(anything): # TODO: use this as the core for spPrint and just print() once
    if type(anything) == sp.Add:
      return sp.StrPrinter({'order':'none'})._print_Add(anything)
    elif type(anything) == sp.Mul:
      return sp.StrPrinter({'order':'none'})._print_Mul(anything)
    elif type(anything) == sp.Rational:
      return sp.StrPrinter({'order':'none'})._print_Rational(anything)
    else:
      return sp.StrPrinter({'order':'none'})._print(anything)
    
  return delim.join([_spStr(thing) for thing in anything])


# def canDivideExactly(num, den): 
#   # https://stackoverflow.com/a/34371850
#   # fails this: canDivideExactly(74163, 20000) # so i'll just count decimal places
#   from sys import float_info
#   f = Fraction(num, den)
#   return (
#     # denominator is a power of 2
#     f.denominator & (f.denominator - 1) == 0 and
#     # numerator exponent can be represented
#     f.numerator.bit_length() <= float_info.max_exp and
#     # numerator significant bits can be represented without loss
#     len(format(f.numerator, 'b').rstrip('0')) <= float_info.mant_dig
#   )



def floatDecimalPlaces(flt): 
  return len(str(flt).split(".")[1].rstrip('0'))

# I THINK THIS WAS NOT WORKING...
# def divideIfExact(Fraction_or_Rational):
#   from fractions import Fraction
#   if type(Fraction_or_Rational) != Fraction: frac = Fraction_or_Rational
#   else:
#     num, den = sp.fraction(sp.together(Fraction_or_Rational)) # we could skip the sp.together
#     frac = Fraction(num, den)
  
#   if canDivideExactly(frac.numerator, frac.denominator):
#   	return frac.numerator / frac.denominator
  
#   int_part = frac.numerator // frac.denominator
#   frac_part = Fraction_or_Rational - int_part
#   with evaluate(False): return int_part + frac_part

#....... compatibility ........................................................

def lambdifier(expr_or_eq, *required_symbol_args, **symbol_with_defaults):
  '''
  like sympy.lamdify but...
  1) arg1: is exprssion or, if equality, uses the right hand expression:
      WARNING: you should be sure the left hand expression is what you want to return
  2) supsequent positional args are the symbol arguments to the lamdified function that 
      do not have default values
  3) additional kwargs in the form of symbol=default_value are used to define the 
      remaining lamdified function's arguments with default values that are, therefore, optional
  '''
  expr = expr_or_eq.rhs if expr_or_eq.is_Equality else expr_or_eq
  symbol_args = list(required_symbol_args) # a tuple
  for symb, value in symbol_with_defaults.items():
    symbol_args.append(f'{symb}={value}')
    # symbol_args += (f'{symb}={value}', ) # DON'T REMOVE COMMA: 
    # # see first comment to https://stackoverflow.com/a/8538676
  # return sp.lambdify(tuple(symbol_args), expr)
  return sp.lambdify(tuple(symbol_args), expr)

#....... display of information ...............................................

def ppMode(mode=None, **kwargs): # pretty print selection
  if not kwargs:
    if   mode == 'unicode': sp.init_printing(pretty_print=True, use_unicode=True)
    elif mode == False: sp.init_printing(pretty_print=False)
    elif mode == True or mode == None : sp.init_printing(pretty_print=True, use_unicode=False)
    else: print(f'WARNING: ppMode got unknown option: {mode}')
  else: # defer to (forward keyword arguments to)   sp.init_printing
    sp.init_printing(**kwargs)


def pp(thing, rm=r'({|})'):
  from re import compile, sub
  return print(sub(compile(rm), '', sp.pretty(thing, use_unicode=True)))

#....... Fractional numbers and FP precision ..................................

def repetendLen(a, b): # test with (58000, 89)-> 44
  # from: https://stackoverflow.com/a/46388419
  # NOTE: This function does not returns the number of decimal places needed, it returns
  # the length of the repeating sequence found in resulting float: i.e. (1,3) returns 1 
  # If the resulting float does not have repeating decimals, it returns 0
  n = a % b
  if n == 0: return 0

  mem = {}
  n *= 10
  pos = 0

  while True:
    pos += 1
    n = n % b
    if n == 0: return 0
    if n in mem:
      i = mem[n]
      return pos - i
    else: mem[n] = pos
    n *= 10



# # https://codegolf.stackexchange.com/a/78938
# repetend=lambda n,t=1,q=[],*d:q[(*d,t).index(t):]or repetend(n,t%n*10,q+[t//n],*d,t)

def repetendStr(numr, denr, all_portions=False): 
  '''Given the division first arg by the second: return the repeating portion after the decimal point as str.
  if all_portions=False, return a 2-tuple: 
    the integer part with decimal point followed any non repeating numbers as string,
    the repeating part a string (repetend), or empty string if there isn't any repetend
  tests: 
    repetendStr(1, 6)  # '6'      because 1/6 = 0.16....where 6 repeats forever
    repetendStr(1, 11) # '09'     because 1/11 == 0.09...        where 09 repeats forever
    repetendStr(1, 28) # '571428' because 1/11 == 0.03571428... where 571428 repeats forever
    repetendStr(58000, 89) # '68539325842696629213483146067415730337078651'
    
  original: https://www.geeksforgeeks.org/find-recurring-sequence-fraction/
  '''
  res = "" ; mp = {} # maps already seen remainders as keys and their indices in res as vals. 
  # Note: we need indices for cases like 1/6, where recurring sequence doesn't start from first remainder.
  rem = numr % denr  # Find first remainder
  while ((rem != 0) and (rem not in mp)): # Keep finding remainder until it is 0 or repeats
    mp[rem] = len(res)      # Store this remainder
    rem = rem * 10          # Multiply remainder with 10
    res += str(rem // denr) # append rem / denr to result.
    rem = rem % denr        # Update remainder
  if all_portions:
    if rem == 0: return [f'{numr/denr}', ''] 
    else: return f'{numr//denr}.{res[:mp[rem]]}', res[mp[rem]:] 
  elif (rem == 0): return ""
  else: return res[mp[rem]:]

# https://stackoverflow.com/a/33885706
def overline(str_able): return '\u0305'.join([*str(str_able)])+u'\u0305' if str_able else ''


# # TODO: this but better (maybe dynamically choose to leave it as a fraction if float is irrational):
# def rnd(num, tol=10): # raising tol reduces error correcting
#   rounded = round(num)
#   if rounded == num: return int(rounded)
#   off_by = abs(num - rounded) 
#   if off_by > 1.0/(10.0**tol): return num
#   else:
#     # print("{} error corrected to {}".format(num,rounded))
#     return int(rounded)


def divToUnicode(numr, denr):
  nonrep, repetend = repetendStr(numr, denr, all_portions=True)
  return f'{nonrep}{overline(repetend)}' # fine if repetend is empty: overline checks this






#............. TODO ...........................................................

# def exprAreEqual(*exprs) :
#   subtracted=None
#   for expr in exprs:



# def calc(eq, let=None, get=None):
#   if not let and not get:
#     all_symbols = eq.free_symbols

#   if not isinstance(let, dict): # https://stackoverflow.com/a/9485467
#     i = iter(let) 
#     let = dict(zip(i, i))
#   if not instanceof(get, tuple, list, set):
#     get=[get]
  

  # if known and unknown:
  #   return sp.solve(known, unknown)
#   sp.solve(eq2.subs(x, 2), y) 
#   sp.solve([eq1, eq2], [t, v0])[0]