import sympy as sp

from eeMath.eeSymbols import v_p, v_p, v_n, v_out, R_v_n, R_nf, R_pf, v_in, i_out

opamp_nfb_V_expr = sp.simplify( v_p + (v_p - v_n) * R_nf/R_v_n )
