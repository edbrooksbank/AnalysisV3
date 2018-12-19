"""
Module Documentation here
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:41 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-16 18:20:01 +0000 (Thu, March 16, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets


# This only works when we have a QtApp instance working; hence it need to go somewhere else.
#from ccpn.framework.PathsAndUrls import fontsPath
#QtGui.QFontDatabase.addApplicationFont(os.path.join(fontsPath, 'open-sans/OpenSans-Regular.ttf'))


class Font(QtGui.QFont):

    def __init__(self, fontName, size, bold=False, italic=False, underline=False, strikeout=False):
        """
        Initialise the font fontName
        :param fontName: font name
        :param size: size of font
        :param bold (optional): make font bold
        :param italic (optional):make fint italic

         to retrieve:
         self.fontName -> fontName
         QFont methods:
         self.pointSize() -> size
         self.italic() -> italic
         self.bold() -> bold
        """

        QtGui.QFont.__init__(self, fontName, size)
        self.fontName = fontName
        self.setBold(bold)
        self.setItalic(italic)
        self.setUnderline(underline)
        self.setStrikeOut(strikeout)
