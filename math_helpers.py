import sympy as sp
# import numpy as np
# from sympy import symbols, Eq, evaluate, sympify, parse_expr, init_printing, Rational, solve, simplify
# import matplotlib.pyplot as plt

###### MATH HELPERS ###############################################################################



# # TODO: this but better (maybe dynamically choose to leave it as a fraction if float is irrational):
# def rnd(num, tol=10): # raising tol reduces error correcting
#   rounded = round(num)
#   if rounded == num: return int(rounded)
#   off_by = abs(num - rounded) 
#   if off_by > 1.0/(10.0**tol): return num
#   else:
#     # print("{} error corrected to {}".format(num,rounded))
#     return int(rounded)

def transposeEq(eq, var, multiple_solutions='allow'):
  # multiple_solution ='first'|'fail'|'expect'|'allow' which mean:
  # return first (never array) | fail (never return array) | always return array | return array if multiple
  # in all cases, an empty array is returned if there are no solutions
  solutions = sp.solve(eq, var)
  if   len(solutions) == 1:
    if multiple_solutions == 'expect': return [sp.Eq(var, solutions[0])]
    else: return sp.Eq(var, solutions[0])
  elif  len(solutions) > 1:
    if multiple_solutions == 'first': return sp.Eq(var, solutions[0])
    elif multiple_solutions == 'fail': raise Exception("multiple_solutions prevented")
    else:
      for i, solution in enumerate(solutions): solutions[i] = sp.Eq(var, solutions[i])
      return solutions
  else:
    return []



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

def divToUnicode(numr, denr):
  nonrep, repetend = repetendStr(numr, denr, all_portions=True)
  return f'{nonrep}{overline(repetend)}' # fine if repetend is empty: overline checks this



def evalF(anything):
  # TODO: maybe see if there is precision loss and avoid it by not .evalf in that case
  try: return anything.evalf() 
  except: return anything

def solveSysEq(eqs, symbs, evalf=True):
  # normally sp would return a dict of symbol values but this function 
  # will return an array of those values in the order they were passed to 
  # symbs to enable easier destructuring/unpacking to new python variables
  sol_dict = sp.solve(eqs, symbs)
  return [evalF(sol_dict[symb]) for symb in symbs]


def ppMode(mode=None, **kwargs): # pretty print selection
  if not kwargs:
    if   mode == 'unicode': sp.init_printing(pretty_print=True, use_unicode=True)
    elif mode == False: sp.init_printing(pretty_print=False)
    elif mode == True or mode == None : sp.init_printing(pretty_print=True, use_unicode=False)
    else: print(f'WARNING: ppMode got unknown option: {mode}')
  else: # defer to (forward keyword arguments to)   sp.init_printing
    sp.init_printing(**kwargs)



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