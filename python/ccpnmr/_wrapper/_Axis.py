"""GUI Display Strip class

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
from ccpncore.util import pid as Pid

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
from ccpn._wrapper._AbstractWrapperObject import AbstractWrapperObject
from ccpn._wrapper._Project import Project
from ccpnmr._wrapper._SpectrumDisplay import SpectrumDisplay
from ccpncore.api.ccpnmr.gui.Task import Axis as ApiAxis


class Axis(AbstractWrapperObject):
  """Display Axis for 1D or nD spectrum"""
  
  #: Short class name, for PID.
  shortClassName = 'GA'

  #: Name of plural link to instances of class
  _pluralLinkName = 'axes'
  
  #: List of child classes.
  _childClasses = []
  

  # CCPN properties  
  @property
  def apiAxis(self) -> ApiAxis:
    """ CCPN Axis matching Axis"""
    return self._wrappedData
    
  @property
  def _key(self) -> str:
    """local id, of form code.stripSerial"""
    return Pid.IDSEP.join((self._wrappedData.code, str(self._wrappedData.sripSerial)))

    
  @property
  def _parent(self) -> SpectrumDisplay:
    """Parent (containing) object."""
    return self._project._data2Obj.get(self._wrappedData.spectrumDisplay)

  @property
  def code(self) -> str:
    """Fixed string Axis code"""
    return self._wrappedData.code

  @property
  def position(self) -> float:
    """Centre point position for displayed region, in current unit."""
    return self._wrappedData.position

  @position.setter
  def position(self, value):
    self._wrappedData.position = value

  @property
  def width(self) -> float:
    """Width for displayed region, in current unit."""
    return self._wrappedData.width

  @width.setter
  def width(self, value):
    self._wrappedData.width = value

  @property
  def unit(self) -> str:
    """Display unit for axis"""
    return self._wrappedData.unit

  # NBNB TBD This should be settable, but changing it requires changing the position
  # values. For now we leave it unsettable.

  # NBNB TBD the 'regions' attribute may not be needed. leave it out

  @property
  def nmrAtoms(self) -> tuple:
    """nmrAtoms connected to axis"""
    ff = self._project._data2Obj.get
    return tuple(ff(x) for x in self._wrappedData.resonances)

  @nmrAtoms.setter
  def nmrAtoms(self, value):
    self._wrappedData.resonances = tuple(x._wrappedData for x in value)

  # Implementation functions
  @classmethod
  def _getAllWrappedData(cls, parent:SpectrumDisplay)-> list:
    """get wrappedData (ccp.gui.Strip) in serial number order"""
    return parent._wrappedData.sortedAxes()

  def delete(self):
    """Overrides normal delete"""
    raise  ValueError("Axes cannot be deleted independently")

# Connections to parents:
SpectrumDisplay._childClasses.append(Axis)

# We should NOT have any newAxis functions


# Notifiers:
className = ApiAxis._metaclass.qualifiedName()
Project._apiNotifiers.extend(
  ( ('_newObject', {'cls':Axis}, className, '__init__'),
    ('_finaliseDelete', {}, className, 'delete')
  )
)
