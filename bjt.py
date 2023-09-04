from sympy import Eq, evaluate, exp

from eeMath.math_helpers import lambdifier
from eeMath.thermal import *
from eeMath.eeSymbols import alpha, beta, beta_0, i_B, i_C, i_E, I_S, I_S0, V_T, v_BE, v_CE, v_CB, V_A
from eeMath.eeSymbols import v_diff, v_B1, v_B2, v_p, v_m, i_Ep, i_Em, i_tail


# BJT gain characteristics
bjt_alpha_equalities = []
bjt_beta_equalities = []

with evaluate(False):
  bjt_alpha_equalities.append(Eq( alpha, i_C / i_B ))
  bjt_alpha_equalities.append(Eq( alpha, beta / (beta + 1) ))

  bjt_beta_equalities.append(Eq( beta,  i_C / i_B ))
  bjt_beta_equalities.append(Eq( beta, alpha / (1 - alpha) ))

bjt_i_E_equalities = []
bjt_i_C_equalities = []
bjt_i_B_equalities = []

# BJT basic current characteristics
with evaluate(False):
  bjt_i_E_equalities.append(Eq( i_E, i_C + i_B ))
  bjt_i_C_equalities.append(Eq( i_C, i_C - i_B ))
  bjt_i_B_equalities.append(Eq( i_B, i_E - i_C ))


bjt_I_S_equalities = []

# BJT Active Mode Equations
with evaluate(False):
  bjt_i_C_equalities.append(Eq( i_C, I_S * exp( v_BE/V_T ) ))
  bjt_i_C_equalities.append(Eq( i_C, beta * i_B ))
  bjt_i_B_equalities.append(Eq( i_B, i_C / beta ))
  bjt_I_S_equalities.append(Eq( I_S, I_S0 * (1 + (v_CE / V_A)) ))
  bjt_beta_equalities.append(Eq( beta, beta_0 * (1 + (v_CE / V_A)) ))
  bjt_i_B_equalities.append(Eq( i_B, ( I_S0 * exp(v_CE / V_T) ) / beta_0 ))
  bjt_i_E_equalities.append(Eq( i_E, (1 + (1/beta)) * i_C ))
  bjt_i_E_equalities.append(Eq( i_E, (1 + beta) * i_B )) # correct? src: https://www.electricaltechnology.org/2020/11/bipolar-junction-transistor-bjt-formulas-and-equations.html
  bjt_i_B_equalities.append(Eq( i_B, i_E / (beta +1) ))  # very useful but only correct if previous is, which I think it is. 

# BJT differential pair
with evaluate(False):
  # source: https://www.ee.iitb.ac.in/~sequel/ee230/mbpth_diff_1.pdf
  bjt_diffpair_i_E_eq = Eq( i_E, (I_S/alpha) * exp((v_B1 - v_B2)/V_T) ) # might be bad
  bjt_diffpair_i_Ep_eq = Eq( i_Ep, i_tail / (1 + exp(-(v_p-v_m)/V_T)) )
  bjt_diffpair_i_Em_eq = Eq( i_Em, i_tail / (1 + exp((v_p-v_m)/V_T)) )





