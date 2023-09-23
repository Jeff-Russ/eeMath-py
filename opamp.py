import sympy as sp
from sympy import Eq, evaluate, simplify

from eeMath.eeSymbols import getSymb, real_finite, real_nonneg
from eeMath.eeSymbols import v_p, v_p, v_m, v_out, R_v_m, R_nfb, R_pfb, v_in, i_out, v_pIn, v_offset, v_gain, V_REF,R_GND, R_v_p, R_pREF, R_nREF, V_pREF, V_nREF, v_p_gain, v_m_gain
from eeMath.eeFundamentals import vRJunct, vDivExpr


opamp_nfb_v_out_expr = simplify( v_p + (v_p - v_m) * R_nfb/R_v_m )
opamp_nfb_v_out_eq = Eq(v_out, opamp_nfb_v_out_expr)

with evaluate(False):
  opamp_nfb_v_out_eq = Eq(v_out, v_p + (v_p - v_m) * R_nfb/R_v_m)

opamp_v_p_eq_v_m = Eq(v_p, v_m)

# Below link is the same as above but based on link this without R3 & R4
# https://www.ti.com/lit/an/sboa262a/sboa262a.pdf?ts=1693938343937&ref_url=https%253A%252F%252Fwww.google.com%252F
with evaluate(False):
  opamp_noninv_v_gain_eq = Eq(v_gain, (R_nfb + R_v_m)/R_v_m)
  opamp_noninv_v_offset_eq = Eq(v_offset, -V_nREF * (R_nfb/R_v_m))
  opamp_noninv_v_out_of_offset_gain_eq = Eq(v_out, v_p * ( v_gain ) + v_offset)
  opamp_noninv_v_out_eq = opamp_noninv_v_out_of_offset_gain_eq.subs({
    v_gain: opamp_noninv_v_gain_eq.rhs,
    v_offset: opamp_noninv_v_offset_eq.rhs
  })

def opampNoninvGainAndOffset(sym_subs: dict(V_REF=None, R_v_m=None, R_nfb=None) ):
  return opamp_noninv_v_gain_eq.rhs.subs(sym_subs), opamp_noninv_v_offset_eq.rhs.subs(sym_subs)



