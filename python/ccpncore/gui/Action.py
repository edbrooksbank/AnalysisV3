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
from PyQt4 import QtGui, QtCore

from ccpncore.gui.Base import Base
from ccpncore.util.Translation import translator

class Action(QtGui.QAction, Base):
  def __init__(self, parent, text, callback=None, shortcut=None, checked=True, checkable=False, icon=None, **kw):

    text = translator.translate(text)

    if shortcut:
      if type(shortcut) == type(''):
        shortcut = QtGui.QKeySequence(", ".join(tuple(shortcut)))
      QtGui.QAction.__init__(self, text, parent, shortcut=shortcut, checkable=checkable)
      self.setShortcutContext(QtCore.Qt.ApplicationShortcut)
    # elif icon:
    #   QtGui.QAction.__init__(self, icon, text, parent, triggered=callback, checkable=checkable)

    else:
      QtGui.QAction.__init__(self, text, parent, checkable=checkable)

    if checkable:
      self.setChecked(checked)
      
    if callback:
      # PyQt4 always seems to add a checked argument for Action callbacks
      self.triggered.connect(lambda checked, *args, **kw: callback(*args, **kw))

    # Base.__init__(self, **kw)


