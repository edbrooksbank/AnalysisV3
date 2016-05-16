"""Module Documentation here

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
from ccpn.util.Undo import Undo
# from ccpnmodel.ccpncore.lib.Io import Api as apiIo
from ccpnmodel.ccpncore.testing.CoreTesting import CoreTesting

class PeakUndoTest(CoreTesting):

  # Path of project to load (None for new project)
  projectPath = 'CcpnCourse1b'
    
  def test_new_peak_undo(self):
    
    project = self.project
    nmrProject = project.currentNmrProject or project.findFirstNmrProject()
    experiment = nmrProject.findFirstExperiment(name='HSQC')
    dataSource = experiment.findFirstDataSource(name='HSQC-115')
    peakList = dataSource.newPeakList()
    
    project._undo = Undo()
    project._undo.newWaypoint()
    peak = peakList.newPeak()
    project._undo.undo()
    assert len(peakList.peaks) == 0, 'len(peakList.peaks) = %d' % len(peakList.peaks)
    
  def test_new_peak_undo_redo(self):
    
    project = self.project
    nmrProject = project.currentNmrProject or project.findFirstNmrProject()
    experiment = nmrProject.findFirstExperiment(name='HSQC')
    dataSource = experiment.findFirstDataSource(name='HSQC-115')
    peakList = dataSource.newPeakList()
    
    project._undo = Undo()
    project._undo.newWaypoint()
    peak = peakList.newPeak()
    project._undo.undo()
    project._undo.redo()
    assert len(peakList.peaks) == 1, 'len(peakList.peaks) = %d' % len(peakList.peaks)
    
 
