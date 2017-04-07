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
__dateModified__ = "$dateModified: 2017-04-07 11:40:42 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from PyQt4 import QtGui, QtCore


from ccpn.framework.Translation import Translation

from pyqtgraph.dockarea import Dock

HALIGN_DICT = {
  'left': QtCore.Qt.AlignLeft,
  'right': QtCore.Qt.AlignRight,
  'center': QtCore.Qt.AlignHCenter,
  'l': QtCore.Qt.AlignLeft,
  'r': QtCore.Qt.AlignRight,
  'c': QtCore.Qt.AlignHCenter,
}

VALIGN_DICT = {
  'top': QtCore.Qt.AlignTop,
  'bottom': QtCore.Qt.AlignBottom,
  'center': QtCore.Qt.AlignVCenter,
  'centre': QtCore.Qt.AlignVCenter,
  't': QtCore.Qt.AlignTop,
  'b': QtCore.Qt.AlignBottom,
  'c': QtCore.Qt.AlignVCenter,
}

POLICY_DICT = {
  'fixed': QtGui.QSizePolicy.Fixed,
  'minimum': QtGui.QSizePolicy.Minimum,
  'maximum': QtGui.QSizePolicy.Maximum,
  'preferred': QtGui.QSizePolicy.Preferred,
  'expanding': QtGui.QSizePolicy.Expanding,
  'minimumExpanding': QtGui.QSizePolicy.MinimumExpanding,
  'ignored': QtGui.QSizePolicy.Ignored,
}

FRAME_DICT = {
  # Shadow
  'plain': QtGui.QFrame.Plain,
  'raised': QtGui.QFrame.Raised,
  'sunken': QtGui.QFrame.Sunken,
  # Shapes
  'noFrame': QtGui.QFrame.NoFrame,
  'box': QtGui.QFrame.Box,
  'panel': QtGui.QFrame.Panel,
  'styledPanel': QtGui.QFrame.StyledPanel,
  'hLine': QtGui.QFrame.HLine,
  'vLine': QtGui.QFrame.VLine,
}


class Base():

  def __init__(self, tipText=None, grid=(None, None), gridSpan=(1,1), stretch=(0,0),
               hAlign=None, vAlign=None, hPolicy=None, vPolicy=None,
               fShape=None, fShadow=None,
               bgColor=None, fgColor=None,
               isFloatWidget=False):

    # Tool tips
    if tipText:
      self.setToolTip(tipText)

    if isinstance(self, Dock):
      return

    parent = self.parent() if hasattr(self, 'parent') else None # Not all Qt objects have a parent
    # print('parent',parent)
    if parent and not isFloatWidget:
      # Setup gridding within parent
      if isinstance(parent, Dock):
        layout = parent.widgetArea.layout()
      else:
        layout = parent.layout()
      if not layout:
        layout = QtGui.QGridLayout(parent)
        # layout.setSpacing(2)

        # setContentsMargin(left, top, right, bottom)
        #layout.setContentsMargins(2,2,2,2)
        layout.setContentsMargins(1,1,1,1)
        layout.setContentsMargins(0, 0, 0, 0)
        parent.setLayout( layout )
      if isinstance(layout, QtGui.QGridLayout):
        row, col = self._getRowCol(grid)
        rowStr, colStr = stretch
        layout.setRowStretch(row, rowStr)
        layout.setColumnStretch(col, colStr)

        rowSpan, colSpan = gridSpan
        hAlign = HALIGN_DICT.get(hAlign, 0)

        vAlign = VALIGN_DICT.get(vAlign, 0)
        align = hAlign | vAlign
        layout.addWidget(self, row, col, rowSpan, colSpan, QtCore.Qt.Alignment(align))

    if hPolicy or vPolicy:
      hPolicy = POLICY_DICT.get(hPolicy, 0)
      vPolicy = POLICY_DICT.get(vPolicy, 0)
      self.setSizePolicy(hPolicy, vPolicy)

    # Setup colour overrides (styles used primarily)
    if bgColor:
      self.setAutoFillBackground(True)
      rgb = QtGui.QColor(bgColor).getRgb()[:3]
      self.setStyleSheet("background-color: rgb(%d, %d, %d);" %  rgb)

    if fgColor:
      self.setAutoFillBackground(True)
      rgb = QtGui.QColor(fgColor).getRgb()[:3]
      self.setStyleSheet("foreground-color: rgb(%d, %d, %d);" %  rgb)

    # define frame styles
    if fShape or fShadow:
      """
      Define frame properties:
      TODO: GWV: routine is called but appears not to change much in the appearance
      """
      shape = FRAME_DICT.get(fShape, QtGui.QFrame.NoFrame)
      shadow = FRAME_DICT.get(fShadow, 0)
      #print('Base.framestyle>', shape | shadow)
      self.setFrameStyle(shape | shadow)
      self.setMidLineWidth(2)

  def _getRowCol(self, grid):

    if isinstance(self.parent(), Dock):
      layout = self.parent().layout
    else:
      layout = self.parent().layout()

    if grid:
      row, col = grid
      if row is None:
        row = 1

      if col is None:
        col = 1
    else:
      row = layout.rowCount()
      col = 0

    return row, col






 
