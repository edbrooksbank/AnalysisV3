"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
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

from collections.abc import Sequence
from ccpn._wrapper._AbstractRestraintContribution import AbstractRestraintContribution
from ccpn._wrapper._Project import Project
from ccpn._wrapper._RdcRestraint import RdcRestraint
from ccpncore.api.ccp.nmr.NmrConstraint import RdcContribution as Ccpn_RdcContribution


class RdcContribution(AbstractRestraintContribution):
  """Rdc Contribution."""
  
  #: Short class name, for PID.
  shortClassName = 'RC'

  # Number of atoms in a Restraint item - set in subclasses
  restraintItemLength = RdcRestraint.restraintItemLength

  #: Name of plural link to instances of class
  _pluralLinkName = 'rdcContributions'
  
  #: List of child classes.
  _childClasses = []


  # CCPN properties  
  @property
  def ccpnContribution(self) -> RdcContribution:
    """ CCPN RdcContribution matching RdcContribution"""
    return self._wrappedData

  @property
  def _parent(self) -> RdcRestraint:
    """Parent (containing) object."""
    return  self._project._data2Obj[self._wrappedData.rdcConstraint]
    
  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:RdcRestraint)-> list:
    """get wrappedData - all RdcConstraint children of parent RdcConstraintList"""
    return parent._wrappedData.sortedContributions()

# Connections to parents:
RdcRestraint._childClasses.append(RdcContribution)

def newContribution(parent:RdcRestraint, targetValue:float=None, error:float=None,
                    weight:float=None, upperLimit:float=None,  lowerLimit:float=None,
                    additionalUpperLimit:float=None, additionalLowerLimit:float=None,
                    restraintItems:Sequence=()) -> RdcContribution:
  """Create new child RdcContribution"""
  constraint = parent._wrappedData
  obj = constraint.newRdcContribution(targetValue=targetValue, error=error,
                                           weight=weight, upperLimit=upperLimit,
                                           lowerLimit=lowerLimit,
                                           additionalUpperLimit=additionalUpperLimit,
                                           additionalLowerLimit=additionalLowerLimit)
  result = parent._project._data2Obj.get(obj)
  result.restraintItems = restraintItems
  return result

RdcRestraint.newRestraint = newContribution

# Notifiers:
className = Ccpn_RdcContribution._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':RdcContribution}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete')
  )
)
