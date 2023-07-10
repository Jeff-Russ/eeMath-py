


###### GENERAL HELPERS ############################################################################

#.......function decorators ...................................................


def func_attr(**attrs): # https://stackoverflow.com/a/54030205
  def wrap(f):
    f.__dict__.update(attrs)
    return f
  return wrap


#.......string helpers ........................................................

from io import StringIO
# printToStr/printlToStr redirect print to a (returned) variable
def printToStr(*args, **kwargs):
  '''printToStr forwards all parameters to print, redirecting print's output string to the return'''
  output = StringIO()
  print(*args, file=output, **kwargs)
  contents = output.getvalue()
  output.close()
  return contents

def printlToStr(*args, **kwargs):
  '''printlToStr forwards all parameters to print, inserting `end=''`, 
  redirecting print's output string to the return'''
  kwargs['end'] = ''
  return printToStr(*args, **kwargs)


#.......iterators/list/set/collections helpers .......................................

# NOTE: requires: func_attr()
@func_attr(type=list)
def iSeq(first_or_len, last=None, step=None, seq_type=None, internal_call=False):
  '''iSeq is mostly similar to *NIX shell's seq and a little similar to python's range()
  1) Like range, the 3rd argument is `step` size rather than the second, as is the case with sh seq.
  2) Like range, iSeq can only work with integers
  3) Unlike range, the range starts with 1 like sh seq by default, unless both first and second args provided.
  4) Unlike range, 2nd arg `last` is inclusive, like sh seq's 3rd arg, not the non-inclusive `stop` 2nd arg of range.
  5) Unlike range, iSeq returns a list by default rather than a range object. But iSeq can be make to do so or 
      be set to any type by either setting iSeq.type=<sometype> or passing seq_type=<sometype>, {where the latter
      only applies to one call and the former set for all future calls unless reset again by the same means.}
      TODO: all of that above in curly brackets is to be completed. For now, either method of setting persists.
  6) Unlike range all but the first arg are named so you can skip any by passing None or by naming the called ones.'''
  if seq_type is not None: iSeq.type = seq_type 
  if internal_call or iSeq.type is range:
    if not first_or_len: return range(first_or_len) # will be empty or error
    s = first_or_len
    if step is None: 
      if last is None: return range(1, s+1) if s > 0 else range(s)                  # (len), empty if neg
      else: return range(s, last+1) if last >= s else range(s, last-1, -1)          # (first,last) 
    elif last is None: return range(1, s+1, step) if s > 0 else range(1, s-1, step) # (len,None,step) 
    else: return range(s, last+1, step) if last >= s else range(s, last-1, step)    # (first,last,step)
  else: return iSeq.type(iSeq(first_or_len, last, step, internal_call=True))        # cast to type

class ISeq(): 
  '''ISeq just makes objects that store an iSeq as obj.iseq, but can make it via strings.
  ISeq objects also have obj.first and obj.last properties set during construction.'''
  def __init__(self, first_or_range_str, last=None, delim=None, seq_type=list):
    '''ISeq just makes objects that store an iSeq as obj.iseq, but can make it via strings.
      ISeq objects also have obj.first and obj.last properties set during construction.'''
    from re import split as re_split, findall as re_findall
    if last is None:
      if isinstance(first_or_range_str, str):
        if delim is None:
          found = re_findall(r'[^0-9 ]+', first_or_range_str) # detect delim
          delim = found[0] if found else ' '
        # args = re_split(f'[ ]*{delim}[ ]*', first_or_range_str)
        args = re_split(f'[ ]*{delim}[ ]*', first_or_range_str)
        first = args.pop(0)
        last = args.pop(0) if len(args) else ''
        if args: raise ValueError(f"constructor string should only be two ints separated by '${delim}'" )
        self.first = int(first)
        self.last = int(last) if len(last) else self.first 
      else: 
        if delim is None: delim = ' '
        self.first = self.last = int(first_or_range_str)
      self.delim = delim
    else:
      self.first = int(first_or_range_str)
      self.last = int(last)
      if delim is None: self.delim = '-' # DEFAULT DELIM: maybe we should make this set-able somehow
      else: self.delim = delim
    orig_type = iSeq.type ; iSeq.type = seq_type
    self.seq = iSeq( int(self.first), int(self.last))
    iSeq.type = orig_type
  
    # def strBoth(self): return f'{self.from_iseq} {self.to_iseq}'
    # def strFrom(self): return f'{self.from_iseq}'
    # def strTo(self): return f'{self.to_iseq}'


  def strRange(self): return f'{self.first}{self.delim}{self.last}' if len(self.seq) > 1 else f'{self.first}'

  def __str__(self): return self.strRange()
  
  def __repr__(self): return self.strRange()

  def __len__(self): return len(self.seq)


