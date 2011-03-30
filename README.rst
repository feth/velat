Velat
=====

apropos
-------
This is a basic shared expenses balance calculator.
It was made mainly as an exercise to get acquainted to enthought.traits API.

The typical usecase is: you go on holiday or week end with some good friends,
and you don't want to keep track of money all the time. Velat ("debts", in
finnish) will do it for you: just remember who paid for what, how much, and who
took part in what. At the very least you'll want to have only one big activity
(expense), and count everything in it.
Also, you can lend money to you friends without taking part in their activities of course.

The accounting data can be saved/restored so that anyone agrees on one's own computer that the balance is fair.

proverb
-------

.. [fr] Les bons comptes font les bons amis.
.. [en] Short reckonings make long friends.

And I prefer have a machine count for me.

the software
------------
This is a working lib, with simple GUI/other interfaces to be built around (a Qt4 Gui is almost done).
I think the heuristic is not perfect. And I saw it raise rounding issues... (assertionerrors)

:Licence: AGPL, see COPYING

:Installation: See INSTALL

:Authors: - Main code by Feth Arezki: feth <AT> tuttu.info
          - Alot of packaging help by Julien Miotte aka Mike Perdide <mike dot perdide at gmail dot com>