def opampNfbBuilder(v_m_count=1, v_p_count=1, as_tuple=False, quiet=False):
  ''' opampNfbBuilder builds a set of equalities for a an op-amp with negative feedback by
  taking two numbers: 
    v_p_count is the number of voltages to non-inverting input resistor pairs and 
    v_m_count is the number of voltages to inverting input resistor pairs.

  FOR HELP:
    >>> opampNfbBuilder('help') # prints opampNfbBuilder.__doc__
  OR
    help_doc = opampNfbBuilder('__doc__') # returns __doc__
  
  QUICK USAGE EXAMPLE:
    1. recommended usage: create symbols opampNfbBuilder would create before calling:

      v_m1, R_m1, v_m2, R_m2 = symbs('v_m1, R_m1, v_m2, R_m2')
      # v_p1, R_p1, v_p2, R_p2 = symbs('v_p1, R_p1, v_p2, R_p2') # (if we used v_p_count=2)
      v_out_eq = opampNfbBuilder(v_m_count=2)[v_out] # same as opampNfbBuilder(v_m_count=2)

    you can also have multiple non-inverting input: 
      
      opampNfbBuilder(2, 2) # same as opampNfbBuilder(v_m_count=2, v_p_count=2)

    2. not-as recommended: have opampNfbBuilder create symbols:

      oa = opampNfbBuilder(2)
      print(oa['new_symbols']) # shows dictionary of var_name: symbol_obj
      v_m1 = oa['created']['v_m1']
      R_m1 = oa['created']['R_m1']
      v_m2 = oa['created']['v_m2']
      R_m2 = oa['created']['R_m2']

      v_out_eq = oa[v_out]
  
  opampNfbBuilder, by default, returns a dictionary in the form:
  {
    v_out: Eq(v_out, <expr>),
    v_p:   Eq(v_p, <expr>),
    v_m:   Eq(v_m, <expr>),
    'created':  { 'v_p{i}': v_p{i}, R_p{i}': R_p{i}, ..., 
                  'v_m{i}': v_m{i}, R_m{i}': R_m{i}, ..., 
                  # (if not already declared with symbs())
                }, 
    'global': {
      'v_out': v_out, 'v_p': v_p, 'v_m': v_m, 'R_nfb': R_nfb
      # 'global' also has symbs shown in 'created' above if already declared
      } 
  }

  Since this function might creates new symbols, the above dictionary catalogs them such that you can 
  create variable to reference them. '''

  if v_m_count == 'help':
    print(opampNfbBuilder.__doc__)
    return
  elif v_m_count == '__doc__':
    return opampNfbBuilder.__doc__

  v_p, v_p_was_new     = getSymb(f'v_p', create='inform', about=f"opamp's non-inverting input voltage", **real_finite)
  v_m, v_m_was_new     = getSymb(f'v_m', create='inform', about=f"opamp's inverting input voltage", **real_finite)
  v_out, v_out_was_new = getSymb(f'v_out', create='inform', about=f"opamp's output voltage", **real_finite)
  R_nfb, R_nfb_was_new = getSymb(f'R_nfb', create='inform', about=f"opamp's output voltage", **real_nonneg)

  vp_Rp_pairs = []
  vm_Rm_pairs = [(v_out, R_nfb)]

  r = {
    v_out: None,
    v_p: None, 
    v_m: None,
    'created': {},
    'global': {} 
  }
  def registerSymb(*symb_name_wasnew):
    for symb, name, was_new in symb_name_wasnew:
      if was_new:
        if not quiet: print(f'{name} symbol was created')
        r['created'][name] = symb
      else:
        if not quiet: print(f'{name} symbol was global')
        r['global'][name] = symb

  registerSymb((v_p,'v_p',v_p_was_new), (v_m,'v_m',v_m_was_new), (v_out,'v_out',v_out_was_new), (R_nfb,'R_nfb',R_nfb_was_new))
  
  if v_p_count == 1: r[v_p] = simplify(Eq(v_p, v_p))

  else:
    for i in range(1, v_p_count+1) :
      v_symb, v_was_new = getSymb(f'v_p{i}', create='inform', about=f'v_p{i} (this symbol) -> R_p{i} -> v_p (opamp input)', **real_finite)
      r_symb, r_was_new = getSymb(f'R_p{i}', create='inform', about=f'v_p{i} -> R_p{i} (this symbol) -> v_p (opamp input)', **real_nonneg)
      registerSymb((v_symb, f'v_p{i}', v_was_new), (r_symb, f'R_p{i}', r_was_new))
      vp_Rp_pairs.append( (v_symb, r_symb) )

    r[v_p] = simplify(Eq(v_p, vRJunct( *vp_Rp_pairs ) ))
  
  for i in range(1, v_m_count+1) :
    v_symb, v_was_new = getSymb(f'v_m{i}', create='inform', about=f'v_m{i} (this symbol) -> R_m{i} -> v_m (opamp input)', **real_finite)
    r_symb, r_was_new = getSymb(f'R_m{i}', create='inform', about=f'v_m{i} -> R_m{i} (this symbol) -> v_m (opamp input)',  **real_nonneg)
    
    vm_Rm_pairs.append( (v_symb, r_symb) )
    registerSymb((v_symb, f'v_m{i}', v_was_new), (r_symb, f'R_m{i}', r_was_new))
  
  r[v_m] = simplify(Eq(v_m, vRJunct( *vm_Rm_pairs ) ))

  v_out_solved = sp.solve([Eq(v_p, v_m), r[v_m], r[v_p]], v_out)
  if isinstance(v_out_solved, dict) :
    for k in v_out_solved: r[k] = Eq(k, v_out_solved[k])
  else: r[v_out] = v_out_solved

  return (r[v_out], r[v_p], r[v_m], r['created'], r['global']) if as_tuple else r


