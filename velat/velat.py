from cPickle import dump as pickle, load as unpickle

import peinard
from base import Expense, NOBODY, Person, Transfer


def autoperson(*args, **kwargs):
    if not hasattr(autoperson, 'index'):
        autoperson.index = 0
    autoperson.index += 1
    return Person("person %d" % autoperson.index)

def autoexpense(*args, **kwargs):
    if not hasattr(autoexpense, 'index'):
        autoexpense.index = 0
    autoexpense.index += 1
    return Expense("expense %d" % autoexpense.index)

def autotransfer(*args, **kwargs):
    if not hasattr(autotransfer, 'index'):
        autotransfer.index = 0
    autotransfer.index += 1
    return Transfer(
        giver=NOBODY, receiver=NOBODY, value=0.0, context= "%d" % autotransfer.index
        )

class VelatException(object):
    pass

class InvalidAPICall(object):
    pass

class Velat(object):

    def __init__(self, name="", expenses=None, persons=None, transfers=None, description=""):
       self.expenses = expenses or []
       self.persons = persons or []
       self.transfers = transfers or []
       self.description = description

    def actions_log(self):
        """
        Iterator that yields (person, credit) or (person, dept) pairs
        """
        for transfer in self.transfers:
            yield transfer.giver, transfer.value
            yield transfer.receiver, - transfer.value
        for expense in self.expenses:
            for person, balance in expense.balance():
                yield person, balance

    def totals(self):
        totals = {}
        for person, balance in self.actions_log():
            totals.setdefault(person, 0)
            totals[person] += balance
        return totals

    def solve(self):
        """
        Preconisations
        optimizes the number of exchanges
        Returns a list of transfers that should be performed
        """
        return peinard.heuristic(self.totals())

    def solve_sorted(self):
        """
        cf solve(): sorted list (ie. always the same)
        """
        solution = self.solve()
        solution.sort()
        return solution

    def add_person(self, name):
        if any(person.name == name for person in self.persons):
            raise ValueError("Person of name '%s' already registered" % name)
        person = Person(name)
        self.persons.append(person)
        return person

    def add_expense(self, name, payer=None, owers=None, payers=None,
            amount=None):
        expense = Expense(name)

        if payers is None:
            payers = {}

        if (payer and payers) or (payer and not amount):
            raise InvalidAPICall()

        if payer and amount:
            payers = {payer: amount}

        for payer, amount in payers.items():
            expense.take_part(person, paid=amount, shares=1)

        self.expenses.append(expense)
        return expense

    def add_transfer(self, giver, receiver, amount, context=""):
        transfer = Transfer(giver, receiver, amount, context)
        self.transfers.append(transfer)
        return transfer

    def save(self, filename):
        with open(filename, 'w') as filedesc:
            pickle(self, filedesc)

    def len_expenses_and_parts(self):
        return len(self.expenses) + sum(
                len(expense.parts) for expense in self.expenses
                )

def load(filename):
    with open(filename, 'r') as filedesc:
        return unpickle(filedesc)