# NOTE: requires: iSeq()
class MapISeqsToISeqs():
  def __init__(self, from_iseq=None, to_iseq=None, repr_mode='both', str_mode='both'):
    if not isinstance(from_iseq, ISeq): # from_iseq should be int-able, defining first val in from_iseq
      if not isinstance(to_iseq, ISeq): raise ValueError(f"`to_iseq` must be an instance of ISeq if `from_iseq` is not" )
      self.to_iseq = to_iseq
      from_first = int(from_iseq)
      offset = len(to_iseq) - 1 
      from_last = from_first + offset if to_iseq.last >= to_iseq.first else from_first - offset
      # print(f'creating from_iseq, that spans {from_first} to {from_last}')
      self.from_iseq = ISeq(from_first, from_last)

    elif not isinstance(to_iseq, ISeq): # to_iseq should be int-able, defining first val in to_iseq
      if not isinstance(from_iseq, ISeq): raise ValueError(f"`from_iseq` must be an instance of ISeq if `to_iseq` is not" )
      self.from_iseq = from_iseq
      to_first = int(to_iseq)
      offset = len(from_iseq) - 1 
      to_last = to_first + offset if from_iseq.last >= from_iseq.first else to_first - offset
      # print(f'creating to_iseq, that spans {to_first} to {to_last}')
      self.to_iseq = ISeq(to_first, to_last)

    if len(self.from_iseq) != len(self.to_iseq): raise ValueError(f"from_iseq` and `to_iseq` must the same length" )

    if repr_mode in ['from', 'to', 'both' ]: self.repr_mode = repr_mode
    else: raise ValueError(f"repr_mode can onl bet set to 'from'|'to'|'both'" )

    if str_mode in ['from', 'to', 'both' ]: self.str_mode = str_mode
    else: raise ValueError(f"str_mode can only bet set to 'from'|'to'|'both'" )

  def reprMode(self, mode='to'): 
    if mode in ['from', 'to', 'both' ]: self.repr_mode = mode
    else: raise ValueError(f"reprMode can onl bet set to 'from'|'to'|'both'" )

  def strBoth(self): return f'{self.from_iseq} {self.to_iseq}'
  def strFrom(self): return f'{self.from_iseq}'
  def strTo(self): return f'{self.to_iseq}'

  def getStr(self, mode):
    if   mode ==  'to': return self.strTo()
    elif mode ==  'from': return self.strFrom()
    else: return self.strBoth()

  def __str__(self): 
    _str = self.getStr(self.str_mode)
    return _str

  def __repr__(self):
    _str = self.getStr(self.repr_mode)
    return _str

def flatten(*lists): return [x for row in lists for x in row]

def partitionByContiguousInt(*nums):
  '''partitionByContiguousInt accept a collection of number or a variable number or number arguments
  and returns a collection of collections where each inner collection is contigous grouping of the numbers
  passed in. The type of the return (and it's inner collections) is a the same as the type passed in if one
  argument is given, else it is a list.'''
  from itertools import groupby
  from operator import itemgetter

  if len(nums)==1: nums = nums[0]
  else: nums = list(nums)
  partitioned = []
  for k, g in groupby(enumerate(nums), lambda i_x: i_x[0] - i_x[1]):
    try: partitioned.append(type(nums)(map(itemgetter(1), g))) # try casting to caller's type
    except: partitioned.append(list(map(itemgetter(1), g)))    #  fallback to list
  if type(nums) != list and type(nums) != set:
    try: return type(nums)(partitioned) # try casting to caller's type
    except: return partitioned          #  fallback to list
  else:  return partitioned 



def missingInts(*iterables):
  '''https://stackoverflow.com/a/16974075 Pass one ore more iterables of ints (sorted or not, with any minimum value) and 
  if they're contigous, returns is empty list, else return a list of all missing ints. No need to sort.'''
  flattened = sorted([x for row in iterables for x in row])
  start, end = flattened[0], flattened[-1]
  return sorted(set(range(start, end + 1)).difference(flattened))


