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

from ccpn.ui.gui.widgets.Action import Action
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.guiSettings import menuFont
from ccpn.framework.Translation import translator


class Menu(QtGui.QMenu, Base):
  def __init__(self, title, parent, isFloatWidget=False, **kw):
    title = translator.translate(title)
    QtGui.QMenu.__init__(self, title, parent)
    Base.__init__(self, isFloatWidget=isFloatWidget, **kw)
    self.isFloatWidget = isFloatWidget
    self.setFont(menuFont)


  def addItem(self, text, shortcut=None, callback=None, checked=True, checkable=False):
    action = Action(self.parent(), text, callback=callback, shortcut=shortcut,
                         checked=checked, checkable=checkable, isFloatWidget=self.isFloatWidget)
    self.addAction(action)
    return action
    # print(shortcut)
    
  def addMenu(self, title):
    menu = Menu(title, self)
    QtGui.QMenu.addMenu(self, menu)
    return menu

  def _addQMenu(self, menu):
    ''' this adds a normal QMenu '''
    QtGui.QMenu.addMenu(self, menu)
    return menu


class MenuBar(QtGui.QMenuBar):
  def __init__(self, parent):

    QtGui.QMenuBar.__init__(self, parent)
    self.setFont(menuFont)