# vDivExpr(v_p, R_v_p, R_pREF, V_pREF)
# v_p
# R_v_p
# V_pREF
# R_pREF

# v_m
# R_v_m
# R_nfb

# Below is this circuit, exactly: https://www.ti.com/lit/an/sboa262a/sboa262a.pdf?ts=1693938343937&ref_url=https%253A%252F%252Fwww.google.com%252F
# Common usage: difference/differencial amp (where the R_nfb/R_v_m == R_pREF/R_v_p so is v_p - v_m):
# https://en.wikipedia.org/wiki/Operational_amplifier_applications#Differential_amplifier_(difference_amplifier)
with evaluate(False):
  opamp_4R_v_p_gain_eq = Eq(v_p_gain, ( (R_nfb+R_v_m) * R_pREF )/( (R_pREF+R_v_p) * R_v_m ) )
  opamp_4R_v_m_gain_eq = Eq(v_m_gain, R_nfb/R_v_m )
  opamp_4R_v_out_eq = Eq(v_out, v_p * (opamp_4R_v_p_gain_eq.rhs) - v_m * (opamp_4R_v_m_gain_eq.rhs) )

# Below is a variant of the above, adding a non-zero voltage, V_pREF,  at R_pREF
with evaluate(False):
  # opamp_4R_V_pREF_v_out_eq = opamp_nfb_v_out_eq.rhs.subs()
  # opamp_4R_V_pREF_v_out_eq = Eq(v_out, ((vDivExpr(v_p, R_v_p, R_pREF, V_pREF))) - v_m * (R_nfb/R_v_m))
  opamp_4R_V_pREF_v_out_eq = Eq(
    v_out,
    opamp_noninv_v_out_eq.rhs.subs({
      V_nREF: v_m, v_p: vDivExpr(v_p, R_v_p, R_pREF, V_pREF)
    })
  )
  

