"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:40:34 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"

__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.core.testing.WrapperTesting import WrapperTesting

class IntegralListTest(WrapperTesting):

  # Path of project to load (None for new project)
  projectPath = None
    
  def test_2dIntegral(self):
    params1 = dict(value=99., valueError=1.,
                  annotation='Why Bother?',  comment='really!')
    params2 = dict(figureOfMerit=0.92, bias=7, slopes=(0.3,0.9), limits=((1,2),(21,22)))
    params = params1.copy()
    params.update(params2)


    spectrum = self.project.createDummySpectrum(axisCodes=('Hc','Ch'), name='HSQC-tst')
    integralList = spectrum.newIntegralList(title='Int2d', comment='No!')
    self.undo.undo()
    self.undo.redo()
    integral1 = integralList.newIntegral()
    for key, val in params.items():
      setattr(integral1, key, val)
    self.undo.undo()
    self.undo.redo()
    integral2 = integralList.newIntegral(**params)
    integral3 = integralList.newIntegral(value=99., pointLimits=((1,2),(21,22)))
    for key in params1:
      setattr(integral2, key, None)
    integral2.limits = ((None,None), (None,None))
    integral2.bias = 0
    integral2.figureOfMerit = 0
    integral2.slopes = (0,0)
    # Undo and redo all operations

    self.undo.undo()
    self.undo.redo()

  def test_1dIntegral(self):
    spectrum = self.project.createDummySpectrum(axisCodes=('H'), name='H1D-tst')
    integralList = spectrum.newIntegralList()
    integral1 = integralList.newIntegral()
    integral2 = integralList.newIntegral(value=99., valueError=1., bias=7, slopes=(0.9,),
                                         figureOfMerit=0.92, annotation='Why Bother?',
                                         comment='really!', limits=((1,2),))
    integral3 = integralList.newIntegral(value=99., pointLimits=((21,23),))
    # Undo and redo all operations

    self.undo.undo()
    self.undo.redo()

