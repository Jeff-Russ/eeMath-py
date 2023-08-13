
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
#   EXCEPTION v_c and i_c are reserved for BTJ collector voltage/current: use *_cout or *_cin

########## SYMBOL HELPERS #########################################################################

from re import split as re_split
from collections import OrderedDict


@func_attr(latexify='auto', force_subscript=True,force_subscript_warning=False, hist=OrderedDict())
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
  # test with: symbs('R R1 R_2 Rvb R_v_m R_v_mf')
  # should error: symbs('R1 R_1')
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
  hist_update = OrderedDict()
  hist_attrs['about'] = str(hist_attrs['about']) if 'about' in hist_attrs else '' # about:str is a required attribute for symbs

  if symbs.latexify:
    varnames = symbnames
    for i in range(len(varnames)):
      if symbs.latexify != 'auto' or varnames[i].isidentifier():
        symbnames[i] = varnameToLaTeX(varnames[i], replace_each)
      elif replace_each: symbnames[i] = strReplaceEach(varnames[i], replace_each)
      # else: we already have symbnames[i] so leave it alone
      hist_update[symbnames[i]] = {'provided_name': varnames[i], 'sympy_name': symbnames[i], **hist_attrs, **kwargs}
  else:
    for i in range(len(symbnames)):
      if replace_each: symbnames[i] = strReplaceEach(symbnames[i], replace_each)
      hist_update[symbnames[i]] = {'provided_name': symbnames[i], 'sympy_name': symbnames[i], **hist_attrs, **kwargs}

  dups =  {x for x in symbnames if symbnames.count(x) > 1}
  if dups: raise ValueError(printlToStr('Duplicate symbol string representations:', *dups))
  symbnames = ' '.join(symbnames)
  symbs_tuple = symbols(symbnames, **kwargs)

  # rather than modifying, delete any entries and re-add to bump their position up
  symbs.hist = OrderedDict({k: symbs.hist[k] for k in symbs.hist if k not in hist_update})
  symbs.hist.update(hist_update)
  
  return symbs_tuple

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

# eeOperators
V, I = symbols('V I', **real_finite)
R, P_watts = symbols('R P_watts', **real_nonneg)

# generic components 
R, R_1, R_2, R_3, R_4, R_5, R_6, R_IN, R_in, R_GND, R_pull = symbs('R, R_1, R_2, R_3, R_4, R_5, R_6, R_IN, R_in, R_GND, R_pull', about='generic resistors', **real_nonneg)
C, C_1, C_2, C_3, C_4, C_5 = symbs('C, C_1, C_2, C_3, C_4, C_5', about='generic capacitors', **real_nonneg)
D, D_1, D_2, D_3, D_4 = symbs('D, D_1, D_2, D_3, D_4 ', about='generic diodes', **real_nonneg)

# generic voltages
V_REF, V_pREF, V_nREF, V_pull = symbs('V_REF, V_pREF, V_nREF, V_pull', about='generic voltages', **real_finite)

tau_1, tau_2, tau_3, tau_4, tau_5, tau_6, tau_7 = symbs('\tau_1, \tau_2, \tau_3, \tau_4, \tau_5, \tau_6, \tau_7', about='time constants', **real_finite)

# for ota.py and opamp.py:
v_p, v_m, i_abc, i_out, v_out = symbs('v_p, v_m, i_abc, i_out, v_out', about='states at chip pins (not via resistors)', **real_finite)
v_in, v_mIn, v_pIn = symbs('v_in, v_mIn, v_pIn', about='voltage input to chip config, not chip pins (i.e. via resistors)', **real_finite )
R_v_m, R_fb, R_nfb, R_pfb, R_out = symbs('R_v_m, R_fb R_nfb, R_pfb, R_out', **real_nonneg)


# Note frequency:
n_midi, f_Hz = symbs('n_midi, f_Hz', **real_finite)


# TODO: finish BTJ 


# BTJ Gain Characteristics:
# alpha, beta = symbs(r'{\alpha} {\beta}', **real_nonneg)
alpha, beta = symbs('alpha, beta', replace_each={'al': r'\al', 'b': r'\b'}, **real_nonneg)

# BJT large signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Large-signal_models):
I_B, I_C, I_E, I_ES, V_BE, V_CE, V_CB = symbs('I_B, I_C, I_E, I_ES, V_BE, V_CE, V_CB', **real_finite)
V_T, a_F  = symbs(r'V_T, {\alpha_F}', **real_nonneg)

R_B, R_C, R_E  = symbs('R_B, R_C, R_E', **real_nonneg) # With resistor
V_R_B, V_R_C, V_R_E  = symbs('V_R_B, V_R_C, V_R_', **real_nonneg) # Involving Resistor

# BJT small signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Small-signal_models):
i_b, i_c, i_e = symbs('i_b, i_c, i_e', **real_finite)

# https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch8-2.pdf


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



    