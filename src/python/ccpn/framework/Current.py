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

import operator
import typing
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
from ccpn.core.Peak import Peak
from ccpn.core.Integral import Integral
from ccpn.core.NmrChain import NmrChain
from ccpn.core.NmrResidue import NmrResidue
from ccpn.core.NmrAtom import NmrAtom
from ccpn.ui._implementation.Strip import Strip
from ccpn.ui._implementation.SpectrumDisplay import SpectrumDisplay

# TODO: refactoring using _definitions needed
# Classes (in addition to Project) that have a corresponding 'current' field
_currentClasses = [Spectrum, SpectrumGroup, Peak, Integral, NmrChain, NmrResidue, NmrAtom,
                   SpectrumDisplay, Strip, ]

# 'current' fields that do not correspond to a wrapper class. Must be plural and end in 's'
_currentExtraFields = ['regions', 'positions']

# Fields in current (there is a current.xyz attribute with related functions
# for every 'xyz' in fields
_fields = [x._pluralLinkName for x in _currentClasses] + _currentExtraFields

def noCap(string):
  """return de-capitalised string"""
  if len(string) <= 0: return string
  return string[0].lower() + string[1:]


class Current:

  # Definitions of the attributes of the Current object
  _definitions = [
    # attribute name,                      storage name,        description
    (noCap(Integral.className),            '_integral',        'last selected integral'),
    (noCap(Integral._pluralLinkName),      '_integrals',       'all selected integrals'),

    (noCap(NmrAtom.className),             '_nmrAtom',         'last selected nmrAtom'),
    (noCap(NmrAtom._pluralLinkName),       '_nmrAtoms',        'all selected nmrAtoms'),

    (noCap(NmrChain.className),            '_nmrChain',        'last selected nmrChain'),
    (noCap(NmrChain._pluralLinkName),      '_nmrChains',       'all selected nmrChains'),

    (noCap(NmrResidue.className),          '_nmrResidue',      'last selected nmrResidue'),
    (noCap(NmrResidue._pluralLinkName),    '_nmrResidue',      'all selected nmrResidues'),

    ('regions',                            '_regions',         'last selected region'),

    (noCap(Peak.className),                '_peak',            'last selected peak'),
    (noCap(Peak._pluralLinkName),          '_peaks',           'all selected peaks'),

    ('positions',                          '_positions',       'last cursor position'),

    (noCap(Spectrum.className),            '_spectrum',        'current spectrum'), # broken
    (noCap(Spectrum._pluralLinkName),      '_spectra',         'list with all spectra present in a module'), # (broken)

    (noCap(SpectrumDisplay.className),     '_spectrumDisplay', 'current spectrumDisplay'), # (broken)

    (noCap(SpectrumGroup.className),       '_spectrumGroup',   'current spectrum'), # broken
    (noCap(SpectrumGroup._pluralLinkName), '_spectrumGroups',  'list with all spectra present in a module'), # (broken)

    (noCap(Strip.className),               '_strip',           'selected strip'),
    (noCap(Strip._pluralLinkName),         '_strips',          'lists with all strips'),
  ]

  # create the doc-string dynamically from definitions above;
  # cannot do newlines as Python console falls over when querying using the current? syntax (too many newlines?)
  __doc__ = \
  """The current object gives access to the collection of active or selected objects and values.\n\nCurrently implemented:\n""" \
  + '; '.join(('%s (%s)' % (f,v) for f,t,v in _definitions)) \
  + '\n\nUse print(current) to get a list of attribute, value pairs'

  def __init__(self, project):
    # initialise non-=auto fields
    self._project = project

    for field in _fields:
      setattr(self, '_' + field, [])

    # initialise notifies
    notifies = self._notifies = {}
    for field in _fields:
      notifies[field] = []

  def registerNotify(self, notify, field):
    # Notifiers are attached to the Current OBJECT, not to the class
    # They are therefore removed when a new project is created/loaded
    # Otherwise it is the responsibility of the adder to remove them when no longer relevant
    # for which the notifier function object must be kept around.
    # The function is attached to the field and is executed after the field value changes
    # In practice this goes through the setter for (the equivalent of) Current.spectra
    # The notifier function is passed the Current object as its only parameter,
    # which allows you to access the project, the value just changed or anything else.
    # If you need a graphics object (e.g. a module) you must make and register a bound method
    # on the module.

    self._notifies[field].append(notify)

  def unRegisterNotify(self, notify, field):
    """Remove 'current' notifier"""
    self._notifies[field].remove(notify)

  @property
  def project(self):
    """Project attached to current"""
    return self._project

  def __str__(self):
    """
    Return string representation of self listing all attribute, value pairs
    """
    maxlen = max((len(f) for f,t,v in self._definitions))
    fmt = 'current.%-' + str(maxlen) + 's : %s'
    #return "current\n" + '\n'.join((fmt % (f,getattr(self,f)) for f,t,v in _definitions))
    return '\n'.join((fmt % (f,getattr(self,f)) for f,t,v in self._definitions))

  @classmethod
  def  _addClassField(cls, param:typing.Union[str, AbstractWrapperObject]):
    """Add new 'current' field with necessary function for input
    param (wrapper class or field name)"""

    if isinstance(param, str):
      plural = param
      singular = param[:-1]  # It is assumed that param ends in plural 's'
    else:
      # param is a wrapper class
      plural = param._pluralLinkName
      singular = param.className
      singular = singular[0].lower() + singular[1:]

    # getter function for _field; getField(obj) returns obj._field:
    getField = operator.attrgetter('_' + plural)

    # getFieldItem(obj) returns obj[field]
    getFieldItem = operator.itemgetter(plural)

    # setField(obj, value) sets obj._field = value and calls notifiers
    def setField(self, value, plural=plural):
      if len(set(value)) != len(value):
        raise ValueError( "Current %s contains duplicates: %s" % (plural, value))
      setattr(self, '_'+plural, value)
      funcs = getFieldItem(self._notifies) or ()
      for func in funcs:
        func(value)

    def getter(self):
      return tuple(getField(self))
    def setter(self, value):
      setField(self, list(value))
    #
    setattr(cls, plural, property(getter, setter, None, "Current %s" % plural))

    def getter(self):
      ll = getField(self)
      return ll[-1] if ll else None
    def setter(self, value):
      setField(self, [value])
    #
    setattr(cls, singular, property(getter, setter, None, "Current %s" % singular))

    def adder(self, value):
      """Add %s to current.%s""" % (singular, plural)
      values = getField(self)
      if value not in values:
        setField(self, values + [value])
    #
    setattr(cls, 'add' + singular.capitalize(), adder)

    def remover(self, value):
      """Remove %s from current.%s""" % (singular, plural)
      values = getField(self)
      if value in values:
        values.remove(value)
      setField(self, values)
    #
    setattr(cls, 'remove' + singular.capitalize(), remover)

    def clearer(self):
      """Clear current.%s""" % plural
      setField(self, [])
    #
    setattr(cls, 'clear' + plural.capitalize(), clearer)

    if not isinstance(param, str):
      # param is a class - Add notifiers for deleted objects
      def cleanup(self:AbstractWrapperObject):
        current = self._project._appBase.current
        if current:
          fieldData = getField(current)
          if self in fieldData:
            fieldData.remove(self)
      cleanup.__name__ = 'current_%s_deletion_cleanup' % singular
      #
      param._setupCoreNotifier('delete', cleanup)

# Add fields to current
for cls in _currentClasses:
  Current._addClassField(cls)
for field in _currentExtraFields:
  Current._addClassField(field)
