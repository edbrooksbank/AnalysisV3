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
from ccpn.testing.Testing import Testing

# from ccpn.lib.spectrum import Spectrum

class SpectrumTest(Testing):

  def __init__(self, *args, **kw):
    Testing.__init__(self, 'CcpnCourse1a', *args, **kw)
    self.spectrumName = '115'

  def test_getPlaneData(self):
    spectrum = self.getSpectrum()
    planeData = spectrum.getPlaneData()
    print('planeData.shape =', planeData.shape)
    print('planeData =', planeData[508:,2045:])
    
  def test_getSliceData(self):
    spectrum = self.getSpectrum()
    sliceData = spectrum.getSliceData()
    print('sliceData.shape =', sliceData.shape)
    print('sliceData =', sliceData)
    