def dupElement(*hashables, all_dups=False):
  '''https://stackoverflow.com/a/9835819 Pass one ore more collections of hashables and get 
  any element that apear more than once in any hashable or between hashables
  if all_dups==True, return array will itself have duplicates for those elements found more than twice
  (if an elements is found 1+n times it will appear in the return n times)
  '''
  ''''from https://towardsdatascience.com/iterable-ordered-mutable-and-hashable-python-objects-explained-1254c9b9e421:
  In particular, all the primitive data types (strings, integers, floats, complex, boolean, bytes), 
  ranges, frozensets, functions, and classes, both built-in and user-defined, are always hashable, 
  while lists, dictionaries, sets, and bytearrays are unhashable.
  ME: sets cannot contain unhasables so a list of lists cannot be converted to a set but a list of ints can.
  '''
  flattened = [x for row in hashables for x in row]
  seen = set()
  with_all_dups = [x for x in flattened if x in seen or seen.add(x)]
  return with_all_dups if all_dups else list(set(with_all_dups))


def sameElements(*sortables):
  '''returns True if all sortables (arrays/tuples/set/strings) have the same elements, 
  ignoring order but not duplicates(not all the same if one has dup and other does not)'''
  # return sorted(a) == sorted(b) # <- if we only had two args
  first = sorted(sortables[0])
  for sortable in sortables[1:]:
    if first != sorted(sortable): return False
  return True

def setOperation(operator, *settables):
  '''pass a set operator (- & | or ^), then two or more sets/lists/strings whatever can become a set
  and the returned result is (((settables[0] op setables[1]) op setables[2]) op setables[3]) etc.
  The function attempt to cast the returned result to the type of the zeroth settable passed in,
  falling back to a set if it fails'''
  # https://softhints.com/python-3-list-and-set-operations/  
  result = set(settables[0])
  if operator == '-':
    for settable in settables[1:]: result -= set(settable)
  elif operator == '&':
    for settable in settables[1:]: result &= set(settable)
  elif operator == '|':
    for settable in settables[1:]: result |= set(settable)
  elif operator == '^':
    for settable in settables[1:]: result ^= set(settable)
  else: raise ValueError(f"invalid set operator: '{operator}'. Use:\n" \
      "\t'-' for difference,\n\t'&' for intersection,\n\t'|' for union,\n\t'^' for symmetricdifference")
  if type(settables[0]) == str: return ''.join(result)
  elif type(settables[0]) != type(result):
    try: return type(settables[0])(result) # convert to type of first arg passed
    except: return result                  # fallback
  else: return result

# pass two or more sets/lists/strings whatever can become a set:
def setDiff(*settables): return setOperation('-', *settables)    # return all if first not ANY SUBSEQUENT
def setIntersect(*settables): return setOperation('&', *settables) # return common to ALL
def setUnion(*settables): return setOperation('|', *settables) 
def setSymmDiff(*settables): return setOperation('^', *settables) 

def stringifyEach(iterable): return type(iterable)(str(x) for x in iterable)

def stringifyJoin(iterable, joiner=',', prepend_append=''): 
  '''Convert each element in iterable to string and then join with joiner (default is ',')
  and if len(prepend_append) is:
      0... nothing is prepended or appended
      1... that char is both prepended and appended
      2... prepend_append[0] is prepended, prepend_append[1] is appended
    > 2... half of it (or half-1 if len is odd) is prepended and the second half is appended '''
  if prepend_append:
    if len(prepend_append) == 1:
      return f"{prepend_append}{joiner.join(str(x) for x in iterable)}{prepend_append}" 
    half_len = len(prepend_append) // 2
    return f"{prepend_append[:half_len]}{joiner.join(str(x) for x in iterable)}{prepend_append[half_len:]}"
  else: return f"{joiner.join(str(x) for x in iterable)}"
  

def appendAny(collection_ob, *items, append_string=False):
  '''appendAny(collection_ob, *items, append_string=False)
  appends each item in items to collection_ob, which can be any type that can
  be converted a list (but not be a string unless append_string==True), and 
  returns appended collection_ob in the type it was passed as. 
  see https://stackoverflow.com/a/25101183'''
  if isinstance(collection_ob, list): return collection_ob + list(items)
  elif isinstance(collection_ob, str):
    if not append_string: raise ValueError(f'Cannot append to string when append_string={append_string}')
    return ''.join(list(collection_ob) + list(items))
  return type(collection_ob)(list(collection_ob) + list(items))

