
from sympy import symbols, Symbol
from eeMath.general_helpers import func_attr, printlToStr


# NOTE: I put all symbols in here and then import from other files. Why?
# Because I had multiple files using the same symbols and that's a problem

# Naming conventions (enforced if latexSymbs is used intead of symbols/Symbol)
# NO CHARACTER THAT DON'T HAVE AN OBVIOUS WAY OF INCLUDING IN A VALID VARIABLE NAME
#    So no V_+ or V+. Not only do they not work as varnames, they don't work in QtConsole's LaTeX
# not counting subscripts:
#    Lowercase is for signals and other things that change in value IRL 
#    Uppercase is for voltage supply/refs, component values and things that don't change IRL
# in subcripts:
#    p is for postive, n is for negative. For example:
#        V_p and V_n are postive and negative rails. v_p and v_n are opamp/ota inputs
#    feedback is f
#        If it's obvious whether the feedback is postive or negative, just use R_f, for example
#        For explicit polarity, examples: R_nf and R_pf. They look like C vals but those would be
#           nF and pF. Also, if we did R_fn, that clearly looks like a function.
# double subscript are fine in these cases:
#    R_v_n is a resistor in series to an op-amps negative input (v_n). R_v_p for the other input
# voltage and current control:
#   small v_ or i_ then subscript is 'c' or 'v', each possibly followed by 'in' or 'out'
#   EXCEPTION v_c and i_c are reserved for BTJ collector voltage/current: use *_cout or *_cin

########## SYMBOL HELPERS #########################################################################

from re import split as re_split
from collections import OrderedDict

@func_attr(force_subscript=True,force_subscript_warning=True, hist=OrderedDict())
def latexSymbs(string_names, *, force_subscript=None, force_subscript_warning=None, cls=Symbol, **kwargs):
  '''
  Use this in place of symbols/Symbol to make Symbol object since this function let you pass in the
  string representations that are the same at the variable names, automatically converting them to latex
  string before passing them along to symbols(). In the provided string, commas or space can be used 
  as delimiters (a comma + any number of spaces OR any number of spaces), so you can just cut and paste
  to or from what you are asssigning to.
  NOTE: if any name passed is not a valid identifier, no processing of it will be done as it is assumed
  the caller is passing LaTeX rather than a variable name. This is useful for symbol names that have
  non-ascii characters such as /alpha, which would have to be an ascii 'a' in python.
  TODO: With latexSymbs being use for all symbol declarations
  1) we can add a global registry mapping symbol str reps <-> variable names (as passed to latexSymbs)
  2) Having latexSymbs check this registry and warn/block redeclarations as per 2 new latexSymbs props
  3) Make laTeXToPy func which users can pass latex to in order to see python that would define it. 
  '''
  # test with: latexSymbs('R R1 R_2 Rvb R_v_n R_v_nf')
  # should error: latexSymbs('R1 R_1')

  if force_subscript is not None: latexSymbs.force_subscript = force_subscript
  if force_subscript_warning is not None: latexSymbs.force_subscript_warning = force_subscript_warning
  kwargs['cls'] = cls
  provided_names = re_split(',[ ]*|[ ]+', string_names)
  names = provided_names
  hist_update = OrderedDict()

  for name_i, name in enumerate(provided_names):
    if name.isidentifier() : names[name_i] = varnameToLaTeX(name)
    hist_update[names[name_i]] = {'provided_name': name, **kwargs}

  dups =  {x for x in names if names.count(x) > 1}
  if dups: raise ValueError(printlToStr('Duplicate symbol string representations:', *dups))
  names = ' '.join(names)
  symbs_tuple = symbols(names, **kwargs)

  # rather than modifying, delete any entries and re-add to bump their position up
  latexSymbs.hist = OrderedDict({k: latexSymbs.hist[k] for k in latexSymbs.hist if k not in hist_update})
  latexSymbs.hist.update(hist_update)
  
  return symbs_tuple


def varnameToLaTeX(name): # helper for latexSymbs and user
  if not name.isidentifier() : return name
  subscripts = name.split('_')
  letter = subscripts[0]
  subscripts = subscripts[1:]

  if len(letter) > 1 : 
    if latexSymbs.force_subscript:
      subscripts.insert(0, letter[1:])
      letter = letter[0]
      if latexSymbs.force_subscript_warning:
        print(f'Warning: subscript forcibly to applied to {name} after {letter} because latexSymbs.force_subscript==True')
        print(f'         You can suppress this warning with latexSymbs.force_subscript_warning==False')

  if len(subscripts):
    for ss_i, ss in enumerate(subscripts):
      if len(ss) > 1 : subscripts[ss_i] = '{'+ss+'}'

    subscripts = '_'.join(subscripts)
    return '{'+letter+'_'+subscripts+'}'
  else:
    return name
  

# helpers for passing to symbols/Symbol/latexSymbs 
real_nonneg = {'real':True, 'nonnegative':True}
real_finite = {'real':True, 'finite':True}

########## GLOBAL SYMBOL DECLARATIONS #############################################################

# eeOperators
V, I = symbols('V I', **real_finite)
R = symbols('R', **real_nonneg)

# generic components 
R_1, R_2, R_3, R_4, R_5, R_6 = symbols('{R_1} {R_2} {R_3} {R_4} {R_5} {R_6}', **real_nonneg)
C_1, C_2, C_3, C_4, C_5 = symbols('{C_1} {C_2} {C_3} {C_4} {C_5}', **real_nonneg)
D_1, D_2, D_3, D_4 = symbols('{D_1} {D_2} {D_3} {D_4}', **real_nonneg)

# for ota.py and opamp.py:
v_in, v_p, v_n, i_abc, i_out, v_out = \
symbols(r'{v_{in}} {v_{p}} {v_{n}} {i_{abc}} {i_{out}} {v_{out}} ', **real_finite)
R_v_n, R_nf, R_pf, R_out = symbols(r'{R_{v_n}} {R_{nf}} {R_{pf}} {R_{out}}', **real_nonneg)

# Note frequency:
n_midi, f_Hz = symbols(r'{n_{midi}} {f_{Hz}}', **real_finite)


# TODO: finish BTJ 


# BTJ Gain Characteristics:
alpha, beta = latexSymbs(r'{\alpha} {\beta}', **real_nonneg)

# BJT large signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Large-signal_models):
I_B, I_C, I_E, I_ES, V_BE, V_CE, V_CB = latexSymbs('I_B, I_C, I_E, I_ES, V_BE, V_CE, V_CB', **real_finite)
V_T, a_F  = latexSymbs(r'V_T, {\alpha_F}', **real_nonneg)

R_B, R_C, R_E  = latexSymbs('R_B, R_C, R_E', **real_nonneg) # With resistor
V_R_B, V_R_C, V_R_E  = latexSymbs('V_R_B, V_R_C, V_R_', **real_nonneg) # Involving Resistor

# BJT small signal models (https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Small-signal_models):
i_b, i_c, i_e = symbols(r'{i_b} {i_c} {i_e}', **real_finite)

# https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch8-2.pdf


# control voltages and currents:
v_cin, i_cout = symbols(r'{v_{cin}} {i_{cout}}', **real_finite)


# I'm considering adding an .about attribute to the symbol class to 
# store a string description of a given symbol. 
# https://medium.com/@nschairer/python-dynamic-class-attributes-24a89df8da7d

# I'm also considering having some global dictionary to act as directory so the user
#  can list out the symbols available, particularly those created within this lib

# But in any case, here I'm make some quicker to use meta-constructor functions for
# making symbols, given particular restrictions of components, V/I sources and v/i signals.


# def newResistors():
    