"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = "$Revision: 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================
__author__ = 'simon'

from PyQt4 import QtGui

from ccpncore.gui.Base import Base

class Splitter(QtGui.QSplitter, Base):

  def __init__(self, parent=None, **kw):

    QtGui.QSplitter.__init__(self, parent)
    Base.__init__(self, parent, **kw)

    self.doResize = False

  def createHandle(self):

    return SplitterHandle(self, self.orientation())

  def resizeEvent(self, event):

    self.doResize = True
    eventResult = QtGui.QSplitter.resizeEvent(self, event)
    self.doResize = False

    return eventResult

class SplitterHandle(QtGui.QSplitterHandle):

  def __init__(self, parent, orientation):

    QtGui.QSplitterHandle.__init__(self, orientation, parent)

  def mousePressEvent(self, event):

    self.parent().doResize = True
    return QtGui.QSplitter.mousePressEvent(self, event)

  def mouseReleaseEvent(self, event):

    self.parent().doResize = False
    return QtGui.QSplitter.mouseReleaseEvent(self, event)
