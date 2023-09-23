import sympy as sp

def parallelR(*R_tuple):
  '''pass a bunch of resistance and get the resistance of them all in parallel'''
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


# Resistor Values
# https://eepower.com/resistor-guide/resistor-standards-and-codes/resistor-values/#