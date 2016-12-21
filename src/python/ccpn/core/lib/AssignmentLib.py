"""Library functions for (semi)automatic assignment routines

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================

__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================

CCP_CODES = ('Ala', 'Cys', 'Asp', 'Glu', 'Phe', 'Gly', 'His', 'Ile', 'Lys', 'Leu', 'Met', 'Asn',
             'Pro', 'Gln', 'Arg', 'Ser', 'Thr', 'Val', 'Trp', 'Tyr')

ATOM_NAMES = {'13C': ['C', 'CA', 'CB', 'CD', 'CD*', 'CD1', 'CD2', 'CE', 'CE*', 'CE1', 'CE2', 'CE3',
              'CG', 'CG1', 'CG2', 'CH2', 'CZ', 'CZ2', 'CZ3'], '1H': ['H', 'HA', 'HA2', 'HA3', 'HB',
              'HB*', 'HB2', 'HB3', 'HD*', 'HD1', 'HD1*', 'HD2', 'HD2*', 'HD3', 'HE', 'HE*', 'HE1',
              'HE22', 'HE3', 'HG', 'HG1', 'HG1*', 'HG12', 'HG13', 'HG2', 'HG2*', 'HG3', 'HH', 'HH11',
              'HE2', 'HE21', 'HH12', 'HH2', 'HH21', 'HH22', 'HZ', 'HZ*', 'HZ2', 'HZ3'],'15N': ['N',
              'ND1', 'NE', 'NE1', 'NE2', 'NH1', 'NH2', 'NZ']}

from ccpn.util import Common as commonUtil

from ccpn.core.Chain import Chain
from ccpn.core.ChemicalShiftList import ChemicalShiftList
from ccpn.core.NmrResidue import NmrResidue
from ccpn.core.Peak import Peak
from ccpn.core.PeakList import PeakList
from ccpn.core.Project import Project

from ccpnmodel.ccpncore.lib.assignment.ChemicalShift import getSpinSystemResidueProbability, getAtomProbability, getResidueAtoms, getCcpCodes, getSpinSystemScore
import typing
import numpy

def isInterOnlyExpt(experimentType:str) -> bool:
  """
  Determines if the specified experiment is an inter-residual only experiment
  """
  if not experimentType:
    return False
  expList = ('HNCO', 'CONH', 'CONN', 'H[N[CO', 'seq.', 'HCA_NCO.Jmultibond')
  experimentTypeUpper = experimentType.upper()
  if(any(expType in experimentTypeUpper for expType in expList)):
    return True
  return False


def assignAlphas(nmrResidue:NmrResidue, peaks:typing.List[Peak]):
  """
  Assigns CA and CA-1 NmrAtoms to dimensions of pairs of specified peaks, assuming that one has
  a height greater than the other, e.g. in an HNCA or HNCACB experiment.
  """
  if len(peaks) > 1:
    chain = nmrResidue.nmrChain
    newNmrResidue = chain.fetchNmrResidue(nmrResidue.sequenceCode+'-1')
    a3 = newNmrResidue.fetchNmrAtom(name='CA')
    a4 = nmrResidue.fetchNmrAtom(name='CA')
    if peaks[0].height > peaks[1].height:
      peaks[0].assignDimension(axisCode='C', value=[a4])
      peaks[1].assignDimension(axisCode='C', value=[a3])
    if peaks[0].height < peaks[1].height:
      peaks[0].assignDimension(axisCode='C', value=[a3])
      peaks[1].assignDimension(axisCode='C', value=[a4])
  elif len(peaks) == 1:
    peaks[0].assignDimension(axisCode='C', value=[nmrResidue.fetchNmrAtom(name='CA')])


def assignBetas(nmrResidue:NmrResidue, peaks:typing.List[Peak]):
  """
  Assigns CB and CB-1 NmrAtoms to dimensions of specified peaks.
  """
  if len(peaks) > 1:
    chain = nmrResidue.nmrChain
    newNmrResidue = chain.fetchNmrResidue(nmrResidue.sequenceCode+'-1')
    a3 = newNmrResidue.fetchNmrAtom(name='CB')
    a4 = nmrResidue.fetchNmrAtom(name='CB')
    if abs(peaks[0].height) > abs(peaks[1].height):
      peaks[0].assignDimension(axisCode='C', value=[a4])
      peaks[1].assignDimension(axisCode='C', value=[a3])

    if abs(peaks[0].height) < abs(peaks[1].height):
      peaks[0].assignDimension(axisCode='C', value=[a3])
      peaks[1].assignDimension(axisCode='C', value=[a4])

  elif len(peaks) == 1:
    peaks[0].assignDimension(axisCode='C', value=[nmrResidue.fetchNmrAtom(name='CB')])


def getNmrResiduePrediction(nmrResidue:NmrResidue, chemicalShiftList:ChemicalShiftList, prior:float=0.05) -> list:
  """
  Takes an NmrResidue and a ChemicalShiftList and returns a dictionary of the residue type to
  confidence levels for that NmrResidue.
  """

  predictions = {}
  spinSystem = nmrResidue._wrappedData
  for code in CCP_CODES:
    predictions[code] = float(getSpinSystemResidueProbability(spinSystem, chemicalShiftList._wrappedData, code, prior=prior))
  tot = sum(predictions.values())
  refinedPredictions = {}
  for code in CCP_CODES:
    if tot > 0:
      v = int(predictions[code]/tot * 100)
      if v > 0:
        refinedPredictions[code] = v

  finalPredictions = []

  for value in sorted(refinedPredictions.values(), reverse=True)[:5]:
    key = [key for key, val in refinedPredictions.items() if val==value][0]
    finalPredictions.append([key, str(value)+' %'])

  return finalPredictions


def getNmrAtomPrediction(ccpCode:str, value:float, isotopeCode:str, strict:bool=False) -> list:
  """
  Takes a ccpCode, a chemical shift value and an isotope code and returns a dictionary of
  atom type predictions to confidence values..
  """

  predictions = {}
  for atomName in getResidueAtoms(ccpCode, 'protein'):
    if atomName in ATOM_NAMES[isotopeCode]:
      predictions[ccpCode, atomName] = getAtomProbability(ccpCode, atomName, value)
  tot = sum(predictions.values())
  refinedPredictions = {}
  for key, value in predictions.items():
    if strict:
      if value > 1e-3:
        v = int(value/tot * 100)
      else:
        v = 0
    else:
      v = int(value/tot * 100)
    if v > 0:
      refinedPredictions[key] = v

  finalPredictions = []

  for value in sorted(refinedPredictions.values(), reverse=True)[:5]:
    key = [key for key, val in refinedPredictions.items() if val==value][0]
    finalPredictions.append([key, value])

  return finalPredictions


def copyPeakListAssignments(referencePeakList:PeakList, matchPeakList:PeakList):
  """
  Takes a reference peakList and assigns NmrAtoms to dimensions
  of a match peakList based on matching axis codes.
  """

  import numpy
  from sklearn.ensemble import RandomForestClassifier
  project = referencePeakList.project
  refAxisCodes = referencePeakList.spectrum.axisCodes
  matchAxisCodes = matchPeakList.spectrum.axisCodes
  if len(refAxisCodes) < len(matchAxisCodes):
    mappingArray = commonUtil._axisCodeMapIndices(refAxisCodes, matchAxisCodes)
  else:
    mappingArray = commonUtil._axisCodeMapIndices(matchAxisCodes, refAxisCodes)
  refPositions = [numpy.array([peak.position[dim] for dim in mappingArray if dim is not None])
                  for peak in referencePeakList.peaks]
  refLabels = [[peak.pid] for peak in referencePeakList.peaks]
  clf=RandomForestClassifier()
  clf.fit(refPositions, refLabels)

  for peak in matchPeakList.peaks:
    matchArray = []
    for dim in mappingArray:
      if dim is not None:
        matchArray.append(peak.position[dim])

    result = ''.join((clf.predict(numpy.array(matchArray))))

    tolerances = peak.peakList.spectrum.assignmentTolerances
    dimNmrAtoms = project.getByPid(result).dimensionNmrAtoms
    refPositions = project.getByPid(result).position
    if all([abs(refPositions[ii] - peak.position[ii]) < tolerances[ii] for ii in mappingArray if ii is not None]):
      [peak.assignDimension(axisCode=refAxisCodes[ii], value=dimNmrAtoms[ii]) for ii in mappingArray if ii is not None]


def propagateAssignments(peaks:typing.List[Peak]=None, referencePeak:Peak=None, current:object=None,
                         tolerances:typing.List[float]=None):
  """
  Propagates dimensionNmrAtoms for each dimension of the specified peaks to dimensions of other
  peaks.
  """

  if referencePeak:
    peaksIn = [referencePeak, ]
  else:
    if peaks:
      peaksIn = peaks
    else:
      peaksIn = current.peaks
  if not tolerances:
    tolerances = []

  dimNmrAtoms = {}

  for peak in peaksIn:
    for i, dimensionNmrAtom in enumerate(peak.dimensionNmrAtoms):

      key = peak.peakList.spectrum.axisCodes[i]
      if dimNmrAtoms.get(key) is None:
        dimNmrAtoms[key] = []

      if len(peak.dimensionNmrAtoms[i]) > 0:
        for dimensionNmrAtoms in peak.dimensionNmrAtoms[i]:
          nmrAtom = dimensionNmrAtoms

          dimNmrAtoms[key].append(nmrAtom)


  shiftRanges = {}
  spectrum = peak.peakList.spectrum
  assignmentTolerances = list(spectrum.assignmentTolerances)
  for tol in assignmentTolerances:
    if tol is None:
      index = assignmentTolerances.index(tol)
      tolerance = spectrum.spectralWidths[index]/spectrum.pointCounts[index]
      spectrumTolerances = list(spectrum.assignmentTolerances)
      spectrumTolerances[index] =  tolerance
      spectrum.assignmentTolerances = spectrumTolerances
  for peak in peaksIn:
    for i, axisCode in enumerate(peak.peakList.spectrum.axisCodes):

      if axisCode not in shiftRanges:
        shiftMin, shiftMax = peak.peakList.spectrum.spectrumLimits[i]
        shiftRanges[axisCode] = (shiftMin, shiftMax)

      else:
          shiftMin, shiftMax = shiftRanges[axisCode]

      if i < len(tolerances):
        tolerance = tolerances[i]
      else:
        tolerance = peak.peakList.spectrum.assignmentTolerances[i]

      pValue = peak.position[i]

      extantNmrAtoms = []

      for dimensionNmrAtom in peak.dimensionNmrAtoms:
        extantNmrAtoms.append(dimensionNmrAtom)

      assignNmrAtoms = []
      closeNmrAtoms = []

      for nmrAtom in dimNmrAtoms[axisCode]:
        if nmrAtom not in extantNmrAtoms:
          shiftList = peak.peakList.spectrum.chemicalShiftList
          shift = shiftList.getChemicalShift(nmrAtom.id)

          if shift:

            sValue = shift.value

            if not (shiftMin < sValue < shiftMax):
              continue

            assignNmrAtoms.append(nmrAtom)

            if abs(sValue-pValue) <= tolerance:
              closeNmrAtoms.append(nmrAtom)

      if closeNmrAtoms:
        for nmrAtom in closeNmrAtoms:
          peak.assignDimension(axisCode, nmrAtom)

      elif not extantNmrAtoms:
        for nmrAtom in assignNmrAtoms:
          peak.assignDimension(axisCode, nmrAtom)


def getSpinSystemsLocation(project:Project, nmrResidues:typing.List[NmrResidue],
                           chain:Chain, chemicalShiftList:ChemicalShiftList)  -> list:
  """
  Determines location of a set of NmrResidues in the specified chain using residue type
  predictions.
  """


  # TODO NBNB rename variables so api level objects have .api...' names
  # Also consider moving to ccpnmodel, or refactoring. NBNB

  nmrProject = project._wrappedData
  spinSystems = [nmrResidue._wrappedData for nmrResidue in nmrResidues]
  chain = chain._wrappedData
  shiftList = chemicalShiftList._wrappedData

  scoreMatrix = []

  ccpCodes = getCcpCodes(chain)

  N = len(ccpCodes)

  for spinSystem0 in spinSystems:
    scoreList = [None] * N

    if spinSystem0:
      shifts = []
      for resonance in spinSystem0.resonances:
        shift = resonance.findFirstShift(parentList=shiftList)
        if shift:
          shifts.append(shift)

      scores = getSpinSystemScore(spinSystem0, shifts, chain, shiftList)

      for i, ccpCode in enumerate(ccpCodes):
        scoreList[i] = (scores[ccpCode], ccpCode)

      scoreList.sort()
      scoreList.reverse()

    scoreMatrix.append(scoreList)


  window = len(nmrResidues)
  textMatrix = []
  objectList = []

  if chain and scoreMatrix:
    matches = []

    assignDict = {}
    for spinSystem in nmrProject.resonanceGroups:
      residue = spinSystem.assignedResidue
      if residue:
        assignDict[residue] = spinSystem

    residues = chain.sortedResidues()
    seq = [r.ccpCode for r in residues]

    seq = [None, None] + seq + [None, None]
    residues = [None, None] + residues + [None, None]
    nRes = len(seq)

    if nRes >= window:
      scoreDicts = []
      ccpCodes  = getCcpCodes(chain)

      for scores in scoreMatrix:
        scoreDict = {}
        for ccpCode in ccpCodes:
          scoreDict[ccpCode] = None

        for data in scores:
          if data:
            score, ccpCode = data
            scoreDict[ccpCode] = score

        scoreDicts.append(scoreDict)
      sumScore = 0.0
      for i in range(nRes-window):

        score = 1.0

        for j in range(window):
          ccpCode = seq[i+j]
          score0 = scoreDicts[j].get(ccpCode)

          if (ccpCode is None) and (spinSystems[j]):
            break
          elif score0:
            score *= score0
          elif score0 == 0.0:
            break

        else:
          matches.append((score, residues[i:i+window]))
          sumScore += score

      matches.sort()
      matches.reverse()


      for i, data in enumerate(matches[:10]):
        score, residues = data
        if sumScore > 0:
          score /= sumScore
        datum = [i+1, 100.0*score]

        for residue in residues:
          if residue:
            datum.append(residue.seqCode)
          else:
            datum.append(None)
            # colors.append(None)

        textMatrix.append(datum)
        residues2 = [project._data2Obj.get(residue) for residue in residues]
        objectList.append([100*score, residues2])

    return objectList


def nmrAtomPairsByDimensionTransfer(peakLists:typing.Sequence[PeakList]) -> dict:
  """From one or more peakLists belonging to the same spectrum,
  get a dictionary of magnetisationTransferTuple (See Spectrum.magnetisationTransfers
  for documentation) to a set of NmrAtom pairs tha are coupled by the magnetisation transfer.
  If the two dimensions have the same nucleus, the NmrAtom pairs are sorted, otherwise
  they are in the dimension order.

  Peak.assignedNmrAtoms is used to determine which NmrAtoms are connected"""

  # For subsequent filtering, I recommend:
  # isInterOnlyExpt (this file)
  # NmrAtom.boundNmrAtoms

  result = {}
  if peakLists:

    spectrum = peakLists[0].spectrum
    if any (x for x in peakLists[1:] if x.spectrum is not spectrum):
      raise ValueError("PeakLists do not belong to the same spectrum: %s" % peakLists)

    magnetisationTransfers = spectrum.magnetisationTransfers
    for mt in magnetisationTransfers:
      result[mt] = set()

    # Get sets of NmrAtom pairs
    for peakList in peakLists:
      for peak in peakList.peaks:
        for assignment in peak.assignedNmrAtoms:
          for mt, aSet in result.items():
            nmrAtoms = (assignment[mt[0]-1], assignment[mt[1]-1])
            if not None in nmrAtoms:
              aSet.add(nmrAtoms)

    # Sort NmrAtoms where the nucleus is the same on both sides (or one is undetermined)
    for mt, aSet in result.items():
      tt = spectrum.isotopeCodes
      isotopeCodes = (tt[mt[0]-1], tt[mt[1]-1])
      if None in isotopeCodes or isotopeCodes[0] == isotopeCodes[1]:
        newSet = set(tuple(sorted(x for x in nmrAtoms)) for nmrAtoms in aSet)
        result[mt] = newSet

  return result


def getBoundNmrAtomPairs(nmrAtoms, nucleus) -> list:
  """
  Takes a set of NmrAtoms and a nucleus e.g. 'H' or 'C' and returns a list of unique pairs of
  nmrAtoms in the input that are bound to each other.
  """
  result = []
  for na1 in nmrAtoms:
    if na1.name.startswith(nucleus):
      for na2 in na1.boundNmrAtoms:
        if na2 in nmrAtoms:
          result.append(tuple(sorted([na1, na2])))

  return list(set(result))


def findClosePeaks(peak, matchPeakList, tolerance=0.02):
  """
  Takes an input peak and finds all peaks in the matchPeakList that are close in space to the position
  of the input peak. A close peak is defined as one for which the euclidean distance between its position
  and that of the input peak is less than the specified tolerance. AxisCodes are used to match dimensions
  between peaks to ensure correct distance calculation.
  """
  closePeaks = []
  refAxisCodes = peak.axisCodes
  matchAxisCodes = matchPeakList.spectrum.axisCodes
  mappingArray = [refAxisCodes.index(axisCode) for axisCode in refAxisCodes
                  if axisCode in matchAxisCodes]
  mappingArray2 = [matchAxisCodes.index(axisCode) for axisCode in refAxisCodes
                   if axisCode in matchAxisCodes]
  refPeakPosition = numpy.array([peak.position[dim] for dim in mappingArray if dim is not None])

  for mPeak in matchPeakList.peaks:
    matchArray = []
    for dim in mappingArray2:
      matchArray.append(mPeak.position[dim])

    dist = numpy.linalg.norm(refPeakPosition-numpy.array(matchArray))
    if dist < tolerance:
      closePeaks.append(mPeak)

  return closePeaks

def copyPeakAssignments(refPeak, peaks):

  refAxisCodes = refPeak.axisCodes
  for peak in peaks:
    matchAxisCodes = peak.axisCodes
    mappingArray2 = [matchAxisCodes.index(axisCode) for axisCode in refAxisCodes if axisCode in matchAxisCodes]
    for jj, dim in enumerate(mappingArray2):
      atom = refPeak.dimensionNmrAtoms[jj][0]
      axisCode = peak.axisCodes[dim]
      peak.assignDimension(axisCode, [atom])