def prependAny(collection_ob, *items, prepend_string=False):
  '''prependAny(collection_ob, *items, prepend_string=False)
  prepends each item in items to collection_ob, which can be any type that can
  be converted a list (but not be a string unless append_string==True), and 
  returns appended collection_ob in the type it was passed as. 
  see https://stackoverflow.com/a/25101183'''
  if isinstance(collection_ob, list): return list(items) + collection_ob 
  elif isinstance(collection_ob, str):
    if not prepend_string: raise ValueError(f'Cannot prepend to string when prepend_string={prepend_string}')
    return ''.join(list(items) + list(collection_ob))
  return type(collection_ob)(list(items) + list(collection_ob))

# from collections.abc import Sequence

#....... Dictionary helpers ...................................................

def tuplesToDict(*tuples, multival_type=list, to_dict=None):
  if to_dict is None: to_dict = {}
  if len(tuples)==1:
    tuples = tuples[0]
    # print(f'got a collection of tuples: {tuples}')
  for k, *vals in tuples:
    if k in to_dict.keys():
      try: # print(f'attempting append key: {k}', end=' ')
        to_dict[k] = appendAny(to_dict[k], *vals, append_string=False)
      except: #print('Failed. attempting prepend', end=' ')
        try: to_dict[k] = prependAny(to_dict[k], *vals, prepend_string=False)
        except: # print('Failed. manually prepending...', end=' ')
          to_dict[k] = [ to_dict[k], *vals ]
        print('')
    elif not vals: to_dict[k] = None
    elif len(vals) == 1: # print(f'adding one element to new key: {k}')
      to_dict[k] = vals[0]
    else: # print(f'adding multiple elements to new key: {k}')
      to_dict[k] = multival_type(vals)
  return to_dict


#.......function/object/variable inspection ...................................


def ppObj(ob):
  from yaml import dump as yaml_dump
  print(yaml_dump(ob))

from inspect import getsource, getmembers #, stack 



def showdef(fn) : print(getsource(fn)) # use to see lambdify'd function definitions 

# def membersListOfDict(obj):
#   members = getmembers(obj)
#   lofd = []
#   for idx, member in enumerate(members):
#     # remove "<" at start and "'>" at end then split at first space
#     type_of_type, *fulltype = f'{member[1]}'[1:-2].split(" ", 1) 
#     if fulltype: fulltype = fulltype[0]
#     else: 
#       fulltype
      
#       fulltype=f'{type(member[1]).__module__}.{type(member[1]).__name__}'
#       print(f'no space in members[{idx}]')

#     "class 'sympy.calculus.accumulationbounds.AccumulationBounds"
#     type


# import sympy
# sympy.sign
# sympy.core.function.FunctionClass



# # from https://stackoverflow.com/a/18425523
# import inspect 
# def retrieve_name(var):
#   callers_local_vars = inspect.currentframe().f_back.f_locals.items()
#   return [var_name for var_name, var_val in callers_local_vars if var_val is var]

def instanceof(*args):
  if len(args) == 1: return args[0].__class__.__name__
  else: return isinstance(args[0], tuple(args[1:]))

def classof(*args): 
  '''with 1 arg: returns string of class name 
  with 2 args: returns true of class name of arg 1 is arg 2 (string)
  with > 2 args: returns true of class name of arg 1 is any subsequent arg (strings)'''
  if len(args) == 1: return args[0].__class__.__name__
  else: return True if args[0].__class__.__name__ in args[1:] else False

def zerothDictKey(d):
  if not d or not isinstance(d, dict): return {}  # if the dict is empty return an empty dict (empty dicts are not valid keys)
  else: return list(d.keys())[0]

# NOTE: requires: zerothDictKey()
def zerothLeafDictKey(d):
  d_ptr = d
  key = zerothDictKey(d_ptr)
  while zerothDictKey(d_ptr) != {}: 
    key = zerothDictKey(d_ptr)
    d_ptr = d_ptr[key]
  return key

def fullnameFromClass(cls): return f'{cls.__module__}.{cls.__name__}'

