"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:51 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtCore, QtWidgets

class CallbackTimer(QtCore.QTimer):
  def __init__(self, callback):
    super().__init__()
    self.setSingleShot(True)
    # self.connect(self, QtCore.PYQT_SIGNAL('timeout()'), callback)
    self.timeout.connect(callback)

if __name__ == '__main__':

  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.Button import Button
  from ccpn.ui.gui.widgets.MainWindow import MainWindow

  def callbackFunc():

    print('callbackFunc()')

  timer = CallbackTimer(callbackFunc)
  
  def startTimer():
    
    if not timer.isActive():
      print('start timer')
      timer.start()
    
  app = TestApplication()

  window = MainWindow()
  frame = window.mainFrame

  button = Button(frame, text='Start timer', callback=startTimer, grid=(0,0))
  button = Button(frame, text='Quit', callback=app.quit, grid=(1,0))

  window.show()

  app.start()

    
