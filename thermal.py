import sympy as sp
from eeMath.consts import consts
from eeMath.eeSymbols import t_Kelvin, t_Celsius, t_Fahr, V_T 

kelvin_of_celsius_expr = t_Celsius + 273.15
kelvin_of_fahr_expr = (t_Fahr - 32) * 5/9 + 273.15

def tempConvert(temp, unit, to_unit):
  f = unit[0].upper()
  t = to_unit[0].upper()
  if f == t: return temp
  mode = f'{f} {t}'
  if   mode == 'C F': return (temp * 9/5) + 32
  elif mode == 'C K': return temp + 273.15
  elif mode == 'K C': return temp - 273.15
  elif mode == 'K F': return (temp - 273.15) * 9/5 + 32
  elif mode == 'F K': return (temp - 32) * 5/9 + 273.15
  elif mode == 'F C': return (temp - 32) * 5/9 


# THIS WORKS BEST WITH FALSTAD + real_ota
VT_68F = sp.Rational(1263, 50000) # 293.13K, 67.964F, 19.98C
# = 0.02526 (exact) making 1/(2*V_T) = 19.794140 (approx)

VT_20C = VT_68F

# THIS WORKS BEST WITH FALSTAD + ideal_ota
VT_74F = sp.Rational(23, 900) # 296.56K, 74.138F, 23.4C 
# = 0.02585 where 5 repeats making 1/(2*V_T) = 19.56521 (approx)
VT_23C = VT_74F


VT_74F = sp.Rational(2521, 100000)


VT_spice = sp.Rational(517, 20000) # 299.98K, 80.3F, 26.83C (supposed to be 300K exactly)
# = 0.02585 mV making 1/(2*V_T) = 10000/517 ≈ 19.342359767891683

VT_falstad = sp.Rational(5173, 200000) # 300.15K, 80.6F, 27.0C
# - 25.865 mV, making 1/(2*V_T) = 19.3311424705 (exactly)

# Standard datasheet V_T approx:
VT_approx = sp.Rational(5, 192) # ≈ 302.2K, 84.29F, 29.0C
# = 26.0416̅ mV (exactly) making 1/(2*V_T) = 19.2 (exactly)
VT2_approx = sp.Rational(5, 96) # 2 * VT_approx 


VT_90F = sp.Rational(5, 190) # ≈ 305.38K, 90F, 32.232C
# ≈ 26.3158 mV making 1/(2*V_T) = 19.2 (exactly)
VT_32C = VT_90F
# VT_32 = sp.Rational(19, 1000)

VT_93F = sp.Rational(5, 189) # ≈ 306.9978K, 92.926F, 33.8478C
# ≈ 26.455 mV,  making 1/(2*V_T) = 18.9 (exactly)
# The above is a little bit off, or maybe the next one is? Prefer the one with exact 1/(2*V_T)
# VT_falstad = sp.Rational(5291, 200000) # (of Falstad OTA) ≈ 306.9975K, 92.93F, 33.85C
# ≈ 26.4 mV, making 1/(2*V_T) ≈ 18.9 (approx)
VT_34C = VT_93F

def VTofTemp(temp, temp_unit='C'):
  '''https://en.wikipedia.org/wiki/Boltzmann_constant#The_thermal_voltage'''
  t_unit = temp_unit[0].upper()
  if   t_unit == 'C' : temp += 273.15  # Celsius to Kelvin
  elif t_unit == 'F' : temp = (temp - 32) * 5/9 + 273.15 # Fahrenheit to Kelvin
  elif t_unit != 'K' : raise ValueError(f'temp_unit must be Celsius, Fahrenheit or Kelvin (got {temp_unit})')
  return (consts['k'] * temp) / consts['q']

def tempOfVT(VT_val, temp_unit='C'):
  t_unit = temp_unit[0].upper()
  temp_K = (consts['q'] * VT_val) / consts['k']
  if   t_unit == 'K': return temp_K
  elif t_unit == 'C' : return temp_K - 273.15  # Kelvin to Celsius
  elif t_unit == 'F' : return (temp_K - 273.15) * 9/5 + 32 # Kelvin to Fahrenheit
  else: raise ValueError(f'temp_unit must be Celsius, Fahrenheit or Kelvin (got {temp_unit})')


def mVofVT(VT_val, exact=False):
  '''returns VT_val in mV as float'''
  mvolts = VT_val * 1000
  if not exact and hasattr(mvolts, 'evalf'): return mvolts.evalf()
  else: return mvolts

def factorOfVT(VT_val, exact=False):
  '''returns 1/(2*VT_val) as float'''
  factor = 1/(2*VT_val)
  if not exact and hasattr(factor, 'evalf'): return factor.evalf()
  else: return factor

def VTofFactor(factor, exact=False):
  VT_val = 1/(2* factor)
  if not exact and hasattr(VT_val, 'evalf'): return VT_val.evalf()
  else: return VT_val

