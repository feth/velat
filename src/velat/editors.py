from PyQt4.QtGui import QDialog, QMessageBox

from .expense_edit_ui import Ui_expensedialog
from .person_edit_ui import Ui_persondialog
from .transfer_edit_ui import Ui_transferdialog
from .velat import autoperson, autoexpense, autotransfer


def _autotransfer_gui(window):
    if len(window.velat.persons) < 2:
        window.say("Cannot create a transfer between less than 2 persons.")
        QMessageBox.information(
            window,
            "Impossible operation",
            "I cannot create a transfer between less than 2 persons, "
            "you may want to create some persons first."
            )
        return
    dialog = TransferDialog(window)
    if dialog.exec_() == dialog.Rejected:
        return None
    return dialog.transfer


class TransferDialog(QDialog, Ui_transferdialog):
    def __init__(self, window, transfer=None):
        #window as parent
        QDialog.__init__(self, window)
        self.setupUi(self)
        for combo in self.giver, self.receiver:
            combo.setModel(window.personsmodel)

        self.window = window

        new = transfer is None

        if new:
            transfer = autotransfer()
        else:
            for word in 'giver', 'receiver':
                combo = getattr(self, word)
                person = getattr(transfer, word)
                index = self.window.velat.persons.index(person)
                combo.setCurrentIndex(index)

        self.value.setValue(transfer.value)
        self.transfer = transfer

    def accept(self):
        self.transfer.save()

        self._reportvalues()

        errormsg = self.transfer.error_msg()
        if errormsg:
            QMessageBox.warning(
                self,
                "Incorrect input",
                errormsg
                )
            self.transfer.restore()
            return

        QDialog.accept(self)

    def _reportvalues(self):
        for item in "giver receiver".split():
            setattr(
                self.transfer,
                item,
                self.window.velat.persons[getattr(self, item).currentIndex()]
                )
        self.transfer.value = self.value.value()
        self.transfer.context = unicode(self.context.toPlainText())


class PersonsDialog(QDialog, Ui_persondialog):
    def __init__(self, window, person):
        self.window = window
        self.person = person

        QDialog.__init__(self, window)
        self.setupUi(self)

        self.name.setText(self.person.name)
        self.information.setPlainText(self.person.information)

    def accept(self):
        if not unicode(self.name.text()):
            QMessageBox.warning(
                self,
                "Incorrect input",
                "Person name cannot be empty"
                )
            return

        self._reportvalues()
        QDialog.accept(self)

    def _reportvalues(self):
        self.person.name = unicode(self.name.text())
        self.person.information = unicode(self.information.toPlainText())


class ExpensesDialog(QDialog, Ui_expensedialog):
    def __init__(self, window, expense):
        self.window = window
        self.expense = expense

        QDialog.__init__(self, window)
        self.setupUi(self)

EDITORS = {
    'expense': ExpensesDialog,
    'person': PersonsDialog,
    'transfer': TransferDialog,
    }

ITEM_FACTORIES = {
    'person': autoperson,
    'expense': autoexpense,
    'transfer': _autotransfer_gui,
    }
