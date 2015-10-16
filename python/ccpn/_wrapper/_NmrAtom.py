"""Module Documentation here

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

import operator
from ccpn import AbstractWrapperObject
from ccpn import Project
from ccpn import NmrResidue
from ccpn import Atom
from ccpn import Peak
from ccpncore.lib import Constants
from ccpncore.api.ccp.nmr.Nmr import Resonance as ApiResonance
from ccpncore.lib.spectrum.Spectrum import name2IsotopeCode
from ccpncore.util import Pid
from ccpncore.util.Types import Union, Tuple


class NmrAtom(AbstractWrapperObject):
  """Nmr Atom, used for assigning,peaks and shifts. (corresponds to ApiResonance)."""

  
  #: Short class name, for PID.
  shortClassName = 'NA'
  # Attribute it necessary as subclasses must use superclass className
  className = 'NmrAtom'

  #: Name of plural link to instances of class
  _pluralLinkName = 'nmrAtoms'
  
  #: List of child classes.
  _childClasses = []
  

  # CCPN properties  
  @property
  def _apiResonance(self) -> ApiResonance:
    """ CCPN atom matching Atom"""
    return self._wrappedData


  @property
  def _parent(self) -> NmrResidue:
    """Parent (containing) object."""
    return self._project._data2Obj[self._wrappedData.resonanceGroup]
  
  nmrResidue = _parent
    
  @property
  def _key(self) -> str:
    """Atom name string (e.g. 'HA') regularised as used for ID"""
    return self._wrappedData.name.translate(Pid.remapSeparators)

  @property
  def name(self) -> str:
    """Atom name string (e.g. 'HA')"""
    return self._wrappedData.name

  @property
  def atom(self) -> Atom:
    """Atom to which NmrAtom is assigned. NB resetting the atom will rename the NmrAtom"""
    atom = self._wrappedData.atom
    return None if atom is None else self._project._data2Obj.get(atom)

  @atom.setter
  def atom(self, value:Atom):
    self._wrappedData.atom = None if value is None else value._wrappedData

  @property
  def isotopeCode(self) -> str:
    """isotopeCode of NmrAtom. Set automatically on creation (from NmrAtom name) and cannot be reset"""
    return self._wrappedData.isotopeCode


  def assignedPeaks(self) -> Tuple[Peak]:
    """All ccn.Peaks assigned to the ccpn.NmrAtom"""
    apiResonance = self._wrappedData
    apiPeaks = [x.peakDim.peak for x in apiResonance.peakDimContribs]
    apiPeaks.extend([x.peakDim.peak for x in apiResonance.peakDimContribNs])

    data2Obj = self._project._data2Obj
    result = [sorted(data2Obj[x] for x in set(apiPeaks))]
    #
    return result

  def rename(self, value:str=None):
    """Rename object, changing id, Pid, and internal representation"""
    # NB This is a VERY special case
    # - API code and notifiers will take care of resetting id and Pid
    if value:
      isotopeCode = self._wrappedData.isotopeCode
      newIsotopeCode = name2IsotopeCode(value)
      if isotopeCode == 'unknown':
        self._wrappedData.isotopeCode = newIsotopeCode
      elif newIsotopeCode != isotopeCode:
        raise ValueError("Cannot rename %s type NmrAtom to %s" % (isotopeCode, value))

    self._wrappedData.name = value or None

  def reassigned(self, atomId:str=None, chainCode:str=None, sequenceCode:Union[int,str]=None,
               residueType:str=None, name:str=None, mergeToExisting=True) -> 'NmrAtom':
    """Get NmrAtom reassigned according to residueId or other parameters.
    Result may be self changed in place or a copy (with self deleted), so ALWAYS use the return value.
    Setting atomId deassigns empty residueType or name fields,
    while empty parameters (e.g. chainCode=None) cause no change.
    If the nmrAtom being reassigned to exists and merging is allowed, the two will be merged.
    NB Merging is NOT undoable
    """
    clearUndo = False
    undo = self._apiResonance.root._undo
    apiResonance = self._apiResonance
    apiResonanceGroup = apiResonance.resonanceGroup
    if isinstance(sequenceCode, int):
      sequenceCode = str(sequenceCode)
    elif not sequenceCode:
      # convert empty string to None
      sequenceCode = None

    if atomId:
      if any((chainCode, sequenceCode, residueType, name)):
        raise ValueError("reassigned: assignment parameters only allowed if atomId is None")
      else:
        # Remove colon prefix, if any, and set parameters
        atomId = atomId.split(Pid.PREFIXSEP,1)[-1]
        # NB trick with setting ll first required
        # because the pssed-in Pid may not ahve all three components
        ll = [None, None, None, None]
        for ii,val in enumerate(Pid.splitId(atomId)):
          ll[ii] = val
        chainCode, sequenceCode, residueType, name = ll
        if chainCode is None:
          raise ValueError("chainCode part of atomId cannot be empty'")
        if sequenceCode is None:
          raise ValueError("sequenceCode part of atomId cannot be empty'")

    else:
      # set missing parameters to existing values
      chainCode = chainCode or apiResonanceGroup.nmrChain.code
      sequenceCode = sequenceCode or apiResonanceGroup.sequenceCode
      residueType = residueType or apiResonanceGroup.residueType
      name = name or apiResonance.name

    oldNmrResidue = self.nmrResidue
    nmrChain = self._project.fetchNmrChain(chainCode)
    if residueType:
      nmrResidue = nmrChain.fetchNmrResidue(sequenceCode, residueType)
    else:
      nmrResidue = nmrChain.fetchNmrResidue(sequenceCode)

    if name:
      # result is matching NmrAtom, or (if None) self
      result = nmrResidue.getNmrAtom(name) or self
    else:
      # No NmrAtom can match, result is self
      result = self

    if nmrResidue is oldNmrResidue:
      if name != self.name:

        if result is self:
          # NB self.name can never be returned as None
          self._wrappedData.name = name or None

        elif mergeToExisting:
          clearUndo = True
          result._wrappedData.absorbResonance(self._apiResonance)

        else:
          raise ValueError("New assignment clash with existing assignment,"
                           " and merging is disallowed")

    else:
      if result is self:
        if nmrResidue.getNmrAtom(self.name) is None:
          self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
          if name != self.name:
            self._wrappedData.name = name or None
        elif name is None or oldNmrResidue.getNmrAtom(name) is None:
          if name != self.name:
            self._wrappedData.name = name or None
          self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
        else:
          self._wrappedData.name = None  # Necessary to avoid name clashes
          self._apiResonance.resonanceGroup = nmrResidue._apiResonanceGroup
          self._wrappedData.name = name

      elif mergeToExisting:
        # WARNING if we get here undo is no longer possible
        clearUndo = True
        result._wrappedData.absorbResonance(self._apiResonance)

      else:
        raise ValueError("New assignment clash with existing assignment,"
                         " and merging is disallowed")
    #
    if undo is not None and clearUndo:
      undo.clear()
    #
    return result


  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent: NmrResidue)-> list:
    """get wrappedData (ApiResonance) for all NmrAtom children of parent NmrResidue"""
    return sorted(parent._wrappedData.resonances, key=operator.attrgetter('name'))

def getter(self:Atom) -> NmrAtom:
  nmrResidue = self.residue.nmrResidue
  if nmrResidue is None:
    return None
  else:
    obj = nmrResidue._wrappedData.findFirstResonance(name=self._wrappedData.name)
    return None if obj is None else self._project._data2Obj.get(obj)

def setter(self:Atom, value:NmrAtom):
  oldValue = self.nmrAtom
  if oldValue is value:
    return
  elif oldValue is not None:
    oldValue.atom = None

  if value is not None:
    value.atom = self
Atom.nmrAtom = property(getter, setter, None, "NmrAtom to which Atom is assigned")

del getter
del setter
    
def newNmrAtom(self:NmrResidue, name:str=None, isotopeCode:str=None) -> NmrAtom:
  """Create new child NmrAtom. If name is None, use nucleus@serial"""
  nmrProject = self._project._wrappedData
  resonanceGroup = self._wrappedData

  if not isotopeCode:
    if name:
      isotopeCode = name2IsotopeCode(name) or 'unknown'
    else:
      raise ValueError("newNmrAtom requires either name or isotopeCode as input")


  return self._project._data2Obj.get(nmrProject.newResonance(resonanceGroup=resonanceGroup,
                                                             name=name,
                                                             isotopeCode=isotopeCode))

def fetchNmrAtom(self:NmrResidue, name:str):
  """Fetch NmrAtom with name=name, creating it if necessary"""
  resonanceGroup = self._wrappedData
  return (self._project._data2Obj.get(resonanceGroup.findFirstResonance(name=name)) or
          self.newNmrAtom(name=name))

def produceNmrAtom(self:Project, atomId:str=None, chainCode:str=None,
                   sequenceCode:Union[int,str]=None,
                   residueType:str=None, name:str=None) -> NmrAtom:
  """get chainCode, sequenceCode, residueType and atomName from dot-separated  atomId or Pid
  or explicit parameters, and find or create an NmrAtom that matches
  Empty chainCode gets NmrChain:@- ; empty sequenceCode get a new NmrResidue"""

  # Get ID parts to use
  sequenceCode = str(sequenceCode) if sequenceCode else None
  params = [chainCode, sequenceCode, residueType, name]
  if atomId:
    if any(params):
      raise ValueError("produceNmrAtom: other parameters only allowed if atomId is None")
    else:
      # Remove colon prefix, if any
      atomId = atomId.split(Pid.PREFIXSEP,1)[-1]
      for ii,val in enumerate(Pid.splitId(atomId)):
        if val:
          params[ii] = val
      chainCode, sequenceCode, residueType, name = params

  if name is None:
    raise ValueError("NmrAtom name must be set")

  # Produce chain
  nmrChain = self.fetchNmrChain(shortName=chainCode or Constants.defaultNmrChainCode)
  nmrResidue = nmrChain.fetchNmrResidue(sequenceCode=sequenceCode, residueType=residueType)
  return nmrResidue.fetchNmrAtom(name)

    
# Connections to parents:

NmrResidue._childClasses.append(NmrAtom)

NmrResidue.newNmrAtom = newNmrAtom
NmrResidue.fetchNmrAtom = fetchNmrAtom

Project.produceNmrAtom = produceNmrAtom

# Notifiers:
className = ApiResonance._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':NmrAtom}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete'),
    ('_resetPid', {}, className, 'setName'),
    ('_resetPid', {}, className, 'setResonanceGroup'),
    ('_finaliseUnDelete', {}, className, 'undelete'),
  )
)
