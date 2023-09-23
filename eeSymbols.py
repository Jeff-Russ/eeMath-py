
from sympy import symbols, Symbol
from eeMath.general_helpers import func_attr, printlToStr, strReplaceEach


# https://stackoverflow.com/a/1355444


# NOTE: I put all symbols in here and then import from other files. Why?
# Because I had multiple files using the same symbols and that's a problem

# Naming conventions (enforced if symbs is used intead of symbols/Symbol)
# NO CHARACTER THAT DON'T HAVE AN OBVIOUS WAY OF INCLUDING IN A VALID VARIABLE NAME
#    So no V_+ or V+. Not only do they not work as varnames, they don't work in QtConsole's LaTeX
# not counting subscripts:
#    Lowercase is for signals and other things that change in value IRL 
#    Uppercase is for voltage supply/refs, component values and things that don't change IRL
# in subcripts:
#    p is for postive, m is for negative. For example:
#        V_p and V_m are postive and negative rails. v_p and v_m are opamp/ota inputs
#    feedback is f
#        If it's obvious whether the feedback is postive or negative, just use R_fb, for example
#        For explicit polarity, examples: R_nfb and R_pfb. 
# double subscript are fine in these cases:
#    R_v_m is a resistor in series to an op-amps negative input (v_m). R_v_p for the other input
# voltage and current control:
#   small v_ or i_ then subscript is 'c' or 'v', each possibly followed by 'in' or 'out'
#   EXCEPTION v_c and i_c are reserved for BJT collector voltage/current: use *_cout or *_cin

########## SYMBOL HELPERS #########################################################################

from re import split as re_split
from collections import OrderedDict


@func_attr(latexify='auto', force_subscript=True,force_subscript_warning=False, hist=OrderedDict(), subs={})
def symbs(string_names, *, replace_each={}, latexify=None, force_subscript=None, force_subscript_warning=None, hist_attrs={}, cls=Symbol, **kwargs):
  '''
  Use this in place of symbols/Symbol to make Symbol object since this function let you pass in the
  string representations that are the same at the variable names, automatically converting them to latex
  string before passing them along to symbols(). In the provided string, commas or space can be used 
  as delimiters (a comma + any number of spaces OR any number of spaces), so you can just cut and paste
  to or from what you are asssigning to.
  NOTE: if any provided_name passed is not a valid identifier, no processing of it will be done as it is assumed
  the caller is passing LaTeX rather than a variable provided_name. This is useful for symbol names that have
  non-ascii characters such as /alpha, which would have to be an ascii 'a' in python.
  TODO: With symbs being use for all symbol declarations
  1) we can add a global registry mapping symbol str reps <-> variable names (as passed to symbs)
  2) Having symbs check this registry and warn/block redeclarations as per 2 new symbs props
  3) Make laTeXToPy func which users can pass latex to in order to see python that would define it. 
  # NOTE: requires func_attr, printlToStr, strReplaceEach
  '''
  # test with: symbs('R R1 R2 Rvb R_v_m R_v_mf')
  # should error: symbs('R1 R1')
  if latexify is not None:
    symbs.latexify = latexify
    if force_subscript is not None: symbs.force_subscript = force_subscript
    if force_subscript_warning is not None: symbs.force_subscript_warning = force_subscript_warning
  
  if not symbs.latexify:
    if force_subscript is not None: 
      print(f'Warning: ignoring force_subscript={force_subscript} because symb.latexify={symbs.latexify}')
    if force_subscript_warning is not None:
      print(f'Warning: ignoring force_subscript_warning={force_subscript_warning} because symb.latexify={symbs.latexify}')

  kwargs['cls'] = cls


  symbnames =  [x for x in re_split(',[ ]*|[ ]+', string_names) if x.strip()] # the list compr. is to remove all-whitespace els

  if not isinstance(symbs.hist, OrderedDict): symbs.hist = OrderedDict()

  # hist_update = OrderedDict()
  hist_update_arr = []

  hist_attrs['about'] = str(hist_attrs['about']) if 'about' in hist_attrs else '' # about:str is a required attribute for symbs

  if symbs.latexify:
    varnames = symbnames
    for i in range(len(varnames)):
      provided_name = varnames[i]
      if symbs.latexify != 'auto' or varnames[i].isidentifier():
        symbnames[i] = varnameToLaTeX(varnames[i], replace_each)
      elif replace_each: symbnames[i] = strReplaceEach(varnames[i], replace_each)
      # else: we already have symbnames[i] so leave it alone
      # hist_update[symbnames[i]] = {'provided_name': provided_name, 'sympy_name': symbnames[i], **hist_attrs, **kwargs}
      hist_update_arr.append( {'provided_name': provided_name, 'sympy_name': symbnames[i], **hist_attrs, **kwargs} )
  else:
    for i in range(len(symbnames)):
      provided_name = symbnames[i]
      if replace_each: symbnames[i] = strReplaceEach(symbnames[i], replace_each)
      # hist_update[symbnames[i]] = {'provided_name': provided_name, 'sympy_name': symbnames[i], **hist_attrs, **kwargs}
      hist_update_arr.append( {'provided_name': provided_name, 'sympy_name': symbnames[i], **hist_attrs, **kwargs} )

  dups =  {x for x in symbnames if symbnames.count(x) > 1}
  if dups: raise ValueError(printlToStr('Duplicate symbol string representations:', *dups))
  symbnames = ' '.join(symbnames)
  symbs_tuple = symbols(symbnames, **kwargs)

  hist_update = OrderedDict()
  if type(symbs_tuple) == tuple:
    for i in range(len(symbs_tuple)):
      hist_update[symbs_tuple[i]] = hist_update_arr[i]
  elif len(hist_update_arr) == 1:
    hist_update[symbs_tuple] = hist_update_arr[0]
  

  # rather than modifying, delete any entries and re-add to bump their position up
  symbs.hist = OrderedDict({k: symbs.hist[k] for k in symbs.hist if k not in hist_update})
  symbs.hist.update(hist_update)

  # Append symbs.subs with new keys/values where both for each is the symbol to be returned.
  # Unless specified otherwise later on, we set each to itself which disables substitions with subs()

  if isinstance(symbs_tuple, tuple):
    symbs.subs = {**symbs.subs, **{sym:sym for sym in symbs_tuple} }
  elif isinstance(symbs_tuple, Symbol): symbs.subs[symbs_tuple] = symbs_tuple

  return symbs_tuple



