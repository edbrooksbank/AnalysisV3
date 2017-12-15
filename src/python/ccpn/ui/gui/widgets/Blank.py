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
__author__ = "$Author: Ed Brooksbank $"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtCore
from ccpn.ui.gui.popups.Dialog import CcpnDialog
from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea

class Blank(CcpnDialog):
  def __init__(self, parent=None, title='Blank', **kw):
    CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)
    self.setWindowFlags(self.windowFlags() |
                          QtCore.Qt.WindowMaximizeButtonHint |
                          QtCore.Qt.WindowMinimizeButtonHint)

    self.moduleArea = CcpnModuleArea(mainWindow=self)
    self.layout().addWidget(self.moduleArea)

  def changeEvent(self, event):
    if event.type() == QtCore.QEvent.WindowStateChange:
      if self.windowState() & QtCore.Qt.WindowMinimized:
        print('>>>Blank changeEvent: Minimised')
      elif event.oldState() & QtCore.Qt.WindowMinimized:
        print('>>>Blank changeEvent: Normal/Maximised/FullScreen')

        # TODO:ED update table from dataFrame

    else:
      print ('>>>Blank changeEvent', event.type())

    event.ignore()


if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication

  app = TestApplication()
  popup = Blank()

  popup.show()
  popup.raise_()

  app.start()
