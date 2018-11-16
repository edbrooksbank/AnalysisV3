"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = ""
__credits__ = ""
__licence__ = ("")
__reference__ = ("")
#=========================================================================================
# Last code modification:
#=========================================================================================
__modifiedBy__ = "$modifiedBy$"
__dateModified__ = "$dateModified$"
__version__ = "$Revision$"
#=========================================================================================
# Created:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

import json
import re

from PyQt5 import QtGui, QtCore, QtWidgets
import pandas as pd
import os
from types import MethodType
from contextlib import contextmanager

from collections import Iterable
from pyqtgraph import TableWidget
from pyqtgraph.widgets.TableWidget import _defersort, TableWidgetItem
from ccpn.core.lib.CcpnSorting import universalSortKey
from ccpn.core.lib.CallBack import CallBack
from ccpn.core.lib.DataFrameObject import DataFrameObject, DATAFRAME_OBJECT, \
    DATAFRAME_INDEX, DATAFRAME_HASH, DATAFRAME_PID

from ccpn.ui.gui.guiSettings import getColours

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets import MessageDialog
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Splitter import Splitter
from ccpn.ui.gui.widgets.TableModel import ObjectTableModel
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.TableFilter import ObjectTableFilter
from ccpn.ui.gui.widgets.ColumnViewSettings import ColumnViewSettingsPopup
from ccpn.ui.gui.widgets.TableModel import ObjectTableModel
from ccpn.ui.gui.widgets.SearchWidget import attachSearchWidget
from ccpn.core.lib.Notifiers import Notifier
from ccpn.ui.gui.widgets.DropBase import DropBase
from ccpn.ui.gui.lib.GuiNotifier import GuiNotifier
from ccpn.util.Common import makeIterableList
from functools import partial
from collections import OrderedDict

from collections import OrderedDict
from ccpn.util.Logging import getLogger
from types import SimpleNamespace
from contextlib import contextmanager

# BG_COLOR = QtGui.QColor('#E0E0E0')
# TODO:ED add some documentation here

OBJECT_CLASS = 0
OBJECT_PARENT = 1


def __ltForTableWidgetItem__(self, other):
    # new routine to overload TableWidgetItem that crashes when sorting None
    if self.sortMode == 'index' and hasattr(other, 'index'):
        return self.index < other.index
    if self.sortMode == 'value' and hasattr(other, 'value'):
        return (universalSortKey(self.value) < universalSortKey(other.value))
    else:
        if self.text() and other.text():
            return (universalSortKey(self.text()) < universalSortKey(other.text()))
        else:
            return False


def __sortByColumn__(self, col, newOrder):
    try:
        # QtWidgets.QTableWidget.sortByColumn(self, col, newOrder)
        super(QtWidgets.QTableWidget, self).sortByColumn(col, newOrder)
    except Exception as es:
        print(str(es))
    print('>>>sorting')


# define a simple class that can contains a simple id
blankId = SimpleNamespace(className='notDefined', serial=0)

MODULEIDS = {}


def _moduleId(module):
    return MODULEIDS[id(module)] if id(module) in MODULEIDS else -1


# Exporters

def dataFrameToExcel(dataFrame, path, sheet_name='Table', columns=None):
    if dataFrame is not None:

        if columns is not None and isinstance(columns, list): #this is wrong. columns can be a 1d array
            dataFrame.to_excel(path, sheet_name=sheet_name, columns=columns)
        else:
            dataFrame.to_excel(path, sheet_name=sheet_name)


def dataFrameToCsv( dataFrameObject, path, *args):
    dataFrameObject.dataFrame.to_csv(path)

def dataFrameToTsv( dataFrameObject, path, *args):
    dataFrameObject.dataFrame.to_csv(path, sep='\t')

def dataFrameToJson(self, dataFrameObject, path, *args):
    dataFrameObject.dataFrame.to_json(path, orient='split')

# def tableToDataFrame(self):
#     return self._dataFrameObject.dataFrame[self._dataFrameObject.visibleColumnHeadings]

def findExportFormats(path, dataFrame, sheet_name='Table', filterType=None, columns=None):
    formatTypes = OrderedDict([
        ('.xlsx', dataFrameToExcel),
        ('.csv', dataFrameToCsv),
        ('.tsv', dataFrameToTsv),
        ('.json', dataFrameToJson)
    ])

    extension = os.path.splitext(path)[1]
    if extension in formatTypes.keys():
        formatTypes[extension](dataFrame, path, sheet_name, columns)
        return
    else:
        try:
            findExportFormats(str(path) + filterType, sheet_name)
        except:
            getLogger().warning('Format file not supported')


def exportTableDialog(dataFrame, columns=None):
    """Open the ExportDialog to export any dataFrame to different formats """
    if dataFrame is None:
        return
    saveDialog = FileDialog(directory='ccpn_Table.xlsx',  # default saving name
                                 fileMode=FileDialog.AnyFile,
                                 filter=".xlsx;; .csv;; .tsv;; .json ",
                                 text='Save as ',
                                 acceptMode=FileDialog.AcceptSave,
                                 preferences=None)
    path = saveDialog.selectedFile()
    filterType = saveDialog.selectedNameFilter()
    if path:
        findExportFormats(path, dataFrame, filterType=filterType, columns=columns)





