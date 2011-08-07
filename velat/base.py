#coding: utf-8
""" base.py from package velat

    Author and Copyright © Feth Arezki <feth ×AT× tuttu.info>, 2010-2011

    This file is part of velat-core.

    the program velat-core is free software: you can redistribute it and/or
    modify it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    Here be basic types as needed by velat, a simple expenses calculator
"""

from decimal import Decimal
#pylint: disable=F0401
#Not my fault; seems pylint won't import traits.api
from traits.api import HasTraits, Instance, List, Str, TraitHandler
#pylint: disable=F0401
#pylint: disable=W1001
#As pylint does not cut it with HasTraits,
#it believes our classes are old style classes


class DecimalTrait(TraitHandler):
    def validate(self, object, name, value):
        if type(value) is Decimal:
            return value
        elif type(value) is float:
            value = '%.5f' % value

        try:
            value = Decimal(value)
        except InvalidOperation:
            self.error(object, name, value)

        return value

    def info(self):
        return '**given a Decimal, a string, a float or whatever, tries and '\
            'returns a Decimal. For maximum precision, give me a string like '\
            '"2.4567897654"**'


class Person(HasTraits):
    """
    a person is an object to which credits and debts can be assigned
    """
    name = Str
    information = Str

    def __init__(self, name):
        """
        name: string
        """
        self.name = name

    def __repr__(self):
        """
        object like repr. Maybe should contain more than just the name.
        """
        return """<Person "%s">""" % self.name

    def _totalpaid(self):
        """
        How much this person paid
        """
        #FIXME: stub
        return 42
    totalpaid = property(fget=_totalpaid)

    def _totalowed(self):
        """
        How much this person owes
        """
        #FIXME: stub
        return 43
    totalowed = property(fget=_totalowed)

    def __cmp__(self, other):
        return cmp(self.name, other.name)


NOBODY = Person("Nobody")


class Transfer(HasTraits):
    """
    A transfer of money between 2 persons
    giver, receiver, value, and free-form context
    """
    giver = Instance(Person)
    receiver = Instance(Person)
    value = DecimalTrait()
    context = Str

    def unicode(self):
        """
        CLI friendly repr of a transfer
        """
        return "%s -[%f]-> %s" % (self.giver, self.value, self.receiver)

    def error_msg(self):
        """
        return None when valid
        """
        if self.giver == NOBODY:
            return "Please select a valid person as giver"
        if self.receiver == NOBODY:
            return "Please select a valid person as receiver"
        if self.giver == self.receiver:
            return "Giver and receiver are the same"
        if self.value <= 0.0:
            return "Transfered value should be >= 0"
        return

    def _givername(self):
        """
        returns str: the giver
        """
        if self.giver is None:
            return ""
        return self.giver.name
    givername = property(fget=_givername)

    def _receivername(self):
        """
        returns str: the receiver
        """
        if self.receiver is None:
            return ""
        return self.receiver.name
    receivername = property(fget=_receivername)

    def _iter_custom_items(self):
        """
        part of save/restore routine: what should be saved
        """
        #pylint: disable=E1101
        #trait_names belongs to HasTraits
        for name in self.trait_names():
            if name in ('trait_added', 'trait_modified'):
                continue
            yield name, getattr(self, name)
        #pylint: enable=E1101

    def save(self):
        """
        sets self.save_dict as saveable dict
        """
        self.save_dict = dict(self._iter_custom_items())

    def restore(self):
        """
        see save(): uses self.save_dict
        """
        for name_value in self.save_dict.iteritems():
            setattr(self, *name_value)


class PartTaking(HasTraits):
    """
    Taking part in an costly activity / expense means
    * paying something for it
    * taking some shares of its benefits, for instance:
      * one meal (one share),
      * "A takes 1.5 kg of potatoes (1.5 share)
        while B takes 10 kg (10 shares)"
    * taking an extra of known cost, for instance:
      *  "A took an extra cognac for 4€"
    """
    paid = DecimalTrait()
    person = Instance(Person)
    shares = DecimalTrait()
    taken = DecimalTrait()
    context = Str

    def __init__(self, person=NOBODY, paid=0.0, taken=0.0, shares=0.0):
        """
        paid: float
        person: Person
        shares: float
        taken: float
        context: free form str
        """
        self.paid = paid
        self.person = person
        self.shares = shares
        self.taken = taken

    def _balance(self, sharevalue):
        """
        computes balance (float)
        """
        return self.paid - self.taken - self.shares * sharevalue

    def balance(self, sharevalue):
        """
        returns: tuple person - balance (float).
        """
        return self.person, self._balance(sharevalue)

    def infos(self):
        yield('person', self.person.name)
        if self.paid:
            yield ('paid', self.paid)
        if self.taken:
            yield ('taken', self.taken)
        if self.shares:
            yield ('shares', self.shares)

    def __repr__(self):
        """
        object like repr. Maybe should contain more than just the name.
        """
        return """<Part [%s]>""" % ' - '.join('%s: %s' % item for item in self.infos())


class Expense(HasTraits):
    """
    Expenses are costly ativities.
    For instance, cinema is usely being paid for, this is why we call it an
    expense.

    Expenses don't have a cost per se: costs and consumers are declared in the
    'parts' attribute: a list of PartTaking
    """
    name = Str
    parts = List(trait=Instance(klass=PartTaking, factory=PartTaking))

    def __init__(self, name):
        """
        name: str

        An expense really is an activity. It contains parts/shares
        representing the fact of taking part or paying for it.
        """
        self.name = name

    def sharevalue(self):
        """
        Price of the basic proportionnal share.
        """
        sharesnb = 0.0
        cost = 0.0
        oob_cost = 0.0
        for item in self.parts:
            cost += item.paid
            sharesnb += item.shares
            oob_cost += item.taken
        leftcost = cost - oob_cost
        if sharesnb == 0:
            return 1  # we don't care. Neutral element, quicker computation.
        return leftcost / sharesnb

    def balance(self):
        """
        This generator aggregates balances in all shares.
        """
        sharevalue = self.sharevalue()
        return (item.balance(sharevalue) for item in self.parts)

    def newtakepart(self, person, paid=0.0, taken=0.0, shares=0.0):
        """
        new part-taking
        """
        part = PartTaking(person, paid, taken, shares)
        self.parts.append(part)
        return part

    def _paidfor(self):
        """
        How much was paid for this expense? (ie. price)
        """
        return sum(item.paid for item in self.parts)

    paidfor_property = property(fget=_paidfor)

    def _ppl_nb(self):
        """
        How many people took part to this expense/activity?
        """
        return len(frozenset(item.person for item in self.parts))

    ppl_nb_property = property(fget=_ppl_nb)

    def _parts_nb(self):
        """
        How many parts/shares in this expense/activity?
        """
        return len(self.parts)

    parts_nb = property(fget=_parts_nb)
