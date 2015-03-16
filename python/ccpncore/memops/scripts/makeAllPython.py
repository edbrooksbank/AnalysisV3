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
""" Generate autogenerated files from model
All data are read from and written to a file tree of the structure given by
the code repository.
Default is to use the same file tree as the code is loaded from,
determined as the tree that contains memops.universal.constants.

======================COPYRIGHT/LICENSE START==========================

makePython.py: Code generation for CCPN framework

Copyright (C) 2005 Rasmus Fogh (CCPN Project)

=======================================================================

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.
 
A copy of this license can be found in ../../../license/GPL.license
 
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.
 
You should have received a copy of the GNU General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)

- email: ccpn@bioc.cam.ac.uk

=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
R. Fogh, J. Ionides, E. Ulrich, W. Boucher, W. Vranken, J.P. Linge, M.
Habeck, W. Rieping, T.N. Bhat, J. Westbrook, K. Henrick, G. Gilliland,
H. Berman, J. Thornton, M. Nilges, J. Markley and E. Laue (2002). The
CCPN project: An interim report on a data model for the NMR community
(Progress report). Nature Struct. Biol. 9, 416-418.

Rasmus H. Fogh, Wayne Boucher, Wim F. Vranken, Anne
Pajon, Tim J. Stevens, T.N. Bhat, John Westbrook, John M.C. Ionides and
Ernest D. Laue (2005). A framework for scientific data modeling and automated
software development. Bioinformatics 21, 1678-1684.

===========================REFERENCE END===============================
"""

# repository tags for old version to make compatibilty for
#By default takes complete linear versoin list fro current oldVersionTag
#NBNB TODO version 2.0.6 not supported yet.
# NBNB TODO data downgrade not supported yet

import time
import importlib

from ccpncore.memops import Version
from ccpncore.memops.scripts import makePython
from ccpncore.memops.scripts.xmlio import CompatibilityGen

# Default situation - upgrade from all old versions to current one
currentVersion = Version.currentModelVersion
currentUpgradeModule = importlib.import_module('ccpnmodel.%s.upgrade' % currentVersion.getDirName())
oldVersionTags = currentUpgradeModule.versionSequence

        
if __name__ == '__main__':
  
  # make compatibility code
  start = time.time()
  modelPortal = makePython.getModelPortal(currentVersion)
  for oldTag in oldVersionTags[:-1]:
    CompatibilityGen.makeUpgrade(Version.Version(oldTag), currentVersion, modelPortal=modelPortal)
  end = time.time()
  print ("""
  Memops made Compatibility maps, time %s
  """ % (end-start))
  
  # make rest of code
  makePython.makePython(modelPortal)