class QuickTable(TableWidget, Base):
    ICON_FILE = os.path.join(os.path.dirname(__file__), 'icons', 'editable.png')

    styleSheet = """
QuickTable {
    background-color: %(QUICKTABLE_BACKGROUND)s;
    alternate-background-color: %(QUICKTABLE_ALT_BACKGROUND)s;
}

QuickTable::item {
    padding: 2px;
    color: %(QUICKTABLE_ITEM_FOREGROUND)s;
}

QuickTable::item::selected {
    background-color: %(QUICKTABLE_SELECTED_BACKGROUND)s;
    color: %(QUICKTABLE_SELECTED_FOREGROUND)s;
}"""

    def __init__(self, parent=None,
                 mainWindow=None,
                 dataFrameObject=None,  # collate into a single object that can be changed quickly
                 actionCallback=None, selectionCallback=None, checkBoxCallback=None,
                 multiSelect=False, selectRows=True, numberRows=False, autoResize=False,
                 enableExport=True, enableDelete=True, enableSearch=True,
                 hideIndex=True, stretchLastSection=True,
                 **kwds):
        """
        Create a new instance of a TableWidget with an attached Pandas dataFrame
        :param parent:
        :param mainWindow:
        :param dataFrameObject:
        :param actionCallback:
        :param selectionCallback:
        :param multiSelect:
        :param selectRows:
        :param numberRows:
        :param autoResize:
        :param enableExport:
        :param enableDelete:
        :param hideIndex:
        :param kwds:
        """
        super().__init__(parent)
        Base._init(self, **kwds)

        self._parent = parent

        # set the application specfic links
        self.mainWindow = mainWindow
        self.application = None
        self.project = None
        self.current = None

        if self.mainWindow:
            self.application = mainWindow.application
            self.project = mainWindow.application.project
            self.current = mainWindow.application.current
        self.moduleParent = None

        # initialise the internal data storage
        self._dataFrameObject = dataFrameObject
        self._tableBlockingLevel = 0
                
        # set stylesheet
        self.colours = getColours()
        styleSheet = self.styleSheet % self.colours
        self.setStyleSheet(styleSheet)
        self.setAlternatingRowColors(True)

        # set the preferred scrolling behaviour
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerItem)

        # define the multiselection behaviour
        self.multiSelect = multiSelect
        if multiSelect:
            self.setSelectionMode(self.ExtendedSelection)
        else:
            self.setSelectionMode(self.SingleSelection)

        # define the set selection behaviour
        self.selectRows = selectRows
        if selectRows:
            self.setSelectionBehavior(self.SelectRows)
        else:
            self.setSelectionBehavior(self.SelectItems)

        self._checkBoxCallback = checkBoxCallback
        # set all the elements to the same size
        self.hideIndex = hideIndex
        self._setDefaultRowHeight()

        # enable sorting and sort on the first column
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # enable drag and drop operations on the table - why not working?
        self.setDragEnabled(True)
        self.acceptDrops()
        self.setDragDropMode(self.InternalMove)
        self.setDropIndicatorShown(True)

        # set Interactive and last column to expanding
        self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(stretchLastSection)
        self.horizontalHeader().setResizeContentsPrecision(-1)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # enable the right click menu
        self.searchWidget = None
        self._setHeaderContextMenu()
        self._setContextMenu(enableExport=enableExport, enableDelete=enableDelete)
        self._enableSearch = enableSearch

        # populate if a dataFrame has been passed in
        if dataFrameObject:
            self.setTableFromDataFrame(dataFrameObject.dataFrame)

        # enable callbacks
        self._actionCallback = actionCallback
        self._selectionCallback = selectionCallback
        #self._silenceCallback = False
        
        if self._actionCallback:
            self.doubleClicked.connect(self._doubleClickCallback)
        else:
            self.doubleClicked.connect(self._defaultDoubleClick)
        # if self._selectionCallback:
        #     self.itemClicked.connect(self._cellClicked)

        # set the delegate for editing
        delegate = QuickTableDelegate(self)
        self.setItemDelegate(delegate)

        # set the callback for changing selection on table
        model = self.selectionModel()
        model.selectionChanged.connect(self._selectionTableCallback)

        # self.horizontalHeader().sortIndicatorChanged.connect(self._sortChanged)
        # self.horizontalHeader().sectionPressed.connect(self._preSort)
        self.horizontalHeader().sectionClicked.connect(self._postSort)

        # set internal flags
        self._mousePressed = False
        self._tableData = {}
        self._rawData = None  # this is set when called setData()
        self._tableNotifier = None
        self._rowNotifier = None
        self._cellNotifiers = []
        self._selectCurrentNotifier = None
        self._searchNotifier = None
        self._droppedNotifier = None
        self._icons = [self.ICON_FILE]
        self._stretchLastSection = stretchLastSection

        # set the minimum size the table can collapse to
        self.setMinimumSize(30, 30)
        self.searchWidget = None
        # self._parent.layout().setVerticalSpacing(0)

        self.setDefaultTableData()

        self._currentSorted = False
        self._newSorted = False

        TableWidgetItem.__lt__ = __ltForTableWidgetItem__

        # TableWidget.sortByColumn = __sortByColumn__   #MethodType(__sortByColumn__, TableWidget)

    @contextmanager
    def _tableBlockSignals(self, callerId=''):
        """Block all signals from the table
        """
        try:
            # block on first entry
            if self._tableBlockingLevel <= 0:
                # self._tableBlockingLevel = 0
                self.blockSignals(True)
                self.selectionModel().blockSignals(True)
                self.setUpdatesEnabled(False)
                self.project.blankNotification()

            print(' ' * self._tableBlockingLevel, '>>>INC', self._tableBlockingLevel, _moduleId(self.moduleParent), callerId)
            self._tableBlockingLevel += 1
            yield  # yield control to the main process

        finally:
            self._tableBlockingLevel -= 1
            # print(' ' * self._tableBlockingLevel, '>>>DEC', self._tableBlockingLevel, _moduleId(self.moduleParent))

            # unblock all signals on exit
            if self._tableBlockingLevel <= 0:
                # self._tableBlockingLevel = 0
                self.project.unblankNotification()
                self.setUpdatesEnabled(True)
                self.selectionModel().blockSignals(False)
                self.blockSignals(False)

    def _preSort(self, *args):
        """
        catch the press event on a header
        """
        # header = self.horizontalHeader()
        # print ([header.columnSpan(0, col) for col in range(header.count())])
        pass

    def _postSort(self, *args):
        """
        catch the click event on a header
        """
        print('>>> %s _postSort' % _moduleId(self.moduleParent))

        self.resizeColumnsToContents()

    @staticmethod
    def _getCommentText(obj):
        """
        CCPN-INTERNAL: Get a comment from QuickTable
        """
        try:
            if obj.comment == '' or not obj.comment:
                return ''
            else:
                return obj.comment
        except:
            return ''

    @staticmethod
    def _setComment(obj, value):
        """
        CCPN-INTERNAL: Insert a comment into QuickTable
        """
        # ejb - why is it blanking a notification here?
        # NmrResidueTable._project.blankNotification()
        obj.comment = value if value else None
        # NmrResidueTable._project.unblankNotification()

    def _sortChanged(self, col, sortOrder: QtCore.Qt.SortOrder):
        # sort the _dataFrame to match
        # need to read the sorted state when repopulating table
        # this is also called when the table is populated from the pulldown :)
        return

        print('>>>tableSorting', col, sortOrder)
        print('>>>currentIndex', self.currentIndex())

        rows = list(range(self.rowCount()))
        columns = list(range(self.columnCount()))
        headings = []
        for c in columns:
            hi = self.horizontalHeaderItem(c)
            if hi:
                headings.append(self.horizontalHeaderItem(c).text())
            else:
                headings.append('*')

        print(headings)
        if DATAFRAME_PID in headings:
            pidCol = headings.index(DATAFRAME_PID)
            pids = []
            for r in rows:
                pids.append(self.item(r, pidCol).value)
            print(pids)

        self._newSorted = True

    def setActionCallback(self, actionCallback):
        # enable callbacks
        self._actionCallback = actionCallback
        if self._actionCallback:
            self.doubleClicked.connect(self._doubleClickCallback)
        else:
            self.doubleClicked.connect(self._defaultDoubleClick)

    def setSelectionCallback(self, selectionCallback):
        # enable callbacks
        self._selectionCallback = selectionCallback
        if self._selectionCallback:
            self.itemClicked.connect(self._cellClicked)

    def _handleDroppedItems(self, pids, objType, pulldown):
        """
        :param pids: the selected objects pids
        :param objType: the instance of the obj to handle. Eg. PeakList
        :param pulldown: the pulldown of the module wich updates the table
        :return: Actions: Select the dropped item on the table or/and open a new modules if multiple drops.
        If multiple different obj instances, then asks first.
        """
        from ccpn.ui.gui.widgets.SideBar import _openItemObject

        objs = [self.project.getByPid(pid) for pid in pids]

        selectableObjects = [obj for obj in objs if isinstance(obj, objType)]
        others = [obj for obj in objs if not isinstance(obj, objType)]
        if len(selectableObjects) > 0:
            pulldown.select(selectableObjects[0].pid)
            _openItemObject(self.mainWindow, selectableObjects[1:])

        else:
            from ccpn.ui.gui.widgets.MessageDialog import showYesNo

            othersClassNames = list(set([obj.className for obj in others]))
            if len(othersClassNames) > 0:
                if len(othersClassNames) == 1:
                    title, msg = 'Dropped wrong item.', 'Do you want to open the %s in a new module?' % ''.join(othersClassNames)
                else:
                    title, msg = 'Dropped wrong items.', 'Do you want to open items in new modules?'
                openNew = showYesNo(title, msg)
                if openNew:
                    _openItemObject(self.mainWindow, others)

    def _cellClicked(self, item):
        print('>>> %s _cellClicked' % _moduleId(self.moduleParent))

        if item:
            if isinstance(item.value, bool):
                self._checkBoxTableCallback(item)
            try:
                if self._selectionCallback:
                    self._currentRow = item.row()
                    self._currentCol = item.column()
            except:
                # Fixme
                # item has been deleted error
                pass
        #

    def _checkBoxCallback(self, data):
        print('>>> %s _checkBoxCallback' % _moduleId(self.moduleParent))

        pass

    def _defaultDoubleClick(self, itemSelection):

        print('>>> %s _defaultDoubleClick' % _moduleId(self.moduleParent))

        model = self.selectionModel()

        # selects all the items in the row
        selection = model.selectedIndexes()

        if selection:
            row = itemSelection.row()
            col = itemSelection.column()
            if self._dataFrameObject:
                if self._dataFrameObject.columnDefinitions.setEditValues[col]:  # ejb - editable fields don't actionCallback:

                    item = self.item(row, col)
                    item.setEditable(True)
                    # self.itemDelegate().closeEditor.connect(partial(self._changeMe, row, col))
                    # item.textChanged.connect(partial(self._changeMe, item))
                    self.editItem(item)

    def _doubleClickCallback(self, itemSelection):

        with self._tableBlockSignals('_doubleClickCallback'):
            model = self.selectionModel()

            # selects all the items in the row
            selection = model.selectedIndexes()

            if selection:
                row = itemSelection.row()
                col = itemSelection.column()
                # row = self._currentRow        # read from the cellClicked connect
                # col = self._currentCol

                data = {}
                for iSelect in selection:
                    colPid = iSelect.column()
                    colName = self.horizontalHeaderItem(colPid).text()
                    data[colName] = model.model().data(iSelect)

                objIndex = data['Pid']
                # obj = self._dataFrameObject.indexList[objIndex]    # item.index needed

                obj = self.project.getByPid(objIndex)

                if obj:
                    data = CallBack(theObject=self._dataFrameObject,
                                    object=obj,
                                    index=objIndex,
                                    targetName=obj.className,
                                    trigger=CallBack.DOUBLECLICK,
                                    row=row,
                                    col=col,
                                    rowItem=data)

                    if self._actionCallback and self._dataFrameObject and not \
                            self._dataFrameObject.columnDefinitions.setEditValues[col]:  # ejb - editable fields don't actionCallback
                        self._actionCallback(data)

                    elif self._dataFrameObject and self._dataFrameObject.columnDefinitions.setEditValues[col]:  # ejb - editable fields don't actionCallback:
                        item = self.item(row, col)
                        item.setEditable(True)
                        # self.itemDelegate().closeEditor.connect(partial(self._changeMe, row, col))
                        # item.textChanged.connect(partial(self._changeMe, item))
                        self.editItem(item)  # enter the editing mode
                    else:
                        if self._actionCallback:
                            self._actionCallback(data)

    @_defersort
    def setRow(self, row, vals):
        if row > self.rowCount() - 1:
            self.setRowCount(row + 1)
        for col in range(len(vals)):
            val = vals[col]
            item = self.itemClass(val, row)
            item.setEditable(self.editable)
            sortMode = self.sortModes.get(col, None)
            if sortMode is not None:
                item.setSortMode(sortMode)
            format = self._formats.get(col, self._formats[None])
            item.setFormat(format)
            self.items.append(item)
            self.setItem(row, col, item)

            # item.setValue(val)  # Required--the text-change callback is invoked
            # when we call setItem.
            if isinstance(val, bool):  # this will create a check box if the value is a bool
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                state = 2 if val else 0
                item.setCheckState(state)

            if isinstance(val, list or tuple):
                pulldown = PulldownList(None, )
                pulldown.setData(*val)
                self.setCellWidget(row, col, pulldown)


            else:
                item.setValue(val)

    def _changeMe(self, row, col, widget, endEditHint):
        text = widget.text()
        # TODO:ED process setting of object in here

        item = self.item(row, col)

        print('>>>changeMe', row, col)

        # obj = self._dataFrameObject.objects[row]
        # self._dataFrameObject.columnDefinitions.setEditValues[col](obj, text)
        pass

    def _selectionTableCallback(self, itemSelection):
        # TODO:ED generate a callback dict for the selected item
        # data = OrderedDict()
        # data['OBJECT'] = return pid, key/values, row, col

        with self._tableBlockSignals('_selectionTableCallback'):
            if not self._selectionCallback:
                return

            print('>>> %s _selectionTableCallback__' % _moduleId(self.moduleParent))

            # # if not self._silenceCallback:
            #
            # print('>>> %s _selectionTableCallback 3' % _moduleId(self.moduleParent))

            # if not self._mousePressed:
            objList = self.getSelectedObjects()
            # model = self.selectionModel()
            #
            # # selects all the items in the row
            # selection = model.selectedIndexes()
            #
            # if selection:
            # row = itemSelection.row()
            # col = itemSelection.column()
            #
            #   data = {}
            #   objList = []
            #   for iSelect in selection:
            #     col = iSelect.column()
            #     colName = self.horizontalHeaderItem(col).text()
            #     data[colName] = model.model().data(iSelect)
            #
            #     objIndex = data['Pid']
            #     obj = self.project.getByPid(objIndex)
            #     if obj:
            #       objList.append(obj)

            if objList:
                data = CallBack(theObject=self._dataFrameObject,
                                object=objList,
                                index=0,
                                targetName=objList[0].className,
                                trigger=CallBack.DOUBLECLICK,
                                row=0,
                                col=0,
                                rowItem=None)

                self._selectionCallback(data)

    def _checkBoxTableCallback(self, itemSelection):
        print('>>> %s _checkBoxTableCallback' % _moduleId(self.moduleParent))

        state = True if itemSelection.checkState() == 2 else False
        value = itemSelection.value
        if not state == value:
            # if not self._silenceCallback:

            selectionModel = self.selectionModel()
            selectionModel.clearSelection()
            selectionModel.select(self.model().index(itemSelection.row(), 0),
                                  selectionModel.Select | selectionModel.Rows)
            objList = self.getSelectedObjects()

            if objList:
                data = CallBack(theObject=self._dataFrameObject,
                                object=objList,
                                index=0,
                                targetName=objList[0].className,
                                trigger=CallBack.DOUBLECLICK,
                                row=itemSelection.row(),
                                col=itemSelection.column(),
                                rowItem=itemSelection,
                                checked=state)
                textHeader = self.horizontalHeaderItem(itemSelection.column()).text()
                if textHeader:
                    self._dataFrameObject.setObjAttr(textHeader, objList[0], state)
                    # setattr(objList[0], textHeader, state)
            else:
                data = CallBack(theObject=self._dataFrameObject,
                                object=None,
                                index=0,
                                targetName=None,
                                trigger=CallBack.DOUBLECLICK,
                                row=itemSelection.row(),
                                col=itemSelection.column(),
                                rowItem=itemSelection,
                                checked=state)
            self._checkBoxCallback(data)

    def showColumns(self, dataFrameObject):
        # show the columns in the list
        for i, colName in enumerate(dataFrameObject.headings):
            if dataFrameObject.hiddenColumns:

                # always hide the special column DATAFRAME_OBJECT
                if colName in dataFrameObject.hiddenColumns or colName == DATAFRAME_OBJECT:
                    self.hideColumn(i)
                else:
                    self.showColumn(i)

                    if dataFrameObject.columnDefinitions.setEditValues[i]:

                        # need to put it into the header
                        header = self.horizontalHeaderItem(i)

                        icon = QtGui.QIcon(self._icons[0])
                        # item = self.item(0, i)
                        # TableWidget.QTableWidgetItem(icon, 'Boing')  # Second argument
                        # if item:
                        #   item.setIcon(icon)
                        #   self.setItem(0, i, item)
                        if header:
                            header.setIcon(icon)
            else:
                if colName == DATAFRAME_OBJECT:
                    self.hideColumn(i)

    def _setDefaultRowHeight(self):
        # set a minimum height to the rows based on the fontmetrics of a generic character
        self.fontMetric = QtGui.QFontMetricsF(self.font())
        self.bbox = self.fontMetric.boundingRect
        rowHeight = self.bbox('A').height() + 4

        # pyqt4
        # headers = self.verticalHeader()
        # headers.setResizeMode(QtWidgets.QHeaderView.Fixed)
        # headers.setDefaultSectionSize(rowHeight)

        # pyqt5
        headers = self.verticalHeader()
        headers.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        headers.setDefaultSectionSize(rowHeight)

        # and hide the row labels
        if self.hideIndex:
            headers.hide()

        # TODO:ED check pyqt5
        # for qt5 and above
        # QHeaderView * verticalHeader = myTableView->verticalHeader();
        # verticalHeader->setSectionResizeMode(QHeaderView::Fixed);
        # verticalHeader->setDefaultSectionSize(24);

    def mousePressEvent(self, event):
        """handle mouse press events
        Clicking is handled on the mouse release
        """
        self._lastClick = 'click'

        if event.button() == QtCore.Qt.RightButton:
            # stops the selection from the table when the right button is clicked
            event.accept()
        elif event.button() == QtCore.Qt.LeftButton:
            # self.clearSelection()
            # we are selecting from the table
            self._mousePressed = True
            event.ignore()
            super(QuickTable, self).mousePressEvent(event)
        else:
            event.ignore()
            super(QuickTable, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._mousePressed = False

        # print('>>>mouseReleaseEvent', self._lastClick)
        if self._lastClick == "click":
            QtCore.QTimer.singleShot(QtWidgets.QApplication.instance().doubleClickInterval(),
                                     partial(self._handleCellClicked, event))

        super(QuickTable, self).mouseReleaseEvent(event)

    def _handleCellClicked(self, event):
        """handle a single click event, but ignore double click events
        """
        if self._lastClick == "click":
            pos = QtCore.QPoint(event.pos())
            item = self.itemAt(pos)

            self._cellClicked(item)

    def mouseDoubleClickEvent(self, event):
        """set the doubleClick flag
        """
        self._lastClick = 'doubleClick'
        super(QuickTable, self).mouseDoubleClickEvent(event)

    def _setHeaderContextMenu(self):
        """Set up the context menu for the table header
        """
        headers = self.horizontalHeader()
        headers.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self._raiseHeaderContextMenu)

    def _getExportData(self):
        if self._dataFrameObject is not None:
            df = self._dataFrameObject.dataFrame
            return df
    def _getExportDataColums(self):
        if self._dataFrameObject is not None:
            visCol = self._dataFrameObject.visibleColumnHeadings
            return visCol

    def _setContextMenu(self, enableExport=True, enableDelete=True):
        self.tableMenu = QtWidgets.QMenu()
        if enableExport:
            self.tableMenu.addAction("Export Table", self.exportTableDialog)
        if enableDelete:
            self.tableMenu.addAction("Delete", self.deleteObjFromTable)

        # ejb - added these but don't think they are needed
        # self.tableMenu.addAction("Select All", self.selectAllObjects)
        self.tableMenu.addAction("Clear Selection", self.clearSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._raiseTableContextMenu)

    def _raiseTableContextMenu(self, pos):
        print('>>> %s _raiseTableContextMenu' % _moduleId(self.moduleParent))

        pos = QtCore.QPoint(pos.x() + 10, pos.y() + 10)
        action = self.tableMenu.exec_(self.mapToGlobal(pos))

    def _raiseHeaderContextMenu(self, pos):
        print('>>> %s _raiseHeaderContextMenu' % _moduleId(self.moduleParent))

        if self._enableSearch and self.searchWidget is None:
            if not attachSearchWidget(self._parent, self):
                getLogger().warning('Search option not available')

        pos = QtCore.QPoint(pos.x(), pos.y() + 10)  #move the popup a bit down. Otherwise can trigger an event if the pointer is just on top the first item

        self.headerContextMenumenu = QtWidgets.QMenu()
        columnsSettings = self.headerContextMenumenu.addAction("Columns Settings...")
        searchSettings = None
        if self._enableSearch and self.searchWidget is not None:
            searchSettings = self.headerContextMenumenu.addAction("Search")
        action = self.headerContextMenumenu.exec_(self.mapToGlobal(pos))

        if action == columnsSettings:
            settingsPopup = ColumnViewSettingsPopup(parent=self._parent, dataFrameObject=self._dataFrameObject)  #, hideColumns=self._hiddenColumns, table=self)
            settingsPopup.raise_()
            settingsPopup.exec_()  # exclusive control to the menu and return _hiddencolumns

        if action == searchSettings:
            self.showSearchSettings()

    def showSearchSettings(self):
        if self.searchWidget is not None:
            self.searchWidget.show()

    def deleteObjFromTable(self):
        selected = self.getSelectedObjects()
        if selected:
            n = len(selected)
            title = 'Delete Item%s' % ('' if n == 1 else 's')
            msg = 'Delete %sselected item%s from the project?' % ('' if n == 1 else '%d ' % n, '' if n == 1 else 's')
            if MessageDialog.showYesNo(title, msg):

                if hasattr(selected[0], 'project'):
                    thisProject = selected[0].project
                    thisProject._startCommandEchoBlock('application.table.deleteFromTable', [sI.pid for sI in selected])

                    # bug hunt
                    #self._silenceCallback = True
                    for obj in selected:
                        if hasattr(obj, 'pid'):
                            # print ('>>> deleting', obj)
                            obj.delete()
                    #self._silenceCallback = False
                    thisProject._endCommandEchoBlock()

                else:

                    # TODO:ED this is deleting from PandasTable, check for another way to get project
                    for obj in selected:
                        if hasattr(obj, 'pid'):
                            obj.delete()

        self.clearSelection()

    def refreshTable(self):
        self.setTableFromDataFrameObject(self._dataFrameObject)

    def refreshHeaders(self):
        self.hide()
        #self._silenceCallback = True
        # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.setHorizontalHeaderLabels(self._dataFrameObject.headings)
        self.showColumns(self._dataFrameObject)
        # self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(self._stretchLastSection)
        self.setColumnCount(self._dataFrameObject.numColumns)

        self.show()
        #self._silenceCallback = False
        self.resizeColumnsToContents()

        self.update()

        # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)

    # def resizeColumnsToContents(self):
    #   self.hide()
    #   self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    #   super(QuickTable, self).resizeColumnsToContents()
    #   self.show()
    #   self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)

    def setData(self, data):
        """Set the data displayed in the table.
        Allowed formats are:

        * numpy arrays
        * numpy record arrays
        * metaarrays
        * list-of-lists  [[1,2,3], [4,5,6]]
        * dict-of-lists  {'x': [1,2,3], 'y': [4,5,6]}
        * list-of-dicts  [{'x': 1, 'y': 4}, {'x': 2, 'y': 5}, ...]
        * Pandas Dataframes

        """
        if isinstance(data, pd.DataFrame):
            dataFrame = data.transpose()
            data = dataFrame.to_dict(into=OrderedDict)

        self.clear()
        self.appendData(data)
        self._rawData = data

    @contextmanager
    def _quickTableUpdate(self, dataFrameObject, resize=True):
        # keep the original sorting method
        sortOrder = self.horizontalHeader().sortIndicatorOrder()
        sortColumn = self.horizontalHeader().sortIndicatorSection()

        try:
            self.hide()
            #self._silenceCallback = True
            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            # self.setData(dataFrameObject.dataFrame.values)
            yield

        finally:
            # needed after setting the column headings
            self.setHorizontalHeaderLabels(dataFrameObject.headings)
            self.showColumns(dataFrameObject)
            # self.resizeColumnsToContents()
            self.horizontalHeader().setStretchLastSection(self._stretchLastSection)

            # required to make the header visible
            self.setColumnCount(dataFrameObject.numColumns)
            self.reindexTableObjects()

            # re-sort the table
            if sortColumn < self.columnCount():
                self.sortByColumn(sortColumn, sortOrder)

            if resize:
                self.resizeColumnsToContents()

            self.show()
            #self._silenceCallback = False

            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)

    def setTableFromDataFrameObject(self, dataFrameObject):
        # populate the table from the the Pandas dataFrame

        with self._tableBlockSignals('setTableFromDataFrameObject'):

            objs = self.getSelectedObjects()

            self._dataFrameObject = dataFrameObject
            #
            # if dataFrameObject.dataFrame.empty:
            #   self.clearTable()
            # else:
            #   with self._updateTable(self._dataFrameObject):
            #     self.setData(dataFrameObject.dataFrame.values)
            #
            # return

            # self.hide()
            #self._silenceCallback = True

            # keep the original sorting method
            sortOrder = self.horizontalHeader().sortIndicatorOrder()
            sortColumn = self.horizontalHeader().sortIndicatorSection()

            if not dataFrameObject.dataFrame.empty:
                # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

                self.setData(dataFrameObject.dataFrame.values)
            else:
                # set a dummy row of the correct length
                self.setData([list(range(len(dataFrameObject.headings)))])

            # needed after setting the column headings
            self.setHorizontalHeaderLabels(dataFrameObject.headings)
            self.showColumns(dataFrameObject)
            # self.resizeColumnsToContents()
            # self.horizontalHeader().setStretchLastSection(self._stretchLastSection)

            # required to make the header visible
            self.setColumnCount(dataFrameObject.numColumns)

            # re-sort the table
            if sortColumn < self.columnCount():
                self.sortByColumn(sortColumn, sortOrder)

            # clear the dummy row
            if dataFrameObject.dataFrame.empty:
                self.setRowCount(0)

            #self._silenceCallback = False
            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)
            self.horizontalHeader().setStretchLastSection(self._stretchLastSection)
            self.resizeColumnsToContents()

            self._highLightObjs(objs)
            # self.show()

    def getDataFrameFromList(self, table=None,
                             buildList=None,
                             colDefs=None,
                             hiddenColumns=None):
        """
        Return a Pandas dataFrame from an internal list of objects
        The columns are based on the 'func' functions in the columnDefinitions

        :param buildList:
        :param colDefs:
        :return pandas dataFrameObject:
        """
        allItems = []
        objects = []

        # objectList = {}
        # indexList = {}

        if buildList:
            for col, obj in enumerate(buildList):
                listItem = OrderedDict()
                for header in colDefs.columns:
                    listItem[header.headerText] = header.getValue(obj)

                allItems.append(listItem)
                objects.append(obj)

            # indexList[str(listItem['Index'])] = obj
            # objectList[obj.pid] = listItem['Index']

            # indexList[str(col)] = obj
            # objectList[obj.pid] = col

            # indexList[str(col)] = obj
            # objectList[obj.pid] = col

        return DataFrameObject(dataFrame=pd.DataFrame(allItems, columns=colDefs.headings),
                               objectList=objects or [],
                               # indexList=indexList,
                               columnDefs=colDefs or [],
                               hiddenColumns=hiddenColumns or [],
                               table=table)

    def getDataFrameFromRows(self, table=None,
                             dataFrame=None,
                             colDefs=None,
                             hiddenColumns=None):
        """
        Return a Pandas dataFrame from the internal rows of an internal Pandas dataFrame
        The columns are based on the 'func' functions in the columnDefinitions

        :param buildList:
        :param colDefs:
        :return pandas dataFrame:
        """
        allItems = []
        objects = []
        # objectList = None
        # indexList = {}

        buildList = dataFrame.as_namedtuples()
        for ind, obj in enumerate(buildList):
            listItem = OrderedDict()
            for header in colDefs.columns:
                listItem[header.headerText] = header.getValue(obj)

            allItems.append(listItem)

        #   # TODO:ED need to add object links in here, but only the top object exists so far
        #   if 'Index' in listItem:
        #     indexList[str(listItem['Index'])] = obj
        #     objectList[obj.pid] = listItem['Index']
        #   else:
        #     indexList[str(ind)] = obj
        #     objectList[obj.pid] = ind

        return DataFrameObject(dataFrame=pd.DataFrame(allItems, columns=colDefs.headings),
                               objectList=objects,
                               # indexList=indexList,
                               columnDefs=colDefs,
                               hiddenColumns=hiddenColumns,
                               table=table)

    def exportTableDialog(self):
        self.saveDialog = FileDialog(directory='ccpn_Table.xlsx',  #default saving name
                                     fileMode=FileDialog.AnyFile,
                                     filter=".xlsx;; .csv;; .tsv;; .json ",
                                     text='Save as ',
                                     acceptMode=FileDialog.AcceptSave,
                                     preferences=None)
        path = self.saveDialog.selectedFile()
        sheet_name = 'Table'
        if path:
            dataFrameObject = self._dataFrameObject
            if dataFrameObject is not None:
                dataFrame = dataFrameObject.dataFrame
                visColumns = dataFrameObject.visibleColumnHeadings
                ft = self.saveDialog.selectedNameFilter()
                findExportFormats(path, dataFrame, sheet_name=sheet_name, filterType=ft, columns=visColumns)

            else:
                if self._rawData is not None:
                    try:
                        df = pd.DataFrame(self._rawData).transpose()
                        findExportFormats(path, df, sheet_name=sheet_name)
                        # df.to_excel(path, sheet_name=sheet_name)
                    except Exception as e:
                        getLogger().warning(e)

    # def findExportFormats(self, path, sheet_name='Table'):
    #     formatTypes = OrderedDict([
    #         ('.xlsx', self.dataFrameToExcel),
    #         ('.csv', self.dataFrameToCsv),
    #         ('.tsv', self.dataFrameToTsv),
    #         ('.json', self.dataFrameToJson)
    #         ])
    #
    #     extension = os.path.splitext(path)[1]
    #     if extension in formatTypes.keys():
    #         formatTypes[extension](self._dataFrameObject, path, sheet_name)
    #         return
    #     else:
    #         try:
    #             self.findExportFormats(str(path) + self.saveDialog.selectedNameFilter(), sheet_name)
    #         except:
    #             getLogger().warning('Format file not supported')
    #
    # def dataFrameToExcel(self, dataFrameObject, path, sheet_name='Table'):
    #     if dataFrameObject is not None:
    #         visColumns = dataFrameObject.visibleColumnHeadings
    #         # writer = pd.ExcelWriter(path, engine='xlsxwriter')
    #         #
    #         # dataFrameExcel = dataFrameObject.dataFrame.apply(pd.to_numeric, errors='ignore')
    #         # dataFrameExcel.to_excel(writer, sheet_name=sheet_name, index=False, columns=visColumns)
    #         dataFrameObject.dataFrame.to_excel(path, sheet_name=sheet_name, index=False, columns=visColumns)
    #     else:
    #         if self._rawData is not None:
    #             try:
    #                 df = pd.DataFrame(self._rawData).transpose()
    #                 df.to_excel(path, sheet_name=sheet_name)
    #             except Exception as e:
    #                 getLogger().warning(e)
    #
    # def dataFrameToCsv(self, dataFrameObject, path):
    #     dataFrameObject.dataFrame.to_csv(path)
    #
    # def dataFrameToTsv(self, dataFrameObject, path):
    #     dataFrameObject.dataFrame.to_csv(path, sep='\t')
    #
    # def dataFrameToJson(self, dataFrameObject, path):
    #     dataFrameObject.dataFrame.to_json(path, orient='split')
    #
    # def tableToDataFrame(self):
    #     return self._dataFrameObject.dataFrame[self._dataFrameObject.visibleColumnHeadings]

    # def tableToDataFrame(self):
    #   from pandas import DataFrame
    #   headers = self._dataFrameObject.visibleColumnHeadings   #[c.heading for c in self.columns]
    #   rows = []
    #   for obj in self.objects:
    #     rows.append([x.getValue(obj) for x in self.columns])
    #   dataFrame = DataFrame(rows, index=None, columns=headers)
    #   dataFrame.apply(pd.to_numeric, errors='ignore')
    #   return dataFrame

    def scrollToSelectedIndex(self):
        h = self.horizontalHeader()
        for i in range(h.count()):
            if not h.isSectionHidden(i) and h.sectionViewportPosition(i) >= 0:
                if self.getSelectedRows():
                    self.scrollTo(self.model().index(self.getSelectedRows()[0], i),
                                  self.PositionAtCenter)
                    break

    def getSelectedRows(self):

        model = self.selectionModel()

        # selects all the items in the row
        selection = model.selectedRows()

        # if self.selectRows:
        #   selection = model.selectedRows(column=0)
        # else:
        #   selection = model.selectedIndexes()

        rows = [i.row() for i in selection]
        #rows = list(set(rows))
        #rows.sort()

        return rows

    def getSelectedObjects(self):

        model = self.selectionModel()

        # selects all the items in the row
        selection = model.selectedIndexes()

        if selection:
            selectedObjects = []
            rows = []

            for iSelect in selection:
                row = iSelect.row()
                col = iSelect.column()
                colName = self.horizontalHeaderItem(col).text()
                if colName == 'Pid':

                    if row not in rows:
                        rows.append(row)
                        objIndex = model.model().data(iSelect)

                        # if str(objIndex) in self._dataFrameObject.indexList:
                        # obj = self._dataFrameObject.indexList[str(objIndex)]  # item.index needed
                        # selectedObjects.append(obj)

                        obj = self.project.getByPid(objIndex)
                        if obj:
                            selectedObjects.append(obj)

            return selectedObjects
        else:
            return None

    def clearSelection(self):
        """Clear the current selection in the table
        and remove objects form the current list
        """
        with self._tableBlockSignals('clearSelection'):

            objList = self.getSelectedObjects()
            selectionModel = self.selectionModel()
            selectionModel.clearSelection()

            # remove from the current list
            multiple = self._tableData['classCallBack']
            if multiple:  # None if no table callback defined
                multipleAttr = getattr(self.current, multiple)
                if len(multipleAttr) > 0:
                    # need to remove objList from multipleAttr - fires only one current change
                    setattr(self.current, multiple, tuple(set(multipleAttr) - set(objList)))

    def selectObjects(self, objList: list, setUpdatesEnabled: bool = False):
        """Select the object in the table
        """
        # skip if the table is empty
        if not self._dataFrameObject:
            return

        with self._tableBlockSignals('selectObjects'):

            selectionModel = self.selectionModel()
            if objList:

                if not self._mousePressed:
                    selectionModel.clearSelection()  # causes a clear problem here
                    # strange tablewidget cmd/selection problem

                for obj in objList:
                    row = self._dataFrameObject.find(self, str(obj.pid))
                    if row is not None:
                        selectionModel.select(self.model().index(row, 0),
                                              selectionModel.Select | selectionModel.Rows)

    def _highLightObjs(self, selection):

        # skip if the table is empty
        if not self._dataFrameObject:
            return

        with self._tableBlockSignals('_highLightObjs'):

            selectionModel = self.selectionModel()

            if selection:
                uniqObjs = set(selection)

                rowObjs = []
                for obj in uniqObjs:
                    if obj in self._dataFrameObject.objects:
                        rowObjs.append(obj)

                # disable callbacks while populating the table
                #self._silenceCallback = True
                # self.blockSignals(True)
                if not self._mousePressed:
                    selectionModel.clearSelection()  # causes a clear problem here
                    # strange tablewidget cmd/selection problem
                # self.setUpdatesEnabled(False)

                for obj in rowObjs:
                    row = self._dataFrameObject.find(self, str(obj.pid))
                    if row is not None:
                        selectionModel.select(self.model().index(row, 0),
                                              selectionModel.Select | selectionModel.Rows)
                    # selectionModel.setCurrentIndex(self.model().index(row, 0)
                    #                                , selectionModel.SelectCurrent | selectionModel.Rows)

                # self.scrollToSelectedIndex()

                # self.setUpdatesEnabled(True)
                # self.blockSignals(False)
                #self._silenceCallback = False
                # self.setFocus(QtCore.Qt.OtherFocusReason)

    def clearTable(self):
        "remove all objects from the table"
        # self.hide()
        #self._silenceCallback = True

        with self._tableBlockSignals('clearTable'):
            self.clearTableContents()

        # self.show()
        #self._silenceCallback = False
        # self.resizeColumnsToContents()
        # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Interactive)

    def clearTableContents(self, dataFrameObject=None):
        self.clearContents()
        self.verticalHeadersSet = True
        self.horizontalHeadersSet = True
        self.sortModes = {}

        self._dataFrameObject = dataFrameObject if dataFrameObject else None

        if self._dataFrameObject:
            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            # there must be something in the table to set the headers against
            self.setData([list(range(self._dataFrameObject.numColumns)), ])

            self.setHorizontalHeaderLabels(self._dataFrameObject.headings)
            self.showColumns(self._dataFrameObject)
            # self.resizeColumnsToContents()
            self.horizontalHeader().setStretchLastSection(self._stretchLastSection)

            # required to make the header visible
            self.setColumnCount(self._dataFrameObject.numColumns)

        self.setRowCount(0)
        self.items = []

    def reindexTableObjects(self):
        if self._tableData['tableSelection']:
            tSelect = getattr(self, self._tableData['tableSelection'])
            if tSelect:

                multiple = self._tableData['classCallBack']
                # print(tSelect, multiple)
                multipleAttr = getattr(tSelect, multiple)

                if multipleAttr:
                    # newIndex = [multipleAttr.index(rr) for rr in self._objects]

                    objCol = indCol = None
                    for cc in range(self.columnCount()):
                        colName = self.horizontalHeaderItem(cc).text()
                        if colName == DATAFRAME_INDEX:
                            indCol = cc
                            # print (DATAFRAME_INDEX, cc)
                        elif colName == DATAFRAME_OBJECT:
                            objCol = cc
                            # print (DATAFRAME_OBJECT, cc)
                    if objCol and indCol:
                        # print ('INDEXING')
                        # print (multipleAttr)
                        for rr in range(self.rowCount()):

                            thisObj = self.item(rr, objCol).value
                            if thisObj in multipleAttr:
                                self.item(rr, indCol).setValue(multipleAttr.index(thisObj))

    def _updateTableCallback(self, data):
        """
        Notifier callback for updating the table
        """

        with self._tableBlockSignals('_updateTableCallback'):

            # thisTableList = getattr(data[Notifier.THEOBJECT]
            #                         , self._tableData['className'])   # get the table list
            table = data[Notifier.OBJECT]
            #
            # #self._silenceCallback = True
            tableSelect = self._tableData['tableSelection']

            currentTable = getattr(self, tableSelect) if tableSelect else None

            if currentTable and currentTable == table:
                trigger = data[Notifier.TRIGGER]

                if trigger == Notifier.RENAME:

                    # keep the original sorting method
                    sortOrder = self.horizontalHeader().sortIndicatorOrder()
                    sortColumn = self.horizontalHeader().sortIndicatorSection()

                    # self.displayTableForNmrTable(table)
                    self._tableData['changeFunc'](table)

                    # if tableSelect and getattr(self, tableSelect) in thisTableList:
                    #   trigger = data[Notifier.TRIGGER]
                    #
                    #   # keep the original sorting method
                    #   sortOrder = self.horizontalHeader().sortIndicatorOrder()
                    #   sortColumn = self.horizontalHeader().sortIndicatorSection()
                    #
                    #   if table.pid == self._tableData['pullDownWidget'].getText() and trigger == Notifier.DELETE:
                    #
                    #     self.clearTable()
                    #
                    #   elif table.pid == self._tableData['pullDownWidget'].getText() and trigger == Notifier.CHANGE:
                    #
                    #     # self.displayTableForNmrTable(table)
                    #     self._tableData['changeFunc'](table)
                    #
                    #   elif trigger == Notifier.RENAME:
                    #     if table == getattr(self, tableSelect):
                    #
                    #       # self.displayTableForNmrTable(table)
                    #       self._tableData['changeFunc'](table)

                    # re-sort the table
                    if sortColumn < self.columnCount():
                        self.sortByColumn(sortColumn, sortOrder)

            # else:
            #   self.clearTable()

            #self._silenceCallback = False

        getLogger().debug2('<updateTableCallback>', data['notifier'],
                           tableSelect,
                           data['trigger'], data['object'])

    def _updateRowCallback(self, data):
        """
        Notifier callback for updating the table for change in nmrRows
        :param data:
        """
        # thisTableList = getattr(data[Notifier.THEOBJECT]
        #                         , self._tableData['className'])   # get the tableList

        with self._tableBlockSignals('_updateRowCallback'):
            row = data[Notifier.OBJECT]
            trigger = data[Notifier.TRIGGER]

            if not self._dataFrameObject:
                return

            #self._silenceCallback = True

            _update = False
            # try:

            # multiple delete from deleteObjFromTable messes with this
            # if thisRow.pid == self._tableData['pullDownWidget'].getText():

            # is the row in the table
            # TODO:ED move these into the table class

            # keep the original sorting method
            sortOrder = self.horizontalHeader().sortIndicatorOrder()
            sortColumn = self.horizontalHeader().sortIndicatorSection()

            if trigger == Notifier.DELETE:

                # remove item from self._dataFrameObject and table

                if row in self._dataFrameObject._objects:
                    self._dataFrameObject.removeObject(row)
                    _update = True

            elif trigger == Notifier.CREATE:

                # insert item into self._dataFrameObject

                if self._tableData['tableSelection']:
                    tSelect = getattr(self, self._tableData['tableSelection'])
                    if tSelect:

                        # check that the object created is in the list viewed in this table
                        # e.g. row.peakList == tSelect then add
                        if tSelect == getattr(row, self._tableData['tableName']):
                            # add the row to the dataFrame and table
                            self._dataFrameObject.appendObject(row)
                            _update = True

            elif trigger == Notifier.CHANGE:

                # modify the line in the table
                try:
                    _update = self._dataFrameObject.changeObject(row)

                    # TODO:ED it may not already be in the list - check indexing
                    if not _update:
                        if self._tableData['tableSelection']:
                            tSelect = getattr(self, self._tableData['tableSelection'])
                            if tSelect:

                                # check that the object created is in the list viewed in this table
                                # e.g. row.peakList == tSelect then add
                                if tSelect == getattr(row, self._tableData['tableName']):
                                    # add the row to the dataFrame and table

                                    # get the array containing the objects displayed in the table
                                    multiple = self._tableData['classCallBack']
                                    # print(tSelect, multiple)
                                    multipleAttr = getattr(tSelect, multiple)

                                    self._dataFrameObject.appendObject(row, multipleAttr=multipleAttr)
                                    _update = True

                except:
                    getLogger().debug2('Error updating row in table')

            elif trigger == Notifier.RENAME:
                # get the old pid before the rename
                oldPid = data[Notifier.OLDPID]

                if row in self._dataFrameObject._objects:

                    # modify the oldPid in the objectList, change to newPid
                    _update = self._dataFrameObject.renameObject(row, oldPid)

                    # TODO:ED check whether the new object is still in the active list - remove otherwise
                    if self._tableData['tableSelection']:
                        tSelect = getattr(self, self._tableData['tableSelection'])  # eg self.nmrChain
                        if tSelect and not tSelect.isDeleted:  # eg self.nmrChain.nmrResidues
                            objList = getattr(tSelect, self._tableData['rowClass']._pluralLinkName)

                            if objList and row not in objList:
                                # TODO:ED Check current deletion
                                getLogger().debug2('>>> deleting spare object %s' % row, oldPid)
                                self._dataFrameObject.removeObject(row)

                            else:
                                getLogger().debug2('>>> creating spare object %s' % row, oldPid)
                                self._dataFrameObject.appendObject(row)
                        else:
                            self.clearTable()

                        _update = True

        if _update:
            # self.update()
            # re-sort the table
            # if sortColumn < self.columnCount():
            #   self.sortByColumn(sortColumn, sortOrder)
            #
            # # except Exception as es:
            # #   getLogger().warning(str(es)+str(data))
            #
            # #self._silenceCallback = False
            getLogger().debug2('<updateRowCallback>', data['notifier'],
                               self._tableData['tableSelection'],
                               data['trigger'], data['object'])

        return _update

    def _updateCellCallback(self, attr, data):
        """
        Notifier callback for updating the table
        :param data:
        """
        # thisTableList = getattr(data[Notifier.THEOBJECT]
        #                         , self._tableData['className'])   # get the tableList

        with self._tableBlockSignals('_updateCellCallback'):
            cellData = data[Notifier.OBJECT]
            # row = getattr(cell, self._tableData['rowName'])
            # cells = getattr(cellData, attr)
            cells = makeIterableList(cellData)

            #self._silenceCallback = True
            _update = False

            for cell in cells:
                callbacktypes = self._tableData['cellClassNames']
                rowObj = None
                if isinstance(callbacktypes, list):
                    for cBack in callbacktypes:

                        # check if row is the correct type of class
                        if isinstance(cell, cBack[OBJECT_CLASS]):
                            rowObj = getattr(cell, cBack[OBJECT_PARENT])
                            rowCallback = cBack[OBJECT_PARENT]
                            break
                else:
                    rowObj = getattr(cell, callbacktypes[OBJECT_PARENT])
                    rowCallback = callbacktypes[OBJECT_PARENT]

                # concatenate the list - will always return a list
                rowObjs = makeIterableList(rowObj)

                # update the correct row by calling row handler
                for rowObj in rowObjs:
                    newData = data.copy()
                    newData[Notifier.OBJECT] = rowObj
                    newData[Notifier.TRIGGER] = Notifier.CHANGE

                    # check whether we are the row object or still a cell object
                    cellType = self._tableData['rowClass']
                    if isinstance(rowObj, cellType):
                        self._updateRowCallback(newData)
                    else:
                        self._updateCellCallback(rowCallback, newData)

        #self._silenceCallback = False
        getLogger().debug2('<updateCellCallback>', data['notifier'],
                           self._tableData['tableSelection'],
                           data['trigger'], data['object'])

    def _searchCallBack(self, data):
        """
        Callback to populate the search bar with the selected item
        """
        print('>>> %s _searchCallBack' % _moduleId(self.moduleParent))

        value = getattr(data[CallBack.OBJECT], self._tableData['searchCallBack']._pluralLinkName, None)
        if value and self.searchWidget and self.searchWidget.isVisible():
            self.searchWidget.selectSearchOption(self, self._tableData['searchCallBack'], value[0].id)

    def _selectCurrentCallBack(self, data):
        """
        Callback to handle selection on the table, linked to user defined function
        :param data:
        """
        # self._sortChanged(0, 0)

        if not self._tableBlockingLevel:
            print('>>> %s _selectCurrentCallBack' % _moduleId(self.moduleParent))

            self._tableData['selectCurrentCallBack'](data)

    def setTableNotifiers(self, tableClass=None, rowClass=None, cellClassNames=None,
                          tableName=None, rowName=None, className=None,
                          changeFunc=None, updateFunc=None,
                          tableSelection=None, pullDownWidget=None,
                          callBackClass=None, selectCurrentCallBack=None,
                          searchCallBack=None, moduleParent=blankId):
        """
        Set a Notifier to call when an object is created/deleted/renamed/changed
        rename calls on name
        change calls on any other attribute

        :param tableClass - class of table object, selected by pulldown:
        :param rowClass - class identified by a row in the table:
        :param cellClassNames - list of tuples (cellClass, cellClassName):
                                class that affects row when changed
        :param tableName - name of attribute for parent name of row:
        :param rowName - name of attribute for parent name of cell:
        :param changeFunc:
        :param updateFunc:
        :param tableSelection:
        :param pullDownWidget:
        :return:
        """
        # self.clearTableNotifiers()
        self._initialiseTableNotifiers()

        if tableClass:
            self._tableNotifier = Notifier(self.project,
                                           [Notifier.CREATE, Notifier.DELETE, Notifier.RENAME],
                                           tableClass.__name__,
                                           self._updateTableCallback,
                                           onceOnly=True)
        if rowClass:
            # TODO:ED check OnceOnly residue notifiers
            # 'i-1' residue spawns a rename but the 'i' residue only fires a change
            self._rowNotifier = Notifier(self.project,
                                         [Notifier.CREATE, Notifier.DELETE, Notifier.RENAME, Notifier.CHANGE],
                                         rowClass.__name__,
                                         self._updateRowCallback,
                                         onceOnly=True)  # should be True, but doesn't work
            self._rowNotifier.setDebug(True)

            # for 'i-1' nmrResidues
        if isinstance(cellClassNames, list):
            for cellClass in cellClassNames:
                self._cellNotifiers.append(Notifier(self.project,
                                                    [Notifier.CHANGE, Notifier.CREATE, Notifier.DELETE, Notifier.RENAME],
                                                    cellClass[OBJECT_CLASS].__name__,
                                                    partial(self._updateCellCallback, cellClass[OBJECT_PARENT]),
                                                    onceOnly=False))
        else:
            if cellClassNames:
                self._cellNotifiers.append(Notifier(self.project,
                                                    [Notifier.CHANGE, Notifier.CREATE, Notifier.DELETE, Notifier.RENAME],
                                                    cellClassNames[OBJECT_CLASS].__name__,
                                                    partial(self._updateCellCallback, cellClassNames[OBJECT_PARENT]),
                                                    onceOnly=False))

        if selectCurrentCallBack:
            self._selectCurrentNotifier = Notifier(self.current,
                                                   [Notifier.CURRENT],
                                                   callBackClass._pluralLinkName,
                                                   self._selectCurrentCallBack)

        if searchCallBack:
            self._searchNotifier = Notifier(self.current,
                                            [Notifier.CURRENT],
                                            searchCallBack._pluralLinkName,
                                            self._searchCallBack)

        self._tableData = {'updateFunc': updateFunc,
                           'changeFunc': changeFunc,
                           'tableSelection': tableSelection,
                           'pullDownWidget': pullDownWidget,
                           'tableClass': tableClass,
                           'rowClass': rowClass,
                           'cellClassNames': cellClassNames,
                           'tableName': tableName,
                           'className': className,
                           'classCallBack': callBackClass._pluralLinkName if callBackClass else None,
                           'selectCurrentCallBack': selectCurrentCallBack,
                           'searchCallBack': searchCallBack,
                           'moduleParent': moduleParent
                           }

        # add a cleaner id to the opened quickTable list
        self.moduleParent = moduleParent
        MODULEIDS[id(moduleParent)] = len(MODULEIDS)

    def setDefaultTableData(self):
        """Populate an empty table data object
        """
        self._tableData = {'updateFunc': None,
                           'changeFunc': None,
                           'tableSelection': None,
                           'pullDownWidget': None,
                           'tableClass': None,
                           'rowClass': None,
                           'cellClassNames': None,
                           'tableName': None,
                           'className': None,
                           'classCallBack': None,
                           'selectCurrentCallBack': None,
                           'searchCallBack': None,
                           'moduleParent': blankId
                           }

    def _initialiseTableNotifiers(self):
        """Set the initial notifiers to empty
        """
        self._tableNotifier = None
        self._rowNotifier = None
        self._cellNotifiers = []
        self._selectCurrentNotifier = None
        self._droppedNotifier = None
        self._searchNotifier = None

    @staticmethod  # has to be a static method
    def onDestroyed(widget):
        # print("DEBUG on destroyed:", widget)
        widget.clearTableNotifiers()

    def clearTableNotifiers(self):
        """Clean up the notifiers
        """
        if self._tableNotifier is not None:
            self._tableNotifier.unRegister()
            del (self._tableNotifier)
        if self._rowNotifier is not None:
            self._rowNotifier.unRegister()
            del (self._rowNotifier)
        if self._cellNotifiers:
            for cell in self._cellNotifiers:
                if cell is not None:
                    cell.unRegister()
        del self._cellNotifiers
        if self._selectCurrentNotifier is not None:
            self._selectCurrentNotifier.unRegister()
            del (self._selectCurrentNotifier)
        if self._droppedNotifier is not None:
            self._droppedNotifier.unRegister()
            del (self._droppedNotifier)
        if self._searchNotifier is not None:
            self._searchNotifier.unRegister()
            del (self._searchNotifier)

    # def dragEnterEvent(self, event):
    #   ccpnmrJsonData = 'ccpnmr-json'
    #
    #   if event.mimeData().hasUrls():
    #     event.accept()
    #   else:
    #     pids = []
    #     for item in self.selectedItems():
    #       if item is not None:
    #
    #         # TODO:ED check the list of selected as with getSelectedObjects to get pids..
    #         # trouble is, this is working as a dropevent
    #         objFromPid = self.project.getByPid(item.data(0, QtCore.Qt.DisplayRole))
    #         if objFromPid is not None:
    #           pids.append(objFromPid.pid)
    #
    #     itemData = json.dumps({'pids':pids})
    #     event.mimeData().setData(ccpnmrJsonData, itemData)
    #     event.mimeData().setText(itemData)
    #     event.accept()


