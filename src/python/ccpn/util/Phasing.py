"""Module Documentation here

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
__dateModified__ = "$dateModified: 2017-07-07 16:32:59 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================

__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
import numpy
from scipy import signal

from typing import Sequence

def phaseRealData(data:Sequence[float], ph0:float=0.0, ph1:float=0.0,
                  pivot:float=1.0) -> Sequence[float]:
  # data is the (1D) spectrum data (real)
  # ph0 and ph1 are in degrees
  
  data = numpy.array(data)
  data = signal.hilbert(data) # convert real to complex data in best way possible
  data = phaseComplexData(data, ph0, ph1, pivot)
  data = data.real
  
  return data
  
def phaseComplexData(data:Sequence[complex], ph0:float=0.0, ph1:float=0.0,
                     pivot:float=1.0) -> Sequence[complex]:
  # data is the (1D) spectrum data (complex)
  # ph0 and ph1 are in degrees
  
  data = numpy.array(data)
  
  ph0 *= numpy.pi / 180.0
  ph1 *= numpy.pi / 180.0
  pivot -= 1 # points start at 1 but code below assumes starts at 0
 
  npts = len(data)
  angles = ph0 + (numpy.arange(npts) - pivot) * ph1 / npts
  multipliers = numpy.exp(-1j * angles)
  
  data *= multipliers
  
  return data
  
  
