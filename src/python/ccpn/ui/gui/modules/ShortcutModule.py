__author__ = 'simon1'

import os
from functools import reduce

from PyQt4 import QtGui

from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea


class ShortcutModule(CcpnModule):

  def __init__(self, mainWindow):
    CcpnModule.__init__(self, name='Define User Shortcuts')

    self.mainWindow = mainWindow
    self.mainWindow.moduleArea.addModule(self)
    self.rowCount = 0
    self.scrollArea = ScrollArea(self.mainWidget, grid=(0, 0), gridSpan=(1, 2))

    self.shortcutWidget = ShortcutWidget(self, mainWindow)
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.setWidget(self.shortcutWidget)
    self.buttonList = ButtonList(self.mainWidget, grid=(1, 1),
                                 texts=['Cancel', 'Save', 'Save and Close'],
                                 callbacks=[self.close, self.save, self.saveAndQuit])

    self.setStyleSheet('ScrollArea {background-color: #00092d}')
    self.setStyleSheet('ScrollArea > QWidget {background-color: #00092d}')


    # self.scrollArea.layout().addWidget(self.shortcutWidget)

  def save(self):
    newShortcuts = self.shortcutWidget.getShortcuts()
    self.mainWindow._appBase.preferences.shortcuts = newShortcuts


  def saveAndQuit(self):
    self.save()
    self.close()


class ShortcutWidget(QtGui.QWidget, Base):

  def __init__(self, parent, mainWindow, **kw):
    QtGui.QWidget.__init__(self, parent)
    from functools import partial
    self.mainWindow = mainWindow
    self.preferences = mainWindow._appBase.preferences
    Base.__init__(self, **kw)
    i=0
    self.widgets = []
    for shortcut in sorted(self.preferences.shortcuts):
      shortcutLabel = Label(self, grid=(i, 0), text=shortcut)
      self.shortcutLineEdit = LineEdit(self, grid=(i, 1))
      self.shortcutLineEdit.setText(self.preferences.shortcuts[shortcut])
      self.shortcutLineEdit.editingFinished.connect(partial(self.validateFunction, i))
      pathButton = Button(self, grid=(i, 2), icon='icons/applications-system', callback=partial(self._getMacroFile, i))
      self.widgets.append([shortcutLabel, self.shortcutLineEdit, pathButton])
      i+=1


  def getShortcuts(self):
    shortcutDict = {}
    layout = self.layout()
    for i in range(layout.rowCount()):
      shortcut = layout.itemAtPosition(i, 0).widget().text()
      function = layout.itemAtPosition(i, 1).widget().text()
      shortcutDict[shortcut] = function
    return shortcutDict


  def _getMacroFile(self, index):
    shortcutLineEdit = self.widgets[index][1]
    if os.path.exists('/'.join(shortcutLineEdit.text().split('/')[:-1])):
      currentDirectory = '/'.join(shortcutLineEdit.text().split('/')[:-1])
    else:
      currentDirectory = os.path.expanduser(self.preferences.general.userMacroPath)
    dialog = FileDialog(self, text='Select Macro File', directory=currentDirectory,
                        fileMode=1, acceptMode=0,
                        preferences=self.preferences.general)
    directory = dialog.selectedFiles()
    if len(directory) > 0:
      shortcutLineEdit.setText('runMacro("%s")' % directory[0])


  def validateFunction(self, i):
    # check if function for shortcut is a .py file or exists in the CcpNmr V3 namespace
    path = self.widgets[i][1].text()
    namespace = self.mainWindow.namespace

    if path == '':
      return

    if path.startswith('/'):

      if os.path.exists(path) and path.split('/')[-1].endswith('.py'):
        print('pathValid')
        return True

      elif not os.path.exists(path) or not path.split('/')[-1].endswith('.py'):
        if not os.path.exists(path):
          showWarning('Invalid macro path', 'Macro path: %s is not a valid path' % path)
          return False

        if not path.split('/')[-1].endswith('.py'):
          showWarning('Invalid macro file', 'Macro files must be valid python files and end in .py' % path)
          return False

    else:
      stub = namespace.get(path.split('.')[0])
      if not stub:
        showWarning('Invalid function', 'Function: %s is not a valid CcpNmr function' % path)
        return False
      else:
        try:
          reduce(getattr, path.split('.')[1:], stub)
          return True
        except:
          showWarning('Invalid function', 'Function: %s is not a valid CcpNmr function' % path)
          return False