EDIT_ROLE = QtCore.Qt.EditRole


class QuickTableDelegate(QtWidgets.QStyledItemDelegate):
    """
    handle the setting of data when editing the table
    """

    def __init__(self, parent):
        """
        Initialise the delegate
        :param parent - link to the handling table:
        """
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.customWidget = False
        self._parent = parent

    def setModelData(self, widget, mode, index):
        """
        Set the object to the new value
        :param widget - typically a lineedit handling the editing of the cell:
        :param mode - editing mode:
        :param index - QModelIndex of the cell:
        """
        text = widget.text()
        row = index.row()
        col = index.column()

        try:
            rowData = []
            # read the row from the table to get the pid
            for ii in range(self._parent.columnCount()):
                rowData.append(self._parent.item(row, ii).text())

            if DATAFRAME_PID in self._parent._dataFrameObject.headings:

                # get the object to apply the data to
                pidCol = self._parent._dataFrameObject.headings.index(DATAFRAME_PID)
                pid = rowData[pidCol]
                obj = self._parent.project.getByPid(pid)

                # set the data which will fire notifiers to populate all tables
                func = self._parent._dataFrameObject.setEditValues[col]
                if func and obj:
                    func(obj, text)
            else:
                getLogger().debug('table %s does not contain a Pid' % self)

        except Exception as es:
            getLogger().warning('Error handling cell editing: %i %i %s' % (row, col, str(es)))

        # return QtWidgets.QStyledItemDelegate.setModelData(self, widget, mode, index)