class OpampConfig:
  def __init__(self, v_p, v_m, subs={}, in_symb=v_pIn, out_symb=v_out):
    '''
    :param v_p: an expression, symbol or value representing the voltage at the non-inverting input pin. Has get/set
    :param v_m: an expression, symbol or value representing the voltage at the inverting input pin. Has get/set
    :param subs: a dictionary of symbol, value pairs always substituted into v_p and/or v_m. Has get/set
    '''
    self._v_p = v_p
    self._v_m = v_m
    self._eq = Eq(self._v_p, self._v_m)
    self._subs = subs.copy()
    self._in_symb = in_symb
    self._out_symb = out_symb
    
  def solve(self, *solve_for, subs={}):
    '''
    :param solve_for: any number of symbols to be solved for.
    :param subs: a dictionary of symbol, value pairs which are temporarily merged with self.subs in call to solve.
    '''
    # from collections.abc import Iterable
    # if len(solve_for) == 1:
    #   solve_for = solve_for[0] if isinstance(solve_for[0], Iterable) else [solve_for[0]]
    subbed_eq = self._eq.subs(self._subs | subs)

    if len(solve_for) == 1 and solve_for[0] == 'all':
      solve_for = tuple(subbed_eq.free_symbols)
    else:
      if len(solve_for) == 0: solve_for = (self._out_symb,) # default to solve for output voltage
    
    sol = sp.solve(subbed_eq, solve_for)

    if len(sol) == 1: return sol[0]
    else: return sol

  def solveForCoords(self, vin1_vout1, vin2_vout2, subs={}):
    '''solve for a two coordinates provided as two ordered sequences where the 
    first element of each is the input voltage and the second is the desired output voltage.
    NOTE: this requires value symbols set for self.in_symb and self.out_symb.
    the return will the the solution for all free symbols that satifies both requirements,
    that is, the output voltages will be as desired with the given input voltages'''
    if len(vin1_vout1) != 2:
      raise ValueError(f'vin1_vout1 must have 2 elements ({len(vin1_vout1)} given)')
    if len(vin2_vout2) != 2:
      raise ValueError(f'vin2_vout2 must have 2 elements ({len(vin2_vout2)} given)')
    vin1, vout1 = vin1_vout1
    vin2, vout2 = vin2_vout2

    vout1_expr = self.solve(self._out_symb, subs={self._in_symb: vin1, **subs})
    vout2_expr = self.solve(self._out_symb, subs={self._in_symb: vin2, **subs})
    req1_eq = Eq(vout1, vout1_expr)
    req2_eq = Eq(vout2, vout2_expr)

    free_symbols = req1_eq.free_symbols.union(req2_eq.free_symbols)
    return sp.solve([req1_eq, req2_eq], list(free_symbols))


  def gainAndZeroOffset(self, subs={}, offset_at=0):
    subbed = self._eq.subs(self._subs | subs)
    
    # free_symbols = subbed.free_symbols
    # if self._in_symb in free_symbols: free_symbols.remove(self._in_symb)
    # else: raise ValueError(f'in_symb (set to {self._in_symb}) was no in opamp equation')
    # if self._out_symb in free_symbols: free_symbols.remove(self._out_symb)
    # else: raise ValueError(f'out_symb (set to {self._out_symb}) was no in opamp equation')
    # if len(free_symbols) != 0: raise ValueError(f'The following symbols need to be subbed: {free_symbols}')

    out_with_zero_in = self.solve(self._out_symb, subs={self._in_symb: 0, **subs})
    out_with_one_in = self.solve(self._out_symb, subs={self._in_symb: 1, **subs})
    
    if offset_at == 0: offset = out_with_zero_in
    else: offset = self.solve(self._out_symb, subs={self._in_symb: offset_at, **subs})
      
    return { 'gain': out_with_one_in - out_with_zero_in, 'offset': offset }
  
  @property
  def eq(self): return self._eq

  @property
  def v_p(self): return self._v_p

  @property
  def free_symbols(self): return self._eq.subs(self._subs).free_symbols

  @v_p.setter
  def v_p(self, v_p):
    ''':param v_p: an expression, symbol or value representing the voltage at the non-inverting input pin.'''
    self._v_p = v_p 
    self._eq = Eq(self._v_p, self._v_m) 
  
  @property
  def v_m(self): return self._v_m

  @v_m.setter
  def v_m(self, v_m):
    ''':param v_m: an expression, symbol or value representing the voltage at the inverting input pin.
    :param subs: a dictionary of symbol, value pairs always substituted into either/both of the previous.'''
    self._v_m = v_m 
    self._eq = Eq(self._v_p, self._v_m) 
    
  @property
  def subs(self): return self._subs

  @subs.setter
  def subs(self, subs):
    ''':param subs: a dictionary of symbol, value pairs always substituted into v_p and/or v_m'''
    self._subs = subs.copy()

  def subsAdd(self, subs):
    ''':param subs: a dictionary of symbol, value pairs always substituted into v_p and/or v_m'''
    self._subs |= subs

  def unsub(self, *symbols):
    ''':param symbols: any number of symbols to be removed from subs and no longer substituted'''
    for symb in symbols: self._subs.pop(symb, None)
  
  @property
  def in_symb(self): return self._in_symb

  @in_symb.setter
  def v_p(self, in_symb):
    ''':param in_symb: the symbol or value representing the input voltage to the opamp or opamp config'''
    self._in_symb = in_symb 

  @property
  def out_symb(self): return self._out_symb
  

  @out_symb.setter
  def out_symb(self, out_symb):
    ''':param out_symb: the symbol or value representing the input voltage from the opamp'''
    self._out_symb = out_symb 
