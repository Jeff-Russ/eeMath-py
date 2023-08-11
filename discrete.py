
# https://stackoverflow.com/a/47878791

from collections.abc import Sequence, Iterable
from collections.abc import Iterable




def zipUnzip(*iterables, strict=False):
  '''pass n iterables, each of length m and get m iterables, each of length n
  This is basically the zip  built-int but zip returns a zip object (which 
  not exactly a tuple but return can be unpacked at function call) and this 
  function returns a tuple instead'''
  return tuple(zip(*iterables, strict=strict)) 

def unweave(iterable, n=2, return_final_n=False, arg1_name_in_errors='the `iterable` argument'):#, unweave_strings=False):
  '''unweave(iterable, n=2)
  returns n lists, unweaved from a iterable. Weaving is related to the
  idea of splitting a list into two: one with odd indices and the other with
  even indicies. In this case, n is 2, but unweave allows unweaving at any 
  interval.
  Additionally, elements in the iterable can be another (non-string) iterable but:
    NOTE that the inner location must contain exactly n elements and
    NOTE that the inner iterable's locations in the outer must occur right   
          an entire cycle of n indidiviual elements (or an inner iterable  
          after with exactly n elements) has completed. 
  NOTE also that unweave does not enforce that the last cycle is complete, but by
        passing return_final_n=True (3rd arg) will make the zeroth element returned
        be the final output of n: if it is zero, the last cycle was complete,
        and each unweaved interable has a size that is evenly disible by n,
        if it is 1, only the first unweaved interable the got an element 
        from the the last cycle.
  Example:
    unweave( ['x0','y0','z0',('x1','y1','z1'),'x2','y2','z2'], 3 )
    # (   ['x0', 'x1', 'x2'],        ['y0', 'y1', 'y2'],  ['z0', 'z1', 'z2'])

    unweave( ['x0','y0','z0',('x1','y1','z1'),'x2','y2','z2', 'x3'], 3, True )
    # (1, ['x0', 'x1', 'x2', 'x3'],  ['y0', 'y1', 'y2'],   ['z0', 'z1', 'z2'])
  '''
  unweaved_lists = [ [] for _ in range(n) ]
  unweaved_idx = 0
  for el in iterable:
    if not isinstance(el, str) and hasattr(el, '__len__'):
      if unweaved_idx != 0:
        raise ValueError(f'Iterables within {arg1_name_in_errors} must occur after n={n} elements have been unweaved')
      if len(el) == n:
        for unweaved_i, inner_el in enumerate(el):
          unweaved_lists[unweaved_i].append(inner_el)
        unweaved_idx = 0
      else:
        raise ValueError(f'When {arg1_name_in_errors} contains a iterable, the contained iterable must have {n} elements')
    else:
      unweaved_lists[unweaved_idx].append(el) 
      unweaved_idx = (unweaved_idx + 1) % n
  if not return_final_n: return (*unweaved_lists,)
  else: return (unweaved_idx, *unweaved_lists,)

def lens(*sequences):
  '''tuple return is the lengths of each sequence in order passed'''
  return tuple([len(seq) for seq in sequences])

def lensMinMax(*sequences):
  '''tuple return is ( min(lens(*sequences)), max(lens(*sequences)) )'''
  # NOTE: requires lens
  lengths = lens(*sequences)
  return ( min(lengths), max(lengths) )

def weave(*iterables, allow_gaps=True, gap_fill=None):
  '''weave returns one iterable from many, where the first element of the first 
  interable is inserted, then the first element of the second iterable, ...etc 
  until the last iterable's first element is inserted after which 
  each element's second element is inserted and so forth.
  
  The returned iterables length is aways evenly divisible by n but, in the case 
  that not all incomming iterables's lengths are evenly divisible by n, a given 
  returned iterable either omits excess elements if allow_gaps==False or, if 
  allow_gaps==True, includes them, inserting `gap_fill` where other input 
  iterables lenghts have been exceeded.
  
  Examples:
    Gap-less weave: weave([1,4], [2,5], [3,6])  # [1,2,3,4,5,6]
    Filled gaps:    weave([1,4], [2], [3,6])    # [1,2,3,4,None,6]
    Un-filled gaps: weave([1,4], [2], [3,6], allow_gaps=False) # [1,2,3]
  NOTE: requires lensMinMax'''
  if len(iterables) == 1: raise ValueError('weave requires more than one iterable')
  weaved = []
  len_min, len_max = lensMinMax(*iterables)
  for i in range(len_min): weaved.extend( [ iterable[i] for iterable in iterables ] )
  if allow_gaps and (len_max > len_min):
    print(f'no filling gaps starting with {i} (so far we have {weaved})')
    for i in range(len_min, len_max):
      for iterable in iterables: 
        try:    weaved.append(iterable[i])
        except: weaved.append(gap_fill)
  return weaved


