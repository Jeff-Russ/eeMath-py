import sympy as sp
from sympy import Eq
from eeMath.math_helpers import lambdifier

from eeMath.eeSymbols import V_T, g_m, v_in, v_p, v_m, i_abc, i_out, v_out, R_out, t_Kelvin, t_Celsius, t_Fahr, R_fb, R_A, R_X
from eeMath.eeSymbols import i_Ep, i_Em, i_Bp, i_Bm, i_Cp, i_Cm
from eeMath.bjt import *
from eeMath.thermal import VT_approx, kelvin_of_celsius_expr, kelvin_of_fahr_expr, VTofTemp, tempOfVT
# About the above:
# - v_p and v_m are the V+ and V- OTA inputs, we'll use v_in as V+ when v_m is grounded (0)
# - V_T is "thermal voltage" a property of BJT's (in OTA), which  changes with temperature so 
#       V_T ≈ 25mV @ 20°C, and V_T ≈ 26mV @ 25°C
# - i_abc is the OTA control pin aka i_con
# i_out is the actual output of the OTA, which is current controlled. To get voltage:
# R_out resistor pulls the the OTA output to a voltage (typically it's tied to GND)

with sp.evaluate(False): 
  ota_gm = i_abc / (2 * V_T)
  ideal_ota_vcr_R_X_eq = Eq( R_X, (2*R_fb)/(ota_gm*R_A) ) # R_A connects v_m's, assumes R_pulldown's are 10k to -15v
  ideal_ota_i_out = (i_abc / (2 * V_T)) * (v_p - v_m)
  ideal_ota_v_out = R_out * ideal_ota_i_out
  ideal_ota_i_out_eq = Eq( i_out, ideal_ota_i_out)
  ideal_ota_kelvin_i_out_eq  = Eq( i_out, ideal_ota_i_out.subs({V_T: VTofTemp(t_Kelvin, 'K') }) )
  ideal_ota_celsius_i_out_eq = Eq( i_out, ideal_ota_i_out.subs({V_T: VTofTemp(t_Celsius, 'C')}) )
  ideal_ota_fahr_i_out_eq    = Eq( i_out, ideal_ota_i_out.subs({V_T: VTofTemp(t_Fahr, 'F')}) )

  sauer_ota_i_out    = -1 * i_abc * sp.tanh((v_p - v_m)/.052)
  sauer_ota_i_out_eq = Eq( i_out, sauer_ota_i_out )

  real_ota_i_out = i_abc *  sp.tanh((v_p - v_m) / (2 * V_T))
  # real_ota_vcr_R_X_eq = Eq( R_X, (2*R_fb)/(ota_gm*R_A)) # R_A connects v_m's, assumes R_pulldown's are 10k to -15v
  real_ota_v_out = R_out * ideal_ota_i_out
  real_ota_i_out_eq = Eq( i_out, real_ota_i_out)
  real_ota_kelvin_i_out  = Eq( i_out, real_ota_i_out.subs({V_T: VTofTemp(t_Kelvin, 'K') }) )
  real_ota_celsius_i_out = Eq( i_out, real_ota_i_out.subs({V_T: VTofTemp(t_Celsius, 'C')}) )
  real_ota_fahr_i_out    = Eq( i_out, real_ota_i_out.subs({V_T: VTofTemp(t_Fahr, 'F')}) )


discrete_ota_eq = {}
with sp.evaluate(False): 
  discrete_ota_eq[i_out] = Eq( i_out, i_Cp - i_Cm )
  discrete_ota_eq[i_Em] = bjt_diffpair_i_Em_eq.subs({i_tail: i_abc}) # Eq( i_Em, i_tail / (1 + exp((v_p-v_m)/V_T)) )
  discrete_ota_eq[i_Ep] = Eq( i_Ep, i_abc - discrete_ota_eq[i_Em].rhs ) # or Eq( i_Ep, i_tail / (1 + exp(-(v_p-v_m)/V_T)) )
  discrete_ota_eq[i_Bm] = Eq( i_Bm, i_Em / (beta +1) ) 
  discrete_ota_eq[i_Bp] = Eq( i_Bp, i_Ep / (beta +1) ) 
  discrete_ota_eq[i_Cm] = Eq( i_Cm, i_Em - i_Bm )
  discrete_ota_eq[i_Cp] = Eq( i_Cp, i_Ep - i_Bp )




# if we didn't care to ever change V_T, we'd replace the above with:
'''
with sp.evaluate(False): 
  ideal_ota_i_out = (i_abc / (2 * sp.Rational(5, 192))) * (v_p - v_m)
  ideal_ota_v_out = R_out * ideal_ota_i_out
'''


# def otaValsReset():
#   global ota_vals
#   ota_vals = {
#   i_abc: i_abc,
#   v_p: v_p,
#   v_m: v_m,
#   V_T: VT_approx,
#   i_out: i_out,
#   v_out: v_out,
#   R_out: R_out,
# }
# otaValsReset()


# def realOtaWithVals(subs={}, persist=False):
#   global ota_vals
#   unidentified_keys = subs.keys() - ota_vals.keys()
#   if unidentified_keys: 
#     raise ValueError(f'The following subsitutions are for unknown symbols: {unidentified_keys}')
#   merged_subs = {**ota_vals, **subs}
#   result = ideal_ota_i_out.subs(merged_subs)

#   if persist: ota_vals = merged_subs
#   return result

# # These might not work?....
# idealOtaIout = lambdifier(ideal_ota_i_out, i_abc, v_p, v_m=0, V_T=VT_approx)
# idealOtaVout = lambdifier(ideal_ota_v_out, R_out, i_abc, v_p, v_m=0, V_T=VT_approx)



# def OTArecalibrateFrom_VT(VT_value=None) : 
#   '''
#   sets globals (creating them if needed): ideal_ota_i_out_eq and ideal_ota_v_out_eq
#   calibrated by a "thermal voltage" numeric or symbolic argument, defaulting to 26mV
#   '''
#   global ideal_ota_i_out_eq, ideal_ota_v_out_eq, VT_approx
#   if VT_value is None: VT_value = VT_approx
#   ideal_ota_i_out_eq = Eq( i_out, ideal_ota_i_out.subs({V_T: VT_value})).evalf()
#   ideal_ota_v_out_eq = Eq( v_out, ideal_ota_v_out.subs({V_T: VT_value})).evalf()

# OTArecalibrateFrom_VT(VT_approx) # make the globals from approximation