class QuickTableFrame(Frame):
    def __init__(self, *args, **kwargs):
        super(QuickTableFrame, self).__init__(parent=self.mainWidget, setLayout=True, spacing=(0, 0),
                                              showBorder=False, fShape='noFrame',
                                              grid=(1, 0),
                                              hPolicy='expanding', vPolicy='expanding')

        self.quickTable = QuickTable(self, *args, **kwargs)
        self.searchWidget = None


if __name__ == '__main__':
    from ccpn.ui.gui.widgets.Icon import Icon

    from ccpn.ui.gui.widgets.Application import TestApplication
    from ccpn.ui.gui.popups.Dialog import CcpnDialog
    from ccpn.util import Colour
    from ccpn.ui.gui.widgets.Column import ColumnClass, Column


    app = TestApplication()


    class mockObj(object):
        'Mock object to test the table widget editing properties'
        pid = ''
        integer = 3
        exampleFloat = 3.1  # This will create a double spin box
        exampleBool = True  # This will create a check box
        string = 'white'  # This will create a line Edit
        exampleList = [('Mock', 'Test'), ]  # This will create a pulldown
        color = QtGui.QColor('Red')
        icon = Icon('icons/warning')
        r = Colour.colourNameToHexDict['red']
        y = Colour.colourNameToHexDict['yellow']
        b = Colour.colourNameToHexDict['blue']
        colouredIcons = [None, Icon(color=r), Icon(color=y), Icon(color=b)]

        flagsList = [[''] * len(colouredIcons), [Icon] * len(colouredIcons), 1, colouredIcons]  # This will create a pulldown. Make a list with the

        # same structure of pulldown setData function: (texts=None, objects=None, index=None,
        # icons=None, clear=True, headerText=None, headerEnabled=False, headerIcon=None)

        def editBool(self, value):
            mockObj.exampleBool = value

        def editFloat(self, value):
            mockObj.exampleFloat = value

        def editPulldown(self, value):
            mockObj.exampleList = value

        def editFlags(self, value):
            print(value)


    def _checkBoxCallBack(data):
        print(data['checked'])


    popup = CcpnDialog(windowTitle='Test Table', setLayout=True)

    columns = ColumnClass([
        (
            'Float',
            lambda i: mockObj.exampleFloat,
            'TipText: Float',
            lambda mockObj, value: mockObj.editFloat(mockObj, value)
            ),

        (
            'Bool',
            lambda i: mockObj.exampleBool,
            'TipText: Bool',
            lambda mockObj, value: mockObj.editBool(mockObj, value),
            ),

        (
            'Pulldown',
            lambda i: mockObj.exampleList,
            'TipText: Pulldown',
            lambda mockObj, value: mockObj.editPulldown(mockObj, value),
            ),

        (
            'Flags',
            lambda i: mockObj.flagsList,
            'TipText: Flags',
            lambda mockObj, value: mockObj.editFlags(mockObj, value),
            )
        ])
    table = QuickTable(parent=popup, dataFrameObject=None, checkBoxCallback=_checkBoxCallBack, grid=(0, 0))
    df = table.getDataFrameFromList(table, [mockObj] * 5, colDefs=columns)

    table.setTableFromDataFrameObject(dataFrameObject=df)
    table.item(0, 0).setBackground(QtGui.QColor(100, 100, 150))  #color the first item
    combo = QtGui.QComboBox()
    table.setCellWidget(0, 0, combo)
    # table.item(0, 0).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
    # table.item(0, 0).setCheckState(QtCore.Qt.Unchecked)
    # table.item(0,0).setFormat(float(table.item(0,0).format))
    # print(table.item(0,0)._format)
    table.horizontalHeaderItem(1).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
    table.horizontalHeaderItem(1).setCheckState(QtCore.Qt.Checked)

    popup.show()
    popup.raise_()
    app.start()
