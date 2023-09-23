import sympy as sp
import numpy as np
from sympy import symbols, Symbol, Eq, evaluate, sympify, parse_expr, init_printing, Rational, solve, simplify, lambdify
from sympy import latex, print_latex, multiline_latex

# for: reload(eeMath)
from importlib import reload

# eeMathLib_path='/Users/jeffreyruss/Desktop/EE 2023/ python_math (for circuits)'
# # The above must change if the location if the original of this file (not a
# # hardlink to it but the one in the same location as the eeMathLib/ dir) changes location

# from sys import path as sys_path
# # from os import getcwd
# # if getcwd() != eeMathLib_path:
# if eeMathLib_path not in sys_path:
#   sys_path.append('/Users/jeffreyruss/Desktop/EE 2023/ python_math (for circuits)')

# __all__ = [ 'helpers', 'fs', 'eeFundamentals', 'opamp', 'freq_and_time' ]


from eeMath.discrete import *
from eeMath.eeFundamentals import *
# from eeMath.eeOperators import *
from eeMath.eeSymbols import *
# from eeMath.filters import *
from eeMath.general_helpers import *
from eeMath.graphing import *
from eeMath.math_helpers import *
# from eeMath.components import *
from eeMath.resistance import *
from eeMath.thermal import *
from eeMath.freq_and_time import *
# from eeMath.diode import *
from eeMath.bjt import *
from eeMath.opamp import *
from eeMath.ota  import *
# from eeMath.shell_helpers import *
from eeMath.units import *
# from eeMath.VToI import *


from pathlib import Path

# sp.init_printing(use_unicode=False) # for LaTeX output
