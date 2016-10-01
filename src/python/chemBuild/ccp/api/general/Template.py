"""
#######################################################################

CCPN Data Model version 2.1.2

Autogenerated by PyFileApiGen revision 1.57.2.1 on Mon Mar  2 17:25:26 2015
  from data model element ccp.general.Template revision ?

#######################################################################
======================COPYRIGHT/LICENSE START==========================

Template.py: python API for CCPN data model, MetaPackage ccp.general.Template

Copyright (C) 2007  (CCPN Project)

=======================================================================

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
 
A copy of this license can be found in ../../../../license/LGPL.license
 
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
 
You should have received a copy of the GNU Lesser General Public
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
Rasmus H. Fogh, Wayne Boucher, Wim F. Vranken, Anne
Pajon, Tim J. Stevens, T.N. Bhat, John Westbrook, John M.C. Ionides and
Ernest D. Laue (2005). A framework for scientific data modeling and automated
software development. Bioinformatics 21, 1678-1684.


This file was generated with the Memops software generation framework,
and contains original contributions embedded in the framework

===========================REFERENCE END===============================
"""

import io
#import sets
import traceback
import types
import operator

# special function for fast whitespace checking.
# used in DataType Word and Token handcode
import re
containsWhitespace = re.compile('\s').search
containsNonAlphanumeric = re.compile('[^a-zA-Z0-9_]').search
 
from memops.general import Implementation as implementation
ApiError = implementation.ApiError

# imported packages:
import memops.api.AccessControl
import memops.api.Implementation

metaPackage = memops.api.Implementation.topPackage.metaObjFromQualName('ccp.general.Template')

