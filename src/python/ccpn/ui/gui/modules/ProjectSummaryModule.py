"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2016-09-07 12:42:52 +0100 (Wed, 07 Sep 2016) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: skinnersp $"
__date__ = "$Date: 2016-09-07 12:42:52 +0100 (Wed, 07 Sep 2016) $"
__version__ = "$Revision: 9852 $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.Table import ObjectTable, Column

def _percentage(count, totalCount, decimalPlaceCount=0):

  if totalCount:
    return int(round((100.0 * count) / totalCount, decimalPlaceCount))
  else:
    return 0

# PEAKLISTS

def _partlyAssignedPeakCount(peakList):

  return len([peak for peak in peakList.peaks if any(peak.dimensionNmrAtoms)])

def _partlyAssignedPeakPercentage(peakList):

  return _percentage(_partlyAssignedPeakCount(peakList), len(peakList.peaks))

def _fullyAssignedPeakCount(peakList):

  return len([peak for peak in peakList.peaks if all(peak.dimensionNmrAtoms)])

def _fullyAssignedPeakPercentage(peakList):

  return _percentage(_fullyAssignedPeakCount(peakList), len(peakList.peaks))

# CHAINS

def _assignableAtomCount(chain):

  return len([atom for atom in chain.atoms if atom._wrappedData.chemAtom and atom._wrappedData.chemAtom.waterExchangeable])

def _assignedAtomCount(chain):

  return len([atom for atom in chain.atoms if atom.nmrAtom])

def _assignedAtomPercentage(chain):

  return _percentage(_assignedAtomCount(chain), _assignableAtomCount(chain))

class ProjectSummaryModule(CcpnModule):

  def __init__(self, project):

    CcpnModule.__init__(self, name='Project Summary')

    self.project = project
    self._setupData()

    row = 0

    # SPECTRA

    label = Label(self.mainWidget, text='Spectra', grid=(row, 0), hAlign='l')
    row += 1

    columns = [
      Column('#', lambda spectrum: self.spectrumNumberDict[spectrum], tipText='Number'),
      Column('Id', lambda spectrum: spectrum.id, tipText='Spectrum id'),
      Column('Dimension count', lambda spectrum: spectrum.dimensionCount, tipText='Spectrum dimension count'),
      Column('Chemical shiftList',
             lambda spectrum: spectrum.chemicalShiftList.id, tipText='Spectrum chemical shiftList'),
      Column('File path', lambda spectrum: spectrum.filePath, tipText='Spectrum data file path'),
    ]
    self.spectrumTable = ObjectTable(self.mainWidget, columns=columns, objects=self.spectra, grid=(row, 0))
    row += 1

    # PEAKLISTS

    label = Label(self.mainWidget, text='PeakLists', grid=(row, 0), hAlign='l')
    row += 1

    columns = [
      Column('#', lambda peakList: self.peakListNumberDict[peakList], tipText='Number'),
      Column('Id', lambda peakList: peakList.id, tipText='PeakList id'),
      Column('Peak count', lambda peakList: len(peakList.peaks), tipText='Number of peaks in peakList'),
      Column('Partly assigned count', _partlyAssignedPeakCount,
             tipText='Number of peaks in peakList at least partially assigned'),
      Column('Partly assigned %', _partlyAssignedPeakPercentage,
             tipText='Percentage of peaks in peakList at least partially assigned'),
      Column('Fully assigned count', _fullyAssignedPeakCount,
             tipText='Number of peaks in peakList fully assigned'),
      Column('Fully assigned %', _fullyAssignedPeakPercentage,
             tipText='Percentage of peaks in peakList fully assigned'),
    ]

    self.peakListTable = ObjectTable(self.mainWidget, columns=columns, objects=self.peakLists, grid=(row, 0))
    row += 1

    return # TEMP (below code not working and very, very slow)

    # CHAINS

    label = Label(self.mainWidget, text='Chains', grid=(row, 0), hAlign='l')
    row += 1

    columns = [
      Column('#', lambda chain: self.chainNumberDict[chain], tipText='Number'),
      Column('Id', lambda chain: chain.id, tipText='Chain id'),
      Column('Residue count', lambda chain: len(chain.residues), tipText='Number of residues in chain'),
      Column('Assignable atom count', _assignableAtomCount,
             tipText='Number of atoms in chain which are assignable to'),
      Column('Assigned atom count', _assignedAtomCount,
             tipText='Number of atoms in chain which are assigned to'),
      Column('Assigned atom %', _assignedAtomPercentage,
             tipText='Percentage of atoms in chain which are assigned to'),
    ]

    self.chainTable = ObjectTable(self.mainWidget, columns=columns, objects=self.chains, grid=(row, 0))
    row += 1

  def _setupData(self):

    # SPECTRA

    self.spectra = self.project.spectra
    self.spectrumNumberDict = {}
    for n, spectrum in enumerate(self.spectra):
      self.spectrumNumberDict[spectrum] = n+1

    # PEAKLISTS

    self.peakLists = []
    self.peakListNumberDict = {}
    n = 1
    for spectrum in self.spectra:
      self.peakLists.extend(spectrum.peakLists)
      for peakList in spectrum.peakLists:
        self.peakListNumberDict[peakList] = n
        n += 1

    # CHAINS

    self.chains = self.project.chains
    self.chainNumberDict = {}
    for n, chain in enumerate(self.chains):
      self.chainNumberDict[chain] = n+1