def yValsToCoords(y_vals, x0=0, x_step=1):
  l_of_tups = [] 
  x = x0
  for y in y_vals:
    l_of_tups.append( (x, y) )
    x += x_step
  return l_of_tups


def interpCoords(coordinates_or_sorted_x_vals, corresponding_y_vals=None, spline_degree=1, x=None, show_plot=False):
  '''interpCoords(coordinates_or_sorted_x_vals, corresponding_y_vals=None, spline_degree=1, x=None, show_plot=False)
  interpCoords is a wrapper around sympy.interpolating_spline.

  With default kwargs (one argument),
    the first argument can be 
      1. an interable of two-elements iterables, where each an x, y coordinate.
      2. a flatted interable of 1. or
      3. a mixture of 1. and 2.
    were the return is linear Piecewise sympy object (linear because spline_degree=1 default)
  
  The return is the same two positional argument but, in this case:
    the first argument is an iterable of x coordinates
    the second argument is corresponding y values
  
  When spline_degree>1, the interpolation is non-linear and spline_degree is the degree of bspline.
  
  x can be provided: the default (None) is to create an temp x sympy.Symbol within the function body.
    NOTE: to use the returned piecewise, i.e. piecewise.subs(x, 4), you'll want to pass your own x
  
  show_plot can be:
    show_plot=False, (default) which means the Piecewise expression is returned
    show_plot=True, which passes Piecewise expression the sympy.plot, without returning it or
    show_plot='and return, which passes Piecewise expression the sympy.plot, and returns it. 
  # NOTE: imports: sympy.interpolating_spline, numpy.argsort numpy.array, sympy.abc.x (sometimes)'''
  from numpy import argsort, array
  from sympy import interpolating_spline
  if corresponding_y_vals:
    x_vals = coordinates_or_sorted_x_vals
    y_vals = corresponding_y_vals
  else:
    x_vals, y_vals = unweave(coordinates_or_sorted_x_vals, n=2, arg1_name_in_errors='the coordinates argument') 
  
  if len(x_vals) != len(y_vals): raise ValueError('the number of x values does not match the number of y values')

  indices_sorted_by_x_values = argsort(x_vals)
  x_vals = list(array(x_vals)[indices_sorted_by_x_values])
  y_vals = list(array(y_vals)[indices_sorted_by_x_values])

  

  if spline_degree >= len(x_vals): spline_degree = len(x_vals) - 1
  if not x: from sympy.abc import x

  '''
  interpolating_spline(d, x, X, Y), where...
    d (integer >= 1) Degree of Bspline [ME: if d==1, you have linear interpolation]
    x (symbol)
    X (list of strictly increasing real values) X coordinates through which the spline passes
    Y (list of real values) corresponding Y coordinates through which the spline passes
  '''
  s = interpolating_spline(spline_degree, x, x_vals, y_vals)

  if show_plot:
    from sympy import plot
    print(f"x_vals={x_vals}\ny_vals={y_vals}")
    plot(s)
    if show_plot == 'and return': return s
  else: 
    return s



def bitflipUInt(uint, bit_len):
  mask = eval(f'0b{"1"*bit_len}')
  return ~uint & mask

def bitmaskList(bitmask_int, bit_vals, lsb_last=False, inv=False):
  '''takes a non-negative bitmask_int, splits it into bits
  and returns a sublist of a provides list of bit_vals
  where each returned element is an ON bit from provided
  non-negative bitmask_int.
  lsb_last (default=False) (3rd arg) If this is set to 
    True, the LSB in bitmask_int corresponds to the 
    last element of bit_vals rather than the zeroth.
  inv (default=False) (4th arg) If True,
    each returned element is an OFF bit in bitmask_int.
  Examples:
    bitmaskList(2, [-1, -2])       # [-2]
    bitmaskList(2, [-1, -2], True) # [-1]
    bitmaskList(0b101, [1, 2, 3])  # [1, 3]
    bitmaskList(0b00, [1, 2, 3])   # []
    bitmaskList(0b101, [1, 2, 3], inv=True) # [2]
  '''
  if inv: bitmask_int = bitflipUInt(bitmask_int, len(bit_vals))
  from itertools import compress  # lst_els_true_in_bools = compress(lst, bools) ...
  # but it also works if the bools list is integers, but not if bools is a string...
  # So, first convert to list of string integers. Below, the [2:] is to shave off '0b'
  # at start of string bool and the zfill pads 0's on left so len matches bit_vals:
  ibool_lst = list(bin(bitmask_int)[2:].zfill(len(bit_vals))) 
  ibool_lst = list(map(int, ibool_lst)) # then convert to list of integers.
  if not lsb_last: ibool_lst.reverse() # reverse if lsb is last
  return list(compress(bit_vals, ibool_lst)) 
