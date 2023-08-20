

import sympy as sp

VT_approx = sp.Rational(5, 192)  # VT_approx is close to 26mV but is exactly the value 
# that makes 1/(2*VT_approx) = 19.2 ( I got this via sp.nsimplify(0.0260416666666667),
# which I got by sp.Eq(19.2, 1/(2*x)) and then solving for x)

VT2_approx = sp.Rational(5, 96) # 2 * VT_approx 


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
  if temp_unit == 'K': return temp_K
  elif t_unit == 'C' : return temp_K - 273.15  # Kelvin to Celsius
  elif t_unit == 'F' : return (temp_K - 273.15) * 9/5 + 32 # Kelvin to Fahrenheit
  else: raise ValueError(f'temp_unit must be Celsius, Fahrenheit or Kelvin (got {temp_unit})')
  return (consts['q'] * VT_val) / consts['k']

