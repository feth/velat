#coding: utf-8

from PyQt4.QtCore import QObject, Qt, SIGNAL
from PyQt4.QtGui import QAbstractItemView, QCursor, QFileDialog, QInputDialog,\
     QLineEdit, QMainWindow, QMenu, QMessageBox

from .editors import EDITORS, ITEM_FACTORIES, PersonsDialog
from .gui_ui import Ui_velatwin
from .models import ExpensesModel, PersonsModel, TransfersModel
from .velat import Velat, load


FILEFILTER = "Velat files (*.vl);;All files (*)"

EXPENSE_ROLE = Qt.UserRole + 1


def shortentext(text, maxlen, keep_start, keep_end):
    if len(text) <= maxlen:
        return text
    return u"%s…%s" % (text[:keep_start], text[- keep_end:])


def bindclicked(button, function):
    QObject.connect(button, SIGNAL("clicked()"), function)


def _show_row(model, view, row):
    view.setFocus()
    view.setCurrentIndex(model.index(row, 0))


def _selected_rows(view):
    """
    returns Qt indexes, one per row (lowest column)
    """
    indexes = {}
    for index in view.selectedIndexes():
        row = index.row()
        if row not in indexes:
            indexes[row] = index, index.column()
            continue
        column = index.column()
        if column > indexes[row][1]:
            continue
        indexes[row] = index, column

    return tuple(
        index
        for index, column
        in indexes.values()
        )


