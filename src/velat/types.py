#coding: utf-8
""" types.py from package velat

    Author and Copyright © Feth Arezki <feth ×AT× tuttu.info>, 2010

    This code is licenced to anybody willing under the AGPLv3 licence (ie GPL, with
    the additionnal requirement that the code be made available to end users when
    the software is used through the network).
    #TODO: add ref to AGPL

    The author could be quite liberal in granting another licence when asked.


    Here be basic types as needed by velat, a simple expenses calculator
"""

from enthought.traits.api import Float, HasTraits, Instance, List, Str


class Person(HasTraits):
    """
    a person is an object to which credits and debts can be assigned
    """
    name = Str
    information = Str

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return """<Person "%s">""" % self.name

    def _totalpaid(self):
        #FIXME: stub
        return 42
    totalpaid = property(fget=_totalpaid)

    def _totalowed(self):
        #FIXME: stub
        return 43
    totalowed = property(fget=_totalowed)


NOBODY = Person("Nobody")


class Transfer(HasTraits):
    """
    A transfer of money between 2 persons
    """
    giver = Instance(Person)
    receiver = Instance(Person)
    value = Float(0.0)
    context = Str

    def unicode(self):
        return "%s -[%f]-> %s" % (self.giver, self.value, self.receiver)

    def error_msg(self):
        """ return None when valid """
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
        if self.giver is None:
            return ""
        return self.giver.name
    givername = property(fget=_givername)

    def _receivername(self):
        if self.receiver is None:
            return ""
        return self.receiver.name
    receivername = property(fget=_receivername)

    def _iter_custom_items(self):
        for name in self.trait_names():
            if name in ('trait_added', 'trait_modified'):
                continue
            yield name, getattr(self, name)

    def save(self):
        self.save_dict = dict(
            name_value
            for name_value in self._iter_custom_items()
        )

    def restore(self):
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
    paid = Float(0.0)
    person = Instance(Person)
    shares = Float(0.0)
    taken = Float(0.0)
    context = Str

    def __init__(self, person=NOBODY, paid=0.0, taken=0.0, shares=0.0):
        self.paid = paid
        self.person = person
        self.shares = shares
        self.taken = taken

    def _balance(self, sharevalue):
        return self.paid - self.taken - self.shares*sharevalue

    def balance(self, sharevalue):
        return self.person, self._balance(sharevalue)

    def __repr__(self):
        return """<Part [person %s paid %s, took %s and %s shares]>""" % (
            self.person.name, self.paid, self.taken, self.shares
        )


class Expense(HasTraits):
    """
    Expenses are costly ativities.
    For instance, cinema is usely being paid for, this is why we call it an
    expense.

    Expenses don't have a cost per se: costs and consumers are declared in the
    'parts' attribute: a list of PartTaking
    """
    name = Str
    parts=List(trait=Instance(klass=PartTaking, factory=PartTaking))

    def __init__(self, name):
        self.name = name

    def sharevalue(self):
        sharesnb = 0.0
        cost = 0.0
        oob_cost = 0.0
        for item in self.parts:
            cost += item.paid
            sharesnb += item.shares
            oob_cost += item.taken
        leftcost = cost - oob_cost
        if sharesnb == 0:
            return 1 #we don't care. Neutral element, quicker in calculus.
        return leftcost / sharesnb

    def balance(self):
        sharevalue = self.sharevalue()
        return (item.balance(sharevalue) for item in self.parts)

    def newtakepart(self, person, paid=0.0, taken=0.0, shares=0.0):
        part = PartTaking(person, paid, taken, shares)
        self.parts.append(part)
        return part

    def _paidfor(self):
        return sum(item.paid for item in self.parts)

    paidfor_property = property(fget=_paidfor)

    def _ppl_nb(self):
        return len(frozenset(item.person for item in self.parts))

    ppl_nb_property = property(fget=_ppl_nb)

    def _parts_nb(self):
        return len(self.parts)

    parts_nb = property(fget=_parts_nb)

