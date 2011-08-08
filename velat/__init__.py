"""
Velat: a balance calculator for friends.

>>> from velat import Velat
>>> instance = Velat()
>>> instance # doctest:+ELLIPSIS
<velat.velat.Velat object at 0x...>
>>> alice = instance.add_person("alice")
>>> alice = instance.add_person("alice") # doctest:+IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: Person of name 'alice' already registered
>>> alice
<Person "alice">
>>> cinema = instance.add_expense("cinema Star Wars XXIII") # YEAH !
>>> cinema # doctest:+ELLIPSIS
<velat.base.Expense object at 0x...>
>>> cinema.take_part(alice, shares=1)
<Part [person: alice - shares: 1]>
>>> instance.solve()
[(<Person "alice">, None, Decimal('0'))]
>>> bob = instance.add_person("bob")
>>> cinema.take_part(bob, shares=1)
<Part [person: bob - shares: 1]>
>>> instance.solve_sorted()
[(<Person "alice">, None, Decimal('0')), (<Person "bob">, None, Decimal('0'))]
>>> camilla = instance.add_person("camilla")
>>> #uh oh, someone paid 42
>>> cinema.take_part(camilla, paid=42)
<Part [person: camilla - paid: 42]>
>>> instance.solve_sorted()
[(<Person "alice">, <Person "camilla">, Decimal('21.00000')), (<Person "bob">, <Person "camilla">, Decimal('21.00000'))]
>>> damian = instance.add_person("damian")

"""

version=0.1

from velat import Velat
