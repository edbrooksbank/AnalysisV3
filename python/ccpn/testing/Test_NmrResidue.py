"""Test code for NmrResidue

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================
from ccpn.testing.WrapperTesting import WrapperTesting

class NmrResidueTest(WrapperTesting):

  # Path of project to load (None for new project
  projectPath = 'CcpnCourse2c'

  def test_reassign1(self):
    nchain = self.project.getByPid('NC:A')
    nchain0 = self.project.getByPid('NC:@')
    nr1, nr2 = nchain.nmrResidues[:2]
    res1 = nr1.residue
    res2 = nr2.residue
    res3 = self.project.chains[0].residues[2]
    nr3 = res3.nmrResidue
    nr2.residue = None
    assert nr2.longPid == "NmrResidue:A.@2.ARG"
    target =  self.project.getByPid('NR:A.2.LYS')
    target.sequenceCode = None
    assert target.longPid == "NmrResidue:A.@11.LYS"
    nr2.sequenceCode = '2'
    assert nr2.longPid == "NmrResidue:A.2.LYS"
    newNr = nchain0.newNmrResidue()
    assert newNr.longPid == "NmrResidue:@.@89."
    nr3.nmrChain = nchain0
    assert nr3.longPid == "NmrResidue:@.3.GLU"
    newNr.residue = res3
    assert newNr.longPid == "NmrResidue:A.3.GLU"
    nchain.shortName = 'X'
    assert nchain.longPid == "NmrChain:X"
    assert nr2.longPid == "NmrResidue:X.2.ARG"
    
  def test_fetchNmrResidue(self):
    nmrChain = self.project.fetchNmrChain(shortName='@1')
    res1 = nmrChain.fetchNmrResidue(sequenceCode="127B", residueType="ALA")
    res2 = nmrChain.fetchNmrResidue(sequenceCode="127B", residueType="ALA")
    assert res1 is res2, "fetchNmrResidue takes existing NmrResidue if possible"

  def test_fetchEmptyNmrResidue(self):
    nmrChain = self.project.fetchNmrChain(shortName='@1')
    res1 = nmrChain.fetchNmrResidue(sequenceCode=None, residueType="ALA")
    sequenceCode = '@%s' % res1._wrappedData.serial
    assert res1.sequenceCode == sequenceCode
    res2 = nmrChain.fetchNmrResidue(sequenceCode=sequenceCode)
    assert res1 is res2, "empty NmrResidue: fetchNmrResidue takes existing NmrResidue if possible"

  def test_offsetNmrResidue(self):
    nmrChain = self.project.fetchNmrChain(shortName='@1')
    res1 = nmrChain.fetchNmrResidue(sequenceCode="127B", residueType="ALA")
    res2 = nmrChain.fetchNmrResidue(sequenceCode="127B-1", residueType="ALA")
    assert res2._wrappedData.mainResonanceGroup is res1._wrappedData
    res3 = nmrChain.fetchNmrResidue(sequenceCode="127B-1", residueType="ALA")
    assert res2 is res3, "fetchNmrResidue with offset takes existing NmrResidue if possible"
    res1.delete()
    assert res2._wrappedData.isDeleted, "Deleting main NmrResidue also deletes satellites"

  def test_get_by_serialName(self):
    nmrChain = self.project.fetchNmrChain(shortName='@1')
    res1 = nmrChain.fetchNmrResidue(sequenceCode=None, residueType="ALA")
    serialName = '@%s' % res1._wrappedData.serial
    res2 = nmrChain.fetchNmrResidue(sequenceCode=serialName)
    assert res1 is res2
    res3 = nmrChain.fetchNmrResidue(sequenceCode=serialName + '+0')
    assert res3._wrappedData.mainResonanceGroup is res1._wrappedData