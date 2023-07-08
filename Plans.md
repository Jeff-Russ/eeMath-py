# eeMath Plans

# Idea: Universal Equation Class object with methods (no Expressions)

## Premise 

* It would be nice to have Class that extends `Eq`, to always be used in place of it, which has methods for solving and graphing straight on it. 
* It could ==replace the need for lambdify== by doing things like enforce that the equality is graphable or guaranteed to solve to a single number, given the subtitutions provided and the value expected out. In other words, our methods can be made to require a number of args (or keys in passed dict) if the method is expected to return a single valued number. 
* It could also ==replace the need for expressions==: Since sympy expressions are all implicitly equal to zero, maybe a good idea would be to always  use a `Eq` object (or, in our case our class that extends `Eq`) were the `lhs` is `0` instead of ever using expressions. 

## Brainstorming Details. 



We should probably subclass Eq into a number of classes, each enforcing a set of rules

* So one could replace expression by always requiring the lhs be `0` and 
* Another could be used to define constants by having one symbol and nothing else on one side (probably lhs) and a numeric value the other side. 

* In keeping with the idea of a function (and assignments like `let var = value`), it might be a good to have a convention that the "output" is the lhs and the "input" is the substitutions to symbols on the rhs. 
* We could even make all of these subclass objects [callable](https://python-course.eu/oop/callable-instances-classes.php#:~:text=A%20callable%20object%20is%20an,function%22%2C%20i.e.%20using%20brackets.), thus, by default, being lambdified.
  * For graphing (2D), we could have (a) separate method(s)/property(s) that we use to subsitute symbols beforehand such that the object, when `__call__`ed, only expects one argument (`x` on the graph). 
* `Eq` derived object that don't have a single symbol on the lhs could also be made graphable: the additional symbols on the lhs we be required to be subsituted before graphing as well.


