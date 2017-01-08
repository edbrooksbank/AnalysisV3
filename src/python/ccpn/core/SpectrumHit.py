"""
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

import typing
import collections
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Spectrum import Spectrum
from ccpn.core.PseudoDimension import PseudoDimension
from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import SpectrumHit as ApiSpectrumHit
from ccpn.core.lib import Pid
from ccpn.util import Constants


class SpectrumHit(AbstractWrapperObject):
  """Used in screening and metabolomics implementations to describe
a 'hit', i.e. that a Substance has been found to be present (metabolomics) or active (screening) in a given
spectrum.

The Substance referred to is defined by the SubsanceName attribute, which is part of the ID.
For this reason SpectrumHits cannot be renamed."""

  #: Short class name, for PID.
  shortClassName = 'SH'
  # Attribute it necessary as subclasses must use superclass className
  className = 'SpectrumHit'

  _parentClass = Spectrum

  #: Name of plural link to instances of class
  _pluralLinkName = 'spectrumHits'

  #: List of child classes.
  _childClasses = []

  # Qualified name of matching API class
  _apiClassQualifiedName = ApiSpectrumHit._metaclass.qualifiedName()

  # CCPN properties
  @property
  def _apiSpectrumHit(self) -> ApiSpectrumHit:
    """ CCPN SpectrumHit matching SpectrumHit"""
    return self._wrappedData

  @property
  def _key(self) -> str:
    """object identifier, used for id"""

    obj =  self._wrappedData
    return Pid.createId(obj.substanceName, obj.sampledDimension, obj.sampledPoint)

  @property
  def _localCcpnSortKey(self) -> typing.Tuple:
    """Local sorting key, in context of parent."""
    obj =  self._wrappedData
    return(obj.substanceName, obj.sampledDimension, obj.sampledPoint)

  @property
  def _parent(self) -> Spectrum:
    """Spectrum containing spectrumHit."""
    return self._project._data2Obj[self._wrappedData.dataSource]

  spectrum = _parent

  @property
  def substanceName(self) -> int:
    """Name of hit substance"""
    return self._wrappedData.substanceName

  @property
  def pseudoDimensionNumber(self) -> int:
    """Dimension number for pseudoDimension (0 if none),
    if the Hit only refers to one point in a pseudoDimension"""
    return self._wrappedData.sampledDimension

  @property
  def pseudoDimension(self) -> PseudoDimension:
    """PseudoDimension,
    if the Hit only refers to one point in a pseudoDimension"""
    dimensionNumber = self._wrappedData.sampledDimension
    if dimensionNumber == 0:
      return None
    else:
      return self.spectrum.getPseudoDimension(dimensionNumber)

  @property
  def pointNumber(self) -> int:
    """Point number for pseudoDimension (0 if none),
    if the Hit only refers to one point in a pseudoDimension"""
    return self._wrappedData.sampledPoint

  @property
  def figureOfMerit(self) -> float:
    """Figure of merit describing quality of hit, between 0.0 and 1.0 inclusive."""
    return self._wrappedData.figureOfMerit

  @figureOfMerit.setter
  def figureOfMerit(self, value:float):
    self._wrappedData.figureOfMerit = value

  @property
  def meritCode(self) -> str:
    """User-defined merit code string describing quality of hit."""
    return self._wrappedData.meritCode

  @meritCode.setter
  def meritCode(self, value:str):
    self._wrappedData.meritCode = value

  @property
  def normalisedChange(self) -> float:
    """Normalized size of effect (normally intensity change). in range -1 <= x <= 1.
    Positive values denote expected changes,
    while negative values denote changes in the 'wrong' direction,
    e.g. intensity increase where a decrease was expected."""
    return self._wrappedData.normalisedChange

  @normalisedChange.setter
  def normalisedChange(self, value:float):
    self._wrappedData.normalisedChange = value

  @property
  def isConfirmed(self) -> typing.Optional[bool]:
    """True if this Hit is confirmed? True: yes; False; no; None: not determined"""
    return  self._wrappedData.isConfirmed

  @isConfirmed.setter
  def isConfirmed(self, value:bool):
    self._wrappedData.isConfirmed = value

  @property
  def concentration(self) -> float:
    """Concentration determined for the spectrumHit -
    used for e.g. Metabolomics where concentrations are not known a priori."""
    return self._wrappedData.concentration

  @concentration.setter
  def concentration(self, value:float):
    self._wrappedData.concentration = value

  @property
  def concentrationError(self) -> float:
    """Estimated Standard error of SpectrumHit.concentration"""
    return self._wrappedData.concentrationError

  @concentrationError.setter
  def concentrationError(self, value:float):
    self._wrappedData.concentrationError = value

  @property
  def concentrationUnit(self) -> str:
    """Unit of SpectrumHit.concentration, one of: %s """ % Constants.concentrationUnits

    result = self._wrappedData.concentrationUnit
    if result not in Constants.concentrationUnits:
      self._project._logger.warning(
        "Unsupported stored value %s for SpectrumHit.concentrationUnit."
        % result)
    return result

  @concentrationUnit.setter
  def concentrationUnit(self, value:str):
    if value not in Constants.concentrationUnits:
      self._project._logger.warning(
        "Setting unsupported value %s for SpectrumHit.concentrationUnit."
        % value)
    self._wrappedData.concentrationUnit = value

  @property
  def comment(self) -> str:
    """Free-form text comment"""
    return self._wrappedData.details

  @comment.setter
  def comment(self, value:str):
    self._wrappedData.details = value

  @classmethod
  def _getAllWrappedData(cls, parent: Spectrum)-> list:
    """get wrappedData (Nmr.SpectrumHit) for all SpectrumHit children of parent Spectrum"""
    return parent._wrappedData.spectrumHits

# Connections to parents:
def _newSpectrumHit(self:Spectrum, substanceName:str, pointNumber:int=0,
                     pseudoDimensionNumber:int=0, pseudoDimension:PseudoDimension=None,
                    figureOfMerit:float=None,  meritCode:str=None, normalisedChange:float=None,
                    isConfirmed:bool=None, concentration:float=None, concentrationError:float=None,
                    concentrationUnit:str=None, comment:str=None):
  """Create new SpectrumHit within Spectrum"""

  # Default values for 'new' function, as used for echoing to console
  defaults = collections.OrderedDict(
    (('pointNumber', 0), ('pseudoDimensionNumber', 0),
     ('figureOfMerit',None), ('meritCode',None), ('normalisedChange', None),
     ('isConfirmed',None), ('concentration',None), ('concentrationError', None),
     ('concentrationUnit',None), ('comment',None)
     )
  )

  if concentrationUnit not in Constants.concentrationUnits:
    self._project._logger.warning(
      "Unsupported value %s for SpectrumHit.concentrationUnit."
      % concentrationUnit)

  self._startFunctionCommandBlock('newSpectrumHit', substanceName, values=locals(), defaults=defaults,
                                  parName='newSpectrumHit')
  try:
    if pseudoDimension is not None:
      if not pseudoDimensionNumber:
        pseudoDimensionNumber = pseudoDimension.dimension
      elif pseudoDimensionNumber != pseudoDimension.dimension:
        raise ValueError("pseudoDimension %s incompatible with pseudoDimensionNumber %s"
                         % (pseudoDimensionNumber, pseudoDimension))

    obj = self._apiDataSource.newSpectrumHit(substanceName=substanceName,
                                             sampledDimension=pseudoDimensionNumber,
                                             sampledPoint=pointNumber, figureOfMerit=figureOfMerit,
                                             meritCode=meritCode, normalisedChange=normalisedChange,
                                             isConfirmed=isConfirmed, concentration=concentration,
                                             concentrationError=concentrationError,
                                             concentrationUnit=concentrationUnit, details=comment)
  finally:
    self._project._appBase._endCommandBlock()

  return self._project._data2Obj.get(obj)

Spectrum.newSpectrumHit = _newSpectrumHit
del _newSpectrumHit


def getter(self:PseudoDimension) -> typing.List[SpectrumHit]:
  dimensionNumber = self.dimension
  return list(x for x in self.spectrum.spectrumHits if x.dimensionNumber == dimensionNumber)
PseudoDimension.spectrumHits = property(getter, None, None,
  "SpectrumHits (for screening/metabolomics) that refer to individual points in the PseudoDimension"
)
del getter

# Additional Notifiers: