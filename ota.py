import sympy as sp
from eeMath.math_helpers import lambdifier

from eeMath.eeSymbols import V_T, v_in, v_p, v_n, i_abc, i_out, v_out, R_out
# About the above:
# - v_p and v_n are the V+ and V- OTA inputs, we'll use v_in as V+ when v_n is grounded (0)
# - V_T is "thermal voltage" a property of BJT's (in OTA), which  changes with temperature so 
#       V_T ≈ 25mV @ 20°C, and V_T ≈ 26mV @ 25°C
# - i_abc is the OTA control pin aka i_con
# i_out is the actual output of the OTA, which is current controlled. To get voltage:
# R_out resistor pulls the the OTA output to a voltage (typically it's tied to GND)

with sp.evaluate(False): 
  ideal_ota_i_out = (i_abc / (2 * V_T)) * (v_p - v_n)
  ideal_ota_v_out = R_out * ideal_ota_i_out

# if we didn't care to ever change V_T, we'd replace the above with:
'''
with sp.evaluate(False): 
  ideal_ota_i_out = (i_abc / (2 * sp.Rational(5, 192))) * (v_p - v_n)
  ideal_ota_v_out = R_out * ideal_ota_i_out
'''

V_T_approx = sp.Rational(5, 192)  # V_T_approx is close to 26mV but is exactly the value 
# that makes 1/(2*V_T_approx) = 19.2 ( I got this via sp.nsimplify(0.0260416666666667),
# which I got by sp.Eq(19.2, 1/(2*x)) and then solving for x)

# These might not work?....
idealOtaIout = lambdifier(ideal_ota_i_out, i_abc, v_p, v_n=0, V_T=V_T_approx)
idealOtaVout = lambdifier(ideal_ota_v_out, R_out, i_abc, v_p, v_n=0, V_T=V_T_approx)


def OTArecalibrateFrom_V_T(V_T_value=None) : 
  '''
  sets globals (creating them if needed): ideal_ota_i_out_eq and ideal_ota_v_out_eq
  calibrated by a "thermal voltage" numeric or symbolic argument, defaulting to 26mV
  '''
  global ideal_ota_i_out_eq, ideal_ota_v_out_eq, V_T_approx
  if V_T_value is None: V_T_value = V_T_approx
  ideal_ota_i_out_eq = sp.Eq(i_out, ideal_ota_i_out.subs({V_T: V_T_value})).evalf()
  ideal_ota_v_out_eq = sp.Eq(v_out, ideal_ota_v_out.subs({V_T: V_T_value})).evalf()

OTArecalibrateFrom_V_T(V_T_approx) # make the globals from approximation




