from cPickle import dump as pickle, load as unpickle

from traits.api import HasTraits, Instance, List, Str

from algo import heuristic
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

class Velat(HasTraits):
    name = Str
    expenses = List(trait=Instance(klass=Expense, factory=autoexpense))
    persons = List(trait=Instance(klass=Person, factory=autoperson))
    transfers = List(trait=Instance(klass=Transfer))
    description = Str

    def balance(self):
        for transfer in self.transfers:
            yield transfer.giver, transfer.value
            yield transfer.receiver, - transfer.value
        for expense in self.expenses:
            for person, balance in expense.balance():
                yield person, balance

    def totals(self):
        totals = {}
        for person, balance in self.balance():
            totals.setdefault(person, 0)
            totals[person] += balance
        return totals

    def solve(self):
        return heuristic(self.totals())

    def solve_sorted(self):
        solution = self.solve()
        solution.sort()
        return solution

    def newperson(self, name):
        if any(person.name == name for person in self.persons):
            raise ValueError("Person of name '%s' already registered" % name)
        person = Person(name)
        self.persons.append(person)
        return person

    def newexpense(self, name):
        expense = Expense(name)
        self.expenses.append(expense)
        return expense

    def save(self, filename):
        with open(filename, 'w') as filedesc:
            pickle(self, filedesc)

    def listfor(self, word):
        if word == "expense":
            return self.expenses
        if word == "person":
            return self.persons
        if word == "transfer":
            return self.transfers
        raise ValueError(word)

    def len_expenses_and_parts(self):
        return len(self.expenses) + sum(
                len(expense.parts) for expense in self.expenses
                )

def load(filename):
    with open(filename, 'r') as filedesc:
        return unpickle(filedesc)

