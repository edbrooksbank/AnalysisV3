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
__author__ = "$Author: CCPN $"
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:40:44 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"

#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtCore, QtGui

class ToolButton(QtGui.QToolButton):

  def __init__(self, parent=None, spectrumView=None):
    
    QtGui.QToolButton.__init__(self, parent.spectrumToolBar)
    self.spectrumView = spectrumView
    pix=QtGui.QPixmap(120, 10)
    if spectrumView.spectrum.dimensionCount < 2:
      pix.fill(QtGui.QColor(spectrumView.sliceColour))
    else:
      pix.fill(QtGui.QColor(spectrumView.positiveContourColour))
    # spectrumItem.newAction = self.spectrumToolbar.addAction(spectrumItem.name, QtGui.QToolButton)
    # self.spaction = parent.spectrumToolBar.addAction(spectrumView.spectrum.name)#, self)
    # newIcon = QtGui.QIcon(pix)
    # self.spaction.setIcon(newIcon)
    # self.spaction.setCheckable(True)
    # self.spaction.setChecked(True)

    # for spectrumView in parent.spectrumViews:
    #   if spectrumView.spectrum.dimensionCount < 2:
    #     self.spaction.toggled.connect(spectrumView.plot.setVisible)
    #   else:
    # for strip in spectrumView.strips:
    #   print(strip)
    #   item = spectrumView.spectrumItems[strip]
    #   print(strip, item, spectrumView, self.spaction, 'you name it!')
    #   self.spaction.toggled.connect(item.setVisible)
    #   print(self.spaction)
         # for peakListView in spectrumView.peakListViews:
         #   spectrumView.newAction.toggled.connect(peakListView.setVisible)
    # spectrumView.widget = parent.spectrumToolBar.widgetForAction(self.spaction)
    # spectrumView.widget.setFixedSize(60,30)