def getSymb(provided_name, find_all=False, recent=True, details=False, create=False, **kwargs):
  '''This might be a temporary function until we fix symbs to return previously 
  declared symbols rather than make duplicates and fix symbs.hist to index by
  provided name rather than by symbol object. 

  But for the time being, you can use this function to search and/or create
  symbols by their name as string in the following ways (you can optionally
  pass additional kwargs that will be sent to symbs if declaration happens):

  1A. get the most recent symbol, CREATING it if never declared with symbs:
    v_symb = getSymb('v_symb', create=True) # never returns None

  2A. get the least recent symbol, CREATING it if never declared with symbs:
    v_symb = getSymb('v_symb', recent=False, create=True) # never returns None

  You can optionally tell getSymb to tell you it was just created for you by 
  passing `create='inform'`, which returns two items, the symbol one plus
  a boolean which is True if the symbol was just created: 

  1B. v_symb, was_new = getSymb('v_symb', create='inform') 
  2B. v_symb, was_new = getSymb('v_symb', recent=False, create='inform') 

  3a. find the most recent symbol to be declared with symbs:
    v_symb = getSymb('v_symb') # may return None

  4a. find the least recent symbol to be declared with symbs :
    v_symb = getSymb('v_symb', recent=False) # may return None

  5a. get ALL symbols declared with symbs with a given name (most recent first)
    symbs_tuple = getSymb('v_symb', find_all=True) # may be empty

  6a. get ALL symbols declared with symbs with a given name (least recent first)
    symbs_tuple = getSymb('v_symb', find_all=True, recent=False) # may be empty
  
  You can also choose to get the sub-dictionary in the symbs.hist dictionary
    rather than the symbol itself by passing details=True. (THIS OPTION IS
    RESULTS IN create=True BEING IGNORED.):

  3b. v_symb_dict = getSymb('v_symb', details=True) # like 1a. 
  4b...6b are all possible as well, by adding `details=True` to 4a...6b
  '''
  if find_all: results = []
  hist_items = reversed(symbs.hist.items()) if recent else symbs.hist.items()
  
  for symb, d in hist_items:
    if d['provided_name'] == provided_name:
      thing = d if details else symb
      if find_all: results.append(thing)
      elif create == 'inform': return thing, False
      else: return thing
  
  if find_all: return tuple(results)
  elif create:
    if create == 'inform':
      return symbs(provided_name, **kwargs), True
    else:
      return symbs(provided_name, **kwargs)
  else: return None