class Window(Ui_velatwin, QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.statusbar = self.statusBar()

        self.cur_directory = "."
        self.currentfile = ""
        self.velat = None

        self.personsmodel = PersonsModel(self)
        self.expensesmodel = ExpensesModel(self)
        self.transfersmodel = TransfersModel(self)

        self.persons.setModel(self.personsmodel)
        self.transfers.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.expenses.setModel(self.expensesmodel)
        self.transfers.setModel(self.transfersmodel)

        for word in ITEM_FACTORIES:
            self._mknew_factory(word)
            self._edit_factory(word)
            self._remove_factory(word)
            self._menu_factory(word)

        self.setup_signals()

        self.mknewinstance()

    def _addmethod(self, method, methodname):
        method.__name__ = methodname
        setattr(self, methodname, method)

    def _mknew_factory(self, word):
        item_factory = ITEM_FACTORIES[word]
        model = self._model(word)
        view = self._view(word)
        resize = word in 'person transfer'

        def mknew():
            item = item_factory(self)
            if not item:
                return

            row = model.appenditem(item)
            self.say("%s added: '%s'" % (word, item))
            _show_row(model, view, row)
            if resize:
                view.resizeRowsToContents()
            self.setWindowModified(True)

        self._addmethod(mknew, 'mknew%s' % word)

    def _remove_factory(self, word):
        model = self._model(word)
        view = self._view(word)

        def remove():
            for index in _selected_rows(view):
                if QMessageBox.Cancel == QMessageBox.question(
                    self,
                    "Confirm deletion",
                    "Are you sure that you want to delete this item?",
                    QMessageBox.Ok | QMessageBox.Cancel
                    ):
                    return
                model.removeitem(index)

        self._addmethod(remove, 'remove%s' % word)


    def _edit_factory(self, word):
        editorklass = EDITORS[word]
        model = self._model(word)
        view = self._view(word)
        plural = "%ss" % word

        def editor():
            for index in _selected_rows(view):
                model.edititem(index)
        setattr(self, 'editview%s' % word, editor)

        def edititem(point):
            index = view.indexAt(point)
            if not index.isValid():
                return
            def removeitem():
                if QMessageBox.Cancel == QMessageBox.question(
                    self,
                    "Confirm deletion",
                    "Are you sure that you want to delete this item?",
                    QMessageBox.Ok | QMessageBox.Cancel
                    ):
                    return
                model.removeitem(index)
            def edititem():
                container = getattr(self.velat, plural)
                editorklass(self, container[index.row()]).exec_()
            menu = QMenu()
            menu.addAction("Edit item", getattr(self, 'edit%s' % word))
            menu.addAction("Delete item", getattr(self, 'remove%s' % word))
            menu.exec_(QCursor.pos())

    def _menu_factory(self, word):
        view = self._view(word)

        def mkmenu():
            menu = QMenu()
            menu.addAction("Edit item", getattr(self, 'editview%s' % word))
            menu.addAction("Delete item", getattr(self, 'remove%s' % word))
            menu.exec_(QCursor.pos())

        self.connect(view, SIGNAL("customContextMenuRequested(QPoint)"), mkmenu)

    def closeEvent(self, event):
        """
        Overriding closeEvent to offer emergency save
        """
        if self.isWindowModified() and self.cancelor(
            "Discard modifications?",
            """<div>
            Current balance is modified, here are your options:
            <ul>
                <li>Ignore modifications and close anyway<li>
                <li>%s and close<li>
                <li>Cancel closing and go back to edition<li>
            </ul>
            </div>""",
            "Close operation cancelled.",
            ):
            event.ignore()
            return
        event.accept()

    def say(self, message):
        self.statusbar.showMessage(message)

    def setcurrentfile(self, filename):
        self.currentfile = filename
        self._reset_title()
        button_hover = "Save to file '%s'" % self.currentfile
        if not self.currentfile:
            button_text = "Save to file"
            button_hover = "Select the file for save"
        else:
            button_text = "Save to '%s'" % shortentext(self.currentfile, 15, 7, 7)
        self.save.setText(button_text)
        self.save.setToolTip(button_hover)

    def _reset_title(self):
        filepart = " (%s)" % self.currentfile if self.currentfile else ""
        self.setWindowTitle("[*]%s%s - Velat"% (self.velat.name, filepart))

    def setbalancename(self):
        name, changed = QInputDialog.getText(
            self,
            "Set balance name",
            "Set the name for current balance",
            QLineEdit.Normal,
            self.velat.name
            )

        if not changed:
            return

        self.velat.name = unicode(name)
        self._displayname()
        self.setWindowModified(True)

    def itermodels(self):
        yield self.personsmodel
        yield self.expensesmodel
        yield self.transfersmodel

    def loadfile(self):
        if self.cancelor(
            "Discard modifications?",
            """<div>
            Current balance is modified, here are your options:
            <ul>
                <li>Ignore modifications and open another file<li>
                <li>%s and open another file<li>
                <li>Cancel new file and go back to edition<li>
            </ul>
            </div>""",
            "Load file cancelled"
            ):
            return

        filename = QFileDialog.getOpenFileName(
            self,
            "Open a velat file",
            self.cur_directory,
            FILEFILTER
        )
        if not filename:
            return

        for model in self.itermodels():
            model.clear()
        self.velat = load(filename)
        self._load_data(filename)
        self.say("Loaded session from file %s" % self.currentfile)
        self.setWindowModified(False)

    def _load_data(self, filename):
        """
        all data is loaded from self.velat but the file name
        because the file name is not stored at all.
        """
        self._displayname()
        for model in self.itermodels():
            model.load()
        self.freeform.document().setPlainText(self.velat.description)
        self.setcurrentfile(filename)
        for table in self.persons, self.transfers:
            table.resizeRowsToContents()

    def _displayname(self):
        displayed = self.velat.name
        self.balancename.setToolTip(displayed)
        self.balancename.setText(shortentext(displayed, 25, 10, 10))
        self._reset_title()

    def getsavefilename(self):
        filename = QFileDialog.getSaveFileName(
            self,
            "Save a velat file",
            self.cur_directory,
            FILEFILTER
        )
        return filename

    def savefile(self):
        if not self.currentfile:
            #dialog to ask for one
            self.setcurrentfile(self.getsavefilename())

        if not self.currentfile:
            #we got cancellation
            return False

        self.velat.save(self.currentfile)
        self.velat.description = unicode(self.freeform.toPlainText())
        self.say("Session saved into file %s" % self.currentfile)
        self.setWindowModified(False)
        return True

    def savefileas(self):
        savedcurrentfile = self.currentfile
        self.currentfile = ''
        if not self.savefile():
            #restore
            self.currentfile = savedcurrentfile

    def _menuhelper(self, word):

        editorklass = EDITORS[word]
        word = '%ss' % word
        view = getattr(self, '%s' % word)
        model = getattr(self, '%smodel' % word)

        def callback(point):
            index = view.indexAt(point)
            if not index.isValid():
                return
            menu = QMenu()
            def removeitem():
                if QMessageBox.Cancel == QMessageBox.question(
                    self,
                    "Confirm deletion",
                    "Are you sure that you want to delete this item?",
                    QMessageBox.Ok | QMessageBox.Cancel
                    ):
                    return
                model.removeitem(index)
            def edititem():
                container = getattr(self.velat, word)
                editorklass(self, container[index.row()]).exec_()
            menu.addAction("Edit item", edititem)
            menu.addAction("Delete item", removeitem)
            menu.exec_(QCursor.pos())
        return view, callback

    def _bindbuttons(self, tablename):
        for prefix, methodprefix in (
            ('new', 'mknew'), ('edit', 'editview'), ('rem', 'remove')
            ):
            bindclicked(
                getattr(self, '%s%s' % (prefix, tablename)),
                getattr(self, '%s%s' % (methodprefix, tablename))
                )

    def setup_signals(self):
        bindclicked(self.load, self.loadfile)
        bindclicked(self.save, self.savefile)
        bindclicked(self.saveas, self.savefileas)
        bindclicked(self.balancename, self.setbalancename)
        bindclicked(self.newinstance, self.mknewinstance)

        for word in "expense person transfer".split():
            self._bindbuttons(word)

    def personsmenu(self, point):
        index = self.persons.indexAt(point)
        if not index.isValid():
            return
        menu = QMenu()
        def removeitem():
            if QMessageBox.Cancel == QMessageBox.question(
                self,
                "Confirm deletion",
                "Are you sure that you want to delete this item?",
                QMessageBox.Ok | QMessageBox.Cancel
                ):
                return
            self.personsmodel.removeitem(index)
        def edititem():
            PersonsDialog(self, self.velat.persons[index.row()]).exec_()
        menu.addAction("Edit item", edititem)
        menu.addAction("Delete item", removeitem)
        menu.exec_(QCursor.pos())

    def _model(self, word):
        return getattr(self, '%ssmodel' % word)

    def _view(self, word):
        return getattr(self, '%ss' % word)

    def editviewexpense(self):
        print "STUB: editviewexpense"

    def editviewtransfer(self):
        print "STUB: editviewtransfer"

    def removeperson(self):
        print "STUB: removeperson"

    def removeexpense(self):
        print "STUB: removeexpense"

    def removetransfer(self):
        print "STUB: removetransfer"


    def cancelor(self, title, message, cancel_message):
        """
        Message should contain a %s placeholder for the message part
        [save in file '/tmp/file'] in
        "save in file '/tmp/file' and make cofee"
        """
        if not self.isWindowModified():
            return False
        want = QMessageBox.question(
            self,
            title,
            message % self._savemsg(),
            QMessageBox.Ignore | QMessageBox.Save |QMessageBox.Cancel
            )
        if want == QMessageBox.Cancel:
            return True
        if want == QMessageBox.Save:
            if not self.savefile():
                title = "Save cancelled."
                self.say("%s %s" % (title, cancel_message))
                QMessageBox.information(
                    self,
                    title,
                    cancel_message
                    )
                return True

        return False

    def mknewinstance(self):
        if self.cancelor(
            "Discard modifications?",
            """<div>
            Current balance is modified, here are your options:
            <ul>
                <li>Ignore modifications and start anew<li>
                <li>%s and start anew<li>
                <li>Cancel new file and go back to edition<li>
            </ul>
            </div>""",
            "New balance cancelled",
            ):
            return

        self.velat = Velat()
        self.velat.name = "Untitled balance"
        self._load_data("")
        self.say("New empty balance")
        self.setWindowModified(False)

    def _savemsg(self):
        if self.currentfile:
            return "Save modifications in %s" % self.currentfile
        return "Save modifications (select file)"

