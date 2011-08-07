"""
Velat: a balance calculator for friends.

>>> from velat import Velat
>>> instance = Velat()
>>> instance # doctest:+ELLIPSIS
<velat.velat.Velat object at 0x...>
>>> alice = instance.newperson("alice")
>>> alice = instance.newperson("alice") # doctest:+IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: Person of name 'alice' already registered
>>> alice
<Person "alice">
>>> cinema = instance.newexpense("cinema Star Wars XXIII")
>>> cinema # doctest:+ELLIPSIS
<velat.base.Expense object at 0x...>
>>> cinema.newtakepart(alice, shares=1)
<Part [person alice paid 0.0, took 0.0 and 1.0 shares]>
>>> instance.solve()
[(<Person "alice">, None, 0.0)]
>>> bob = instance.newperson("bob")
>>> cinema.newtakepart(bob, shares=1)
<Part [person bob paid 0.0, took 0.0 and 1.0 shares]>
>>> solution = instance.solve_sorted()
>>> solution.sort()
>>> solution
[(<Person "alice">, None, 0.0), (<Person "bob">, None, 0.0)]
>>> camilla = instance.newperson("camilla")
>>> #uh oh, camilla paid 42 but wasn't in the theater
>>> cinema.newtakepart(camilla, paid=42)
<Part [person camilla paid 42.0, took 0.0 and 0.0 shares]>
>>> instance.solve_sorted()
[(<Person "alice">, <Person "camilla">, 21.0), (<Person "bob">, <Person "camilla">, 21.0)]
>>> damian = instance.newperson("damian")
>>> #damian paid 12 and was at the movie
>>> cinema.newtakepart(damian, shares=1, paid=12)
<Part [person damian paid 12.0, took 0.0 and 1.0 shares]>
>>> instance.solve_sorted()
[(<Person "alice">, <Person "camilla">, 18.0), (<Person "bob">, <Person "camilla">, 18.0), (<Person "damian">, <Person "camilla">, 6.0)]
>>> #alice ate popcorns (not 1 more share) for 5$
>>> cinema.newtakepart(alice, taken=5)
<Part [person alice paid 0.0, took 5.0 and 0.0 shares]>
>>> instance.solve_sorted()


"""

import warnings

version=0.1

try:
    from traits.api import HasTraits
except ImportError:
    import sys
    warnings.warn("Missing dependency: enthought.traits "
        "(Package 'python-traits' on debian and ubuntu)."
        "\nExiting.\n", ImportWarning)
    raise

from velat import Velat
