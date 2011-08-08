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
>>> # another usecase on the same instance: restaurant
>>> restaurant = instance.add_expense("restaurant")
>>> # everybody takes a drink and the same menu
>>> # gertrud invites her boyfriend
>>> #hugo pays the bill: 143
>>> # drink prices:
>>> apple_juice = 3
>>> banana_mix = 2
>>> camomilla = 1
>>> tap_water = 0
>>> # not entering the menu price because it is the same for everybody
>>> damian = instance.add_person("damian")
>>> restaurant.take_part(damian, shares=1, taken=apple_juice)
<Part [person: damian - taken: 3 - shares: 1]>
>>> ernest = instance.add_person("ernest")
>>> restaurant.take_part(ernest, shares=1, taken=banana_mix)
<Part [person: ernest - taken: 2 - shares: 1]>
>>> fanny = instance.add_person("fanny")
>>> restaurant.take_part(fanny, shares=1, taken=camomilla)
<Part [person: fanny - taken: 1 - shares: 1]>
>>> gertrud = instance.add_person("gertrud")
>>> restaurant.take_part(gertrud, shares=2, taken=banana_mix + camomilla)
<Part [person: gertrud - taken: 3 - shares: 2]>
>>> hugo = instance.add_person("hugo")
>>> restaurant.take_part(hugo, shares=1, taken=tap_water, paid=143)
<Part [person: hugo - paid: 143 - shares: 1]>
>>> instance.solve_sorted()

"""

version=0.1

from velat import Velat
