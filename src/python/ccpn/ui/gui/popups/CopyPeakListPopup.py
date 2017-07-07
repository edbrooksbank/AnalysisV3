"""
Module Documentation here
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
__dateModified__ = "$dateModified: 2017-04-10 15:35:09 +0100 (Mon, April 10, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.popups.Dialog import CcpnDialog


class CopyPeakListPopup(CcpnDialog):
  def __init__(self, parent=None, title='Copy PeakList', **kw):
    CcpnDialog.__init__(self, parent, setLayout=False, windowTitle=title, **kw)

    self.application = QtCore.QCoreApplication.instance()._ccpnApplication
    self.project = self.application.project

    self._setMainLayout()
    self.setWidgets()
    self.addWidgetsToLayout()

  def _setMainLayout(self):
    self.mainLayout = QtGui.QGridLayout()
    self.setLayout(self.mainLayout)
    self.setWindowTitle("Copy PeakList")
    self.mainLayout.setContentsMargins(20, 20, 20, 5)  # L,T,R,B
    self.setFixedWidth(300)
    self.setFixedHeight(130)

  def setWidgets(self):
    self.sourcePeakListLabel = Label(self, 'Source PeakList')
    self.sourcePeakListPullDown = PulldownList(self)
    self._populateSourcePeakListPullDown()

    self.targetSpectraLabel = Label(self, 'Target Spectrum')
    self.targetSpectraPullDown = PulldownList(self)
    self._populateTargetSpectraPullDown()

    self.okCancelButtons = ButtonList(self, texts=['Cancel', ' Ok '],
                                      callbacks=[self.reject, self._okButton],
                                      tipTexts=['Close Popup', 'Copy PeakList'])

  def addWidgetsToLayout(self):
    self.mainLayout.addWidget(self.sourcePeakListLabel, 0,0)
    self.mainLayout.addWidget(self.sourcePeakListPullDown, 0, 1)
    self.mainLayout.addWidget(self.targetSpectraLabel, 1, 0)
    self.mainLayout.addWidget(self.targetSpectraPullDown, 1, 1)
    self.mainLayout.addWidget(self.okCancelButtons, 2, 1)

  def _okButton(self):
    self.project._startCommandEchoBlock('_okButton')
    try:
      self.sourcePeakList = self.project.getByPid(self.sourcePeakListPullDown.getText())
      self.targetSpectrum = self.project.getByPid(self.targetSpectraPullDown.getText())
      self._copyPeakListToSpectrum()
    finally:
      self.accept()
      self.project._endCommandEchoBlock()

  def _copyPeakListToSpectrum(self):
    if self.sourcePeakList is not None:
      if self.targetSpectrum is not None:
        self.sourcePeakList.copyTo(self.targetSpectrum)

  def _populateSourcePeakListPullDown(self):
    sourcePullDownData = []
    if len(self.project.peakLists)>0:
      for pl in self.project.peakLists:
        sourcePullDownData.append(str(pl.pid))
    self.sourcePeakListPullDown.setData(sourcePullDownData)
    self._selectDefaultPeakList()

  def _populateTargetSpectraPullDown(self):
    targetPullDownData = []
    if len(self.project.spectra)>0:
      for sp in self.project.spectra:
        targetPullDownData.append(str(sp.pid))
    self.targetSpectraPullDown.setData(targetPullDownData)
    self._selectDefaultSpectrum()


  def _selectDefaultPeakList(self):
    if self.application.current.peak is not None:
      defaultPeakList = self.application.current.peak.peakList
      self.sourcePeakListPullDown.select(defaultPeakList.pid)
      # print('Selected defaultPeakList: "current.peak.peakList" ',defaultPeakList) #Testing statement to be deleted
      return
    if self.application.current.strip is not None:
      defaultPeakList = self.application.current.strip.spectra[0].peakLists[-1]
      self.sourcePeakListPullDown.select(defaultPeakList.pid)
      # print('Selected defaultPeakList: "current.strip.spectra[0].peakLists[-1]" ', defaultPeakList)  #Testing statement to be deleted
      return
    else:
      defaultPeakList = self.project.spectra[0].peakLists[-1]
      self.sourcePeakListPullDown.select(defaultPeakList.pid)
      # print('Selected defaultPeakList: "self.project.spectra[0].peakLists[-1]" ', defaultPeakList) #Testing statement to be deleted
      return

  def _selectDefaultSpectrum(self):
    if self.application.current.strip is not None:
      defaultSpectrum = self.application.current.strip.spectra[-1]
      self.targetSpectraPullDown.select(defaultSpectrum.pid)
      # print('Selected defaultSpectrum: "current.strip.spectra[-1]" ', defaultSpectrum) #Testing statement to be deleted
      return
    else:
      defaultSpectrum = self.project.spectra[-1]
      self.targetSpectraPullDown.select(defaultSpectrum.pid)
      # print('Selected defaultSpectrum: "self.project.spectra[-1]" ', defaultSpectrum) #Testing statement to be deleted
      return

if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.popups.Dialog import CcpnDialog
  import ccpn.core.testing.WrapperTesting as WT

  app = TestApplication()
  app._ccpnApplication = app
  app.colourScheme = 'dark'

  thisWT = WT.WrapperTesting()
  thisWT.setUp()

  app.project = thisWT.project

  popup = CopyPeakListPopup()       # too many errors for testing here...

  popup.show()
  popup.raise_()

  app.start()

  WT.WrapperTesting.tearDown(thisWT)
