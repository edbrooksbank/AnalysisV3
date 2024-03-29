"""
Module Documentation here
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:59 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2015-03-16 16:57:10 +0000 (Mon, 16 Mar 2015) $"
#=========================================================================================
# Start of code
#=========================================================================================

from abc import ABC, abstractmethod


class PrintFile(ABC):

    def __init__(self, path, xCount=1, yCount=1, width=800, height=800):
        self.path = path
        self.xCount = xCount
        self.yCount = yCount
        self.width = width
        self.height = height

        self.xNumber = None
        self.yNumber = None

    def __enter__(self):
        self.fp = open(self.path, 'wt')

        return self

    def __exit__(self, *args):
        self.fp.close()

    @abstractmethod
    def startRegion(self, xOutputRegion, yOutputRegion, xNumber=0, yNumber=0):
        pass

    @abstractmethod
    def writeLine(self, x1, y1, x2, y2, colour='#000000'):
        pass

    @abstractmethod
    def writePolyline(self, polyline, colour='#000000'):
        pass

    @abstractmethod
    def writeText(self, text, x, y, colour='#000000', fontsize=10, fontfamily='Verdana'):
        pass
