
from sympy import Eq, evaluate, exp

# from eeMath.math_helpers import lambdifier
from eeMath.thermal import *
from eeMath.eeSymbols import v_D, i_D, n_D, I_S, I_S0


with evaluate(False):
  i_D_shockley_eq = Eq( i_D, I_S * ( (v_D)/(exp(n_D * V_T)) - 1 ) )
  i_D_4148_shockley_eq = Eq( i_D, i_D_shockley_eq.rhs.subs({I_S: 4.35e-09, n_D: 1.906}) )
  



# Z_Z zener Impedance	(typically )