def nameFromClass(cls): return cls.__name__



def classFromName(name):
  ''' Returns the actual class type from a string of the class name 
  or the class as a string in the format f'{cls.__module__}.{cls.__name__}' 
  (which is same format that fullnameFromClass returns, i.e. 'module.submodule.class')
  and returns the class itself. The function still works even if module is not imported
  if the fullname is given, but it must be available to be imported, of course.
  It will not work if the short class name is given but is not imported.'''
  from sys import modules as sys_modules

  before_last_dot, *after_last_dot = name.rsplit('.', 1) # before_last_dot, ['class'] or []
  if after_last_dot: return getattr(sys_modules[before_last_dot], after_last_dot[0])
  else: return getattr(sys_modules[__name__], before_last_dot)


def dummyThruFunc(*a, **d):
  if len(a):
    if len(a) == 1:
      if d: return a[0], d # returns tuple: (a0, {k1:v1,k2:v2})
      else: return a[0]    # returns value
    else:
      if d: return *a, d   # returns tuple: (a0, a1, ... {k1:v1,k2:v2})
      else: return a       # returns tuple: (a0, a1, ...)
  elif d: return d         # returns kwargs dict
  else: return


# NOTE: requires: dummyThruFunc(), nameFromClass(), fullnameFromClass(), ppObj()
def baseClassChain(obj_or_class, output='print', keys='full'):
  '''baseClassChainDict accepts a class or class object and, give the class or object's class,
  returns dictionary with one element, whose key is the class and whose value is another
    dict, whose keys are the parent classes and values are
      dicts whose keys are the parent class's parents and whose values :
        dicts...ETC... all the way up to builtins.object
  The `output` kwarg can be 'print' (default), 'return' or 'both'
  The dictionary is formatted by the `names` kwarg. where...
    keys='full',  (default) the dictionary keys full class name strings (prepended by modules)
    keys='name',            the dictionary keys class name strings
    keys='class',           the dictionary keys are actual classes
    NOTE: the keys customization are not yet implemented (keys is always 'full')
  '''
  def _baseClassChainDict(cls, key_getter):
    class_graph = {}
    cls_key = key_getter(cls)
    class_graph[cls_key] = { } 
    if not cls.__bases__: return class_graph
    for base_cls in cls.__bases__:
      base_key = key_getter(base_cls)
      if base_cls.__bases__: 
        class_graph[cls_key][base_key] = _baseClassChainDict(base_cls, key_getter)[base_key]
      else: class_graph[cls_key][base_key] = {}
    return class_graph
  
  cls = obj_or_class.__class__ if type(obj_or_class) != type else obj_or_class

  if keys == 'class': 
    if output != 'return': # This means we print, but not classes; we'll print full names.
      ppObj(_baseClassChainDict(cls, fullnameFromClass))
      if output == 'print': return
    classes_dict = _baseClassChainDict(cls, dummyThruFunc)
    return classes_dict
  
  if keys == 'name':
    chain_dict = _baseClassChainDict(cls, nameFromClass)
  else: # keys == 'full':
    chain_dict = _baseClassChainDict(cls, fullnameFromClass)

  if output == 'return': return chain_dict
  ppObj(chain_dict)
  if output == 'both': return chain_dict


def zerothDictKey(d): # returns the d.keys()
  if not d or not isinstance(d, dict): return {}  # if the dict is empty return an empty dict (empty dicts are not valid keys)
  else: return list(d.keys())[0]


# NOTE: requires: zerothDictKey()
def zerothLeafDictKey(d):
  ''' pass recursive dict, like the one returned from baseClassChain or 
  derivedClassChain, and get the key whose value is the innermost (empty) dict or not a dict'''
  d_ptr = d
  key = zerothDictKey(d_ptr)
  while zerothDictKey(d_ptr) != {}: 
    key = zerothDictKey(d_ptr)
    d_ptr = d_ptr[key]
  return key


# def moduleClasses(): pass

