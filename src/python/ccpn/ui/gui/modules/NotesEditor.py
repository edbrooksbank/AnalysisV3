__author__ = 'simon1'

from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.Menu import MenuBar
from ccpn.ui.gui.widgets.TextEditor import TextEditor

from ccpn.ui.gui.DropBase import DropBase

from PyQt4 import QtGui


class NotesEditor(DropBase, CcpnModule):

  def __init__(self, parent, project, name='Notes Editor', note=None):
    CcpnModule.__init__(self, name=name)
    widget = QtGui.QWidget()
    self._appBase = project._appBase
    self.project = project
    self.parent = parent
    self.parent.addModule(self)
    self.textBox = TextEditor()
    self.note = note
    widgetLayout = QtGui.QGridLayout()
    widget.setLayout(widgetLayout)
    self.label1 = Label(self, text='Note name')
    self.lineEdit1 = LineEdit(self)
    widget.layout().addWidget(self.label1, 1, 0)
    widget.layout().addWidget(self.lineEdit1, 1, 1, 1, 4)
    widget.layout().addWidget(self.textBox, 2, 0, 1, 5)
    if note:
      self.textBox.setText(note.text)
      self.lineEdit1.setText(self.note.name)
    self.buttonBox = ButtonList(self, texts=['Save', 'Cancel'],
                                callbacks=[self._saveNote, self._reject])
    widget.layout().addWidget(self.buttonBox, 3, 3, 1, 2)
    self.processText = self._processText
    self.layout.addWidget(widget)

  def _setNoteName(self):
    """
    Sets the name of the note based on the text in the Note name text box.
    """
    if not self.note:
      self.note = self.project.newNote(name=self.lineEdit1.text())
    self.note.rename(self.lineEdit1.text())

  def _saveNote(self):
    """
    Saves the text in the textbox to the note object.
    """
    newText = self.textBox.toPlainText()
    self._setNoteName()
    self.note.text = newText
    self.close()

  def _reject(self):
    """
    Closes the note editor ignoring all changes.
    """
    self.close()

  def _processText(self, text, event):
    if not self.note:
      self.note = self.project.newNote()
    self.textBox.setText(text)
    self.overlay.hide()

