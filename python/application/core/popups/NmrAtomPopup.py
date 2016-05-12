from PyQt4 import QtGui

from application.core.widgets.Base import Base
from application.core.widgets.Button import Button
from application.core.widgets.Label import Label
from application.core.widgets.CheckBox import CheckBox
from application.core.widgets.PulldownList import PulldownList

class NmrAtomPopup(QtGui.QDialog, Base):
  def __init__(self, parent=None, nmrAtom=None, **kw):
    super(NmrAtomPopup, self).__init__(parent)
    Base.__init__(self, **kw)

    self.peakListLabel = Label(self, "NmrAtom ", grid=(0, 0))
    self.peakListLabel = Label(self, nmrAtom.id, grid=(0, 1))
    self.nmrResidueLabel = Label(self, 'NmrResidue', grid=(1, 0))
    self.displayedCheckBox = CheckBox(self, grid=(1, 1), checked=False)
    self.symbolLabel = Label(self, 'Peak Symbol', grid=(2, 0))
    self.symbolPulldown = PulldownList(self, grid=(2, 1))
    self.symbolColourLabel = Label(self, 'Peak Symbol Colour', grid=(3, 0))
    self.symbolColourPulldownList = PulldownList(self, grid=(3, 1))
    self.symbolColourMoreButton = Button(self, 'More...', grid=(3, 2))
    self.minimalAnnotationLabel = Label(self, 'Minimal Annotation', grid=(4, 0))
    self.minimalAnnotationCheckBox = CheckBox(self, grid=(4, 1))