'''
NOTE: on dir(), locals(), vars() and globals()
if without args...
dir()             # list of in-scope variables (NOT REALLY...) (if called in function, ONLY HAS the vars defined within, thus far)
locals().keys()   # list from dictionary of local variables (if called in function, ONLY HAS the vars defined within, thus far)
vars().keys()     # list from dictionary of current namespace (if called in function, ONLY HAS the vars defined within, thus far)
        (so far, all the above are the same without args. NOTE: dir and vars could have taken arg(s))
globals().keys()  # list from dictionary of global variables PLUS ANY OF THE ABOVE. That's right all locals are in globals too!?
NOTE: https://docs.python.org/3/library/functions.html#globals says: "For code within functions, this 
      is set when the function is defined and remains the same regardless of where the function is called."
'''
# NOTE: Try this instead of attrs(obj block='dunder'): print([x for x in dir(obj) if not x.startswith('__')]) 
# NOTE: Try this instead of attrs(obj block='private'): print([x for x in dir(obj) if not x.startswith('_')]) 
# try: attrs(sp.core) or attrs(sp.core, types=['type'])
def attrs( # formerly dictionizeAtts
    obj, not_types=None, types=None,  # Default: not_types=['builtin_function_or_method', 'method-wrapper', 'SourceFileLoader']
    # BUT not_types and types ARE NOT WORKING
    block='private', # can be 'private' 'sunder' 'dunder' or None/False meaning no _*  _*_ __*__ or allow any, respectively
    recurse_types=[], max_depth=1, 
    attributes_dict={}, depth=0 # args used by function for recursion
  ):
  '''NOTE: THIS FUNCTION IS KIND OF A MESS SO USE IT AT YOUR OWN PERLIL
  attrs(obj) returns a dict: values are arrays of attribute names in the object and the keys are the type of all the elements therein
  You may also pass:
    not_types=[<typenames...>]     # to blacklist 
      OR
    types=[<typenames...>]         # to whitelist
    recurse_types=[<typenames...>] # types to recurse BUT RECURSION DOES NOT WORK WELL RIGHT NOW
    max_depth=4                    # the maximum depth of recursion
    
  '''

  depth += 1
  object_atts_lst = dir(obj)

  assert(not(not_types and types)), "attrs does not allow passing of both `not_types` and `types` arguments"
  if not not_types and not types:  # default not_types:
    not_types=['builtin_function_or_method', 'method-wrapper', 'SourceFileLoader']

  for attribute in object_atts_lst:
    type_key = type(getattr(obj, attribute)).__name__
    if   not_types and (type_key in not_types): continue # print(f'skipping {attribute} because {type_key} is blacklisted')
    elif types and (type_key not in types): continue # print(f'skipping {attribute} because {type_key} is not whitelisted')
    elif attribute in dir(int): continue # we don't want standard magic/dunder methods/attributes
    elif block == 'private' and attribute.startswith('_'): continue
    elif block == 'sunder'  and attribute.startswith('_') and attribute.endswith('_'): continue
    elif block == 'dunder'  and attribute.startswith('__') and attribute.endswith('__'): continue
    else:
      if type_key not in attributes_dict.keys():
        # print(f'adding type_key: {type_key}')
        attributes_dict[type_key] = []

      # if (attribute in attributes_dict[type_key]) : pass
      if (type_key in recurse_types) and (depth < max_depth):
        try:
          # print(f'recursing into object {inner_obj.__name__} from depth {depth} because type is {type_key}')
          attributes_dict[type_key].append( { attribute: attrs(getattr(obj, attribute), not_types, types, block, recurse_types, max_depth, attributes_dict, depth) } )
        except Exception as e:
          print(f'Exception while attempting to recurse with {attribute} of type {type_key} at depth {depth}: "{e}"')
      else:
        attributes_dict[type_key].append(attribute)

  return attributes_dict



import sympy as sp
# import numpy as np
# from sympy import symbols, Eq, evaluate, sympify, parse_expr, init_printing, Rational, solve, simplify
# import matplotlib.pyplot as plt

def returnOrShow(get,show) :
  if show: ppObj(get)
  else: return get

# NOTE: all require: returnOrShow(), attrs()
def sympy_types(show=False): return returnOrShow(attrs(sp, types=['type'])['type'], show)
def sympy_Eq_attrs(show=False): return returnOrShow(attrs(sp.Eq))
def sympy_core_types(show=False): return returnOrShow(attrs(sp.core, types=['type'])['type'])
def sympy_modules(show=False): return returnOrShow(attrs(sp, types=['module'])['module'])
def sympy_plotting(show=False): return returnOrShow(attrs(sp.plotting))


