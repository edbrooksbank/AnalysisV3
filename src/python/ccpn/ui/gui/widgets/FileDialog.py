"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:40:43 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui

import sys

class FileDialog(QtGui.QFileDialog):

  def __init__(self, parent=None, fileMode=QtGui.QFileDialog.AnyFile, text=None,
               acceptMode=QtGui.QFileDialog.AcceptOpen, preferences=None, **kw):

    QtGui.QFileDialog.__init__(self, parent, caption=text, **kw)


    staticFunctionDict = {
      (0, 0): 'getOpenFileName',
      (0, 1): 'getOpenFileName',
      (0, 2): 'getExistingDirectory',
      (0, 3): 'getOpenFileNames',
      (1, 0): 'getSaveFileName',
      (1, 1): 'getSaveFileName',
      (1, 2): 'getSaveFileName',
      (1, 3): 'getSaveFileName',
      (self.AcceptOpen, self.AnyFile): 'getOpenFileName',
      (self.AcceptOpen, self.ExistingFile): 'getOpenFileName',
      (self.AcceptOpen, self.Directory): 'getExistingDirectory',
      (self.AcceptOpen, self.ExistingFiles): 'getOpenFileNames',
      (self.AcceptSave, self.AnyFile): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFile): 'getSaveFileName',
      (self.AcceptSave, self.Directory): 'getSaveFileName',
      (self.AcceptSave, self.ExistingFiles): 'getSaveFileName',
    }

    self.setFileMode(fileMode)
    self.setAcceptMode(acceptMode)
    if preferences is None:
      self.useNative = False

    if preferences:
      self.useNative = preferences.useNative
      if preferences.colourScheme == 'dark':
        self.setStyleSheet("""
                           QFileDialog QWidget {
                                               background-color: #2a3358;
                                               color: #f7ffff;
                                               }
                          """)
      elif preferences.colourScheme == 'light':
        self.setStyleSheet("QFileDialog QWidget {color: #464e76; }")

    # self.result is '' (first case) or 0 (second case) if Cancel button selected
    if preferences and preferences.useNative and not sys.platform.lower() == 'linux':
      funcName = staticFunctionDict[(acceptMode, fileMode)]
      self.result = getattr(self, funcName)(caption=text, **kw)
    else:
      self.result = self.exec_()

  # overrides Qt function, which does not pay any attention to whether Cancel button selected
  def selectedFiles(self):

    if self.result and not self.useNative:
      return QtGui.QFileDialog.selectedFiles(self)
    elif self.result and self.useNative:
      return [self.result]
    else:
      return []

  # Qt does not have this but useful if you know you only want one file
  def selectedFile(self):

    files = self.selectedFiles()
    if files:
      return files[0]
    else:
      return None






