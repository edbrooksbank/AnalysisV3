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

from collections import OrderedDict

import math

from ccpnmrcore.lib.Window import navigateToNmrResidue, navigateToPeakPosition
from ccpncore.gui.Base import Base
from ccpncore.gui.ButtonList import ButtonList
from ccpncore.gui.Button import Button
from ccpncore.gui.PulldownList import PulldownList
from ccpncore.gui.Dock import CcpnDock
from ccpncore.gui.Label import Label
from ccpncore.gui.ListWidget import ListWidget
from ccpnmrcore.modules.NmrResidueTable import NmrResidueTable

from ccpnmrcore.lib.Window import navigateToNmrResidue

from ccpnmrcore.popups.InterIntraSpectrumPopup import InterIntraSpectrumPopup


class BackboneAssignmentModule(CcpnDock):

  def __init__(self, project):

    super(BackboneAssignmentModule, self).__init__(parent=None, name='Backbone Assignment')


    self.project = project
    self.current = project._appBase.current
    self.numberOfMatches = 5
    self.nmrChains = project.nmrChains
    self.matchModules = []
    self.nmrResidueTable = NmrResidueTable(self, project, callback=self.startAssignment)
    self.displayButton = Button(self.nmrResidueTable, text='Select Match Modules',
                                callback=self.showMatchDisplayPopup, grid=(0, 3))

    self.layout.addWidget(self.nmrResidueTable, 0, 0, 1, 3)
    self.setupShiftDicts()


  def startAssignment(self, nmrResidue=None, row=None, col=None):
    self.assigner.clearAllItems()
    self.navigateTo(nmrResidue, row, col)

  def navigateTo(self, nmrResidue=None, row=None, col=None, strip=None):
    selectedDisplays = [display for display in self.project.spectrumDisplays if display.pid not in self.matchModules]

    if '-1' in nmrResidue.sequenceCode:
      direction = '-1'
      seqCode = nmrResidue.sequenceCode
      newSeqCode = seqCode.replace('-1', '')
      iNmrResidue = nmrResidue.nmrChain.fetchNmrResidue(sequenceCode=newSeqCode)
      navigateToNmrResidue(self.project, nmrResidue, selectedDisplays=selectedDisplays, markPositions=True, strip=strip)
      navigateToNmrResidue(self.project, iNmrResidue, selectedDisplays=selectedDisplays, strip=strip)
      queryShifts = self.interShifts[nmrResidue]
      matchShifts = self.intraShifts
      for display in selectedDisplays:
        if not strip:
          display.strips[0].planeToolbar.spinSystemLabel.setText(iNmrResidue.sequenceCode)
        else:
          strip.planeToolbar.spinSystemLabel.setText(iNmrResidue.sequenceCode)

    else:
      direction = '+1'
      iNmrResidue = nmrResidue
      navigateToNmrResidue(self.project, nmrResidue, selectedDisplays=selectedDisplays, markPositions=True, strip=strip)
      queryShifts = self.intraShifts[nmrResidue]
      matchShifts = self.interShifts
      for display in selectedDisplays:
        if not strip:
          display.strips[0].planeToolbar.spinSystemLabel.setText(nmrResidue.sequenceCode)
        else:
          strip.planeToolbar.spinSystemLabel.setText(nmrResidue.sequenceCode)


    assignMatrix = self.buildAssignmentMatrix(queryShifts, matchShifts=matchShifts)
    self.findMatches(assignMatrix)
    self.assigner.addResidue(iNmrResidue, direction)

  def setupShiftDicts(self):
    self.intraShifts = OrderedDict()
    self.interShifts = OrderedDict()

    for nmrResidue in self.project.nmrResidues:
      nmrAtoms = [nmrAtom.name for nmrAtom in nmrResidue.nmrAtoms]
      shifts = []

        # get inter residue chemical shifts for each -1 nmrResidue

      if 'CA' in nmrAtoms:
        interCa = nmrResidue.fetchNmrAtom(name='CA')
        shift1 = self.project.chemicalShiftLists[0].getChemicalShift(interCa.id)
        shifts.append(shift1)
      if 'CB' in nmrAtoms:
        interCb = nmrResidue.fetchNmrAtom(name='CB')
        shift2 = self.project.chemicalShiftLists[0].getChemicalShift(interCb.id)
        shifts.append(shift2)
      if '-1' in nmrResidue.sequenceCode:
        self.interShifts[nmrResidue] = shifts
      else:
        self.intraShifts[nmrResidue] = shifts



  def findMatches(self, assignMatrix):


    assignmentScores = sorted(assignMatrix[1])[0:self.numberOfMatches]
    for assignmentScore in assignmentScores[1:]:
      matchResidue = assignMatrix[0][assignmentScore]
      if '-1' in matchResidue.sequenceCode:
        seqCode = matchResidue.sequenceCode
        newSeqCode = seqCode.replace('-1', '')
        iNmrResidue = matchResidue.nmrChain.fetchNmrResidue(sequenceCode=newSeqCode)

      else:
        iNmrResidue = matchResidue

      for matchModule in self.matchModules:
        if len(self.project.getByPid(matchModule).strips) < self.numberOfMatches:
          newStrip = self.project.getByPid(matchModule).addStrip()
          newStrip.planeToolbar.spinSystemLabel.setText(iNmrResidue.sequenceCode)
          navigateToNmrResidue(self.project, iNmrResidue, strip=newStrip)
        else:
          strip = self.project.getByPid(matchModule).orderedStrips[assignmentScores.index(assignmentScore)]
          strip.planeToolbar.spinSystemLabel.setText(iNmrResidue.sequenceCode)
          navigateToNmrResidue(self.project, iNmrResidue, strip=strip)

    firstMatchResidue = assignMatrix[0][assignmentScores[0]]
    if '-1' in firstMatchResidue.sequenceCode:
      seqCode = firstMatchResidue.sequenceCode
      newSeqCode = seqCode.replace('-1', '')
      iNmrResidue = matchResidue.nmrChain.fetchNmrResidue(sequenceCode=newSeqCode)

    else:
      iNmrResidue = firstMatchResidue

    for matchModule in self.matchModules:
      module = self.project.getByPid(matchModule)
      navigateToNmrResidue(self.project, iNmrResidue, strip=module.orderedStrips[0])
      module.orderedStrips[0].planeToolbar.spinSystemLabel.setText(iNmrResidue.sequenceCode)


  def setAssigner(self, assigner):
    self.assigner = assigner
    self.project._appBase.current.assigner = assigner

  def qScore(self, query, match):
    if query is not None and match is not None:
      return math.sqrt(((query.value-match.value)**2)/((query.value+match.value)**2))
    else:
      return None


  def buildAssignmentMatrix(self, queryShifts, matchShifts):

    scores = []
    matrix = OrderedDict()
    for res, shift in matchShifts.items():

      if len(queryShifts) > 1 and len(shift) > 1:
        if self.qScore(queryShifts[0], shift[0]) is not None and self.qScore(queryShifts[1], shift[1]) is not None:

          score = (self.qScore(queryShifts[0], shift[0])+self.qScore(queryShifts[1], shift[1]))/2
          scores.append(score)
          matrix[score] = res
      elif len(queryShifts) == 1:
        if self.qScore(queryShifts[0], shift[0]) is not None:

          score = self.qScore(queryShifts[0], shift[0])
          scores.append(score)
          matrix[score] = res

    return matrix, scores

  def showMatchDisplayPopup(self):
    self.popup = SelectMatchDisplaysPopup(self, project=self.project)
    self.popup.exec_()



class SelectMatchDisplaysPopup(QtGui.QDialog, Base):
  def __init__(self, parent=None, project=None, **kw):
    super(SelectMatchDisplaysPopup, self).__init__(parent)
    Base.__init__(self, **kw)
    self.parent = parent
    modules = [display.pid for display in project.spectrumDisplays]
    self.project = project
    modules.insert(0, '  ')
    label1a = Label(self, text="Selected Modules", grid=(0, 0))
    self.modulePulldown = PulldownList(self, grid=(1, 0), callback=self.selectMatchModule)
    self.modulePulldown.setData(modules)
    self.moduleList = ListWidget(self, grid=(2, 0))

    self.buttonBox = ButtonList(self, grid=(3, 0), texts=['Cancel', 'Ok'],
                           callbacks=[self.reject, self.setMatchModules])

  def selectMatchModule(self, item):
    self.moduleList.addItem(item)

  def setMatchModules(self):
    self.parent.matchModules = [self.moduleList.item(i).text() for i in range(self.moduleList.count())]
    self.accept()