###############################################################################
class AbstractProbability(memops.api.Implementation.DataObject):
  r"""Abstract class defining classes used for probability lists. 
AbstractProbability objects have a parent that is the object that has 
the probability (e.g. a ResonanceGroup), a link 'possibility' to various 
possibilities (e.g. a ChemComp), and a weight to determine their 
relative probability. Probabilities are calculated by taking the weight 
of each AbstractProbability object and dividing by the sum of the 
weights in the (appropriate subset of) AbstractProbability objects 
linked to a given parent. 

Implementation note: The presence of the 
'possibility' link must be enforced by the data modeller, as it is not 
checked by the software. 
  """
  #   from data model element ccp.general.Template.AbstractProbability revision ?
  _metaclass = metaPackage.getElement('AbstractProbability')
  _packageName = 'ccp.general.Template'
  _packageShortName = 'TEMP'
  _fieldNames = ('applicationData', 'className', 'fieldNames', 'inConstructor', 'isDeleted', 'metaclass', 'packageName', 'packageShortName', 'qualifiedName', 'weight', 'access', 'activeAccess', 'root', 'topObject',)

  __init__ = memops.api.Implementation.ComplexDataType.__init__

  addApplicationData = memops.api.Implementation.DataObject.addApplicationData

  checkAllValid = memops.api.Implementation.ComplexDataType.checkAllValid

  checkValid = memops.api.Implementation.ComplexDataType.checkValid

  delete = memops.api.Implementation.DataObject.delete

  findAllApplicationData = memops.api.Implementation.DataObject.findAllApplicationData

  findFirstApplicationData = memops.api.Implementation.DataObject.findFirstApplicationData

  getAccess = memops.api.Implementation.DataObject.getAccess

  getActiveAccess = memops.api.Implementation.DataObject.getActiveAccess

  getApplicationData = memops.api.Implementation.DataObject.getApplicationData

  getByNavigation = memops.api.Implementation.MemopsObject.getByNavigation

  getClassName = memops.api.Implementation.ComplexDataType.getClassName

  getExpandedKey = memops.api.Implementation.MemopsObject.getExpandedKey

  getFieldNames = memops.api.Implementation.ComplexDataType.getFieldNames

  getInConstructor = memops.api.Implementation.ComplexDataType.getInConstructor

  getIsDeleted = memops.api.Implementation.MemopsObject.getIsDeleted

  getMetaclass = memops.api.Implementation.ComplexDataType.getMetaclass

  getPackageName = memops.api.Implementation.ComplexDataType.getPackageName

  getPackageShortName = memops.api.Implementation.ComplexDataType.getPackageShortName

  getQualifiedName = memops.api.Implementation.ComplexDataType.getQualifiedName

  getRoot = memops.api.Implementation.MemopsObject.getRoot

  getTopObject = memops.api.Implementation.DataObject.getTopObject
  
  def getWeight(self):
    """
    Get for ccp.general.Template.AbstractProbability.weight
    """
    dataDict = self.__dict__
    result = dataDict.get('weight')
    return result

  removeApplicationData = memops.api.Implementation.DataObject.removeApplicationData

  setAccess = memops.api.Implementation.DataObject.setAccess

  setApplicationData = memops.api.Implementation.DataObject.setApplicationData
  
  def setWeight(self, value):
    """
    Set for ccp.general.Template.AbstractProbability.weight
    """
    dataDict = self.__dict__
    if (isinstance(value, memops.api.Implementation.Float.PythonType)):
      pass
    elif ([x for x in memops.api.Implementation.Float.compatibleTypes if isinstance(value, x)]):
      value = memops.api.Implementation.Float.create(value)
    else:
      raise ApiError("""%s.setWeight:
       memops.Implementation.Float input is not of a valid type""" % self.qualifiedName
       + ": %s" % (value,)
      )

    if (not (value - value == 0.0)):
      raise ApiError("""%s.setWeight:
       Float constraint value_is_not_NaN_or_Infinity violated by value""" % self.qualifiedName
       + ": %s" % (value,)
      )

    topObject = dataDict.get('topObject')
    currentValue = dataDict.get('weight')
    notInConstructor = not (dataDict.get('inConstructor'))

    root = dataDict.get('topObject').__dict__.get('memopsRoot')
    notOverride = not (root.__dict__.get('override'))
    notIsReading = not (topObject.__dict__.get('isReading'))
    notOverride = (notOverride and notIsReading)
    if (notIsReading):
      if (notInConstructor):
        if (not (topObject.__dict__.get('isModifiable'))):
          raise ApiError("""%s.setWeight:
           Storage not modifiable""" % self.qualifiedName
           + ": %s" % (topObject,)
          )

    if (dataDict.get('isDeleted')):
      raise ApiError("""%s.setWeight:
       called on deleted object""" % self.qualifiedName
      )

    if (value == currentValue):
      return

    if (notOverride):
      if (value is None):
        raise ApiError("""%s.setWeight:
         value cannot be None""" % self.qualifiedName
         + ": %s" % (self,)
        )

      pass

    dataDict['weight'] = value
    if (notIsReading):
      if (notInConstructor):
        topObject.__dict__['isModified'] = True

    # doNotifies

    if ((notInConstructor and notOverride)):
      
      _notifies = self.__class__._notifies
      
      ll1 = _notifies['']
      for notify in ll1:
        notify(self)
      
      ll = _notifies.get('setWeight')
      if ll:
        for notify in ll:
          if notify not in ll1:
            notify(self)

  toDetailedString = memops.api.Implementation.ComplexDataType.toDetailedString

  applicationData = memops.api.Implementation.DataObject.applicationData

  className = memops.api.Implementation.ComplexDataType.className

  fieldNames = memops.api.Implementation.ComplexDataType.fieldNames

  inConstructor = memops.api.Implementation.ComplexDataType.inConstructor

  isDeleted = memops.api.Implementation.MemopsObject.isDeleted

  metaclass = memops.api.Implementation.ComplexDataType.metaclass

  packageName = memops.api.Implementation.ComplexDataType.packageName

  packageShortName = memops.api.Implementation.ComplexDataType.packageShortName

  qualifiedName = memops.api.Implementation.ComplexDataType.qualifiedName
  
  weight = property(getWeight, setWeight, None,
  r"""weight (= non-normalised probability) that the parent is associated with 
  this particular possibility. 
  """)

  access = memops.api.Implementation.DataObject.access

  activeAccess = memops.api.Implementation.DataObject.activeAccess

  root = memops.api.Implementation.MemopsObject.root

  topObject = memops.api.Implementation.DataObject.topObject

