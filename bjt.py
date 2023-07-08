from sympy import Eq
from eeMath.math_helpers import lambdifier

from eeMath.eeSymbols import alpha, beta, I_C, I_E, I_B

bjt_alpha_eq = Eq(alpha, I_C / I_E)
bjt_beta_eq = Eq(beta,  I_C / I_B)


bjt_alpha_from_beta_eq = Eq( alpha, beta / (beta - 1) )
bjt_beta_from_alpha_eq = Eq( beta, alpha / (1 - alpha) )



