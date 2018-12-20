"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:37 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.framework import Current


# NBNB This should obviously use the proper objects.as
#  But since the code does not type check or go into the objects, this will do
#

# def test_current_spectra():
#   current = Current.Current(project='dummy')
#   assert (not current.spectra)
#   assert (current.spectrum is None)
#
#   tt = (1,2,3)
#   current.spectra = tt
#   assert (current.spectra == tt)
#   assert (current.spectrum == 3)
#
#   def notifier(value, current=current):
#     current.notifiedSpectra = tuple(value)
#   current.registerNotify(notifier, 'spectra')
#
#   try:
#     current.addSpectrum(4)
#     assert (current.spectrum == 4)
#     assert (current.spectra == tt + (4,))
#     assert (current.notifiedSpectra == tt + (4,))
#   finally:
#     current.unRegisterNotify(notifier, 'spectra')
#
#   current.spectrum = 7
#   assert (current.spectrum == 7)
#   assert (current.spectra == (7,))
#   assert (current.notifiedSpectra == tt + (4,))
#
#   current.clearSpectra()
#   assert (not current.spectra)
#   assert (current.spectrum is None)


def test_current_peaks():
    """Test current.peaks. Since all current functions
    are generated by magic from the same templates, one test should do"""
    current = Current.Current(project='dummy')
    assert (not current.peaks)
    assert (current.peak is None)

    tt = (9, 8, 5)
    current.peaks = tt
    assert (current.peaks == tt)
    assert (current.peak == 5)

    # def notifier(curr):
    #   curr.notifiedPeaks = curr.peaks
    # current.registerNotify(notifier, 'peaks')
    #
    # try:
    #   current.addPeak(47)
    #   assert (current.peak == 47)
    #   assert (current.peaks == tt + (47,))
    #   assert (current.notifiedPeaks == tt+ (47,))
    # finally:
    #   current.unRegisterNotify(notifier, 'peaks')

    current.peak = 27
    assert (current.peak == 27)
    assert (current.peaks == (27,))
    # assert (current.notifiedPeaks == tt + (11,))

    current.clearPeaks()
    assert (not current.peaks)
    assert (current.peak is None)
