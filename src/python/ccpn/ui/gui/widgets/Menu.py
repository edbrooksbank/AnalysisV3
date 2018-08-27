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
__dateModified__ = "$dateModified: 2017-07-07 16:32:54 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets

from ccpn.ui.gui.widgets.Action import Action
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.guiSettings import menuFont
from ccpn.framework.Translation import translator


class Menu(QtWidgets.QMenu, Base):
    def __init__(self, title, parent, isFloatWidget=False, **kw):
        title = translator.translate(title)
        QtWidgets.QMenu.__init__(self, title, parent)
        Base.__init__(self, isFloatWidget=isFloatWidget, **kw)
        self.isFloatWidget = isFloatWidget
        self.setFont(menuFont)
        self.setToolTipsVisible(True)

    def addItem(self, text, shortcut=None, callback=None, checked=True, checkable=False, icon=None, toolTip=None, **kwargs):
        action = Action(self.parent(), text, callback=callback, shortcut=shortcut,
                        checked=checked, checkable=checkable, icon=icon, toolTip=toolTip, isFloatWidget=self.isFloatWidget, **kwargs)
        self.addAction(action)
        return action
        # print(shortcut)

    def _addSeparator(self, *args, **kwargs):
        separator = self.addSeparator()
        return separator

    def addMenu(self, title, **kwargs):
        menu = Menu(title, self)
        QtWidgets.QMenu.addMenu(self, menu)
        return menu

    def _addQMenu(self, menu):
        ''' this adds a normal QMenu '''
        QtWidgets.QMenu.addMenu(self, menu)
        return menu


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent):
        QtWidgets.QMenuBar.__init__(self, parent)
        self.setFont(menuFont)
