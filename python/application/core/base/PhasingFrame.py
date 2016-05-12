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
from PyQt4 import QtGui

from application.core.widgets.Entry import FloatEntry
from application.core.widgets.Label import Label
from application.core.widgets.PulldownList import PulldownList
from application.core.widgets.Slider import Slider
from application.core.widgets.Frame import Frame

directionTexts = ('Horizontal', 'Vertical')

class PhasingFrame(Frame):

  def __init__(self, parent=None, includeDirection=True, callback=None, returnCallback=None, directionCallback=None, **kw):

    Frame.__init__(self, parent, **kw)
    
    self.callback = callback
    self.returnCallback = returnCallback if returnCallback else self.doCallback
    self.directionCallback = directionCallback if directionCallback else self.doCallback

    sliderDict = {
      'startVal': -180,
      'endVal': 180,
      'value': 0,
      #'showNumber': True,
      'tickInterval': 90,
    }
    value = '%4d' % sliderDict['value']
    
    label = Label(self, text='ph0', grid=(0,0))
    self.phLabel0 = Label(self, text=value, grid=(0, 1))
    self.slider0 = Slider(self, callback=self.setPh0, grid=(0, 2), **sliderDict)
    
    sliderDict = {
      'startVal': -360,
      'endVal': 360,
      'value': 0,
      #'showNumber': True,
      'tickInterval': 90,
    }
    value = '%4d' % sliderDict['value']
    
    label = Label(self, text='ph1', grid=(0,3))
    self.phLabel1 = Label(self, text=value, grid=(0, 4))
    self.slider1 = Slider(self, callback=self.setPh1, grid=(0, 5), **sliderDict)
    
    label = Label(self, text='piv', grid=(0,6))
    self.pivotEntry = FloatEntry(self, callback=lambda value: self.returnCallback(), decimals=2, grid=(0,7))
    self.pivotEntry.setMaximumWidth(60)
    
    if includeDirection:
      self.directionList = PulldownList(self, texts=directionTexts,
                                        callback=lambda text: self.directionCallback(), grid=(0,8))
    else:
      self.directionList = None
      
  def getDirection(self):
    
    return directionTexts.index(self.directionList.get()) if self.directionList else 0
    
  def setPh0(self, value):
    self.phLabel0.setText(str(value))
    self.doCallback()
    
  def setPh1(self, value):
    self.phLabel1.setText(str(value))
    self.doCallback()
    
  def doCallback(self):
    if self.callback:
      self.callback()
 
if __name__ == '__main__':

  import os
  import sys

  def myCallback(ph0, ph1, pivot, direction):
    print(ph0, ph1, pivot, direction)
    
  qtApp = QtGui.QApplication(['Test Phase Frame'])

  #QtCore.QCoreApplication.setApplicationName('TestPhasing')
  #QtCore.QCoreApplication.setApplicationVersion('0.1')

  widget = QtGui.QWidget()
  frame = PhasingFrame(widget, callback=myCallback)
  widget.show()
  widget.raise_()
  
  sys.exit(qtApp.exec_())
 
