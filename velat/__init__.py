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
<Part [person: alice - shares: 1]>
>>> instance.solve()
[(<Person "alice">, None, 0.0)]
>>> bob = instance.newperson("bob")
>>> cinema.newtakepart(bob, shares=1)
<Part [person: bob - shares: 1]>
>>> instance.solve_sorted()
[(<Person "alice">, None, 0.0), (<Person "bob">, None, 0.0)]
>>> camilla = instance.newperson("camilla")
>>> #uh oh, someone paid 42
>>> cinema.newtakepart(camilla, paid=42)
<Part [person: camilla - paid: 42]>
>>> instance.solve_sorted()
[(<Person "alice">, <Person "camilla">, 21.0), (<Person "bob">, <Person "camilla">, 21.0)]
>>> damian = instance.newperson("damian")



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