# def allSymbs(symb=None, show=[]):
#   '''
#   show
#     if passed as an array of string(s), each element should be a key that exists in a symbs.hist
#     if passed as an array of one or two integers(s), with the first or second optionally being an 
#       empty string, these are used as the subscript to accessing the symbs.hist OrderedDict elements
#       by the sequence the symbols where created. For example: 
#         allSymbs(show=[-1]) # shows the last symbol added
    
#   '''
#   if not show:
#     if symb is None: return symbs.hist
#     else: return symbs.hist[str(symb)]
#   elif symb is None: 



def varnameToLaTeX(provided_name, replace_each={}): # helper for symbs and user
  # if not provided_name.isidentifier() : return provided_name
  # NOTE: requires: strReplaceEach
  if replace_each:
    provided_name = strReplaceEach(provided_name, replace_each)
  subscripts = provided_name.split('_')
  letter = subscripts[0]
  subscripts = subscripts[1:]

  if len(letter) > 1 and letter[0] != '\\':
    if symbs.force_subscript:
      subscripts.insert(0, letter[1:])
      letter = letter[0]
      if symbs.force_subscript_warning:
        print(f'Warning: subscript forcibly to applied to {provided_name} after {letter} because symbs.force_subscript==True')
        print(f'         You can suppress this warning with symbs.force_subscript_warning==False')

  if len(subscripts):
    for ss_i, ss in enumerate(subscripts):
      if len(ss) > 1 : subscripts[ss_i] = '{'+ss+'}'

    subscripts = '_'.join(subscripts)
    return '{'+letter+'_'+subscripts+'}'
  else:
    return provided_name
  

# helpers for passing to symbols/Symbol/symbs 
real_nonneg = {'real':True, 'nonnegative':True} # usage: symbols|symbs(st, **real_nonneg)
real_finite = {'real':True, 'finite':True} # usage: symbols|symbs(st, **real_finite)

########## GLOBAL SYMBOL DECLARATIONS #############################################################

n_bits, n_bit, n_bin = symbs('n_bits, n_bit, n_bin',  about='binary', **real_finite)

p_cnt = symbs('p_cnt',  about='percent as ratio 0..1', **real_finite)

# Diodes and Other Semiconductors
v_D = symbs('v_D', about="voltage across diode", **real_finite)
i_D = symbs('i_D', about="current through diode", **real_finite)
n_D = symbs('n_D', about="deality factor of diode (typically 1-2 - 1N4148 is 1.906)", **real_finite)


# thermal
t_Kelvin, t_Celsius, t_Fahr = symbs('t_Kelvin, t_Celsius, t_Fahr', about='temperatures with units', **real_nonneg)

V_T = symbs('V_T',  about='Thermal Voltage (BJT, etc)',  **real_nonneg)


# BJT 

# alpha, beta = symbs(r'{\alpha} {\beta}', **real_nonneg)
alpha, beta = symbs('alpha, beta', replace_each={'al': r'\al', 'b': r'\b'},  about='BJT gain characteristics', **real_nonneg)
a_F  = symbs(r'{\alpha_F}', **real_nonneg)

# BJT large signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Large-signal_models):
I_B, I_C, I_E, V_BE, V_CE, V_CB = symbs('I_B, I_C, I_E, V_BE, V_CE, V_CB', about='BJT large signal model', **real_finite)


# BJT small signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Small-signal_models):
i_B, i_C, i_E, v_BE, v_CE, v_CB = symbs('i_B, i_C, i_E, v_BE, v_CE, v_CB', about='BJT small signal model', **real_finite)



I_ES  = symbs('I_ES', about='BJT (reverse) saturation current of the B-E diode (on the order of e-15 (fA) to e-12 (pA))', **real_finite)
I_S  = symbs('I_S', about='Diode or BJT (reverse) saturation current (BJT: on the order of e-15 (fA) to e-12 (pA), 1N4148: 4.352e-9)', **real_finite)
I_S0 = symbs('I_S0',  about='BJT (active mode) I_S0 = I_S when v_CE is 0', **real_nonneg)
beta_0 = symbs('beta_0', replace_each={'b': r'\b'},  about='BJT (active mode) forward common-emitter current gain at zero bias, beta_0 = beta when v_CE is 0', **real_nonneg)

V_A  = symbs('V_A', about='BJT Early voltage (typically 15–150V; smaller for smaller devices)', **real_nonneg)

