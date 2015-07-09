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


import pyqtgraph as pg

from pyqtgraph.dockarea import Dock

from PyQt4 import QtCore

import math

from ccpncore.gui.Button import Button
from ccpncore.gui.Base import Base
from ccpncore.gui.PulldownList import PulldownList
from ccpncore.gui.Dock import CcpnDockLabel, CcpnDock
from ccpnmrcore.modules.PeakTable import PeakListSimple
from ccpnmrcore.popups.InterIntraSpectrumPopup import InterIntraSpectrumPopup
from ccpnmrcore.popups.SelectSpectrumDisplayPopup import SelectSpectrumDisplayPopup

class BackboneAssignmentModule(CcpnDock, Base):

  def __init__(self, project=None):

    CcpnDock.__init__(self, parent=None, name='Backbone Assignment')

    self.displayButton = Button(self, text='Select Modules', callback=self.showDisplayPopup)
    self.spectrumButton = Button(self, text='Select Inter/Intra Spectra', callback=self.showInterIntraPopup)
    self.layout.addWidget(self.displayButton, 0, 0, 1, 1)
    self.layout.addWidget(self.spectrumButton, 0, 2, 1, 1)
    self.directionPullDown = PulldownList(self, grid=(0, 4), callback=self.selectAssignmentDirection)
    self.directionPullDown.setData(['', 'i-1', 'i+1'])
    # hsqcDisplay = hsqcDisplay
    self.project = project
    self.current = project._appBase.current
    self.peakTable = PeakListSimple(self, peakLists=project.peakLists, callback=self.findMatchingPeaks)
    self.layout.addWidget(self.peakTable, 2, 0, 1, 6)

    self.lines = []
    self.numberOfMatches = 5


  def findMatchingPeaks(self, peak=None, row=None, col=None, nmrResidue=None):

    for display in self.referenceDisplays:
      hsqcDisplay = self.project.getById(display)
      if peak:
        self.assigner.clearAllItems()
        positions = peak.position
        self.current.nmrResidue = self.project.getById(peak.dimensionNmrAtoms[0][0]._parent.pid)
        hsqcDisplay.strips[-1].spinSystemLabel.setText(self.current.nmrResidue.sequenceCode)
        hsqcDisplay.strips[-1].zoomToRegion([peak.position[0]-0.2, peak.position[0]+0.2,
                                                  peak.position[1]-2, peak.position[1]+2])
        self.line1 = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.line2 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.line1.setPos(QtCore.QPointF(0, peak.position[1]))
        self.line2.setPos(QtCore.QPointF(peak.position[0], 0))
        hsqcDisplay.strips[-1].viewBox.addItem(self.line1)
        hsqcDisplay.strips[-1].viewBox.addItem(self.line2)
        for queryDisplay in self.queryDisplays:
          queryWindow = self.project.getById(queryDisplay)
          queryWindow.orderedStrips[0].spinSystemLabel.setText(self.current.nmrResidue.sequenceCode)
          queryWindow.orderedStrips[0].changeZPlane(position=positions[1])
          queryWindow.orderedStrips[0].orderedAxes[0].position=positions[0]

          for line in self.lines:
            queryWindow.orderedStrips[0].plotWidget.removeItem(line)
          if len(self.lines) == 0:

            line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
            line.setPos(QtCore.QPointF(positions[0], 0))
            queryWindow.orderedStrips[0].plotWidget.addItem(line)

          else:
            self.lines[0].setPos(QtCore.QPointF(positions[0], 0))


        self.current.nmrResidue = self.project.getById(peak.dimensionNmrAtoms[0][0]._parent.pid)
        print(self.current.nmrResidue, 'current.nmrResidue', peak.dimensionNmrAtoms[0][0]._parent.pid)

      elif nmrResidue is not None:
        hsqcDisplay.strips[-1].viewBox.removeItem(self.line1)
        hsqcDisplay.strips[-1].viewBox.removeItem(self.line2)
        self.current.nmrResidue = nmrResidue
        positions = [self.project.chemicalShiftLists[0].findChemicalShift(nmrResidue.fetchNmrAtom(name='H')).value,
                     self.project.chemicalShiftLists[0].findChemicalShift(nmrResidue.fetchNmrAtom(name='N')).value]

        hsqcDisplay.strips[-1].zoomToRegion([positions[0]-0.2, positions[0]+0.2,
                                                  positions[1]-2, positions[1]+2])


        self.line1 = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.line2 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        self.line1.setPos(QtCore.QPointF(0, positions[1]))
        self.line2.setPos(QtCore.QPointF(positions[0], 0))
        hsqcDisplay.strips[-1].viewBox.addItem(self.line1)
        hsqcDisplay.strips[-1].viewBox.addItem(self.line2)

    self.assigner.spectra = {'ref': self.refSpectra, 'intra': self.intraSpectra, 'inter':self.interSpectra}
    self.assigner.addResidue(self.current.nmrResidue)
    assignMatrix = self.getQueryShifts(self.current.nmrResidue)
    self.findMatches(assignMatrix)


  def getQueryShifts(self, currentNmrResidue):
    intraShifts = {}
    interShifts = {}

    for nmrResidue in self.project.nmrResidues:
      intraShifts[nmrResidue] = []
      interShifts[nmrResidue] = []
      if '-1' in nmrResidue.sequenceCode:
        # get inter residue chemical shifts for each -1 nmrResidue
        interCa = nmrResidue.fetchNmrAtom(name='CA')
        interShifts[nmrResidue].append(self.project.chemicalShiftLists[0].findChemicalShift(interCa))
        interCb = nmrResidue.fetchNmrAtom(name='CB')
        interShifts[nmrResidue].append(self.project.chemicalShiftLists[0].findChemicalShift(interCb))

      if '-1' not in nmrResidue.sequenceCode:
        # get intra residue chemical shifts for each nmrResidue
        intraCa = nmrResidue.fetchNmrAtom(name='CA')
        intraShifts[nmrResidue].append(self.project.chemicalShiftLists[0].findChemicalShift(intraCa))

        intraCb = nmrResidue.fetchNmrAtom(name='CB')
        intraShifts[nmrResidue].append(self.project.chemicalShiftLists[0].findChemicalShift(intraCb))


    if self.direction == 'i-1':
      seqCode = currentNmrResidue.sequenceCode+'-1'
      queryNmrResidue = currentNmrResidue.nmrChain.fetchNmrResidue(sequenceCode=seqCode)
      queryShifts = interShifts[queryNmrResidue]
      matchShifts=intraShifts

    elif self.direction == 'i+1':
      print(currentNmrResidue)
      queryShifts = intraShifts[currentNmrResidue]
      matchShifts=interShifts


    assignMatrix = self.buildAssignmentMatrix(queryShifts, matchShifts=matchShifts)

    return assignMatrix

  def findMatches(self, assignMatrix):

    assignmentScores = sorted(assignMatrix[1])[0:self.numberOfMatches]
    for assignmentScore in assignmentScores[1:]:
      matchResidue = assignMatrix[0][assignmentScore]
      if self.direction == 'i+1':
        seqCode = matchResidue.sequenceCode.replace('-1', '')
        parentMatchResidue = matchResidue.nmrChain.fetchNmrResidue(sequenceCode=seqCode)
        matchResidue = parentMatchResidue
      else:
        matchResidue = matchResidue
      zAtom = [atom for atom in matchResidue.atoms if atom.apiResonance.isotopeCode == '15N']
      xAtom = [atom for atom in matchResidue.atoms if atom.apiResonance.isotopeCode == '1H']
      yAtoms = [atom for atom in matchResidue.atoms if atom.apiResonance.isotopeCode == '13C']

      zShift = self.project.chemicalShiftLists[0].findChemicalShift(zAtom[0]).value
      xShift = self.project.chemicalShiftLists[0].findChemicalShift(xAtom[0]).value
      yShifts = []
      for atom in yAtoms:
        if atom is not None:
          if self.project.chemicalShiftLists[0].findChemicalShift(atom) is not None:
            yShifts.append(self.project.chemicalShiftLists[0].findChemicalShift(atom).value)
      line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
      line.setPos(QtCore.QPointF(xShift, 0))
      for matchDisplay in self.matchDisplays:
        matchWindow = self.project.getById(matchDisplay)
        newStrip = matchWindow.addStrip()
        newStrip.changeZPlane(position=zShift)
        newStrip.spinSystemLabel.setText(matchResidue.sequenceCode)
        for shift in yShifts:
          line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
          line.setPos(QtCore.QPointF(0, shift))

    firstMatchResidue = assignMatrix[0][assignmentScores[0]]
    if self.direction == 'i+1':
      seqCode = firstMatchResidue.sequenceCode.replace('-1', '')
      parentMatchResidue = firstMatchResidue.nmrChain.fetchNmrResidue(sequenceCode=seqCode)
      firstMatchResidue = parentMatchResidue

    zAtom = [atom for atom in firstMatchResidue.atoms if atom.apiResonance.isotopeCode == '15N']
    xAtom = [atom for atom in firstMatchResidue.atoms if atom.apiResonance.isotopeCode == '1H']
    yAtoms = [atom for atom in firstMatchResidue.atoms if atom.apiResonance.isotopeCode == '13C']
    zShift = self.project.chemicalShiftLists[0].findChemicalShift(zAtom[0]).value
    xShift = self.project.chemicalShiftLists[0].findChemicalShift(xAtom[0]).value
    yShifts = []
    for atom in yAtoms:
      if self.project.chemicalShiftLists[0].findChemicalShift(atom) is not None:
        yShifts.append(self.project.chemicalShiftLists[0].findChemicalShift(atom).value)

    line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
    line.setPos(QtCore.QPointF(xShift, 0))
    for matchDisplay in self.matchDisplays:
      matchWindow = self.project.getById(matchDisplay)
      matchWindow.orderedStrips[0].changeZPlane(position=zShift)
      matchWindow.orderedStrips[0].spinSystemLabel.setText(firstMatchResidue.sequenceCode)
      matchWindow.orderedStrips[0].plotWidget.addItem(line)
      for shift in yShifts:
        line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('w', style=QtCore.Qt.DashLine))
        line.setPos(QtCore.QPointF(0, shift))
        # matchWindow.orderedStrips[0].plotWidget.addItem(line)


  def setAssigner(self, assigner):
    self.assigner = assigner
    self.project._appBase.current.assigner = assigner

  def qScore(self, query, match):
    if query is not None and match is not None:
      return math.sqrt(((query.value-match.value)**2)/((query.value+match.value)**2))
    else:
      return None

  def selectAssignmentDirection(self, value):
    if value == 'i-1':
      self.assigner.direction = 'left'
      self.direction = 'i-1'

    elif value == 'i+1':
      self.assigner.direction = 'right'
      self.direction = 'i+1'


  def buildAssignmentMatrix(self, queryShifts, matchShifts):

    scores = []
    matrix = {}
    for res, shift in matchShifts.items():
      if len(shift) > 1:
        if self.qScore(queryShifts[0], shift[0]) is not None and self.qScore(queryShifts[1], shift[1]) is not None:

          score = (self.qScore(queryShifts[0], shift[0])+self.qScore(queryShifts[1], shift[1]))/2
          scores.append(score)
          matrix[score] = res
      elif len(shift) == 1:
        if self.qScore(queryShifts[0], shift[0]) is not None:

          score = self.qScore(queryShifts[0], shift[0])
          scores.append(score)
          matrix[score] = res

    return matrix, scores

  def showInterIntraPopup(self):
    popup = InterIntraSpectrumPopup(self, project=self.project)
    popup.exec_()

  def showDisplayPopup(self):
    popup = SelectSpectrumDisplayPopup(self, project=self.project)
    popup.exec_()




