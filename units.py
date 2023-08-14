prefix_order = [
  'q', 'r', 'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', 'c', 'd', 
  'da', 'h', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q'
]
# TODO: just make metric_prefixes an OrderedDict ya dummy!
metric_prefixes = {
  'q': 1e-30, # quecto 0.000000000000000000000000000001
  'r': 1e-27, # ronto 0.000000000000000000000000001
  'y': 1e-24, # yocto 0.000000000000000000000001
  'z': 1e-21, # zepto 0.000000000000000000001
  'a': 1e-18, # atto 0.000000000000000001
  'f': 1e-15, # femto 0.000000000000001
  'p': 1e-12, # pico 0.000000000001
  'n': 1e-9,  # nano 0.000000001
  'u': 1e-6,  # micro 0.000001
  'm': 1e-3,  # milli 0.001
  'c': 1e-2,  # centi 0.01
  'd': 1e-1,  # deci 0.1
  'da': 1e1,  # deca 10
  'h': 1e2,   # hecto 100
  'k': 1e3,   # kilo 1000
  'M': 1e6,   # mega 1000000
  'G': 1e9,   # giga 1000000000
  'T': 1e12,  # tera 1000000000000
  'P': 1e15,  # peta 1000000000000000
  'E': 1e18,  # exa 1000000000000000000
  'Z': 1e21,  # zetta 1000000000000000000000
  'Y': 1e24,  # yotta 1000000000000000000000000
  'R': 1e27,  # ronna 1000000000000000000000000000
  'Q': 1e30,  # quetta 1000000000000000000000000000000
}
# TODO: also this: https://stackoverflow.com/questions/31906377/sympy-and-units-for-electric-systems

def getUnits(*units): # NOTE: destructuring fails when only getting one unit.
  '''example: getUnits('pA nA') or getUnits('pA,nA') or getUnits('pA','nA')
  The first letter of each unit requested should be a key in metric_prefixes (or starts 
  with 'da' for a 'deci' unit). You can add whatever you want after this unit prefix:
  they'll be ignored by this function by you'll likely use them in the variable names you unpack
  the return to. if a unit is not recognized, 1 is return for that unit making this valid:
    pA, nA, A = getUnits('pA, nA, A')'''
  returns = []
  from re import split as re_split
  units =  [x for x in re_split(',[ ]*|[ ]+', ','.join(units)) if x.strip()] # the list compr. is to remove all-whitespace els
  for unit in units:
    if unit.startswith('da'): returns.append(metric_prefixes['da'])
    elif unit[0] in metric_prefixes: returns.append(metric_prefixes[unit[0]])
    else: returns.append(1)
  return tuple(returns)


def unit(*units):
  u = getUnits(*units)
  if len(u) > 1: raise ValueError('unit recieved more than one unit!')
  return u[0]

getUnit = unit

########## MAKE SOME GLOBALS ######################################################################


# Current:
pA, nA, uA, mA = getUnits('pA, nA uA, mA')
µA = uA

# Capacitance:
pF, nF, uF = getUnits('pF, nF, uF')

# Resistance:
mΩ, Ω, kΩ, MΩ = getUnits('mΩ, Ω, kΩ, MΩ')

# Voltage:
uV, mV = getUnits('uV, mV')
µV = uV


# Time:
us, ms = getUnits('us, ms')
µs = us

def generateMetricPrefixesFor(unit_name, min='p', max='G', skip_min='c', skip_max='h' ):
  '''
  generate global numeric variables whose names are each an 
  SI metrix prefix + unit_name 
  and whose values are the multiplier for that metric previx.
  The number of global generated are limited by the min and max args
  which each should be a metric prefix character (or two in the case of 'da')
  for the lowest and highest (inclusive) to generate with any in from the  
  skip_min='c'  to skip_max='h' (inclusive) excluded. The defaults for
  skip_min and skip max will skip:
  'h', 'da', 'd', 'c' which are hecto, deca, deci and centi
  '''
  start_idx = prefix_order.index(min)
  stop_idx = prefix_order.index(max) + 1

  if skip_min and skip_max:
    check_skips = True
    skip_min_idx = prefix_order.index(skip_min)
    skip_max_idx = prefix_order.index(skip_max) 
  elif not skip_min and not skip_max: check_skips = True
  else: raise ValueError("if skip_min is provided, then skip_min and visa-versa")
    
  for i in range(start_idx, stop_idx):
    if check_skips and i >= skip_min_idx and i <= skip_max_idx: continue
    prefix = prefix_order[i]
    varname = f'{prefix}{unit_name}'
    value = metric_prefixes[prefix]
    print(f'{varname}', end=' ')
    globals()[varname] = value # https://stackoverflow.com/a/4010869

# # doing this here doesn't work. do it from QtConsole:
# print("eeMath.units available:")
# generateMetricPrefixesFor('A', min='p', max='G') # pA nA uA mA kA MA GA 
# # usage: 1.5*pA,
# generateMetricPrefixesFor('Ohm', min='u', max='G') # uOhm mOhm kOhm MOhm GOhm 
# # usage: 1.4kOhm
# generateMetricPrefixesFor('V', min='p', max='k') 
# # usage: 1.4kmv


def parseNum(str_or_num, prefer_int=True):
  '''parse an integer or float string that may have an metric unit'''
  if isinstance(str_or_num, int):
    return str_or_num
  if isinstance(str_or_num, float):
    if prefer_int and str_or_num == int(str_or_num): return int(str_or_num)
    else: return str_or_num
  temp = None
  if isinstance(str_or_num, str):
    from re import search
    temp = search(r'[a-zA-Z]', str_or_num)
  if temp is not None:
    idx = temp.start()
    unit = str_or_num[idx]
    # if unit == 'µ': unit = 'u' # TODO: does not work because not [a-zA-Z]
    as_flt = float(str_or_num[:idx])
    as_flt *= metric_prefixes[unit]
  else:
    as_flt = float(str_or_num)
  as_int = int(as_flt) 
  if prefer_int and as_int == as_flt: return as_int
  else: return as_flt

