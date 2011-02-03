from PyQt4.QtCore import QAbstractItemModel, QAbstractTableModel, QModelIndex,\
     QVariant, Qt, SIGNAL

from .editors import EDITORS
from .velat import autoexpense, autoperson, autotransfer

class VelatTableModel(QAbstractTableModel):

    def __init__(self, window, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.window = window

    def rowCount(self, index=None):
        if self.window.velat is None:
            return 0
        return len(self.list)

    def columnCount(self, index=None):
        return len(self.COLNAMES)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return QVariant()
        item = self.list[index.row()]
        attribute = self.COL2ATTR[index.column()]
        if not attribute:
            return QVariant()
        value = getattr(item, attribute)
        return QVariant(value)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.list):
            item = self.list[index.row()]
            column = index.column()
            self._setvalue(item, column, value)
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if section >= len(self.COLNAMES):
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.COLNAMES[section]
        return section + 1

    def _list(self):
        if self.window.velat is None:
            return ()
        return self.window.velat.listfor(self.LISTNAME)

    list = property(fget=_list)

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.list.insert(position + row, self.factory())
        self.endInsertRows()
        return True

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.list))
        del self.list[:]
        self.endRemoveRows()

    def load(self):
        rows = len(self.list)
        if rows == 0:
            return
        self.beginInsertRows(QModelIndex(), 0, rows)
        self.endInsertRows()
        #this is too strong:
        self.reset()

    def flags(self, index):
        if not index.isValid() or not self.EDITABLE_COLS[index.column()]:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)

    def appenditem(self, item):
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        self.list.append(item)
        self.endInsertRows()
        return row + 1

    def removeitem(self, index):
        row = index.row()
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.list[row]
        self.endRemoveRows()

    def edititem(self, index):
        item = self.list[index.row()]
        EDITORS[self.LISTNAME](self.window, item).exec_()


class PersonsModel(VelatTableModel):

    LISTNAME = "person"
    COL2ATTR = ("name", "totalpaid", "totalowed")
    COLNAMES = ("Name", "Total paid", "Total owed")
    EDITABLE_COLS = (True, False, False)

    def factory(self):
        return autoperson()

    def _setvalue(self, person, column, value):
        if column == 0:
            person.name = unicode(value.toString())
        if column == 3:
            person.information = unicode(value.toString())


class TransfersModel(VelatTableModel):

    LISTNAME = "transfer"
    COL2ATTR = ("givername", "receivername", "value", "context")
    COLNAMES = ("giver", "receiver", "value", "Context")
    EDITABLE_COLS = (False,) * len(COLNAMES) #actually none, we'll show a popup

    def factory(self):
        return autotransfer()

    def _setvalue(self, transfer, column, value):
        print column, value


class ExpensesModel(QAbstractItemModel):

    LISTNAME = "expense"
    COL2ATTR = ("name", "paidfor_property", "ppl_nb_property", "", "", "", "", "")
    COLNAMES = (
        "Expense, cost, Persons involved", #cols for expense
        "Person", "Sum paid", "Parts taken", "Value taken", "Comment" #PartTaking
        )
    EDITABLE_COLS = (False,) * len(COLNAMES) #actually none, we'll show a popup
    _COLS_NB = len(COLNAMES)


    def __init__(self, window, parent=None, *args):
        QAbstractItemModel.__init__(self, parent, *args)
        self.window = window

    def _row_to_item(self, row):
        #so that we get 0 on first expense
        current_row = -1

        for exp_index, expense in enumerate(self.window.velat.expenses):
            current_row += 1
            if current_row == row:
                return expense
            parts_nb = expense.parts_nb
            if row >= current_row + parts_nb:
                current_row += parts_nb
                continue
            return expense.parts[row - current_row]

    def parent(self, child):
        value = VelatTableModel.parent(child)
        print "parent of child", child, '->', value
        return value

    def load(self):
        pass

    def columnCount(self, index):
        return self._COLS_NB

    def rowCount(self, index):
        return self.window.velat.len_expenses_and_parts()

