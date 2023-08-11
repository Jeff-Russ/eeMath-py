import sympy as sp

from eeMath.eeSymbols import v_p, v_p, v_m, v_out, R_v_m, R_nfb, R_pfb, v_in, i_out, v_pIn


opamp_nfb_v_out_expr = sp.simplify( v_p + (v_p - v_m) * R_nfb/R_v_m )
opamp_nfb_v_out_eq = sp.Eq(v_out, opamp_nfb_v_out_expr)

opamp_v_p_eq_v_m = sp.Eq(v_p, v_m)

class OpampConfig:
  def __init__(self, v_p, v_m, subs={}, in_symb=v_pIn, out_symb=v_out):
    '''
    :param v_p: an expression, symbol or value representing the voltage at the non-inverting input pin. Has get/set
    :param v_m: an expression, symbol or value representing the voltage at the inverting input pin. Has get/set
    :param subs: a dictionary of symbol, value pairs always substituted into v_p and/or v_m. Has get/set
    '''
    self._v_p = v_p
    self._v_m = v_m
    self._eq = sp.Eq(self._v_p, self._v_m)
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
    req1_eq = sp.Eq(vout1, vout1_expr)
    req2_eq = sp.Eq(vout2, vout2_expr)

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
    self._eq = sp.Eq(self._v_p, self._v_m) 
  
  @property
  def v_m(self): return self._v_m

  @v_m.setter
  def v_m(self, v_m):
    ''':param v_m: an expression, symbol or value representing the voltage at the inverting input pin.
    :param subs: a dictionary of symbol, value pairs always substituted into either/both of the previous.'''
    self._v_m = v_m 
    self._eq = sp.Eq(self._v_p, self._v_m) 
    
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
