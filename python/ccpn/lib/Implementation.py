"""For future implementation - not currentlyin use, but do NOT delete

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

from collections import OrderedDict, Mapping, MutableSequence
import itertools
import abc

NO_DEFAULT = object()

# NBNB TBD - not currently in use, but do NOT delete - Rasmus Fogh

class AbstractPropertyView:
  """View on a collection property of the parent object.
  Behaves as a tuple with additional property.fieldName access.
  NB the storage is by order. The field names may change dynamically.

  The MutablePropertyView class acts as a mix-in that adds  mutability

  The _fields and _dataObjects properties must be set in a subclass,
  as much the _dataTag class attribute.
  The value of self is calculated as if it were
  tuple(getattr(x, self._dataTag) for x in self._dataObjects)

  NB This class cannot be pickled,
  but then as a view on CCPN wrapper instances it should not be.
  """

  __slots__ = ['_container']

  #Name of attribute in _dataObjects to get and set. Must be set in subclass
  _dataTag = None

  def __init__(self, container):
    """parent object the view is attached to"""
    self._container = container

  @property
  @abc.abstractmethod
  def _fields(self):
    """Field names in order - should default to '_0', '_1', etc."""
    raise NotImplementedError("_fields property must be implemented in subclass")

  @property
  @abc.abstractmethod
  def _dataObjects(self):
    """Data-holding objects in order."""
    raise NotImplementedError("_dataObjects property must be implemented in subclass")

  def _asdict(self):
    return OrderedDict(zip(self._fields, self))

  def __eq__(self, other):
    return (isinstance(other, self.__class__) and self._container == other._container)

  def __ne__(self, other):
      return not self.__eq__(other)

  def __repr__(self):
    return "%s:%s(%s)" % (self.__class__.___name__, self._container.id,
                          ','.join(repr(x) for x in self))

  def __len__(self):
    return len(self._dataObjects)

  def __getitem__(self, idx):
    ll = self._dataObjects
    if isinstance(idx, slice):
      # this isn't super-efficient, but works
      return [getattr(ll[ii], self._dataTag) for ii in range(*idx.indices(len(ll)))]

    return getattr(ll[idx], self._dataTag)

  def __getattr__(self, tag):
    try:
      idx = self._fields.index(tag)
    except ValueError:
      raise AttributeError("Instance of %s has no attribute %s" % (self.__class__.__name__, tag))
    else:
      return getattr(self._dataObjects[idx], self._dataTag)

  def __iter__(self):
    ll = self._dataObjects
    return (getattr(ll[ii], self._dataTag) for ii in range(len(ll)))

  def count(self, value):
    return sum(1 for v in iter(self) if v == value)

  def index(self, value, start=NO_DEFAULT, stop=NO_DEFAULT):
    # not the most efficient way to implement this, but it will work
    ll = list(self)
    if start is NO_DEFAULT and stop is NO_DEFAULT:
      return ll.index(value)
    if stop is NO_DEFAULT:
      return ll.index(value, start)
    return ll.index(value, start, stop)


class MutablePropertyView:
  """MixIn class to add mutability to PropertyView"""

  __slots__ = []

  def __setattr__(self, tag, value):
    try:
      idx = self._fields.index(tag)
    except ValueError:
      raise AttributeError("Instance of %s has no attribute %s" % (self.__class__.__name__, tag))
    else:
      setattr(self._dataObjects[idx], self._dataTag, value)

  def __setitem__(self, idx, value):
    return setattr(self._dataObjects[idx], self._dataTag, value)

  def _update(self, _other=None, **kwds):
    if hasattr(_other, '_asdict'):
      _other = _other._asdict()

    if isinstance(_other, Mapping):
      tmp = []
      for field_name in self._fields:
        try:
          other_value = _other[field_name]
        except KeyError:
          pass
        else:
          tmp.append((field_name, other_value))
        _other = tmp
    elif _other is None:
       _other = []

    chained = itertools.chain(_other, (x for x in kwds.items()
                                       if x[0] in self._fields))
    for key, value in chained:
      setattr(self, key, value)

# class ListView(MutableSequence):
#   """This class provides a list that is a view of underlying API data"""
#   def __init__(self):
#     raise NotImplementedError("Not implemented yet)")