###############################################################################
class MultiTypeValue(memops.api.Implementation.DataObject):
  r"""Typed value data
  """
  #   from data model element ccp.general.Template.MultiTypeValue revision ?
  _metaclass = metaPackage.getElement('MultiTypeValue')
  _packageName = 'ccp.general.Template'
  _packageShortName = 'TEMP'
  _fieldNames = ('applicationData', 'booleanValue', 'className', 'fieldNames', 'floatValue', 'inConstructor', 'intValue', 'isDeleted', 'metaclass', 'packageName', 'packageShortName', 'qualifiedName', 'textValue', 'access', 'activeAccess', 'root', 'topObject',)

  __init__ = memops.api.Implementation.ComplexDataType.__init__

  addApplicationData = memops.api.Implementation.DataObject.addApplicationData

  checkAllValid = memops.api.Implementation.ComplexDataType.checkAllValid

  checkValid = memops.api.Implementation.ComplexDataType.checkValid

  delete = memops.api.Implementation.DataObject.delete

  findAllApplicationData = memops.api.Implementation.DataObject.findAllApplicationData

  findFirstApplicationData = memops.api.Implementation.DataObject.findFirstApplicationData

  getAccess = memops.api.Implementation.DataObject.getAccess

  getActiveAccess = memops.api.Implementation.DataObject.getActiveAccess

  getApplicationData = memops.api.Implementation.DataObject.getApplicationData
  
  def getBooleanValue(self):
    """
    Get for ccp.general.Template.MultiTypeValue.booleanValue
    """
    dataDict = self.__dict__
    result = dataDict.get('booleanValue')
    return result

  getByNavigation = memops.api.Implementation.MemopsObject.getByNavigation

  getClassName = memops.api.Implementation.ComplexDataType.getClassName

  getExpandedKey = memops.api.Implementation.MemopsObject.getExpandedKey

  getFieldNames = memops.api.Implementation.ComplexDataType.getFieldNames
  
  def getFloatValue(self):
    """
    Get for ccp.general.Template.MultiTypeValue.floatValue
    """
    dataDict = self.__dict__
    result = dataDict.get('floatValue')
    return result

  getInConstructor = memops.api.Implementation.ComplexDataType.getInConstructor
  
  def getIntValue(self):
    """
    Get for ccp.general.Template.MultiTypeValue.intValue
    """
    dataDict = self.__dict__
    result = dataDict.get('intValue')
    return result

  getIsDeleted = memops.api.Implementation.MemopsObject.getIsDeleted

  getMetaclass = memops.api.Implementation.ComplexDataType.getMetaclass

  getPackageName = memops.api.Implementation.ComplexDataType.getPackageName

  getPackageShortName = memops.api.Implementation.ComplexDataType.getPackageShortName

  getQualifiedName = memops.api.Implementation.ComplexDataType.getQualifiedName

  getRoot = memops.api.Implementation.MemopsObject.getRoot
  
  def getTextValue(self):
    """
    Get for ccp.general.Template.MultiTypeValue.textValue
    """
    dataDict = self.__dict__
    result = dataDict.get('textValue')
    return result

  getTopObject = memops.api.Implementation.DataObject.getTopObject

  removeApplicationData = memops.api.Implementation.DataObject.removeApplicationData

  setAccess = memops.api.Implementation.DataObject.setAccess

  setApplicationData = memops.api.Implementation.DataObject.setApplicationData
  
  def setBooleanValue(self, value):
    """
    Set for ccp.general.Template.MultiTypeValue.booleanValue
    """
    dataDict = self.__dict__
    if (value is not None):
      if (not (value in [True, False])):
        raise ApiError("""%s.setBooleanValue:
         memops.Implementation.Boolean input is not in enumeration [True, False]""" % self.qualifiedName
         + ": %s" % (value,)
        )

    topObject = dataDict.get('topObject')
    currentValue = dataDict.get('booleanValue')
    notInConstructor = not (dataDict.get('inConstructor'))

    root = dataDict.get('topObject').__dict__.get('memopsRoot')
    notOverride = not (root.__dict__.get('override'))
    notIsReading = not (topObject.__dict__.get('isReading'))
    notOverride = (notOverride and notIsReading)
    if (notIsReading):
      if (notInConstructor):
        if (not (topObject.__dict__.get('isModifiable'))):
          raise ApiError("""%s.setBooleanValue:
           Storage not modifiable""" % self.qualifiedName
           + ": %s" % (topObject,)
          )

    if (dataDict.get('isDeleted')):
      raise ApiError("""%s.setBooleanValue:
       called on deleted object""" % self.qualifiedName
      )

    if (value == currentValue):
      return

    if (notOverride):
      pass

    dataDict['booleanValue'] = value
    if (notIsReading):
      if (notInConstructor):
        topObject.__dict__['isModified'] = True

    # doNotifies

    if ((notInConstructor and notOverride)):
      
      _notifies = self.__class__._notifies
      
      ll1 = _notifies['']
      for notify in ll1:
        notify(self)
      
      ll = _notifies.get('setBooleanValue')
      if ll:
        for notify in ll:
          if notify not in ll1:
            notify(self)

  def setFloatValue(self, value):
    """
    Set for ccp.general.Template.MultiTypeValue.floatValue
    """
    dataDict = self.__dict__
    if (value is not None):
      if (isinstance(value, memops.api.Implementation.Float.PythonType)):
        pass
      elif ([x for x in memops.api.Implementation.Float.compatibleTypes if isinstance(value, x)]):
        value = memops.api.Implementation.Float.create(value)
      else:
        raise ApiError("""%s.setFloatValue:
         memops.Implementation.Float input is not of a valid type""" % self.qualifiedName
         + ": %s" % (value,)
        )

      if (not (value - value == 0.0)):
        raise ApiError("""%s.setFloatValue:
         Float constraint value_is_not_NaN_or_Infinity violated by value""" % self.qualifiedName
         + ": %s" % (value,)
        )

    topObject = dataDict.get('topObject')
    currentValue = dataDict.get('floatValue')
    notInConstructor = not (dataDict.get('inConstructor'))

    root = dataDict.get('topObject').__dict__.get('memopsRoot')
    notOverride = not (root.__dict__.get('override'))
    notIsReading = not (topObject.__dict__.get('isReading'))
    notOverride = (notOverride and notIsReading)
    if (notIsReading):
      if (notInConstructor):
        if (not (topObject.__dict__.get('isModifiable'))):
          raise ApiError("""%s.setFloatValue:
           Storage not modifiable""" % self.qualifiedName
           + ": %s" % (topObject,)
          )

    if (dataDict.get('isDeleted')):
      raise ApiError("""%s.setFloatValue:
       called on deleted object""" % self.qualifiedName
      )

    if (value == currentValue):
      return

    if (notOverride):
      pass

    dataDict['floatValue'] = value
    if (notIsReading):
      if (notInConstructor):
        topObject.__dict__['isModified'] = True

    # doNotifies

    if ((notInConstructor and notOverride)):
      
      _notifies = self.__class__._notifies
      
      ll1 = _notifies['']
      for notify in ll1:
        notify(self)
      
      ll = _notifies.get('setFloatValue')
      if ll:
        for notify in ll:
          if notify not in ll1:
            notify(self)

  def setIntValue(self, value):
    """
    Set for ccp.general.Template.MultiTypeValue.intValue
    """
    dataDict = self.__dict__
    if (value is not None):
      if (isinstance(value, memops.api.Implementation.Int.PythonType)):
        pass
      elif ([x for x in memops.api.Implementation.Int.compatibleTypes if isinstance(value, x)]):
        value = memops.api.Implementation.Int.create(value)
      else:
        raise ApiError("""%s.setIntValue:
         memops.Implementation.Int input is not of a valid type""" % self.qualifiedName
         + ": %s" % (value,)
        )

    topObject = dataDict.get('topObject')
    currentValue = dataDict.get('intValue')
    notInConstructor = not (dataDict.get('inConstructor'))

    root = dataDict.get('topObject').__dict__.get('memopsRoot')
    notOverride = not (root.__dict__.get('override'))
    notIsReading = not (topObject.__dict__.get('isReading'))
    notOverride = (notOverride and notIsReading)
    if (notIsReading):
      if (notInConstructor):
        if (not (topObject.__dict__.get('isModifiable'))):
          raise ApiError("""%s.setIntValue:
           Storage not modifiable""" % self.qualifiedName
           + ": %s" % (topObject,)
          )

    if (dataDict.get('isDeleted')):
      raise ApiError("""%s.setIntValue:
       called on deleted object""" % self.qualifiedName
      )

    if (value == currentValue):
      return

    if (notOverride):
      pass

    dataDict['intValue'] = value
    if (notIsReading):
      if (notInConstructor):
        topObject.__dict__['isModified'] = True

    # doNotifies

    if ((notInConstructor and notOverride)):
      
      _notifies = self.__class__._notifies
      
      ll1 = _notifies['']
      for notify in ll1:
        notify(self)
      
      ll = _notifies.get('setIntValue')
      if ll:
        for notify in ll:
          if notify not in ll1:
            notify(self)

  def setTextValue(self, value):
    """
    Set for ccp.general.Template.MultiTypeValue.textValue
    """
    dataDict = self.__dict__
    if (value is not None):
      if (isinstance(value, memops.api.Implementation.String.PythonType)):
        pass
      else:
        raise ApiError("""%s.setTextValue:
         memops.Implementation.String input is not of a valid type""" % self.qualifiedName
         + ": %s" % (value,)
        )

    topObject = dataDict.get('topObject')
    currentValue = dataDict.get('textValue')
    notInConstructor = not (dataDict.get('inConstructor'))

    root = dataDict.get('topObject').__dict__.get('memopsRoot')
    notOverride = not (root.__dict__.get('override'))
    notIsReading = not (topObject.__dict__.get('isReading'))
    notOverride = (notOverride and notIsReading)
    if (notIsReading):
      if (notInConstructor):
        if (not (topObject.__dict__.get('isModifiable'))):
          raise ApiError("""%s.setTextValue:
           Storage not modifiable""" % self.qualifiedName
           + ": %s" % (topObject,)
          )

    if (dataDict.get('isDeleted')):
      raise ApiError("""%s.setTextValue:
       called on deleted object""" % self.qualifiedName
      )

    if (value == currentValue):
      return

    if (notOverride):
      pass

    dataDict['textValue'] = value
    if (notIsReading):
      if (notInConstructor):
        topObject.__dict__['isModified'] = True

    # doNotifies

    if ((notInConstructor and notOverride)):
      
      _notifies = self.__class__._notifies
      
      ll1 = _notifies['']
      for notify in ll1:
        notify(self)
      
      ll = _notifies.get('setTextValue')
      if ll:
        for notify in ll:
          if notify not in ll1:
            notify(self)

  toDetailedString = memops.api.Implementation.ComplexDataType.toDetailedString

  applicationData = memops.api.Implementation.DataObject.applicationData
  
  booleanValue = property(getBooleanValue, setBooleanValue, None,
  r"""Boolean type value
  """)

  className = memops.api.Implementation.ComplexDataType.className

  fieldNames = memops.api.Implementation.ComplexDataType.fieldNames
  
  floatValue = property(getFloatValue, setFloatValue, None,
  r"""Float type value
  """)

  inConstructor = memops.api.Implementation.ComplexDataType.inConstructor
  
  intValue = property(getIntValue, setIntValue, None,
  r"""Integer type value
  """)

  isDeleted = memops.api.Implementation.MemopsObject.isDeleted

  metaclass = memops.api.Implementation.ComplexDataType.metaclass

  packageName = memops.api.Implementation.ComplexDataType.packageName

  packageShortName = memops.api.Implementation.ComplexDataType.packageShortName

  qualifiedName = memops.api.Implementation.ComplexDataType.qualifiedName
  
  textValue = property(getTextValue, setTextValue, None,
  r"""Text type value
  """)

  access = memops.api.Implementation.DataObject.access

  activeAccess = memops.api.Implementation.DataObject.activeAccess

  root = memops.api.Implementation.MemopsObject.root

  topObject = memops.api.Implementation.DataObject.topObject
