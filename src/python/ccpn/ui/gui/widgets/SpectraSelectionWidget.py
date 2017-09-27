"""
A widget to select spectra or spectrum group as input data for modules or popup
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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:26 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import decimal
from functools import partial
from PyQt4 import QtCore, QtGui
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from collections import OrderedDict
from ccpn.ui.gui.popups.Dialog import CcpnDialog      # ejb
from ccpn.ui.gui.widgets.Widget import Widget


class SpectraSelectionWidget(Widget,Base):

  def __init__(self, parent=None, mainWindow=None, **kw):
    Widget.__init__(self, parent)
    Base.__init__(self, setLayout=True, **kw)

    self.project = None # Testing reasons
    # Derive application, project, and current from mainWindow
    if mainWindow is not None:
      self.mainWindow = mainWindow
      self.application = mainWindow.application
      self.project = mainWindow.application.project
      self.current = mainWindow.application.current

    self.allSpectraCheckBoxes = []
    self.allSG_CheckBoxes = []
    self.positions = []
    self._setSelectionScrollArea()
    self._setWidgets()


  def _setSelectionScrollArea(self):

    self.scrollArea = ScrollArea(self, setLayout=False, grid=(1,0),)
    self.scrollArea.setWidgetResizable(True)
    self.scrollAreaWidgetContents = Frame(self, setLayout=True)
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    # self.scrollAreaWidgetContents.getLayout().setAlignment(QtCore.Qt.AlignTop)


  def _setWidgets(self):

    self.selectSpectraOption = RadioButtons(self,
                                              texts=['Spectra', 'Groups'],
                                              selectedInd=0,
                                              callback=self.showSpectraOption,
                                              tipTexts=None,
                                              grid=(0,0))
    if self.project is not None:
      if len(self.project.spectra)>0:
        # self.selectAllcheckBox = CheckBox(self.scrollAreaWidgetContents, text='Select All', grid=(0, 0), hAlign='c', vAlign='t')
        self.selectAllSpectraCheckBox = CheckBox(self.scrollAreaWidgetContents, checked=True, text='Select All Spectra ', grid=(0, 0), hAlign='l',
                                                 vAlign='t')

        self.selectAllSpectrumGroupsCheckBox = CheckBox(self.scrollAreaWidgetContents, text='Select All SpectrumGroups ', grid=(0, 0),
                                                 hAlign='l',
                                                 vAlign='t')
        self.selectFromCurrentStrip = Button(self.scrollAreaWidgetContents,
                                               text='Select From Current Strip', grid=(0,1), callback=self._checkSpectraFromCurrentStrip,
                                               hAlign='l',
                                               vAlign='t')

      self._addSpectrumCheckBoxes()
      self._addSpectrumGroupsCheckBoxes()
      self.selectAllSpectraCheckBox.stateChanged.connect(self._checkAllSpectra)
      self.selectAllSpectrumGroupsCheckBox.stateChanged.connect(self._checkAllSpectrumGroups)
      if self.selectAllSpectraCheckBox.isChecked():
        self._checkAllSpectra(QtCore.Qt.Checked)
      self.showSpectraOption()

  def updateWidgets(self):
    self._deleteAllCheckBoxes()
    self._addSpectrumCheckBoxes()
    self._addSpectrumGroupsCheckBoxes()

  def _addSpectrumCheckBoxes(self):

    self.allSpectraCheckBoxes = []
    if self.project is not None:
      for i, spectrum in enumerate(self.project.spectra, start=2):
        self.spectrumCheckBox = CheckBox(self.scrollAreaWidgetContents, text=str(spectrum.pid), grid=(i, 0), callback=self._toggleCheckBoxSelectAllSpectra, hAlign='l',vAlign='t')
        self.allSpectraCheckBoxes.append(self.spectrumCheckBox)

  def _checkSpectraFromCurrentStrip(self):
    if self.current.strip is not None:
      self.selectAllSpectraCheckBox.setCheckState(0)
      self.selectAllSpectrumGroupsCheckBox.setCheckState(0)
      if not self.current.strip.spectrumDisplay.isGrouped:
        for spView in self.current.strip.spectrumDisplay.spectrumViews:
          if spView is not None:
            if self.selectSpectraOption.getIndex() == 0:
              for checkBox in self.allSpectraCheckBoxes:
                if checkBox.text() == spView.spectrum.pid:
                  checkBox.setChecked(True)
      else:
        if len(self.allSG_CheckBoxes)>0:
          for checkBox in self.allSG_CheckBoxes:
            if checkBox.text() in  [sg.pid for sg in self.current.strip.spectrumDisplay.spectrumGroupToolBar._spectrumGroups]:
              checkBox.setChecked(True)

    else:
      print('Select Current strip first')
      self._checkAllSpectra(0)
    self._toggleCheckBoxSelectAllSpectra()


  def _deleteAllCheckBoxes(self):pass
    # while self.scrollAreaWidgetContents.getLayout().count():
    #   item = self.scrollAreaWidgetContents.getLayout().takeAt(0)
    #   # if item in self.allSG_CheckBoxes or self.allSpectraCheckBoxes:
    #   print(item)
    #   item.widget().deleteLater()

  def clearLayout(self, layout):
    if layout != None:
      while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
          child.widget().deleteLater()
        elif child.layout() is not None:
          self.clearLayout(child.layout())

  def _addSpectrumGroupsCheckBoxes(self):

    self.allSG_CheckBoxes = []
    if self.project is not None:
      for i, sg in enumerate(self.project.spectrumGroups, start=2):
        self.spectrumGroupCheckBox = CheckBox(self.scrollAreaWidgetContents, text=str(sg.pid),callback=self._toggleCheckBoxSelectAllSpectrumGroup,
                                              grid=(i, 0),  hAlign='l',vAlign='t')
        self.allSG_CheckBoxes.append(self.spectrumGroupCheckBox)

  def _toggleCheckBoxSelectAllSpectra(self):
      allChecked = [checkBox.isChecked() for checkBox in self.allSpectraCheckBoxes]
      if False in allChecked:
        self.selectAllSpectraCheckBox.setCheckState(1)
      else:
        self.selectAllSpectraCheckBox.setCheckState(2)
      if not any(allChecked): #if they are sp all unchecked(all False), set SelectAll unchecked
        self.selectAllSpectraCheckBox.setCheckState(0)
      if self.selectAllSpectraCheckBox.checkState() != 1:
        self.selectAllSpectraCheckBox.setTristate(False)

  def _toggleCheckBoxSelectAllSpectrumGroup(self):
      # self.selectFromCurrentStrip.setChecked(False)
      allChecked = [checkBox.isChecked() for checkBox in self.allSG_CheckBoxes]
      if False in allChecked:
        self.selectAllSpectrumGroupsCheckBox.setCheckState(1)
      else:
        self.selectAllSpectrumGroupsCheckBox.setCheckState(2)
      if not any(allChecked): #if they are sp all unchecked(all False), set SelectAll unchecked
        self.selectAllSpectrumGroupsCheckBox.setCheckState(0)
      if self.selectAllSpectrumGroupsCheckBox.checkState() != 1:
        self.selectAllSpectrumGroupsCheckBox.setTristate(False)


  def _checkAllSpectrumGroups(self, state):
    # self.selectFromCurrentStrip.setChecked(False)
    if self.selectAllSpectrumGroupsCheckBox.checkState() != 1:
      self.selectAllSpectrumGroupsCheckBox.setTristate(False)

    if len(self.allSG_CheckBoxes) > 0:
      for cb in self.allSG_CheckBoxes:
        if state == 2:
          cb.setChecked(True)
        elif state == 0:
          cb.setChecked(False)
        else:
          continue

  def _checkAllSpectra(self, state):
    self.selectFromCurrentStrip.setChecked(False)
    if self.selectAllSpectraCheckBox.checkState() != 1:
      self.selectAllSpectraCheckBox.setTristate(False)

    if len(self.allSpectraCheckBoxes)>0:
      for cb in self.allSpectraCheckBoxes:
        if state == 2:
          cb.setChecked(True)
        elif state == 0:
          cb.setChecked(False)
        else:
          continue

  def _getSelectedSpectra(self):
    spectra = []
    for cb in self.allSpectraCheckBoxes:
      if cb.isChecked():
        spectrum = self.project.getByPid(str(cb.text()))
        spectra.append(spectrum)
    return spectra

  def _getSpectrumGroupsSpectra(self):
    spectra = []
    for sg in self.allSG_CheckBoxes:
      if sg.isChecked():
        spectrumGroup = self.project.getByPid(str(sg.text()))
        spectra += spectrumGroup.spectra
    return spectra



  def showSpectraOption(self):

    if self.selectSpectraOption.getIndex() == 0:
      self.selectAllSpectraCheckBox.show()
      self.selectAllSpectrumGroupsCheckBox.hide()

      for cb in self.allSpectraCheckBoxes:
        cb.show()
      for sg in self.allSG_CheckBoxes:
        sg.hide()

    else:
      self.selectAllSpectraCheckBox.hide()
      self.selectAllSpectrumGroupsCheckBox.show()
      for cb in self.allSpectraCheckBoxes:
        cb.hide()
      for sg in self.allSG_CheckBoxes:
        sg.show()





if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication

  app = TestApplication()

  popup = CcpnDialog(windowTitle='Test')
  popup.setGeometry(200, 200, 200, 200)

  widget = SpectraSelectionWidget(popup, mainWindow=None)
  popup.show()
  popup.raise_()
  app.start()
