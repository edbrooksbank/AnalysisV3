from sklearn import svm
import numpy
from ccpn.lib.assignment import isInterOnlyExpt, getExptDict, assignAlphas, assignBetas
from ccpn.lib.assignment import copyAssignments



if len(project.nmrChains) == 0:
  c = project.newNmrChain()
else:
  c = project.nmrChains[0]

hsqcPeakList = project.getById('PL:HSQC-115.1')

shiftList = project.chemicalShiftLists[0]

for peak in hsqcPeakList.peaks:
  r = c.newNmrResidue()
  a = r.newNmrAtom(name='N')
  a2 = r.newNmrAtom(name='H')
  atoms = [[a2], [a]]
  # peak.dimensionNmrAtoms = atoms
  peak.assignDimension(axisCode='N', value=[r.fetchNmrAtom(name='N')])
  peak.assignDimension(axisCode='H', value=[r.fetchNmrAtom(name='H')])



for peakList in project.peakLists[1:]:
  copyAssignments(hsqcPeakList, peakList)
  # if isInterOnlyExpt(peakList.spectrum.experimentType):
  #   for peak in peakList.peaks:
  #     array = [peak.position[hdim], peak.position[ndim]]
  #     result = clf.predict(array)
  #     print(result)
  #     if not peak.height:
  #       peak.height = peak.apiPeak.findFirstPeakIntensity().value
  #     if peak.height > 0:
  #       name = 'CA'
  #     else:
  #       name = 'CB'
  #     r = project.getById(result[0])
  #     seqCode =  r.sequenceCode+'-1'
  #     newNmrResidue = c.fetchNmrResidue(sequenceCode=seqCode)
  #     newNmrAtom = newNmrResidue.fetchNmrAtom(name=name)
  #     # try:
  #     #   shiftList.newChemicalShift(value = peak.position[cdim], nmrAtom=newNmrAtom)
  #     # except:
  #     #   pass
  #     peak.assignDimension(axisCode='C', value=[newNmrAtom])

#
# for ssLabel in ssLabels:
#
#   nmrResidue = project.getById(ssLabel)
#   for peaks in nmrResidue.fetchNmrAtom(name='N').assignedPeaks:
#     exptDict = getExptDict(project)
#     for peak in peaks:
#       if peak.peakList.spectrum.experimentType in exptDict:
#         if not peak.height:
#           peak.height = peak.apiPeak.findFirstPeakIntensity().value
#         exptDict[peak.peakList.spectrum.experimentType].append(peak)
#   for exptType in exptDict.keys():
#     if not isInterOnlyExpt(exptType):
#       for peak in exptDict[exptType]:
#         if peak.height > 0:
#           peak.assignDimension(axisCode='C', value=[nmrResidue.fetchNmrAtom(name='CA')])
#         if peak.height < 0:
#           peak.assignDimension(axisCode='C', value=[nmrResidue.fetchNmrAtom(name='CB')])
#     else:
#       negativePeaks = [peak for peak in exptDict[exptType] if peak.height < 0]
#       positivePeaks = [peak for peak in exptDict[exptType] if peak.height > 0]
#       assignAlphas(nmrResidue=nmrResidue, peaks=positivePeaks)
#       assignBetas(nmrResidue=nmrResidue, peaks=negativePeaks)
#
# print('DONE')
#