R_B, R_C, R_E  = symbs('R_B, R_C, R_E', about='BJT with resistor', **real_nonneg) # With resistor

v_RB, v_RC, v_RE  = symbs('v_RB, v_RC, v_RE', about='BJT involving resistor (small signal model)', **real_finite) # Involving Resistor

# differencial pairs (for op-amp, OTA, etc)
v_B1, v_B2 = symbs('v_B1, v_B2', about='BJT differential pair (ending 2 is other side of pair)', **real_finite) # Involving Resistor
v_diff, i_tail = symbs('v_diff, i_tail', about='BJT differential pair', **real_finite) # Involving Resistor
i_Ep, i_Em, i_Bp, i_Bm, i_Cp, i_Cm = symbs('i_Ep, i_Em, i_Bp, i_Bm, i_Cp, i_Cm', about='BJT differential pair currents (m=inverting, p=non-invert)', **real_finite) # Involving Resistor


# https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch8-2.pdf


# Transconductance
g_m = symbs('g_m',  about='Transconductance',  **real_nonneg)

# generic values
V, I = symbs('V I', about='generic values', **real_finite)
R, P_watts = symbs('R P_watts', about='generic values', **real_nonneg)


t, t_s, t_ms, t_us, t_ns, t_ps = symbs('t, t_s, t_ms, t_us, t_ns, t_ps', about='time variables', **real_finite)
vps = symbs('vps', about='volts per second', **real_finite)
v_0, v_t, v_now, v_then = symbs('v_0, v_t, v_now, v_then', about='voltages over time (small signal)', **real_finite)
v_C, v_D, v_R = symbs('v_C, v_D, v_R', about='voltages across components (small signal)', **real_finite)
i_C, i_D, i_R = symbs('i_C, i_D, i_R', about='currents across components (small signal)', **real_finite)

# generic components 
R_in, R_out, R_A, R_X, R_F, R_REF, R_pREF, R_nREF = symbs('R_in, R_out, R_A, R_X, R_F, R_REF, R_pREF, R_nREF', about='generic resistors', **real_nonneg)
r_in, r_out, r_x, = symbs('r_in, r_out, r_x', about='variable resistors or resistance variables', **real_nonneg)
R, R1, R2, R3, R4, R5, R6, Rll, R_IN, R_in, R_GND, R_pull = symbs('R, R1, R2, R3, R4, R5, R6, Rll, R_IN, R_in, R_GND, R_pull', about='generic resistors', **real_nonneg)
C, C1, C2, C3, C4, C5 = symbs('C, C1, C2, C3, C4, C5', about='generic capacitors', **real_nonneg)
D, D1, D2, D3, D4 = symbs('D, D1, D2, D3, D4 ', about='generic diodes', **real_nonneg)

# generic voltages
V_REF, V_pREF, V_nREF, V_pull = symbs('V_REF, V_pREF, V_nREF, V_pull', about='generic voltages', **real_finite)


tau1, n_tau = symbs(r'{\tau_1}, {n_{\tau}}', about='time constants', **real_finite)


# for ota.py and opamp.py:
v_offset, v_gain, v_p_gain, v_m_gain = symbs('v_offset, v_gain, v_p_gain, v_m_gain', about='generic amplifier parameter', **real_finite)
v_p, v_m, i_abc, i_out, v_out = symbs('v_p, v_m, i_abc, i_out, v_out', about='states at chip pins (not via resistors)', **real_finite)
v_in, v_mIn, v_pIn = symbs('v_in, v_mIn, v_pIn', about='voltage input to chip config, not chip pins (i.e. via resistors)', **real_finite )
R_v_m, R_fb, R_nfb, R_pfb, R_out, R_v_p = symbs('R_v_m, R_fb R_nfb, R_pfb, R_out, R_v_p', **real_nonneg)


i_out = symbs('i_out', **real_finite)

# Note frequency:
n_midi, f_Hz = symbs('n_midi, f_Hz', **real_finite)



# control voltages and currents:
v_cin, i_cout = symbs('v_cin, i_cout', **real_finite)


# I'm considering adding an .about attribute to the symbol class to 
# store a string description of a given symbol. 
# https://medium.com/@nschairer/python-dynamic-class-attributes-24a89df8da7d

# I'm also considering having some global dictionary to act as directory so the user
#  can list out the symbols available, particularly those created within this lib

# But in any case, here I'm make some quicker to use meta-constructor functions for
# making symbols, given particular restrictions of components, V/I sources and v/i signals.


# w

# def newResistors():



    