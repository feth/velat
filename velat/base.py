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


def _to_decimal(value):
    """
    given a Decimal, a string, a float or whatever, tries and
    returns a Decimal. For maximum precision, give me a string like
    "2.4567897654"
    """
    if type(value) is Decimal:
        return value
    elif type(value) is float:
        value = '%.5f' % value

    value = Decimal(value)

    return value

def _valid_section(sections, column, edit=False):
    sections_nb = len(sections)
    if column > sections_nb:
        raise ValueError('%s is not in 0..%d' % (value, sections_nb))
    if not edit:
        return
    if not sections[column][1]:
        raise ValueError('This value is not editable')

class TabularObject(object):
    SECTIONS = () # tuple of tuples: ('name', editable_bool)


    def get_by_col(self, column):
        sections = self.SECTIONS
        _valid_section(sections, column)
        return getattr(self, sections[column][0])
    
    def set_by_col(self, column, value):
        sections = self.SECTIONS
        _valid_section(sections, column, edit=True)
        setattr(self, sections[column][0], value)

class Person(TabularObject):
    """
    a person is an object to which credits and debts can be assigned
    """

    SECTIONS = ('name', True), ('information', True), ('balance', False)

    def __init__(self, name, information=""):
        """
        name: string
        """
        self.name = name
        self.information = information

    def __repr__(self):
        """
        object like repr. Maybe should contain more than just the name.
        """
        return """<Person "%s">""" % self.name

    def _balance(self):
        """
        How much this person owes
        """
        #FIXME: stub
        return 43
    balance = property(fget=_balance)

    def __cmp__(self, other):
        return cmp(self.name, other.name)



NOBODY = Person("Nobody")


class Transfer(TabularObject):
    """
    A transfer of money between 2 persons
    giver, receiver, value, and free-form context
    """

    SECTIONS = ('giver', False), ('receiver', False), ('value', False), \
            ('context', True)

    def __init__(self, giver, receiver, value, context=""):
        """
        Parameters
        ----------
        giver, receiver: Person
        value: decimal compatible
        """
        self.giver = giver
        self.receiver = receiver
        self.value = _to_decimal(value)
        self.context = context

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


class PartTaking(object):
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

    def __init__(self, person, paid=0, shares=0, taken=0, context=""):
        """
        Parameters:
        -----------
        person: Person
        paid, shares, taken : Decimal compatible
        """
        self.paid = _to_decimal(paid)
        self.person = person
        self.shares = _to_decimal(shares)
        self.taken = _to_decimal(taken)
        self.context = context

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


class Expense(TabularObject):
    """
    Expenses are costly ativities.
    For instance, cinema is usualy being paid for, this is why we call it an
    expense.

    Expenses don't have a cost per se: costs and consumers are declared in the
    'parts' attribute: a list of PartTaking
    """

    SECTIONS = ('name', True), ('parts', False)

    def __init__(self, name):
        """
        name: str
        parts: list of PartTaking

        An expense really is an activity. It contains parts/shares
        representing the fact of taking part or paying for it.
        """
        self.name = name
        self.parts = []

    def share_value(self):
        """
        Price of the basic proportionnal share.

        For instance, if 5 person paid 50$, then the share value is 10$
        (if we consider each person took exacly one share)
        """
        sharesnb = _to_decimal(0.0)
        cost = _to_decimal(0.0)
        oob_cost = _to_decimal(0.0)
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
        sharevalue = self.share_value()
        return (item.balance(sharevalue) for item in self.parts)

    def take_part(self, person, paid=0.0, taken=0.0, shares=0.0):
        """
        An user take part in this expense.

        :paid: What this person paid for this expense.
        :shares: The number of shares this person represents.
        :taken: The extra amount specifically consumed by one user.
                Use case: Everybody took the same menu but Alice, who took
                foie gras for an extra 10$.

        All paid, shares and taken are decimals. (Read again, "shares" is also 
        a decimal).
        """
        part = PartTaking(person, paid=paid, taken=taken, shares=shares)
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
