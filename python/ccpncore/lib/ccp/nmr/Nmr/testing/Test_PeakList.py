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
# import numpy

from ccpncore.testing.CoreTesting import CoreTesting

class PeakListPickPeaksTest(CoreTesting):

  # Path of project to load (None for new project)
  projectPath = 'CcpnCourse1a'

  def Test_PickPeaks(self, *args, **kw):
    
    dataSource = self.nmrProject.findFirstExperiment(name='HSQC').findFirstDataSource()
    peakList = dataSource.findFirstPeakList()
    numPoints = [dataDim.numPoints for dataDim in dataSource.sortedDataDims()]
    startPoint = [0, 0]
    endPoint = numPoints
    posLevel = 1.0e8

    peaks = peakList.pickNewPeaks(startPoint, endPoint, posLevel, fitMethod='gaussian')
    print('number of peaks', len(peaks))
    assert len(peaks) == 4, 'len(peaks) = %d' % len(peaks)
    
    for peak in peaks:
      print([peakDim.position for peakDim in peak.sortedPeakDims()])
    
  def Test_PickPeaks2(self, *args, **kw):
    
    dataSource = self.nmrProject.findFirstExperiment(name='HSQC').findFirstDataSource()
    peakList = dataSource.findFirstPeakList()
    numPoints = [dataDim.numPoints for dataDim in dataSource.sortedDataDims()]
    startPoint = [600, 100]
    endPoint = [700, 150]
    posLevel = 1.0e8

    peaks = peakList.pickNewPeaks(startPoint, endPoint, posLevel, fitMethod='gaussian')
    print('number of peaks', len(peaks))
    assert len(peaks) == 3, 'len(peaks) = %d' % len(peaks)
    
    for peak in peaks:
      print([peakDim.position for peakDim in peak.sortedPeakDims()])
  