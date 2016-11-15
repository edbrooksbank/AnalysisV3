__author__ = 'simon1'

from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.TextEditor import TextEditor

from ccpn.ui.gui.DropBase import DropBase

from PyQt4 import QtGui


class MacroEditor(DropBase, CcpnModule):

  def __init__(self, parent, mainWindow, name, showRecordButtons=False):
    CcpnModule.__init__(self, name=name)

    self.parent = parent
    self.mainWindow = mainWindow
    self.parent.addModule(self)
    self.preferences = self.mainWindow.preferences
    # macro selection
    self.label1 = Label(self, 'Macro Name')
    self.lineEdit1 = LineEdit(self)
    self.button = Button(self, 'Select...', callback=self._openMacroFile)
    # macro editing area
    self.textBox = TextEditor()

    # layouts
    #widget = QtGui.QWidget()
    widget = self.mainWidget
    widgetLayout = QtGui.QGridLayout()
    widget.setLayout(widgetLayout)
    widget.layout().addWidget(self.label1,    0, 0, 1, 1)
    widget.layout().addWidget(self.lineEdit1, 0, 1, 1, 3)
    widget.layout().addWidget(self.button,    0, 4, 1, 1)
    widget.layout().addWidget(self.textBox,   1, 0, 1, 5)

    self.buttonBox = ButtonList(self, texts=['Start', 'Stop', 'Close', 'Save Macro'],
                                callbacks=[self._startMacroRecord, self._stopMacroRecord, self._reject, self._saveMacro])
    self.buttonBox.buttons[1].setDisabled(True)
    self.buttonBox.buttons[0].setEnabled(True)
    widget.layout().addWidget(self.buttonBox, 2, 3, 1, 2)

#    self.layout().setSpacing(1)
    self.layout.addWidget(widget)

    if showRecordButtons is False:
      self.buttonBox.buttons[0].hide()
      self.buttonBox.buttons[1].hide()


  def _saveMacro(self):
    """
    Saves the text inside the textbox to a file, if a file path is not specified, a save file dialog
    appears for specification of the file path.
    """
    if self.lineEdit1.text() == '':
      self._saveMacroAs()
    else:
      with open(self.lineEdit1.text(), 'w') as f:
        f.write(self.textBox.toPlainText())
        f.close()

    # newText = self.textBox.toPlainText()
    # self.macroFile.write(newText)

  def _saveMacroAs(self):
    """
    Opens a save file dialog and saves the text inside the textbox to a file specified in the dialog.
    """
    macroPath = self.preferences.general.userMacroPath
    # colourScheme = self.preferences.general.colourScheme
    newText = self.textBox.toPlainText()
    dialog = FileDialog(self, fileMode=FileDialog.AnyFile, text='Save Macro As...',
                        acceptMode=FileDialog.AcceptSave, preferences=self.preferences.general,
                        directory=macroPath, filter='*.py')
    filePath = dialog.selectedFile()
    if filePath:
      with open(filePath, 'w') as f:
        f.write(newText)
        f.close()

  def _openMacroFile(self):
    """
    Opens a file dialog box at the macro path specified in the application preferences and loads the
    contents of the macro file into the textbox.
    """
    macroPath = self.preferences.general.userMacroPath
    dialog = FileDialog(self, text='Open Macro', fileMode=FileDialog.ExistingFile,
                        acceptMode=FileDialog.AcceptOpen, directory=macroPath,
                        preferences=self.preferences.general, filter='*.py')

    filePath = dialog.selectedFile()
    if filePath:
      with open(filePath, 'r') as f:
        self.textBox.clear()
        for line in f.readlines():
          self.textBox.insertPlainText(line)
        self.macroFile = f

      self.lineEdit1.setText(filePath)

  def _startMacroRecord(self):
    """
    Starts recording of a macro from commands performed in the software and output to the console.
    """
    self.mainWindow.recordingMacro = True
    self.buttonBox.buttons[1].setEnabled(True)
    self.buttonBox.buttons[0].setDisabled(True)


  def _stopMacroRecord(self):
    """
    Stops macro recording.
    """
    self.mainWindow.recordingMacro = False
    self.buttonBox.buttons[1].setDisabled(True)
    self.buttonBox.buttons[0].setEnabled(True)

  def _reject(self):
    self.close()

