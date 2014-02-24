"""
NBNB This code must work for python 2,1 up to and including python 3.x
DO NOT normalise, as the code is loaded into ObjectDomain (Jython 2.1)

MetaModel Implementation information:

- allowedTags define the allowed tags, and the allowed ranges of their values.
See memops.metamodel.TaggedValues for further information

- parameterData give information for setting, checking and writing MetaModel 
attributes. It is used for attributes that may be given as input parameters -
internal implementation attributes are set explicitly.
parameterData has the following legal tags:

- 'default' describes the default setting of a parameter.
  It is an actual value, not a string representation.
  Anything without a default is a mandatory input parameter.
  
- 'type' is either a Python class or type (for direct type checking),
 or a string typeCode for cases where special checking is needed.
 The legal string typeCodes are: Boolean,  Token, StringDict, and content.
 The latter is used for private implementation attributes, to prevent
 overwriting. 
 If 'type' is not set, the parameter can be of any type ('object'). In practice
 there will generally be some kind of type checking in the checkValid function.
 An example would be the value constants (see below).

- 'namelist'. Allowed only for type == 'content'. Content is stored in a shared
  dictionary (elementDict). The namelist is the name of the attribute that holds
  the relevant list of names to extract a subset from the elementDict. E.g. the
  parameter 'classes' will have as a 'namelist' attribute the list of contained
  class names.

- 'hicard' is the maximum number of objects. Default is 1. Any other number,
including unlimited (infinity), means this is a list.

- 'enumeration' means the parameter must be within the enumerated list of values

- 'isFixed' means that the parameter must be identical to its default

- 'setterFunc' is the name of a function that is called on setting of the 
MetamodelElement attribute, instead of the standard setting code. It serves
for attributes/links that needs more complex actions than just setting a value.
if is is set to 'unsettable', the attribute may not be set.

- 'getterFunc' is the name of a function that is called on getting of the 
MetamodelElement attribute, instead of the standard getting code. It serves
for attributes/links that needs more complex actions than just getting a value

__setattr__ and __getattr__ take care of type checking, and information hiding.
Other checking is done only in checkValid.


Implementation attributes are in principle private, and start with '__'
following the standard Python convention. Also following standard Python
the private attributes can be accessed from the outside, and sometimes are.
Non-implementation attributes are generally kept in the normal __dict__, 
and are exported directly. Collections and dictionaries, which can not be 
exported directly, are kept in the __dataDict dictionary.
Contained elements are kept in the __elementDict or __constraints dictionaries.
New attributes can be freely defined. These are kept in the __dict__ as for
normal Python objects.
The _tempData dictionary has no parameterData record and is treated as a 
'new attribute'. It is used for temporary information storage during
object creation. For valid objects it must be empty.

Some of the business rules for MetaClass parameters are enforced in the 
finaliseMetaClass function.

#############################################################################

Value constants:

MetaDataType.enumeration, MetaConstant.value, MetaAttribute.defaultValue and
MetaParameter.defaultValue are all value constants, and must be of MetaDataType
type. They are passed in as python values (not strings). The implementation
checks their validity using MetaDataType.isValid.

#############################################################################

General rules:

- The MetaModelElement.isImplicit attribute is used for elements that are
generated automatically in the course of code generation. By definition all
information in these elements can be derived from other, non-temporary
elements. Implicit elements are not written to disk when the model is stored.

- A number of elements, mainly operations, are generated automatically. 
Accordingly, name clashes may appear only during code generation, and possibly
for certain implementations only. To avoid duplication there is no up-front
check against such name clashes, and it is not known for sure if the model is
valid in this respect until all implementation generations have been tried.

#############################################################################

Names:

 - Element names are of type Token. This means they must be made of digits, 
 lower and upper case letters, and underscore, and may not start with a digit.
 
 - Some names have length limits: MetaClass names, 
 ClassElement names, and package shortNames. See relevant checkValid for details
 
 - Names that start with underscore ('_') are valid only for implicit elements.
 Autogenerated elements may start with underscore.
 Implementation attributes, functions etc. should start with underscore
 
 - As a matter of style, the names of AbstractDataTypes, constants, exceptions
 and packages not containing other packages should start with upper case, 
 and names of AbstractValues and MetaOperations should start with lower case.
 Except for MetaOperations, no element name should contain an underscore.
 
 - Some names may conflict with naming rules in certain implementations or
 programming languages. These are mapped to different names. Where possible the
 mapping is used only internally in the implementation, but there may be cases
 (like Python reserved words) that require changing the publicly  visible name.
 The usename attribute is intended for such renaming. It is  temporary, intended
 for use by ModelAdapt, and is reset when packages are reset. Usename attributes
 are ignored in model comparison if ignoreImplicit  is set to True.
 TODO Usename is not yet in use in the generation machinery

#############################################################################
   
Packages:

  Packages serve to organise both the Model description, the API code,
  and the data storage. 
  All elements of the data model are contained in packages.
  All packages are ultimately contained in a single, topmost package,
  currently called RootPackage (the name is set in ImpConstants). The name of
  this package is omitted in qualified package names.
  Package memops.Implementation (name may change in later versions), is reserved
  for the implementation, and must be imported by all other packages.
  
  Packages are linked to each other through the following relationships:

  - Containment:
   Package A contains package B.
   A package P that contains other packages can contain nothing else, and does
   not correspond to Model, API Code or Data files. Packages such as P serve
   only to organise the other packages and are implemented as a directory
   structure for Model and code files. Packages that contain other packages
   cannot import or be imported by other packages. 

  - Import:  Importing a package makes it known to the importing package, but
   the two remain distinct and do not share a namespace (for Code) or mix their
   data in the same file (for Data). Code from imported packages are implemented
   with 'import otherPackage' in Python. Elements from the imported packages can
   be used in most ways at the Code level. The only exception is that a class
   cannot have subclasses in another package if it is non-abstract or involved
   in a link. Abstract, derived, and implementation links are exempt from this
   rule.

   If package A imports package B, B is in A.importedPackages, and  A is in
   B.accessedPackages. Links that cross package boundaries must be navigable
   from the importing package to the imported package, and may be navigable both
   ways. If navigable both ways, information about the link (at both model, code
   and data level) are kept solely in the importing package. When
   loading a package of data in a file implementation, loading of imported
   packages of data are  triggered automatically. Links that are mandatory
   (locard != 0) or frozen  (changeablility == frozen) must be towards an
   imported (rather than accessed) package.

#############################################################################
 
 Constraints:

 - Constraints may be used for all ConstrainedElements, except MetaParameters.

 - Constraints may not be attached to derived elements

 - Constraints are evaluated in check_valid and also before modifying the 
  data in modifier functions (set and add/remove)

 - Constraints attached to MetaClasses and MetaDataObjTypes are evaluated only
  in check_valid.

 - Constraint codeStubs are given in the manner of tagged values. The precise
 rules for values may vary slightly by language
. For Python they are given as 
  python code strings, correctly indented starting flush left, with two spaces 
  indent, and may not contain multiline strings. Note that the rules for code
  stubs are not checked in the checkValid function. Their correctness as code
  can be checked only on compilation/testing of the final API.
  The code may make use of 'self' and 'value' or their language equivalents.
  For Constraints on MetaDataTypes only 'value' may be used, For constraints
  on MetaClasses and MetaDataObjTypes only 'self' may be used.

 - Constraints where 'self' is allowed are always evaluated on fully formed 
 objects in a legal state. They may therefore assume the existence of any 
 mandatory attributes and links etc. It is recommended to prefer constraints
 that are evaluated in modifier operations, i.e. to use MetaClass and
 MetaDataObjType constraints only if nothing else will serve.
 Constraints on attributes that make use only of 'value' should ideally be
 avoided in  favour of creating constrained data types - this allows
 verification of the values as an alternative to try-except, at least in 
 principle

 - Constraints on ClassElements with hicard != 1 are evaluated for each
 individual object in the collection ('value' is set successively to each
 object rather than to the set of objects).Constraints on the collection as
 such must be implemented as constraints on the containing MetaClass or
 MetaDataObjType.
 
 The following rules are at least partially verified in checkValid:
 
 - There can be no constraints on derived links or parent/child links.

 - Constraints on roles across package boundaries must be on the importing side.

 - For intra-package links, Constraints for one-to-many (or many-to-one)
  binavigable links must be located so they constrain the -to-one link. For
  other binavigable links constraints can be put on either side of the
  association, but all constraints must be on the same side. The location of the
  constraint in the Model makes no difference to its evaluation.

 - Constraints may be given in two different notations:
  1) a string that when executed sets the variable 'isValid' to a truth value
  and that contains the string 'isValid'
  2) a single line that evaluates to a truth value and that does not contain
  the string 'isValid'.

#############################################################################

Organisation of Objects and Classes:

Except for multiple inheritance (see below), all classes must be a subclass of
the topmost base class  (currently called MemopsObject). NonAbstract classes in
the Implementation package must further be subclasses of ImplementationObject,
while all classes outside Implementation must be subclasses of DataObject. All
MetaDataObjTypes must be subclasses of MemopsDataTypeObject.

All non-abstract classes have a link to another class called the parent class.
This link must be mandatory (1..1) and frozen, and defined as a composition
link in UML (filled black diamond). UML composition is used only for this 
purpose. The name of the link can be anything. 
The set of parent-child links form a tree rooted in the MemopsRoot class; a 
MemopsRoot object has no parent and has no UML composition link.

Subtypes of TopObject are children of the MemopsRoot object; all other
classes except MemopsRoot are children of a class in the same package.

All classes (abstract or not) with a non-abstract parent link must have a
main key, unless the parent-child link is  one-to-one. This main key is a set of
attributes and/or links of the whose value identifies it uniquely among the
objects with the same class and the same parent object. The parent-child links
define a unique path from the Project object to each object, and knowing the
main keys allows you to chose the right object at each step on the path. The
precise rules for parent and main keys in the presence of inheritance are
described below.

Rules governing parents and keys:

 - All non-abstract classes have a parent, except for class Project. 
   The parent-child links form a tree.

 - Parent-child links may be either one-to-many or one-to-one.
   The latter are referred to as 'only children'.

 - All classes with a non-abstract parent have a main key, except for only
   children. Only children have no main key.

 - The local key ('main key') of each object must define it uniquely within the
  link to its parent object.

 - The local key consists of an attribute, a link, or an ordered tuple of 
  attributes and links.

 - Only attributes and links belonging to a class can be used as keys for
  the class. These may originally have been defined in either the class or a
  superclass.

 - All attributes and links partaking in a local key must be frozen non-derived,
 and mandatory, and locard must be equal to hicard. Cardinality 0..1 is 
 forbidden, even though it could in theory be accommodated. Links to classes in
 accessed (i.e. not imported) packages are not allowed as keys.
 
 - TopObject keys may only contain attributes and links to other TopObjects

 - The global key ('key') of an object is a list concatenating the local keys
 of itself and all its parents, starting at root level and going down.

 - The combination of class name, and global key must be a unique
 object identifier. Each object and non-abstract class must have a key.

 - The key serves to provide a unique identifying string for each object, for
  use in both GUI, object printing, and interfile references.

 - An abstract superclass may have a key defined. If it does not, the subclasses
  have individual definitions for their keys. These keys need bear no 
  relationship to each other.

 - Parent-child links between two abstract classes may be abstract. These links
  are overridden by links between the subclasses of the abstract classes.
  Abstract classes may have abstract one-way parent links to non-abstract 
  classes.

 - Keys and parents cannot be overridden in subclasses. It follows that if a
  superclass has a key (parent link), that key (parent link) is the same for 
  its subclasses. An abstract class can have a key even if it does not have a 
  parent..

 - A class may not have two different child classes (including subclasses) with
  the same name.

#############################################################################

Cardinalities:

Attributes with hicard == 1 must be isUnique=True, isOrdered=False

In the current implementation, two-way links must have isUnique=True at
both ends. This could be relaxed, but the code generation machinery does not
currently support it correctly.

To allow for (presumed) problems with database implementations, two-way links
are not allowed to have isOrdered=True at both ends.

There are no limitations on attributes, one-way links, derived links, or
Implementation links.

#############################################################################
  
Rules governing inheritance:

 - Multiple inheritance is allowed, as follows:
The base class for MetaClasses is MemopsObject; 
The base class for MetaDataTypeObjects is MemopsDataTypeObject.
Inheritance follows the Python model: depth-first, following the order of
 supertypes. Diamond inheritance is handled by keeping only the last 
 occurrence in the list of supertypes for any class.
Each class can have at most one direct superclass that inherits from 
 the base.
If present this class must be first in the list of supertypes.
Non-abstract MetaClasses and MetaDataTypeObjects must descend from the base.
Only MetaClasses that descend from the base may participate in non-abstract 
links.
Only classes that descend from the base may have elements that override
 elements of other classes.
The first supertype in the list is returned as obj.supertype (derived) and 
 obj.getSupertype().
For languages that do not allow multiple inheritance (possibly for all 
 languages) classes that do not descend from the base are merged into their 
 subclasses before code generation starts.
  
 - Superclasses involved in links can not have subclasses in other packages, 
  unless the links are abstract, derived, or implementation,
 
 - Non-abstract MetaDataObjTypes may not have subtypes in other packages. 
  
 - Most metaAttributes and metaLinks are present in both a type and its
  supertype. Contained elements (AbstractValues and MetaOperations) and
  MetaConstraints are only present in the Element where they belong, but are
  valid for all subtypes as well. Functions that get elements by name will
  automatically look in all supertypes till it finds the desired element.
  Functions that get lists of elements come in two versions, 'get' and
  'getAll'. The 'get' version (in Python replaced by the standard obj.attr
  syntax) will get only the elements contained directly, while the getAll
  version gets elements from both the object and its supertype objects.

 - Operations may override each other. The name and number of parameters must be
  the same, except for constructors. Most attributes must be the same in the
  overriding and overridden operations, but container, guid, documentation, and
  code stubs may be different. Tagged values must be the same, but the
  overriding operation and its parameters may have extra tagged values.
  Parameter defaults may also differ. The rules for MetaOperation targets depend
  on their type. For targets of ClassElement type the target of the overriding
  operation must override the target of the overridden operation. For
  MetaParameter valueTypes the type of the overriding parameter must be a
  subtype of the type of the overridden parameter.

 - Associations and roles may be overridden only if they are defined as 
  abstract.
  The cardinality of the overriding element must be a subset of the
  cardinality of the overridden.
  If the abstract element has high-cardinality different from one, the
  overriding element must also have high-cardinality different from one.
  The valueType of the overriding element must be a subtype of the 
  valueType of the overridden. Overriding attributes may have a defaultValue
  if the overridden attribute does not, but may not override actual default 
  values.
  Otherwise all parameters except 'isAbstract', 'container', 'documentation', 
  'changeability', 'isDerived', 'guid', and 'constraints' must be the same for 
  abstract and overriding association. Constraints and tagged values defined 
  for the overridden attribute are inherited down and may not be overridden.
  The overriding role may have extra constraints and tagged values.
  
  There are extra rules for overriding of Associations:
  Abstract associations must be overridden in all non-abstract subclasses,
  and abstract roles must be contained in abstract classes. 
  The overriding associations must be between subclasses of these classes.
  Unless both the overridden role is one-way, the otherRoles must override 
  each other like the roles. Note that an abstract one-way association may 
  be overriddden by a two-way association.
 
 - MetaParameters may override each other without restraint if both are
 implicit. Otherwise most attributes must be identical. The two may differ in
 container (obviously), the overriding parameter may have extra
 tagged values, and the its valueType may be a subtype of the one it is 
 overriding.
 The cardinality of the overriding element must be a subset of the
 cardinality of the overridden.
 If the abstract element has high-cardinality different from one, the
 overriding element must also have high-cardinality different from one.
 The MetaParameter rules apply equally to parameters of MetaExceptions
 and their supertypes, and to parameters of MetaOperations and the
 MetaOperations they override.
  
 
#############################################################################

 Special cases:
 
 - The isAutomatic attribute in ClassElement is used for attributes or links
 that are set automatically by the implementation, but that must then be stored
 and loaded normally. Currently it is used only for 'serial', but timestamps 
 would be an obvious case.
 
 - The attribute name 'serial' (given in serial_attribute) is used for object
 serial numbers. The code for handling this is hardwired. Attributes with this
 name are illegal in DataObjTypes.
 Attributes with this name must be of type Int, cardinality 1..1, 
 isAutomatic == True, and changeability = frozen.
 
#############################################################################

 Rules for operations :
 
 - The legal opTypes for public functions are given in 
 memops.metamodel.OpTypes.operationData
 opTypes are divided in groups 'query', 'modify', 'create', 'delete' and
 'other'.
 
 Operations have a 'target' that describes what the operation is acting on.  
 Operations that are linked to attributes and roles (e.g. get, set, add, remove,
 findFirst, findAll) have the attribute or role as target. The role or attribute
 must belong to the class itself. Factory functions(opType 'new') have the class
 being created as target.  There are also a number of functions that operate on
 the object containing  them (opTypes 'init', and the 'delete' and 'checkValid'
 opTypes); these have the containing class as target. They generally have the
 same name as their opType and are not inherited. All operations mentioned so
 far are generated automatically, but may be overridden by handwritten
 alternatives. Operations of these types may not be entered where there is no
 autogenerated version to override.

 There are also operations that can only be entered by hand and have no
 autogenerated equivalent. These have the opTypes 'otherQuery', 'otherModify',
 'otherCreate', 'otherDelete', and 'other'. For technical reasons to do with
 the implementation of fine-grained access control, these functions have
 themselves.as targets.
 
 - Operation subOpTypes distinguish operation variants. This is intended
 for languages that allow several overloaded operations with the same name but
 different calling interfaces. 
 
 - Names of operations with attribute or role targets and of factory functions
 are generally made by concatenating the opType and the target name (with first
 letter in upper case). These are inherited. 

 - Operations are given in the following circumstances:
  'get' functions: for all elements. For derived elements the function must
  be explicitly defined.
  'set' functions: for all elements except parent/child links and derived 
  unchangeable elements. For derived changeable elements the function must
  be explicitly defined. Unchangeable elements, links where the other end is 
  unchangeable, and automatic elements all have private set functions; these
  will throw an error unless isReading or override are set when they are called.
  They are intended for use by the implementation only. 
  - 'add' functions: for all elements with hicard != 1
   with the same exceptions as for 'set'
  - 'remove' functions: for all elements with hicard != 1
   with the same exceptions as for 'set'
  - 'sorted': for all elements with hicard != 1 and isOrdered==False
    These functions return a sorted list of the linked-to objects.
    For child links the list is sorted by local key,
    in other cases by (class, fullKey).
  - 'findFirst' functions: for all roles or DataObjType attributes 
    with hicard != 1 without exception
  - 'findAll' functions: for all roles or DataObjType attributes 
     with hicard != 1 without exception
  findFirst returns the first element fitting the search criteria. For 
  unordered collections the function may return any element that fulfills
  the search criteria.
  findAll returns a list of all elements fitting the criteria.
  For implementations with access control the 'find' commands will ignore 
  objects where the caller does not have appropriate permission, whereas
  'get' will either return all objects or throw an error.

 - Operations will only be given explicitly in the UML model where they differ
  from the autogenerated norm. They will be fully specified, except that 
  parameters will be given explicitly only for the 'other' opTypes.
  Any operation given explicitly in the model will be non-autogenerated.
  The code must be given in the codeStubs attribute.

 - Code stub rules may differ between languages. Python code stubs are given 
  as a string, correctly indented starting flush left, with two spaces indent. 
  code:python will not work correctly with 
  multiline strings, as the indentation is modified by adding initial spaces. 
  The code is intended to be transformed into a method of the class, and uses 
  'self' as normal for such methods. Note that the rules for code
 stubs, are not checked in the checkValid function. Their correctness as code
 can be checked only on compilation/testing of the final API.
  For operations that return a value the code must set a parameter called
  'result' (or its language equivalent) to the desired value.
  As a matter of style single-input-parameter functions of 'other' opType should
  have the parameter called 'value'.

 - The ComplexDataType attribute constructorCodeStubs contains code stubs to
  add to the class constructor. The code stub is added after the end of object 
  creation but before the validation check. It is intended to handle 
  creation of mandatory child objects, and other operations that modify the
  data. It is not executed if isReading==True or override == True.
  Syntax as for MetaOperation code stubs. It is illegal for abstract 
  ComplexDataTypes.

 - The MetaClass attribute destructorCodeStubs contains code stubs to
  add to the class destructor. The code is added during checking of which
  objects to delete, before any data are changed, and should not modify the data
  either. It is intended to constrain when objects may legally be deleted. 
  Syntax as for MetaOperation code stubs. It is illegal for abstract 
  Classes.
  postDestructorCode works like destructorCode, but is executed immediately 
  before the object is actually deleted. It serves to make changes in other
  objects.

 - Operations with opTypes that are normally autogenerated may not have explicit
 parameters; Metaparameters in these cases are generated automatically.
 
 Optional parameters are those with cardinality 0..1. These can only be input
 parameters. If no explicit default value is given, the default is automatically
 set to None. Default parameters are stored as actual values (not strings).
 
 Parameters of collection type (hicard != 1) may be optional if a default 
 value is provided. 
 
#############################################################################

 Rules for code tagged values :
 
 Code stubs are used in Constraints, Operations and in ComplexDataTypes
 (constructor and destructor code). code stubs are always StringDicts.
 The dictionary key may consist of up to three parts, with a colon (':')
 as separator. The three parts are interpreted as 
 'language:implementation:variant'
 The same rules are used for DataType.typeCodes
 
#############################################################################

 Derived classes:
 
 Derived classes are not stored, but are generated on the fly from information
 stored elsewhere, for compatibility or convenience. They were introduced to
 allow the ccp.molecule.MolStructure.Coord class to be used for compatibility
 after coordinate data were moved to matrices. 
 Attributes and roles of a derived class, must be either derived or 
 Implementation, except for the parent link and keys. 
 The modeller must make handcoded operations for all link getters that get 
 the class so that class instances are created at need. Also the factory 
 creator function must be written to retrieve existing instances if present 
 instead of creating new ones. Other functions related to the link are 
 generated as normal, and will make use of the handcoded getter functions.
 
#############################################################################

"""

# imports:
import string
import copy
import time

from ccpncore.memops import Constants as memopsConstants
from ccpncore.memops.metamodel import Util as metaUtil
from ccpncore.memops.metamodel import TaggedValues
from ccpncore.memops.metamodel import OpTypes
from ccpncore.memops.metamodel import Constants as metaConstants
from ccpncore.memops import Util as memopsUtil


infinity = memopsConstants.infinity
IntType = metaConstants.IntType
StringType = metaConstants.StringType
TupleType = metaConstants.TupleType
sentinel = metaConstants.sentinel
MemopsError = metaConstants.MemopsError



# Python 2.1 dual-use constants

try:
  junk = True
  junk = False
except NameError:
  globals()['True'] = not 0
  globals()['False'] = not True

booleans = (True, False)

def transferGuid(obj, targetContainer):
  """ Make new guid for obj when copied into a new container, e.g.
  for inheriting down an element.
  guid is deterministic, being composed of object and container guid
  """

  return '__'.join((obj.guid, targetContainer.guid))


#############################################################################
#
# model comparison functions
#
#############################################################################

def compareModels(model1, model2, elementPairings=None, ignoreImplicit=True):
  """ Compare two models assuming same guid means same element
  
  model1 and model2 may be either MetaModelElements or file names
  
  elementPairings are pairs of guids (model1, model2) that are set to
  be identical even though the guids differ. Necessary e.g. when an 
  element is divided among subclasses, or several elements are merged in
  a new superclass.
  
  If ignoreImplicit implicit elements and the usename tag are ignored
  
  NBNB TBD May need reworking to allow for inherited-down elements
  (using originalGuid)
  
  Returns dictionary : {
  'dict1':     'guid:element' dictionary for model 1
  'dict2':     'guid:element' dictionary for model 2
  'unique1:    set of elements found only in model1
  'unique2:    set of elements found only in model2
  'differ':    dictionary of 'guid:list-of-tag' of 
               which tags differ for which guids
  'namematch': dictionary of 'qualifiedName:list-of-tag' of
               which tags differ for unique objects with identical names
               but different guids
  """

  start = time.time()

  # check for identical models
  top1 = model1.topPackage()
  top2 = model2.topPackage()
  if top1 is top2:
    raise MemopsError("%s and %s are from the same model" % (model1, model2))

  # set up
  result = {}
  dict1 = makeObjDict(top1, ignoreImplicit)
  result['dict1'] = dict1.copy()
  dict2 = makeObjDict(top2, ignoreImplicit)
  result['dict2'] = dict2.copy()
  differ = result['differ'] = []
  namematch = result['namematch'] = {}
  unique1 = set()

  # check elementPairings
  dicts = (dict1, dict2)
  if elementPairings:
    for guids in elementPairings:

      # check element pairs are consistent with models
      for ii in 0, 1:
        jj = 1 - ii
        guid = guids[ii]
        if guid not in dicts[ii]:
          raise MemopsError(
            "%s from elementPairings not found in model %s " % (guid, ii))
        if guid in dicts[jj]:
          raise MemopsError(
            "%s (%s) from elementPairings found in model %s " % (
              guid, dicts[jj][guid], jj))

      # check diffs and append
      diffs = compareElements(dict1[guids[0]], dict2[guids[1]],
                              ignoreImplicit=ignoreImplicit)
      differ.append((guids[0], guids[1], diffs))

    # clean element dicts
    for guids in elementPairings:
      for ii in 0, 1:
        dicts[ii].pop(guids[ii], None)

  # compare models
  for guid, ee in dict1.items():
    qName = ee.qualifiedName()
    ee2 = dict2.get(guid)

    if ee2 is None:
      # no match
      unique1.add(ee)

    else:
      # same guid found in both models
      del dict2[guid]

      # compare elements
      diffs = compareElements(ee, ee2, ignoreImplicit=ignoreImplicit)
      if diffs:
        differ.append((ee.guid, ee.guid, diffs))
        if ee.guid is None:
          print('WARNING %s has no guid' % ee.qualifiedName)

    # check for name matches
    try:
      ee2b = top2.metaObjFromQualName(qName)
    except:
      ee2b = None

    if ee2b is not None and ee2b is not ee2:
      # name match without guid match
      diffs = compareElements(ee, ee2b, ignoreImplicit=ignoreImplicit)
      diffs.remove('guid')
      namematch[qName] = (diffs, ee.guid, ee2b.guid)

  # complete result and return
  result['unique1'] = unique1
  result['unique2'] = set(dict2.values())

  end = time.time()
  print('End comparing models, time used %s' % (end - start))

  #
  return result


def compareElements(ee, ee2, ignoreImplicit=True, language='python'):
  """ compare two MetaModelElements. Returns list of tags that differ.
  Language-specific values are only compared for language 'language'
  """

  # tagged values that are skipped as irrelevant
  ignoreTagVals = set(['repositoryTag', 'repositoryId', 'docDiagramNames', 'packageGroup',
                      'isDraft', 'isReferenceData'])

  # dictionaries with language
  languageCoded = set(['typeCodes', 'codeStubs', 'constructorCodeStubs', 'destructorCodeStubs',
                   'postDestructorCodeStubs'])

  result = set()

  clazz = ee.__class__
  if ee2.__class__ is clazz:

    elems = [ee, ee2]

    for tag, pData in clazz.parameterData.items():

      # set up
      hicard = pData.get('hicard')
      pType = pData.get('type')

      if pType == 'content':
        continue

      if ignoreImplicit and tag == 'usename':
        continue

      values = []
      for ii in (0, 1):
        vals = getattr(elems[ii], tag)

        if hicard in (1, None):
          if pData.get('isLink'):
            # NB the 'and' guards against x being None
            vals = ((vals and vals.guid),)
          else:
            vals = (vals,)

        elif pData.get('isLink'):
          # multilink - sort before comparison
          vals = [x.guid for x in vals]
          vals.sort()

        values.append(vals)

      # modify tagged values to remove irrelevant differences:
      if tag == 'taggedValues':
        for tt in values:
          dd = tt[0]
          for ss in ignoreTagVals:
            if ss in dd:
              del dd[ss]

      # compare values - languiage-specific codes
      if tag in languageCoded:
        if values[0][0].get(language) == values[1][0].get(language):
          continue

      # do compare
      if len(values[0]) != len(values[1]):
        result.add(tag)
      else:
        for ii in range(len(values[0])):
          if values[0][ii] != values[1][ii]:
            result.add(tag)
            break

  else:
    # elements are from different classes
    result.add('class')
    if ee.guid != ee2.guid:
      result.add('guid')


  #
  return result


def makeObjDict(rootElement, ignoreImplicit=False, crucialOnly=False):
  """ make a guid:element dictionary
  """

  result = {}

  ll = [rootElement]
  for ee in ll:
    if crucialOnly and isinstance(ee, MetaOperation):
      continue
    if not (ignoreImplicit and ee.isImplicit):
      result[ee.guid] = ee
      ll.extend(ee._MetaModelElement__elementDict.values())
      if isinstance(ee, ConstrainedElement):
        ll.extend(ee._ConstrainedElement__constraints.values())
  #
  return result


#############################################################################
#
# consistency checking functions
#
#############################################################################

def finaliseMetaClass(clazz):
  """ Enforces  some of the design rules for MetaClasses and their parameters,
  and sets some derived parameter attributes
  """

  # lists of supported values
  allowedParTags = {'default':None, 'type':None, 'hicard':IntType,
                    'enumeration':TupleType, 'isFixed':None,
                    'setterFunc':StringType, 'getterFunc':StringType,
                    'namelist':StringType, 'isLink':IntType, }

  miscParTypes = ('Boolean', 'Token', 'StringDict', 'content')

  pythonParTypes = (StringType, IntType)

  unTypedPars = (
    (MetaDataType, 'enumeration'), (MetaAttribute, 'defaultValue'),
    (MetaParameter, 'defaultValue'), (MetaConstant, 'value'),
  )

  for pName, pData in clazz.parameterData.items():

    # check parameter tags and value types
    for tag, val in pData.items():

      try:
        parType = allowedParTags[tag]
      except:
        raise MemopsError(
          "%s: illegal tag %s for parameter %s" % (clazz.__name__, tag, pName))

      if parType is not None and not isinstance(val, parType):
        raise MemopsError(
          "%s: tag %s for parameter %s has illegal value %s" % (
            clazz.__name__, tag, pName, val))

      # special checks


    # Booleans
    if pData.get('isFixed', sentinel) not in (True, False, sentinel):
      # NBNB we use sentinel to check that there is a value in the dictionaru
      # We can not use 'in pData', because we must conform to Python 2.1
      raise MemopsError("%s: tag isFixed for parameter %s has illegal value %s" % (
        clazz.__name__, pName, pData.get('isFixed')))

    # 'type' tag
    myType = pData.get('type')

    if pData.get('nameList') and (myType != 'content' or pName == 'constraints'):
      raise MemopsError(
        "%s: parameter %s is not standard content but has 'namelist'" % (
          clazz.__name__, pName))

    if myType is None:
      if (clazz, pName) not in unTypedPars:
        raise MemopsError(
          "%s: parameter %s has no explicit type " % (clazz.__name__, pName))

    elif myType in miscParTypes:
      if myType == 'StringDict' and pData.get('hicard', 1) != 1:
        raise MemopsError(
          "%s: tag %s for parameter %s is StringDict but has hicard %s" % (
            clazz.__name__, tag, pName, pData.get('hicard')))

    elif myType in pythonParTypes:
      pass

    elif issubclass(myType, MetaModelElement):
      pData['isLink'] = True



    else:
      raise MemopsError("%s: parameter %s has unsupported type %s" % (
        clazz.__name__, pName, myType))


#############################################################################
#
# classes
#
#############################################################################


class MetaModelElement:
  """ Base class for all MetaModel elements
  """

  # information for handling input parameters
  parameterData = {

    # input parameters

    # NB container type must be set outside class definition
    'container':{},
    'name':{'type':'Token', },
    'usename':{'type':'Token', 'getterFunc':'getUsename', 'default':None},
    'guid':{'type':StringType, },
    'documentation':{'type':StringType, 'default':'', },
    'taggedValues':{'type':'StringDict', 'default':{}, },
    'isImplicit':{'type':'Boolean', 'default':False, },
  }

  allowedTags = TaggedValues.allowedTags['MetaModelElement']

  # attribute used for guid uniqueness check
  guidDict = None

  def __getattr__(self, tag):
    """ getattr.
    There are four classes of gettable attributes
    1) Those stored in the __dict__, where this functions is not called
       This includes those that start with '__' and have their names mangled.
       These may or may not have a parameterData record
    2) Those with a getterFunc
    3) Those with type == 'content', that are stored in the elementDict
    4) Collections and dictionaries that are stored in the __dataDict and are 
       copied on exit
       
    """

    try:
      pData = self.__class__.parameterData[tag]
    except KeyError:
      raise AttributeError(
        "%s object has no attribute %s" % (self.__class__, tag))

    # defined attribute
    getterFunc = pData.get('getterFunc')

    if getterFunc:
      return getattr(self, getterFunc)()

    elif pData.get('type') == 'content':
      if tag == 'constraints':
        ll = list(self._ConstrainedElement__constraints.items())
        ll.sort()
        return [x[1] for x in ll]
      else:
        # get named elements from elementDict
        return [self.__elementDict[x] for x in
                getattr(self, pData['namelist'])]

    else:
      try:
        return copy.copy(self.__dataDict[tag])
      except KeyError:
        raise AttributeError(
          "%s object has no attribute %s" % (self.__class__, tag))

  def __setattr__(self, tag, value):

    pData = self.parameterData.get(tag)

    if pData is None:
      # non-defined parameters
      self.__dict__[tag] = value

    else:
      # check parameter type
      pType = pData.get('type')
      hicard = pData.get('hicard', 1)
      setterFunc = pData.get('setterFunc')

      if setterFunc == 'unsettable':
        raise MemopsError(
          "Tried to set implementation attribute %s in class %s" % (
            tag, self.__class__.__name__))

      elif pType == 'content':
        raise MemopsError("Tried to set content attribute %s in class %s" % (
          tag, self.__class__.__name__))

      elif setterFunc:
        getattr(self, setterFunc)(value)

      elif pType == 'StringDict':
        # copy to avoid sharing internal objects
        self.__dataDict[tag] = copy.copy(value)

      elif hicard != 1:
        # copy to avoid sharing internal objects
        self.__dataDict[tag] = copy.copy(value)

      else:
        self.__dict__[tag] = value


  def __init__(self, **params):
    """ basic init. NB only parameters with parameterData records can be set
    """

    # set up
    parameterData = self.parameterData

    # Set implementation attributes
    self.__elementDict = {}
    self.__dataDict = {}
    self._tempData = {}

    # check attributes necessary for normal error handling
    if params.get('name') is None:
      raise MemopsError(
        "Tried to create %s without a name" % self.__class__.__name__)

    if params.get('container') is None:
      if not (isinstance(self, MetaPackage) and params[
        'name'] == metaConstants.rootPackageName):
        raise MemopsError("Tried to create %s %s without a container" % (
          self.__class__.__name__, params['name']))

    # set parameters
    # set order (name and container needed for error handling)
    ll = list(parameterData.keys())
    ll.remove('name')
    ll.remove('container')
    ll = ['name', 'container'] + ll
    # set values
    nFound = 0
    for tag in ll:
      val = params.get(tag, sentinel)
      if val is not sentinel:
        nFound += 1
        setattr(self, tag, val)
      else:
        pData = parameterData[tag]
        val = pData.get('default', sentinel)
        if val is not sentinel:
          if pData.get('setterFunc') != 'unsettable':
            setattr(self, tag, val)

    # check for undefined parameters
    nn = len(params) - nFound
    if nn:
      ll2 = [x for x in params.keys() if x not in ll]
      raise MemopsError("""%s: Input parameters contained %s undefined names:
%s""" % (self, nn, ll2))

    # set link from container
    container = self.container
    if container is not None:
      if isinstance(self, MetaConstraint):
        containerDict = container._ConstrainedElement__constraints
      else:
        containerDict = container.__elementDict
      if self.name in containerDict.keys():
        raise MemopsError("%s already has %s named %s" % (
          container, self.__class__.__name__, self.name))
      else:
        containerDict[self.name] = self


  def __repr__(self):
    """ give ID string for MetaModelElement
    """
    return "<%s: %s>" % (self.__class__.__name__, self.qualifiedName())

  def qualifiedName(self):
    """ Get qualified name of MetaElement relative to topmost package ('root')
    """
    ll = []
    ee = self
    cc = ee.container

    # special case: RootPackage
    if cc is None:
      return self.name

    # normal cases
    while cc is not None:
      ll.append(ee.name)
      ee = cc
      cc = ee.container

    ll.reverse()

    #
    return '.'.join(ll)

  def getUsename(self):
    """getter for semiderived attribute usename
    """

    result = self.__dict__['usename']
    if result is None:
      result = self.name
    #
    return result


  def metaObjFromQualName(self, qname):
    """ find MetaObject given qualified name
    """

    namePath = qname.split('.')

    # find result
    result = self.topPackage()
    for name in namePath[:-1]:
      result = result.__elementDict.get(name)
      if result is None:
        raise MemopsError("No MetaObject corresponding to %s" % qname)

    # final step - account for MetaConstraints
    name = namePath[-1]

    result = result.__elementDict.get(name)

    if result is None and isinstance(self, ConstrainedElement):
      result = self._ConstrainedElement__constraints.get(name)

    if result is None:
      raise MemopsError("No MetaObject corresponding to %s" % qname)

    #
    return result

  def topPackage(self):
    """ return root package (topmost container)
    """
    result = self
    while result.container is not None:
      result = result.container
    #
    return result

  def addTaggedValue(self, tag, value):
    """ Add tagged value
    """

    if type(tag) != StringType:
      raise MemopsError("%s tagged value tag %s is not a string" % (self, tag))
    if type(value) != StringType:
      raise MemopsError(
        "%s tagged value %s value %s is not a string" % (self, tag, value))

    allowedTags = self.allowedTags
    allowedVals = allowedTags.get(tag, sentinel)
    if allowedVals is not sentinel:
      if allowedVals is not None and value not in allowedVals:
        raise MemopsError(
          "%s tag %s has illegal value %s" % (self, tag, value))
    else:
      raise MemopsError("%s : unsupported tag %s " % (self, tag))

    self.__dataDict['taggedValues'][tag] = value

  def removeTaggedValue(self, tag):
    """Remove existing tagged value
    """

    if tag in self.__dataDict['taggedValues'].keys():
      del self.__dataDict['taggedValues'][tag]
    else:
      raise MemopsError("%s has no tagged value %s " % (self, tag))

  def canAccess(self, target):
    """ check if target is accessible from self
    """

    pp1 = self
    while not isinstance(pp1, MetaPackage):
      pp1 = pp1.container

    pp2 = target
    while not isinstance(pp2, MetaPackage):
      pp2 = pp2.container

    if pp1 is pp2 or pp2 in pp1.importedPackages:
      return True
    else:
      return False

  def _getCloningDict(self):
    """ get dictionary of parameters as input for making
    a copy of self.
    
    NB called from subclasses but should not be called from the outside
    """
    result = {}
    for pName, pData in self.__class__.parameterData.items():

      if pName in ('container', 'guid'):
        pass

      elif (pData.get('type') == 'content' or pData.get(
        'setterFunc') == 'unsettable'):
        pass

      else:
        result[pName] = getattr(self, pName)

    tagVals = result['taggedValues']
    if tagVals.get('originalGuid') is None:
      tagVals['originalGuid'] = self.guid

    return result

  def checkValid(self, complete=False):
    """ Check that object is valid. Recursively checks contents
    Includes general attribute checks
    """

    name = self.name

    container = self.container
    if container:
      # container link check
      if isinstance(self, MetaConstraint):
        dd = container._ConstrainedElement__constraints
      else:
        dd = container.__elementDict
      if dd.get(name) is not self:
        raise MemopsError(
          "Two-way container link %s-%s is broken. Bug (1)?" % (
            container, self))

    # general parameter checks
    for tag, pData in self.parameterData.items():

      # set up
      pType = pData.get('type')
      enumeration = pData.get('enumeration')

      # unsettable (implementation) parameters
      if pType == 'content':
        continue

      value = getattr(self, tag)

      # default values
      if value == pData.get('default', sentinel):
        # Always OK.
        # This check takes care of fixed parameters, 
        # optional attributes that are set to None, etc.
        continue

      elif pData.get('isFixed'):
        # check fixed parameters
        raise MemopsError(
          "%s - wrong value %s for fixed attribute %s" % (self, value, tag))

      # string dictionaries
      if pType == 'StringDict':
        for key, val in value.items():
          if not key or not isinstance(key, StringType):
            raise MemopsError(
              "%s: non-string or empty key %s in StringDict %s" % (
                self, key, tag))
          if not val or not isinstance(val, StringType):
            raise MemopsError(
              "%s: non-string or empty value %s in StringDict %s" % (
                self, val, tag))
        continue

      # single or list (for further processing):
      hicard = pData.get('hicard', 1)
      if hicard == 1:
        value = (value,)

      elif hicard != infinity and len(value) > hicard:
        # hicard check
        raise MemopsError("%s.%s - more than %s elements in value: %s" % (
          self, tag, hicard, value))


      # Booleans and other enumerated types
      if pType == 'Boolean':
        enumeration = booleans

      if enumeration is not None:
        for item in value:
          if item not in enumeration:
            raise MemopsError(
              "%s.%s - %s not among allowed values" % (self, tag, value))
        continue

      # string types
      if pType == StringType:
        for item in value:
          if not item or not isinstance(item, StringType):
            raise MemopsError(
              "%s.%s - %s is empty or not a string" % (self, tag, value))

      elif pType == 'Token':
        for item in value:
          if not item or not isinstance(item, StringType):
            raise MemopsError(
              "%s.%s - %s is empty or not a string" % (self, tag, item))
          for char in item:
            if char not in metaConstants.validNameChars:
              raise MemopsError("%s %s %s contains illegal character %s" % (
                self, tag, item, char))

          if item[0] in string.digits:
            raise MemopsError(
              "%s %s %s starts with a digit" % (self, tag, item))

      # special exception - supertype of MemopsObject
      elif tag in ('supertypes', 'supertype') and name == 'MemopsObject':
        pass

        # special exception - supertype of MemopsObject
      elif tag == 'subtypes' and name == 'ComplexDataType':
        pass

        # other cases:
      elif pType is not None:
        for item in value:
          if not isinstance(item, pType):
            raise MemopsError("%s - %s should be type %s for attribute %s" % (
              self, value, pType, tag))

    # specific checks for MetaModelElement attributes      

    # name
    if not self.isImplicit:
      # autogenerated elements can be assumed to be OK
      if name[0] == metaConstants.underscore:
        raise MemopsError(
          "%s: name %s of non-implicit element starts with '_'" % (self, name))

      if (metaConstants.underscore in name[1:] and not isinstance(self,
                                                                 MetaOperation) and not isinstance(
        self, MetaConstraint)):
        print("WARNING, name of %s contains underscore" % self)

    # check correct guid format
    guid = self.guid
    for char in """&'"<>""":
      if char in guid:
        raise MemopsError("%s: guid %s contains illegal character %s" % (
          self, guid, repr(char)))
    # check guid uniqueness
    guidDict = MetaModelElement.guidDict
    if guidDict is not None:
      competitor = guidDict.get(guid)
      if competitor is not None:
        raise MemopsError(
          "%s: guid %s duplicates guid of %s" % (self, guid, competitor))

      else:
        guidDict[guid] = self

      # _tempData dictionary
      if self._tempData:
        raise MemopsError(
          "%s - _tempData dictionary is not emptied, keys are %s" % (
            self, self._tempData.keys()))


    # recursive contents check:
    for obj in self.__elementDict.values():
      obj.checkValid(complete=complete)
      if obj.container is not self:
        raise MemopsError(
          "Two-way container link %s-%s is broken. Bug (2)?" % (self, obj))

# NB required as class is not defined inside itself
MetaModelElement.parameterData['container']['type'] = MetaModelElement

#############################################################################


class ConstrainedElement(MetaModelElement):
  """ abstract class for elements 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(MetaModelElement.parameterData)

  # implementation parameters
  parameterData['constraints'] = {'type':'content'}

  # allowed tagged values
  allowedTags = MetaModelElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['ConstrainedElement'])

  def __init__(self, **params):

    if self.__class__ is ConstrainedElement:
      raise MemopsError(
        "Attempt to create istance of abstract class ConstrainedElement")

    self.__constraints = {}

    MetaModelElement.__init__(self, **params)

    # Set implementation attributes
    self._MetaModelElement__dataDict['constraints'] = {}

  def getAllConstraints(self):
    """ Not really necessary here, but in some subclasses it is overridden.
    """
    return self.constraints

  def getConstraint(self, name):
    """ get contraint by name
    """
    return self.__constraints.get(name)

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """
    MetaModelElement.checkValid(self, complete=complete)

    # validity check constraints
    for constraint in self.__constraints.values():
      constraint.checkValid(complete=complete)
      if constraint.container is not self:
        raise MemopsError(
          "Two-way container link %s-%s is broken. Bug (3)?" % (
            self, constraint))


#############################################################################


class HasParameters(MetaModelElement):
  """ abstract class for elements that have parameters , 
  i.e. MetaOperations and MetaExceptions
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(MetaModelElement.parameterData)
  parameterData.update({'parameters':{'type':'content',
                                      'namelist':'_HasParameters__parameterNames', },
                        'visibility':{'type':'Token',
                                      'enumeration':metaConstants.visibility_enumeration,
                                      'default':metaConstants.public_visibility,
                                      'isFixed':False, }, })

  # allowed tagged values
  allowedTags = MetaModelElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['HasParameters'])

  def __init__(self, **params):

    if self.__class__ is HasParameters:
      raise MemopsError(
        "Attempt to create istance of abstract class HasParameters")

    MetaModelElement.__init__(self, **params)

    # implementation attributes
    self.__parameterNames = []

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """
    MetaModelElement.checkValid(self, complete=complete)


#############################################################################

class HasSupertype:
  """ Abstract class to provide supertype/subtype functionality
  """

  def __init__(self, **params):

    raise MemopsError(
      "Attempt to create istance of abstract class HasSupertype")

  def getSupertype(self):
    """ get supertype (derived attribute)
    """
    ll = self._MetaModelElement__dataDict['supertypes']
    if ll:
      return ll[0]
    else:
      return None

  def setSupertypes(self, supertypes):
    """ setter for link supertypes
    """

    # first clean up
    ll = self._MetaModelElement__dataDict.get('supertypes')
    if ll:
      for obj in ll:
        obj._MetaModelElement__dataDict['subtypes'].remove(self)

    # then reset internal list
    self._MetaModelElement__dataDict['supertypes'] = []

    # now put in data
    for supertype in supertypes:
      self.addSupertype(supertype)

  def removeSupertype(self, supertype):
    """ remove supertype/subtypes link
    """

    ll = self._MetaModelElement__dataDict['supertypes']

    if supertype in ll:
      ll.remove(supertype)
      supertype._MetaModelElement__dataDict['subtypes'].remove(self)

    else:
      raise MemopsError(
        "%s: Attempt to remove non-existing supertype %s" % (self, supertype))

  def addSupertype(self, supertype):
    """ add supertype/subtypes link
    """

    ll = self._MetaModelElement__dataDict['supertypes']

    if supertype not in ll:
      ll.append(supertype)
      supertype._MetaModelElement__dataDict['subtypes'].append(self)

    else:
      raise MemopsError(
        "%s: Attempt to add pre-existing supertype %s" % (self, supertype))

  def getAllSupertypes(self):
    """ recursively get list of self and all its supertypes
    self is the first element of the list.
    Search is depth-first and repects order of individual supertypes
    """

    result = []
    lists = [[self]]
    indices = [-1]
    while indices:
      ind = indices[-1]
      obj = lists[-1][ind]

      # handling of diamond inheritance - python style
      # A class is included only in the last place it appears
      if obj in result:
        result.remove(obj)

      result.append(obj)

      ind = ind + 1
      if ind:
        indices[-1] = ind
      else:
        lists.pop()
        indices.pop()

      ll = obj._MetaModelElement__dataDict['supertypes']
      if ll:
        lists.append(ll)
        indices.append(-len(ll))

    #
    return result

  def getAllSubtypes(self):
    """ recursively get list of self and all its subtypes
    self is the first element of the list
    """

    result = [self]
    for obj in result:
      result.extend(obj._MetaModelElement__dataDict['subtypes'])
    #
    return result

  def getNonAbstractSubtypes(self):
    """ recursively get list of self and all its non-abstract subtypes
    """

    ll = [self]
    for obj in ll:
      ll.extend(obj._MetaModelElement__dataDict['subtypes'])
    return [x for x in ll if not x.isAbstract]

  def getAllElements(self, clazz=None):
    """ utility function - to get all elements, possibly only of a given type
    
    NB should be private in languages that support the concept.
    """

    ll = self.getAllSupertypes()
    ll.reverse()
    elements = {}

    # get all elements
    for obj in ll:
      elements.update(obj._MetaModelElement__elementDict)

    # return sorted list
    items = list(elements.items())
    items.sort()
    if clazz:
      result = [x[1] for x in items if isinstance(x[1], clazz)]
    else:
      result = [x[1] for x in items]

    #
    return result


#############################################################################


class AbstractDataType(ConstrainedElement, HasSupertype):
  """ abstract class for abstract data types 
  (classes, simple and complex dataypes) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ConstrainedElement.parameterData)
  parameterData.update(
    {'isRoot':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'isLeaf':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'isAbstract':{'type':'Boolean', 'default':False, },
     'visibility':{'type':'Token',
                   'enumeration':metaConstants.visibility_enumeration,
                   'default':metaConstants.public_visibility, 'isFixed':True, },
     'supertype':{'setterFunc':'unsettable', 'getterFunc':'getSupertype',
                  'default':None, },
     'supertypes':{'setterFunc':'setSupertypes', 'hicard':infinity, },
     'subtypes':{'setterFunc':'unsettable', 'hicard':infinity, }, })

  # allowed tagged values
  allowedTags = ConstrainedElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['AbstractDataType'])

  def __init__(self, **params):

    if self.__class__ is AbstractDataType:
      raise MemopsError(
        "Attempt to create istance of abstract class AbstractDataType")

    ConstrainedElement.__init__(self, **params)

    # implementation attributes
    dd = self._MetaModelElement__dataDict
    if dd.get('subtypes') is None:
      dd['subtypes'] = []
    if dd.get('supertypes') is None:
      dd['supertypes'] = []

  def getConstraint(self, name):
    """ Get constraint called name
    Return None if nothing found
    
    Recursively search supertypes till you find constraint
    """

    for obj in self.getAllSupertypes():
      result = obj._ConstrainedElement__constraints.get(name)
      if result is not None:
        return result
    else:
      return None

  def getAllConstraints(self):
    """ get all constraints, including those from supertypes
    """

    allSupertypes = self.getAllSupertypes()
    allSupertypes.reverse()
    constraints = {}
    for supertype in allSupertypes:
      constraints.update(supertype._ConstrainedElement__constraints)

    ll = list(constraints.items())
    ll.sort()
    return [x[1] for x in ll]

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    ConstrainedElement.checkValid(self, complete=complete)

    if self.isRoot and self.supertypes:
      raise MemopsError("%s is root but has supertypes" % self)

    for supertype in self.supertypes:

      # abstract class cannot have non-abstract supertype
      if self.isAbstract and not supertype.isAbstract:
        raise MemopsError(
          "Abstract %s has non-abstract supertype %s" % (self, supertype))

      # package access check
      if not self.canAccess(supertype):
        raise MemopsError(
          "%s - cannot access supertype %s" % (self, supertype))

      # check two-way link
      if complete:
        # NB check is too slow to be done routinely
        if supertype.subtypes.count(self) != 1:
          raise MemopsError(
            "Two-way supertype link %s-%s is broken. Bug (1)?" % (
              supertype, self))

    # check that abstract classes have subclasses
    if self.isAbstract and not self.getNonAbstractSubtypes():
      print("WARNING - %s: abstract type lacks non-abstract subtypes" % self)

    subtypes = self.subtypes

    # leaf cannot have subtypes
    if subtypes and self.isLeaf:
      raise MemopsError("%s is leaf but has subtypes" % self)

    # name style
    if self.name[0] not in metaConstants.uppercase:
      print("WARNING, name of %s does not start with upper case" % self)

    # check two-way link
    for obj in subtypes:
      if self not in obj.supertypes:
        raise MemopsError(
          "Two-way supertype link %s-%s is broken. Bug (2)?" % (self, obj))


#############################################################################


class AbstractValue(ConstrainedElement):
  """ abstract class for abstract values (parameters, attributes, and roles) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ConstrainedElement.parameterData)
  parameterData.update({'locard':{'type':IntType, 'default':0, },
                        'hicard':{'type':IntType, 'default':1, },
                        'isOrdered':{'type':'Boolean', 'default':False, },
                        'isUnique':{'type':'Boolean', 'default':True, }, })

  # allowed tagged values
  allowedTags = ConstrainedElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['AbstractValue'])

  def __init__(self, **params):

    if self.__class__ is AbstractValue:
      raise MemopsError(
        "Attempt to create istance of abstract class AbstractValue")

    ConstrainedElement.__init__(self, **params)

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    ConstrainedElement.checkValid(self, complete=complete)

    # limits to locard and hicard
    if self.locard < 0:
      raise MemopsError("%s: locard %s < 0" % (self, self.locard))

    if self.hicard != infinity:
      if self.hicard < 1:
        raise MemopsError("%s: hicard %s < 1" % (self, self.hicard))
      if self.hicard < self.locard:
        raise MemopsError(
          "%s: hicard %s < locard %s" % (self, self.hicard, self.locard))

    # check unique and ordered NBNB TBD more rules to be added later, 
    # maybe elsewhere
    if self.hicard == 1:
      for tag in ('isOrdered', 'isUnique'):
        default = self.parameterData[tag]['default']
        if getattr(self, tag) != default:
          raise MemopsError(
            "%s: %s must be %s for hicard==1" % (self, tag, default))

    # name style
    if self.name[0] not in metaConstants.lowercase:
      print("WARNING, name of %s does not start with lower case" % self)


#############################################################################


class ClassElement(AbstractValue):
  """ abstract class class elements (attributes and roles) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(AbstractValue.parameterData)
  parameterData.update({'visibility':{'type':'Token',
                                      'enumeration':metaConstants.visibility_enumeration,
                                      'default':metaConstants.public_visibility,
                                      'isFixed':True, },
                        'isAbstract':{'type':'Boolean', 'default':False, },
                        'changeability':{'type':'Token',
                                         'enumeration':metaConstants.changeability_enumeration,
                                         'default':metaConstants.changeable, },
                        'isDerived':{'type':'Boolean', 'default':False, },
                        'isImplementation':{'type':'Boolean',
                                            'default':False, },
                        'isAutomatic':{'type':'Boolean', 'default':False, },
                        'baseName':{'type':'Token', }, })

  # allowed tagged values
  allowedTags = AbstractValue.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['ClassElement'])

  def __init__(self, **params):

    if self.__class__ is ClassElement:
      raise MemopsError(
        "Attempt to create istance of abstract class ClassElement")

    AbstractValue.__init__(self, **params)

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    container = self.container

    if isinstance(container, MetaClass):
      Base = self.metaObjFromQualName('.'.join(
        [metaConstants.modellingPackageName,
         metaConstants.implementationPackageName, metaConstants.baseClassName]))
    else:
      Base = self.metaObjFromQualName('.'.join(
        [metaConstants.modellingPackageName,
         metaConstants.implementationPackageName,
         metaConstants.baseDataTypeObjName]))

    name = self.name
    baseName = self.baseName

    # check name length
    if len(name) > metaConstants.maxTagLength:
      raise MemopsError("%s: name %s longer than %s characters" % (
        self, name, metaConstants.maxTagLength))

    if len(baseName) > metaConstants.maxTagLength:
      raise MemopsError("%s: baseName %s longer than %s characters" % (
        self, baseName, metaConstants.maxTagLength))

    AbstractValue.checkValid(self, complete=complete)

    # check changeability
    if self.changeability == metaConstants.add_only:
      raise MemopsError("%s: changeability %s not implemented yet" % (
        self, self.changeability))

    # check baseName usage.

    if baseName != name and self.hicard == 1:
      raise MemopsError(
        "%s hicard is 1 but baseName %s differs from name %s" % (
          self, self.baseName, self.name))

    # give warning for dissimilar name and basename:
    nn = int(len(name) / 2)
    if name[:nn] != baseName[:nn]:
      print("WARNING, %s baseName %s dissimilar to name %s" % (
        self, self.baseName, self.name))


    # get temporary info for operations (avoids repeated getattr calls
    tempOpInfo = []
    for op in container.getAllOperations():
      if op.target is self and op.opSubType is None:
        tempOpInfo.append((op.opType, op.isImplicit))

    # check derived elements:
    if self.isDerived:

      if self.isAutomatic:
        raise MemopsError("%s is both derived and automatic" % self)

      if self.isImplementation:
        raise MemopsError("%s is both derived and Implementation" % self)

      # check for getter:
      getters = [x for x in tempOpInfo if x[0] == 'get']
      if not getters:
        raise MemopsError("derived %s lacks getFunction" % self)

      elif getters[0][1] and not self.isImplicit:
        raise MemopsError("derived %s lacks explicit getFunction" % self)

      # check for setter
      setters = [x for x in tempOpInfo if x[0] == 'set']

      if self.changeability == metaConstants.frozen:
        if setters:
          raise MemopsError(
            "derived unchangeable %s has setFunction" % (self,))

      else:

        if not setters:
          raise MemopsError("derived changeable %s lacks setFunction" % self)

        elif setters[0][1] and not self.isImplicit:
          raise MemopsError(
            "derived changeable %s lacks explicit setFunction" % self)

    # check implementation elements:
    elif self.isImplementation:

      if self.isAutomatic:
        raise MemopsError("%s is both automatic and Implementation" % self)

      # check for getter:
      getters = [x for x in tempOpInfo if x[0] == 'get' and not x[1]]
      if getters:
        raise MemopsError("Implementation %s has explicit getFunction" % self)

      if self.changeability != metaConstants.frozen:
        raise MemopsError("Implementation %s is not frozen" % self)

    else:
      # special check on Base class elements
      if container is Base and self.name != 'override':
        raise MemopsError(
          "%s: ClassElement of %s must be Implementation or Derived" % (
            self, Base))

      # check automatic elements:
      if self.isAutomatic:

        setters = [x for x in tempOpInfo if x[0] == 'set' and not x[1]]
        if setters:
          raise MemopsError("automatic %s has explicit setFunction" % self)

      if self.isAutomatic or self.changeability == metaConstants.frozen:
        for tag in ('add', 'remove'):
          ops = [x for x in tempOpInfo if x[0] == tag]
          if ops:
            raise MemopsError(
              "%s is automatic or frozen and has %sFunction" % (self, tag))

    # NBNB TBD we do not check for 'add' and 'remove' functions here, as
    # they should be done as 'get, add, set'

    # special case - check attribute called 'serial' 
    if name == metaConstants.serial_attribute:

      if not isinstance(self, MetaAttribute):
        raise MemopsError("%s: name 'serial' reserved for attribute" % self)

      if not isinstance(self.container, MetaClass):
        raise MemopsError(
          "%s: name 'serial' only allowed inside MetaClass" % self)

      if self.valueType.name != 'Int':
        raise MemopsError("%s: 'serial' attribute must be type 'Int'" % self)

      serialValues = {'isAutomatic':True, 'changeability':metaConstants.frozen,
                      'hicard':1, 'locard':1, }
      for key, val in serialValues.items():
        x = getattr(self, key)
        if x != val:
          raise MemopsError("%s: %s must be %s, was %s" % (self, key, val, x))

    # check overriding
    allSupertypes = container.getAllSupertypes()
    mayNotOverride = not (Base in allSupertypes)
    for supertype in allSupertypes[1:]:
      superElem = supertype._MetaModelElement__elementDict.get(name)
      if superElem is not None:

        if superElem.__class__ is not self.__class__:
          raise MemopsError(
            "%s overrides %s but types are different" % (superElem, self))

        # classes without supertype cannot override or be overridden
        if mayNotOverride and not superElem.isAbstract:
          raise MemopsError(
            "Name clash between %s and %s - classes do not descend from %s" % (
              superElem, self, Base))

        # superElem must be abstract
        if not superElem.isAbstract:
          raise MemopsError("%s overrides non-abstract %s" % (self, superElem))

        parameterData = self.parameterData
        for tag in parameterData.keys():

          if tag in (
            'isAbstract', 'container', 'documentation', 'guid',
            'changeability', 'isDerived', 'otherRole'):
            # NB different changeability is only allowed because the
            # overridden role has to be abstract
            continue

          if parameterData[tag].get('type') == 'content':
            continue

          val = getattr(self, tag)
          superval = getattr(superElem, tag)
          if val == superval:
            pass

          elif tag == 'defaultValue' and not superval:
            # attributes only
            pass

          elif tag == 'locard':
            if superval > val:
              raise MemopsError(
                "%s: locard %s lower than in overridden %s %s" % (
                  self, val, self.__class__.__name__, superElem))

          elif tag == 'hicard':

            if (superval == 1) != (val == 1):
              raise MemopsError(
                "%s overriding %s: hicard must be 1 in both or neither" % (
                  self, superElem))

            elif superval == infinity:
              pass

            elif val == infinity:
              raise MemopsError(
                "%s: hicard infinity higher than in overridden %s %s" % (
                  self, self.__class__.__name__, superElem))
              pass

            elif superval < val:
              raise MemopsError(
                "%s: hicard %s higher than in overridden %s %s" % (
                  self, val, self.__class__.__name__, superElem))

          elif tag == 'taggedValues':
            for tt, vv in superval.items():
              if val.get(tt) != vv:
                raise MemopsError(
                  "%s: tagged value %s not the same as in overridden %s %s" % (
                    self, tt, self.__class__.__name__, superElem))

          elif tag == 'valueType':
            if superval not in val.getAllSupertypes():
              if superval.qualifiedName() != 'memops.Implementation.Any':
                raise MemopsError(
                  "%s overrides %s but valueType %s is not subtype of %s" % (
                    self, superElem, val, superval))

          else:
            raise MemopsError(
              "%s overrides %s but differs for %s" % (self, superElem, tag))

        for name in self._ConstrainedElement__constraints.keys():
          if superElem.getConstraint(name) is not None:
            raise MemopsError(
              "%s constraint %s overrides inherited constraint" % (self, name))


#############################################################################


class ComplexDataType(AbstractDataType):
  """ Abstract superclass of MetaClass and MetaDataObjType
  """
  parameterData = memopsUtil.semideepcopy(AbstractDataType.parameterData)
  parameterData['constructorCodeStubs'] = {'type':'StringDict', 'default':{}, }
  parameterData['attributes'] = {'type':'con'
                                        ''
                                        'tent',
                                 'namelist':'_ComplexDataType__attributeNames'}
  parameterData['operations'] = {'type':'content',
                                 'namelist':'_ComplexDataType__operationNames'}

  # allowed tagged values
  allowedTags = AbstractDataType.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['ComplexDataType'])

  def __init__(self, **params):

    AbstractDataType.__init__(self, **params)

    # Set implementation attributes
    self.__attributeNames = []
    self.__operationNames = []

  def addConstructorCodeStub(self, tag, value):
    """ Add constructorCodeStub
    """

    if type(tag) != StringType:
      raise MemopsError("%s codeStub tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s codeStub %s value %s is not a string" % (self, tag, value))

    if tag not in metaConstants.codeStubTags:
      raise MemopsError("%s : unsupported codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['constructorCodeStubs'][tag] = value

  def removeConstructorCodeStub(self, tag):
    """Remove existing ConstructorCodeStub
    """

    if self._MetaModelElement__dataDict['constructorCodeStubs'].get(tag,
                                                                    sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['constructorCodeStubs'][tag]
    else:
      raise MemopsError("%s has no ConstructorCodeStub %s " % (self, tag))

  def inheritDown(self):
    """ Copy all contained elements and constraints down to subtypes
    """

    for ll in (self.attributes, self.constraints):
      for obj in ll:
        dd = obj._getCloningDict()
        for subtype in self.subtypes:
          dd['container'] = subtype
          dd['guid'] = transferGuid(obj, subtype)
          obj.__class__(**dd)

    if hasattr(self, 'roles'):
      for obj in self.roles:
        if obj.isImplementation and not obj.otherRole:
          dd = obj._getCloningDict()
          for subtype in self.subtypes:
            dd['container'] = subtype
            dd['guid'] = transferGuid(obj, subtype)
            obj.__class__(**dd)

        else:
          raise MemopsError(
            "%s: attempt to inherit down non-implementation or two-way role" % (
              obj))

    for obj in self.operations:
      dd = obj._getCloningDict()
      target = obj.target
      for subtype in self.subtypes:

        dd['container'] = subtype
        dd['guid'] = transferGuid(obj, subtype)
        newObj = obj.__class__(**dd)

        if target:
          container = obj.container
          if target is container:
            newObj.target = subtype
          elif target is obj:
            newObj.target = newObj
          elif target.container is container:
            newObj.target = subtype.getElement(target.name)

        for par in obj.parameters:
          dd2 = par._getCloningDict()
          dd2['container'] = newObj
          dd2['guid'] = transferGuid(par, newObj)
          par.__class__(**dd2)

  def getElement(self, name):
    """ Get contained element called name
    Return None if nothing found
    
    Recursively search supertypes till you find element
    """

    ll = self.getAllSupertypes()

    for obj in ll:
      result = obj._MetaModelElement__elementDict.get(name)
      if result is not None:
        return result
    else:
      return None

  # synonym functions
  getAttribute = getElement
  getOperation = getElement

  def getAllAttributes(self):
    """ get contained atttributes, including those from supertypes
    """
    return self.getAllElements(clazz=MetaAttribute)

  def getAllOperations(self):
    """ get contained operations, including those from supertypes
    """
    return self.getAllElements(clazz=MetaOperation)

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    AbstractDataType.checkValid(self, complete=complete)

    # check code
    constructorCode = self._MetaModelElement__dataDict['constructorCodeStubs']
    if constructorCode:

      if self.isAbstract:
        raise MemopsError(
          "Abstract ComplexDataType %s has special constructor" % self)

      codeTags = metaConstants.codeStubTags
      for codeTag in constructorCode.keys():

        # check code tags
        if codeTag not in codeTags:
          raise MemopsError(
            "%s: Ilegal dcontructorCodeStubs tag %s" % (self, codeTag))

    # check uniqueness of Operations signatures:
    opCheckDict = {}
    for op in self.getAllOperations():
      tt = (op.opType, op.opSubType, op.target)
      if opCheckDict.get(tt):
        raise MemopsError(
          "%s: Class has another operation with opType,opSubType,target %s" % (
            self, tt))
      else:
        opCheckDict[tt] = True

    # Now check presence of an opSubType=None variant for all operations.
    for opType, opSubType, target in opCheckDict.keys():
      if opSubType is not None and not opCheckDict.get((opType, None, target)):
        raise MemopsError("""%s: opType,opSubType,target is %s.
MetaOperation with opSubType:None not found""" % (self, (opType, opSubType, target)))

    # check presence of non-overridden abstract attributes and operations
    if not self.isAbstract:
      for attr in self.getAllAttributes():
        if attr.isAbstract:
          raise MemopsError(
            "%s is not abstract but has abstract attr %s" % (self, attr.name))
      for op in self.getAllOperations():
        if op.isAbstract:
          raise MemopsError(
            "%s is not abstract but has abstract operation %s" % (
              self, op.name))


#############################################################################


class MetaPackage(MetaModelElement):
  """ abstract class for elements 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(MetaModelElement.parameterData)
  parameterData['container']['default'] = None
  parameterData.update(
    {'isRoot':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'isLeaf':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'isAbstract':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'visibility':{'type':'Token',
                   'enumeration':metaConstants.visibility_enumeration,
                   'default':metaConstants.public_visibility, 'isFixed':True, },
     'shortName':{'type':'Token', 'default':None, },
     'importedPackages':{'hicard':infinity, 'setterFunc':'setImportedPackages',
                         'default':[], },
     'accessedPackages':{'setterFunc':'unsettable', 'hicard':infinity, },
     'classes':{'type':'content', 'namelist':'_MetaPackage__classNames', },
     'dataTypes':{'type':'content',
                  'namelist':'_MetaPackage__dataTypeNames', },
     'dataObjTypes':{'type':'content',
                     'namelist':'_MetaPackage__dataObjTypeNames', },
     'constants':{'type':'content',
                  'namelist':'_MetaPackage__constantNames', },
     'exceptions':{'type':'content',
                   'namelist':'_MetaPackage__exceptionNames', },
     'containedPackages':{'type':'content',
                          'namelist':'_MetaPackage__containedPackageNames', },
     'topObjectClass':{'setterFunc':'unsettable', 'default':None}, })

  # allowed tagged values
  allowedTags = MetaModelElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaPackage'])

  def __init__(self, **params):

    from ccpncore.memops.metamodel import Util as metaUtil

    MetaModelElement.__init__(self, **params)

    # Set implementation attributes
    self.__containedPackageNames = []
    self.__classNames = []
    self.__dataObjTypeNames = []
    self.__dataTypeNames = []
    self.__exceptionNames = []
    self.__constantNames = []

    self.__dict__['topObjectClass'] = None

    self._MetaModelElement__dataDict['accessedPackages'] = []

    # finish link from container
    container = params.get('container')
    if container is not None:
      container.__containedPackageNames.append(params['name'])

    # check container circularity
    metaUtil.checkLinkCircularity(self, 'container')

  def setImportedPackages(self, importedPackages):
    """ setter for link importedPackages
    """

    # first clean up
    ll = self._MetaModelElement__dataDict.get('importedPackages')
    if ll:
      for pp in ll:
        pp._MetaModelElement__dataDict['accessedPackages'].remove(self)

    # then reset internal list
    dd = self._MetaModelElement__dataDict
    if dd.get('importedPackages') is None:
      dd['importedPackages'] = []

    # now put in data
    for importedPackage in importedPackages:
      self.addImportedPackage(importedPackage)

  def addImportedPackage(self, importedPackage):
    """ Add imported package (two-way link)
    """

    # check parameter type
    if not isinstance(importedPackage, MetaPackage):
      raise MemopsError(
        "%s: addImportedPackage parameter should be MetaPackage, was %s" % (
          self, importedPackage))

    importedPackages = self._MetaModelElement__dataDict['importedPackages']
    accessedPackages = importedPackage._MetaModelElement__dataDict[
      'accessedPackages']

    if importedPackage in importedPackages:
      raise MemopsError("%s: addImportedPackage, %s already imported" % (
        self, importedPackage))

    if self in accessedPackages:
      raise MemopsError("%s: addImportedPackage, %s already accesssed" % (
        self, importedPackage))

    # make change
    importedPackages.append(importedPackage)
    accessedPackages.append(self)

  def removeImportedPackage(self, importedPackage):
    """Remove existing importedPackage
    """

    importedPackages = self._MetaModelElement__dataDict['importedPackages']

    if importedPackage in importedPackages:
      accessedPackages = importedPackage._MetaModelElement__dataDict[
        'accessedPackages']
      accessedPackages.remove(self)

    else:
      raise MemopsError("%s: removeImportedPackage, %s was not imported" % (
        self, importedPackage))

  def getElement(self, name):
    """ Get contained element called name
    Return None if nothing found
    """
    return self._MetaModelElement__elementDict.get(name)

  # synonym functions
  getClass = getElement
  getConstant = getElement
  getContainedPackage = getElement
  getDataObjType = getElement
  getDataType = getElement
  getException = getElement

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    from ccpncore.memops.metamodel import Util as metaUtil

    importedPackages = self._MetaModelElement__dataDict['importedPackages']
    accessedPackages = self._MetaModelElement__dataDict['accessedPackages']

    # check containment circularity
    metaUtil.checkLinkCircularity(self, 'container')

    # check two-way import/access link
    for pp in importedPackages:
      if pp._MetaModelElement__dataDict['accessedPackages'].count(self) != 1:
        raise MemopsError(
          "Two-way import/access link %s-%s broken. Bug (1)?" % (self, pp))

    for pp in accessedPackages:
      if pp._MetaModelElement__dataDict['importedPackages'].count(self) != 1:
        raise MemopsError(
          "Two-way import/access link %s-%s broken. Bug (2)?" % (self, pp))

    # check for 'None'; container
    if self.container is None:
      # root package. Check name
      if self.name != metaConstants.rootPackageName:
        raise MemopsError("Root package named %s, must be %s" % (
          self.name, metaConstants.rootPackageName))

      # initialise guid uniqueness check
      MetaModelElement.guidDict = {}

    MetaModelElement.checkValid(self, complete=complete)

    if self.container is None:
      # Root package clean up after guid uniqueness check
      MetaModelElement.guidDict = None

    # check mandatory packages and get implementation package
    RootPackage = self.topPackage()
    ModellingPackage = RootPackage.getElement(
      metaConstants.modellingPackageName)
    if not isinstance(ModellingPackage, MetaPackage):
      raise MemopsError(
        "No package %s found" % metaConstants.modellingPackageName)

    Impl = ModellingPackage.getElement(metaConstants.implementationPackageName)

    if not isinstance(Impl, MetaPackage):
      raise MemopsError("No Implementation package found")

    if self is Impl:
      if self._MetaModelElement__dataDict['importedPackages']:
        raise MemopsError(
          "Implementation package %s may not import other packages" % self.qualifiedName())
      if self.__containedPackageNames:
        raise MemopsError(
          "Implementation package '%s' must contain no other packages" % metaConstants.implementationPackageName)

      # check Implementation classes used elsewhere
      tag = metaConstants.baseDataTypeObjName
      cc = self.getElement(tag)
      if not cc or not isinstance(cc, MetaDataObjType):
        raise MemopsError(
          "Implementation package '%s' does not contain MetaDataObjType %s" % (
            metaConstants.implementationPackageName, tag))
      for tag in metaConstants.implementationClassNames:
        cc = self.getElement(tag)
        if not cc or not isinstance(cc, MetaClass):
          raise MemopsError(
            "Implementation package '%s' does not contain class %s" % (
              metaConstants.implementationPackageName, tag))

      # check special roles:
      cc = self.getElement(metaConstants.dataRootName)
      for tag2 in (
        metaConstants.repositoryRole, metaConstants.packageLocatorRole):
        if not isinstance(cc.getElement(tag2), MetaRole):
          raise MemopsError(
            "MemopsRoot class '%s' does not contain role %s" % (cc, tag2))

    # check container packages:
    if self.__containedPackageNames:

      if accessedPackages or importedPackages:
        raise MemopsError(
          "%s: Packages containing other packages can not import or access" % (
            self,))

      if (
                self.__classNames or self.__dataObjTypeNames or self.__dataTypeNames or self.__exceptionNames or self.__constantNames):
        raise MemopsError(
          "%s: Packages containing other packages can contain nothing else" % (
            self,))

      # check shortName
      if self.shortName is not None:
        raise MemopsError("%s: branch package has shortName" % self)

      # name style check:
      if (self.name[
            0] not in metaConstants.lowercase and self.container is not None):
        print("WARNING, name of %s does not start with lower case" % self)

    elif (
              self.__classNames or self.__dataObjTypeNames or self.__dataTypeNames or self.__exceptionNames or self.__constantNames):
      # leaf package - NB package could be empty, hence the elif

      # check shortName
      if self.shortName is None:
        raise MemopsError("%s: leaf package lacks a shortName" % (self,))

      if len(self.shortName) > metaConstants.maxShortNameLength:
        raise MemopsError("%s: shortName %s longer than %s characters" % (
          self, self.shortName, metaConstants.maxShortNameLength))

      # check TopObject 
      hasNonAbstract = False
      topObjects = []
      TopObjClass = Impl.getElement(metaConstants.topObjClassName)
      for clazz in self.classes:
        if not clazz.isAbstract:
          hasNonAbstract = True

        if clazz.supertype is TopObjClass:
          topObjects.append(clazz)

      if self is not Impl and hasNonAbstract and not topObjects:
        raise MemopsError(
          "%s: has non-abstract classes but lacks TopObject" % (self, ))

      if len(topObjects) > 1:
        raise MemopsError(
          "%s: has several TopObjects: %s" % (self, topObjects))

      # check package importing
      if self is not Impl:
        ll = self.importedPackages
        if Impl not in ll:
          raise MemopsError(
            "package %s does not import the Implementation package" % self)

      # name style check:
      if self.name[0] not in metaConstants.uppercase:
        print("WARNING, name of %s does not start with upper case" % self)

    if self is RootPackage:
      # special checks for root package, and for entire model

      # check for cycles in import/access for packages. 
      # and in supertypes/subtypes for classes
      # Done centrally for speed
      leafPackages = []
      classes = []
      dataTypes = []
      dataObjTypes = []
      exceptions = []
      ll = [self]

      for pp in ll:
        ll2 = pp.containedPackages
        if ll2:
          ll.extend(ll2)
        else:
          leafPackages.append(pp)

        classes.extend(pp.classes)
        dataTypes.extend(pp.dataTypes)
        dataObjTypes.extend(pp.dataObjTypes)
        exceptions.extend(pp.exceptions)

      metaUtil.topologicalSortSubgraph(leafPackages, 'importedPackages')
      for ll in (classes, dataTypes, dataObjTypes, exceptions):
        metaUtil.topologicalSortSubgraph(ll, 'supertypes')

      # checks for diamond multiple inheritance and inheritance order
      for ss in (metaConstants.baseClassName, metaConstants.baseDataTypeObjName):
        dd = {}
        ll = [Impl.getElement(ss)]
        for obj in ll:

          if dd.get(obj):
            raise MemopsError("%s inherits twice from %s" % (obj, ss))

          dd[obj] = True
          subtypes = obj.subtypes
          tmp = [xx for xx in subtypes if
                 xx._MetaModelElement__dataDict['supertypes'][0] is not obj]
          if tmp:
            raise MemopsError(
              "%s: classes should have %s as first supertype" % (tmp, obj))

          ll.extend(subtypes)

# must be done here after end of class definition
MetaPackage.parameterData['importedPackages']['type'] = MetaPackage
MetaPackage.parameterData['accessedPackages']['type'] = MetaPackage
MetaPackage.parameterData['container']['type'] = MetaPackage

#############################################################################

class MetaClass(ComplexDataType):
  """ class for normal Classes
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ComplexDataType.parameterData)
  parameterData['container']['type'] = MetaPackage
  parameterData.update(
    {'isSingleton':{'type':'Boolean', 'default':False, 'isFixed':True, },
     'partitionsChildren':{'type':'Boolean', 'default':False, },
     'isDerived':{'type':'Boolean', 'default':False, },
     'keyNames':{'type':StringType, 'hicard':infinity,
                 'getterFunc':'getKeyNames', 'default':[], },
     'destructorCodeStubs':{'type':'StringDict', 'default':{}, },
     'postDestructorCodeStubs':{'type':'StringDict', 'default':{}, },
     'roles':{'type':'content', 'namelist':'_MetaClass__roleNames', },
     'parentRole':{'getterFunc':'getParentRole', 'setterFunc':'unsettable',
                   'default':None}, })

  # allowed tagged values
  allowedTags = ComplexDataType.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaClass'])

  def __init__(self, **params):

    ComplexDataType.__init__(self, **params)

    # Set implementation attributes
    self.__roleNames = []

    # finish link from container
    params['container']._MetaPackage__classNames.append(params['name'])

    # topObjectClass - special case of Implementation package
    if (params.get('name') == metaConstants.dataRootName and params[
      'container'].name == metaConstants.implementationPackageName):
      params['container'].__dict__['topObjectClass'] = self

  def addKeyName(self, name):
    """ add mainkey name to list
    """

    keyNames = self._MetaModelElement__dataDict['keyNames']

    if name in keyNames:
      raise MemopsError("%s keyName %s is already in list" % (self, name))

    elif not keyNames and self.getKeyNames():
      raise MemopsError("%s keyNames is defined in superclass" % (self, ))

    else:
      keyNames.append(name)

  def removeKeyName(self, name):
    """ remove mainkey name from list
    """

    keyNames = self._MetaModelElement__dataDict['keyNames']

    if not keyNames and self.getKeyNames():
      raise MemopsError("%s keyNames is defined in superclass" % (self, ))

    elif name not in keyNames:
      raise MemopsError("%s keyName %s is not in list" % (self, name))

    else:
      keyNames.remove(name)

  def getKeyNames(self):
    """ get keyNames list, from class or a superclass
    """

    for obj in self.getAllSupertypes():
      # NB ComplexDataType - the topmost superclass has no 'keyNames' attribute
      result = obj._MetaModelElement__dataDict.get('keyNames', [])
      if result:
        break

    return result[:]

  def addDestructorCodeStub(self, tag, value):
    """ Add destructorCodeStub
    """

    if type(tag) != StringType:
      raise MemopsError("%s codeStub tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s codeStub %s value %s is not a string" % (self, tag, value))

    if tag not in metaConstants.codeStubTags:
      raise MemopsError("%s : unsupported codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['destructorCodeStubs'][tag] = value

  def removeDestructorCodeStub(self, tag):
    """Remove existing DestructorCodeStub
    """

    if self._MetaModelElement__dataDict['destructorCodeStubs'].get(tag,
                                                                   sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['destructorCodeStubs'][tag]
    else:
      raise MemopsError("%s has no DestructorCodeStub %s " % (self, tag))

  def addPostDestructorCodeStub(self, tag, value):
    """ Add destructorCodeStub
    """

    if type(tag) != StringType:
      raise MemopsError("%s codeStub tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s codeStub %s value %s is not a string" % (self, tag, value))

    if metaConstants.codeStubTags.get(tag, sentinel) is sentinel:
      raise MemopsError("%s : unsupported codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['postDestructorCodeStubs'][tag] = value

  def removePostDestructorCodeStub(self, tag):
    """Remove existing DestructorCodeStub
    """

    if self._MetaModelElement__dataDict['postDestructorCodeStubs'].get(
      sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['postDestructorCodeStubs'][tag]
    else:
      raise MemopsError("%s has no postDestructorCodeStub %s " % (self, tag))

  getRole = ComplexDataType.getElement

  def delete(self):
    """ remove links to other MetaElements, check that delete is legal.
    Intended for elements specific to some implementation
    NB delete does not cascade.
    """

    # check for presence of roles
    for role in self.getAllRoles():
      if role.isImplementation and role.otherRole is None:
        # allowed
        pass
      else:
        raise MemopsError(
          "Attempt to delete %s, class has non-implementation roles" % self)

    # clear supertype/subtype links
    for obj in self.subtypes:
      obj.removeSupertype(self)
    for obj in self.supertypes:
      self.removeSupertype(obj)

    # clear container links
    container = self.container
    container._MetaPackage__classNames.remove(self.name)
    del container._MetaModelElement__elementDict[self.name]

    #remove container from contents, 
    #to ensure you get an error message irf they are picked up
    for obj in self._MetaModelElement__elementDict.values():
      obj.__dict__['container'] = None

  def getAllRoles(self):
    """ get contained roles, including those from supertypes
    """
    return self.getAllElements(clazz=MetaRole)

  def getParentRole(self):
    """ get class on other side of parent role
    """

    for obj in self.getAllSupertypes():
      result = obj.__dict__.get('parentRole')
      if result is not None:
        break
    #
    return result

  def getParentClass(self):
    """ get class on other side of parent role
    """

    for obj in self.getAllSupertypes():
      parentRole = obj.__dict__.get('parentRole')
      if parentRole is not None:
        return parentRole.valueType
    #
    return None

  def getChildRoles(self):
    """ get child roles
    """
    return [x for x in self.getAllRoles() if
            x.hierarchy == metaConstants.child_hierarchy]

  def getClassElements(self):
    """ get roles and attributes
    """
    return self.attributes + self.roles

  def getAllClassElements(self):
    """ get all roles and attributes, included inherited ones
    """
    return self.getAllAttributes() + self.getAllRoles()

  def getSingleClassElements(self):
    """ get roles and attributes with hicard == 1
    """
    return [x for x in (self.attributes + self.roles) if x.hicard == 1]

  def getAllSingleClassElements(self):
    """ get roles and attributes with hicard == 1, included inherited ones
    """
    return [x for x in (self.getAllAttributes() + self.getAllRoles()) if
            x.hicard == 1]

  def getMultipleClassElements(self):
    """ get roles and attributes with hicard != 1
    """
    return [x for x in (self.getAttributes() + self.getRoles()) if
            x.hicard != 1]

  def getAllMultipleClassElements(self):
    """ get all roles and attributes with hicard != 1, included inherited ones
    """
    return [x for x in (self.getAllAttributes() + self.getAllRoles()) if
            x.hicard != 1]

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    # get constant objects
    RootPackage = self.topPackage()
    ModellingPackage = RootPackage.getElement(
      metaConstants.modellingPackageName)
    Impl = ModellingPackage.getElement(metaConstants.implementationPackageName)
    Base = Impl.getElement(metaConstants.baseClassName)
    DataRoot = Impl.getElement(metaConstants.dataRootName)
    DataObject = Impl.getElement(metaConstants.dataObjClassName)
    ImplObject = Impl.getElement(metaConstants.implObjClassName)
    TopObject = Impl.getElement(metaConstants.topObjClassName)

    ComplexDataType.checkValid(self, complete=complete)

    # check derived classes
    if self.isDerived:
      keyNames = self.getKeyNames()
      for x in self.attributes:
        if not x.isDerived or x.isImplementation or x.name in keyNames:
          raise MemopsError(
            "Element %s of derived class %s neither derived, implementation nor a key" % (
              x.name, self))
      for role in self.roles:
        if not (
                role.isDerived or role.isImplementation or role.name in keyNames or role is self.parentRole):
          raise MemopsError(
            "Element %s of derived class %s neither derived, implementation nor a key" % (
              role.name, self))
        otherRole = role.otherRole

        if otherRole:
          # check that links to derived class have manual getters
          for op in otherRole.container.getAllOperations():
            if (
                    op.target is otherRole and op.opType == 'get' and not op.isImplicit):
              break
          else:
            raise MemopsError(
              "Link %s to derived class %s must have manually defined 'get' function" % (
                otherRole, self))

      if not self.isAbstract:
        parentClass = self.parentRole.valueType
        factoryFunction = metaUtil.getOperation(self, 'new',
                                                inClass=parentClass)
        if not factoryFunction or factoryFunction.isImplicit:
          raise MemopsError(
            "Derived class %s must have manually defined factory function" % self)

    # check keyNames
    for tag in self.getKeyNames():
      keyElement = self.getElement(tag)
      if keyElement is None:
        raise MemopsError(
          "%s keyName %s is not an element in the class" % (self, tag))
      if keyElement.changeability != metaConstants.frozen:
        raise MemopsError("%s key %s is changeable" % (self, tag))
      if keyElement.isDerived:
        # in order to speed up checking and facilitate database impl.
        raise MemopsError("%s key %s is derived" % (self, tag))
      if keyElement.isImplementation:
        # in order to speed up checking and facilitate database impl.
        raise MemopsError("%s key %s is Implementation element" % (self, tag))
      if keyElement.hicard != keyElement.locard:
        raise MemopsError(
          "%s key %s does not have n..n cardinality" % (self, tag))
      if isinstance(keyElement, MetaRole):
        if not self.canAccess(keyElement.valueType):
          raise MemopsError(
            "%s: key %s is link into nonacessible package" % (self, tag))

        if (
              TopObject in self.getAllSupertypes() and not TopObject in keyElement.valueType.getAllSupertypes()):
          raise MemopsError(
            "%s: key %s is link to non-topObject" % (self, tag))

    # check name length
    if len(self.name) > metaConstants.maxClassNameLength:
      raise MemopsError("%s: name %s longer than %s characters" % (
        self, self.name, metaConstants.maxClassNameLength))

    # check that child class names do not conflict with each other
    dd = {}
    for role in self.getAllRoles():
      if role.hierarchy == metaConstants.child_hierarchy:
        for cc in role.valueType.getNonAbstractSubtypes():

          cname = cc.name
          val = dd.get(cname, sentinel)

          if val is not sentinel:
            raise MemopsError(
              "%s has two child classes named %s;\n links are %s and %s" % (
                self, cname, role, val))

          else:
            dd[cname] = role

    # get parentRole
    parentRole = self.parentRole
    if parentRole is not None:

      # set parentClass
      parentClass = parentRole.valueType

      if parentRole.otherRole is None:
        if not parentRole.isAbstract:
          raise MemopsError(
            "%s: non-Abstract class with one-way parentRole" % self)
      elif parentRole.otherRole.hicard == 1:
        # check for only children with key.
        if self.keyNames:
          raise MemopsError(
            "%s: only child has keyNames: %s" % (self, self.keyNames))
      elif not parentRole.isAbstract and not self.keyNames:
        # check that classes with parentRole also have mainKey
        raise MemopsError("%s: class with parentRole lacks keyNames" % self)

    else:
      parentClass = None

    # remove very top class as that is a DataObjType
    allSupertypes = [x for x in self.getAllSupertypes() if
                     x.name != 'ComplexDataType']

    if Base not in allSupertypes and not self.isAbstract:
      raise MemopsError(
        "%s: non-abstract class is not subtype of %s" % (self, Base))

    if self.container is Impl:
      # Implementation package 

      if ImplObject not in allSupertypes and not self.isAbstract:
        raise MemopsError(
          "%s: non-abstract Implementation class is not subtype of %s" % (
            self, ImplObject))

      if parentRole is not None and parentClass is not DataRoot:
        raise MemopsError(
          "%s: has incorrect parentClass %s" % (self, parentClass))

      if self is DataRoot:
        # DataRoot

        if not self.partitionsChildren:
          raise MemopsError(
            "%s: %s does not have partitionsChildren True" % (self, DataRoot))
        if parentRole is not None:
          raise MemopsError("%s: subType of %s has parentRole %s" % (
            self, DataRoot, parentRole))
        if self.container.topObjectClass is not self:
          raise MemopsError(
            "%s has topObjectClass %s, should be %s" % (Impl, DataRoot, self))

      if self is TopObject:
        if not self.partitionsChildren:
          raise MemopsError(
            "%s: %s does not have partitionsChildren True" % (self, TopObject))

    else:

      if DataObject not in allSupertypes:
        if not self.isAbstract:
          raise MemopsError(
            "%s: non-abstract class is not subtype of %s" % (self, DataObject))

        if [x for x in self.roles if x.otherRole and not x.implementation]:
          raise MemopsError(
            "%s: class with non-implementation or two-way role is not subtype of %s" % (
              self, DataObject))

      if TopObject in allSupertypes:
        # TopObject

        if not parentRole:
          raise MemopsError("%s: TopObject has no parentRole" % (self,))

        if parentClass is not DataRoot:
          raise MemopsError(
            "%s: TopObject has incorrect parentClass %s, should be %s" % (
              self, parentClass, DataRoot))

        if parentRole.otherRole.hicard == 1:
          raise MemopsError("%s: TopObject is is an only child" % (self,))

        for role in DataRoot.getAllRoles():
          # check existence of currentRole
          if role.valueType in allSupertypes and role.name.startswith(
            'current'):
            break
        else:
          raise MemopsError(
            "%s: TopObject is not pointed to by a 'current' link" % (self, ))

      else:
        # Normal class

        if parentRole is not None:
          if parentClass.container is not self.container:
            raise MemopsError(
              "%s: has parentClass %s from different package" % (
                self, parentClass))

    # check that links are not inherited across package boundaries
    # except for certain one-way links
    if self is not DataObject:
      if [x for x in self.roles if
          x.otherRole or not x.isAbstract and not x.isDerived and not x.isImplementation]:
        pp = self.container
        ll = [x for x in self.getAllSubtypes() if x.container is not pp]
        if ll:
          raise MemopsError(
            "%s: has both roles and out-of-package subclasses:\n%s" % (
              self, ll))

    # check that non-abstract class has parentRole and mainkey
    if not self.isAbstract and DataRoot not in allSupertypes:
      if parentRole is None:
        raise MemopsError("%s: non-abstract class lacks parentRole" % (self,))

      if not self.keyNames and parentRole.otherRole.hicard != 1:
        raise MemopsError(
          "%s: non-abstract class lacks keyNames and is not only child" % (
            self,))

    # check partitionsChildren behaves correctly
    # NB must not be checked for ComplexDataType class
    if not self.partitionsChildren:
      ll = [x for x in allSupertypes if x.partitionsChildren]
      if ll:
        raise MemopsError(
          "%s does not partition children, but its superclass(es) do:\n%s" % (
            self, ll))

    # check parent role cyclicity
    sup = low = self
    while sup is not None:
      low = sup
      sup = low.getParentClass()
      if sup is self:
        raise MemopsError(
          "%s is (indirectly) its own parentClass" % self)

    # All non-abstract classes must be under root
    if DataRoot not in allSupertypes:
      if not self.isAbstract and low is not DataRoot:
        raise MemopsError("%s does not descend from %s" % (self, DataRoot))

    # check presence of non-overridden abstract roles
    if not self.isAbstract:
      for role in self.getAllRoles():
        if role.isAbstract:
          raise MemopsError(
            "%s is not abstract but has abstract role %s" % (self, role.name))

    # check code
    for tag in ('destructorCodeStubs', 'postDestructorCodeStubs'):
      destructorCode = self._MetaModelElement__dataDict[tag]
      if destructorCode:

        if self.isAbstract:
          raise MemopsError(
            "Abstract class %s has special destructor" % self)

        codeTags = metaConstants.codeStubTags
        for codeTag in destructorCode.keys():

          # check code tags
          if codeTag not in codeTags:
            raise MemopsError("%s: Illegal %s tag %s" % (self, tag, codeTag))

    # check special 'serial' attribute
    serial = self.getElement(metaConstants.serial_attribute)
    if serial is not None:
      if not isinstance(serial, MetaAttribute):
        raise MemopsError(
          "%s - non-MetaAttribute named %s" % (serial, serial.name))

      if (
                not serial.isAutomatic or serial.hicard != 1 or serial.locard != 1 or serial.changeability != metaConstants.frozen or serial.valueType.name != 'Int' ):
        raise MemopsError("""%s:
'%s' attribute must be Int, automatic, non-changeable and 1..1""" % (
          serial, serial.name))

#
MetaClass.parameterData['supertype']['type'] = MetaClass
MetaClass.parameterData['supertypes']['type'] = MetaClass
MetaClass.parameterData['subtypes']['type'] = MetaClass
MetaPackage.parameterData['topObjectClass']['type'] = MetaClass

#############################################################################

class MetaDataObjType(ComplexDataType):
  """ class for complex data objects
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ComplexDataType.parameterData)
  parameterData['container']['type'] = MetaPackage
  parameterData['isChangeable'] = {'type':IntType,
                                   'getterFunc':'getIsChangeable', }

  # allowed tagged values
  allowedTags = ComplexDataType.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaDataObjType'])

  def __init__(self, **params):

    ComplexDataType.__init__(self, **params)

    # finish link from container
    params['container']._MetaPackage__dataObjTypeNames.append(params['name'])

  def getIsChangeable(self):
    for attr in self.getAllAttributes():
      if attr.changeability != metaConstants.frozen:
        return True
    #
    return False

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    BaseDataType = self.metaObjFromQualName('.'.join(
      [metaConstants.modellingPackageName,
       metaConstants.implementationPackageName,
       metaConstants.baseDataTypeObjName]))

    ComplexDataType.checkValid(self, complete=complete)

    # check changeability
    if self.isChangeable:
      raise MemopsError("""%s has changeable attribute - 
       Changeable MetaDataObjTypes not implemented""" % self)

    # check inheritance across package boundaries 
    if not self.isAbstract:
      pp = self.container
      ll = [x for x in self.getAllSubtypes() if x.container is not pp]
      if ll:
        raise MemopsError("%s has out-of-package subtypes %s" % (self, ll))

    # check supertypes
    if BaseDataType not in self.getAllSupertypes():
      if not self.isAbstract:
        raise MemopsError(
          "%s: non-abstract DataObjType is not subtype of %s" % (
            self, BaseDataType))

#
MetaDataObjType.parameterData['supertype']['type'] = MetaDataObjType
MetaDataObjType.parameterData['supertypes']['type'] = MetaDataObjType
MetaDataObjType.parameterData['subtypes']['type'] = MetaDataObjType

#############################################################################

class MetaDataType(AbstractDataType):
  """ class for data types
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(AbstractDataType.parameterData)
  parameterData['container']['type'] = MetaPackage
  parameterData.update({'isOpen':{'type':'Boolean', 'default':True, },
                        'enumeration':{'hicard':infinity, 'default':[], },
                        'length':{'type':IntType, 'default':None, },
                        'typeCodes':{'type':'StringDict', 'default':{}, }, })

  # allowed tagged values
  allowedTags = AbstractDataType.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaDataType'])

  def __init__(self, **params):

    AbstractDataType.__init__(self, **params)

    # finish link from container
    params['container']._MetaPackage__dataTypeNames.append(params['name'])

  def addTypeCode(self, tag, value):
    """ Add typeCode
    """

    if type(tag) != StringType:
      raise MemopsError("%s typeCode tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s typeCode %s value %s is not a string" % (self, tag, value))

    if tag not in metaConstants.codeStubTags:
      raise MemopsError("%s : unsupported codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['typeCodes'][tag] = value

  def removeTypeCode(self, tag):
    """Remove existing TypeCode
    """

    if self._MetaModelElement__dataDict['typeCodes'].get(tag,
                                                         sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['typeCodes'][tag]
    else:
      raise MemopsError("%s has no typeCode %s " % (self, tag))

  def isValid(self, value):
    """ This function is needed because value constants
    must be checked for validity as part of the MetaModel.
    NB for enumerations values must be added to the enumeration
    before the check works.
    """

    # check value in enumeration
    if not self.isOpen:
      # closed enumeration
      if value not in self.enumeration:
        return False

    # check special check function - or just correct PythonType
    baseType = getattr(memopsConstants.baseDataTypeModule,
                       self.typeCodes['python'])
    if hasattr(baseType, 'isValid'):
      if not getattr(baseType, 'isValid')(value):
        return False
    else:
      pythonType = baseType.PythonType
      if not isinstance(value, pythonType):
        return False

    # check length
    if self.length:
      if len(value) > self.length:
        return False

    try:
      for constraint in self._ConstrainedElement__constraints.values():

        code = constraint.codeStubs.get('python')

        import re

        containsWhitespace = re.compile('\s').search
        containsNonAlphanumeric = re.compile('[^a-zA-Z0-9_]').search
        dd = {'value':value, 'True':True, 'False':False, 'string':string,
              'containsWhitespace':containsWhitespace,
              'containsNonAlphanumeric':containsNonAlphanumeric, }

        if code is None:
          isValid = True
        elif code.find('isValid') == -1:
          isValid = eval(code, dd, dd)
        else:
          # NBNB TBD: check with Rasmus
          #exec code in dd
          exec(code, dd)
          isValid = dd['isValid']

        if not isValid:
          return False

    except:
      print("Error checking constraints in %s" % self.qualifiedName())
      raise

    #
    return True

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    AbstractDataType.checkValid(self, complete=complete)

    enumeration = self._MetaModelElement__dataDict.get('enumeration')

    if not self.isOpen and not enumeration:
      raise MemopsError(
        "%s isOpen set to %s for non-enumeration" % (self, self.isOpen))

    for ee in enumeration:
      if not self.isValid(ee):
        raise MemopsError(
          "%s : Illegal enumeration value %s" % (self.qualifiedName(), ee))

    # check single inheritance
    if len(self.supertypes) > 1:
      raise MemopsError("%s has more than one supertype" % self)


#
MetaDataType.parameterData['supertype']['type'] = MetaDataType
MetaDataType.parameterData['supertypes']['type'] = MetaDataType
MetaDataType.parameterData['subtypes']['type'] = MetaDataType

#############################################################################

class MetaException(HasParameters, HasSupertype):
  """ class for exceptions 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(HasParameters.parameterData)
  parameterData['container']['type'] = MetaPackage
  parameterData.update({
    'scope':{'type':'Token', 'enumeration':metaConstants.scope_enumeration,
             'default':metaConstants.instance_level, 'isFixed':True, },
    'supertype':{'setterFunc':'setSupertype',
                 'default':None, }, 'supertypes':{'hicard':infinity, },
    'subtypes':{'setterFunc':'unsettable', 'hicard':infinity, }, })

  # allowed tagged values
  allowedTags = HasParameters.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaException'])

  def __init__(self, **params):

    HasParameters.__init__(self, **params)

    # implementation attributes
    dd = self._MetaModelElement__dataDict
    if dd.get('subtypes') is None:
      dd['subtypes'] = []
    if dd.get('supertypes') is None:
      dd['supertypes'] = []

    # finish link from container
    params['container']._MetaPackage__exceptionNames.append(params['name'])

  getElement = ComplexDataType.getElement

  getParameter = getElement

  def getAllParameters(self):

    return self.getAllElements(clazz=MetaParameter)


  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    HasParameters.checkValid(self, complete=complete)

    parameters = self.parameters

    # check single inheritance
    supertypes = self.supertypes
    if len(supertypes) > 1:
      raise MemopsError("%s has more than one supertype" % self)

    if supertypes:
      supertype = supertypes[0]

      # package access check
      if not self.canAccess(supertype):
        raise MemopsError(
          "%s - cannot access supertype %s" % (self, supertype))

      # check two-way link
      if supertype._MetaModelElement__dataDict['subtypes'].count(self) != 1:
        raise MemopsError(
          "Two-way supertype link %s-%s is broken. Bug (3)?" % (
            supertype, self))

    # name style
    if self.name[0] not in metaConstants.uppercase:
      print("WARNING, name of %s does not start with upper case" % self)

    # check two-way link
    for obj in self._MetaModelElement__dataDict['subtypes']:
      if obj.supertype is not self:
        raise MemopsError(
          "Two-way supertype link %s-%s is broken. Bug (4)?" % (self, obj))

    # checks on Parameters.
    if not self.isImplicit:

      # return parameters
      pars = [x for x in parameters if
              x.direction == metaConstants.return_direction]
      if len(pars) > 1:
        raise MemopsError("%s: more than one return parameter : %s" % (
          self, [x.name for x in pars]))

        # must be set here, after the class definition


MetaException.parameterData['supertype']['type'] = MetaException
MetaException.parameterData['supertypes']['type'] = MetaException
MetaException.parameterData['subtypes']['type'] = MetaException

#############################################################################

class MetaOperation(HasParameters):
  """ class for operations 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(HasParameters.parameterData)
  parameterData['container']['type'] = ComplexDataType
  parameterData.update({
    'scope':{'type':'Token', 'enumeration':metaConstants.scope_enumeration,
             'default':metaConstants.instance_level, },
    'codeStubs':{'type':'StringDict', 'default':{}, },
    'exceptions':{'type':MetaException, 'hicard':infinity, 'default':[], },
    'isQuery':{'type':'Boolean', },
    'isAbstract':{'type':'Boolean', 'default':False, },
    'opType':{'type':'Token',
              'enumeration':tuple(OpTypes.operationData.keys()), },
    'opSubType':{'type':'Token', 'default':None, },
    'target':{'type':MetaModelElement}, })

  # allowed tagged values
  allowedTags = HasParameters.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaOperation'])

  def __init__(self, **params):

    HasParameters.__init__(self, **params)

    # implementation attributes
    self._MetaModelElement__dataDict['exceptions'] = []

    # finish link from container
    params['container']._ComplexDataType__operationNames.append(params['name'])


  def addCodeStub(self, tag, value):
    """ Add codeStub
    """

    if type(tag) != StringType:
      raise MemopsError("%s codeStub tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s codeStub %s value %s is not a string" % (self, tag, value))

    if tag not in metaConstants.codeStubTags:
      raise MemopsError("%s : unsupported  codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['codeStubs'][tag] = value

  def removeConstructorCodeStub(self, tag):
    """Remove existing codeStub
    """

    if self._MetaModelElement__dataDict['codeStubs'].get(tag,
                                                         sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['codeStubs'][tag]
    else:
      raise MemopsError("%s has no codeStub %s " % (self, tag))

  def getElement(self, name):
    """ Get contained element called name
    Return None if nothing found
    """
    return self._MetaModelElement__elementDict.get(name)

  getParameter = getElement

  def addException(self, value):
    """ Add exception to exceptions list
    """

    exceptions = self._MetaModelElement__dataDict['exceptions']

    if not value.isinstance(MetaException):
      raise MemopsError("%s - %s is not a MetaException" % (self, value))

    elif value in exceptions:
      raise MemopsError("%s - exception %s is already in list" % (self, value))

    exceptions.append(value)

  def removeException(self, value):
    """Remove existing exception
    """

    exceptions = self._MetaModelElement__dataDict['exceptions']

    if value in exceptions:
      exceptions.remove(value)

    else:
      raise MemopsError("%s - has no exception %s" % (self, value))

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    # NBNB Some things are checked only in ModelAdapt
    # ops with targetTag != masterOp must replace an autogenerated operation 
    # and must conform to the rules for this operation

    IC = metaConstants

    implPackage = self.metaObjFromQualName(
      '.'.join([IC.modellingPackageName, IC.implementationPackageName]))
    if isinstance(self.container, MetaClass):
      Base = implPackage.getElement(IC.baseClassName)
    else:
      Base = implPackage.getElement(IC.baseDataTypeObjName)

    HasParameters.checkValid(self, complete=complete)

    parameters = self.parameters

    # check code
    codeTags = metaConstants.codeStubTags
    for codeTag in self._MetaModelElement__dataDict['codeStubs'].keys():

      # check code tags
      if codeTag not in codeTags:
        raise MemopsError("%s: Ilegal codeStub tag %s" % (self, codeTag))

    # exception package access check
    for exception in self._MetaModelElement__dataDict['exceptions']:
      if not self.canAccess(exception):
        raise MemopsError(
          "%s - cannot access exception %s" % (self, exception))

    # name style
    if not self.isImplicit and self.name[0] not in metaConstants.lowercase:
      print("WARNING, name of %s does not start with lower case" % self)

    # opType dependent checks
    # check valid opType
    opType = self.opType
    opTypeInfo = OpTypes.operationData.get(opType)
    if opTypeInfo is None:
      raise MemopsError("%s: Illegal optype %s" % (self, opType))

    targetTag = opTypeInfo['targetTag']

    # check isQuery fits opType
    if opTypeInfo['group'] != 'other':
      # Operations with isQuery are allowed on deleted objects.
      # That was the deciding factor in letting isQuery be optional
      # for 'other' operations
      if ((opTypeInfo['group'] not in ('query', 'otherQuery')) != (
        not self.isQuery)):
        # Queries *must* be isQuery. Other opTypes may not, 'other' may choose
        raise MemopsError("%s has group == %s but isQuery == %s" % (
          self, opTypeInfo['group'], self.isQuery))

    # check for explicit parameters
    if targetTag != 'masterOp':
      # only masterOp target is allowed explicit parameters
      for par in parameters:
        if not par.isImplicit:
          raise MemopsError("%s with opType %s has explicit parameter %s" % (
            self, self.opType, par))

    # check target
    target = self.target

    # check target type
    targetTypes = {'ClassElement':ClassElement, 'MetaRole':MetaRole,
                   'MetaAttribute':MetaAttribute, 'ChildClass':MetaClass,
                   'container':ComplexDataType, 'masterOp':MetaOperation, }
    if not isinstance(target, targetTypes[targetTag]):
      raise MemopsError("%s: target %s does not fit target type %s" % (
        self, target, targetTag))

    # type specific checks
    if targetTag == 'container':
      # container target
      if target is not self.container:
        raise MemopsError("%s: target %s differs from op container %s" % (
          self, target, self.container))

    elif targetTag == 'masterOp':
      # masterOp target
      if self.opSubType is None:
        if target is not self:
          raise MemopsError(
            "%s: target should be operation itself, is %s" % (self, target))

      else:
        if (
                target.opType != self.opType or target.target != target or target.opSubType is not None):
          raise MemopsError(
            "%s: target should be opType=None version of operation, is %s" % (
              self, target))

    elif targetTag == 'ChildClass':
      # ChildClass target
      if target.getParentClass() is not self.container:
        raise MemopsError("%s: target should be childclass of %s, is %s" % (
          self, self.container, target))

    else:
      # ClassElement target
      if target.container not in self.container.getAllSupertypes():
        raise MemopsError(
          "%s: target %s must be element of same class as op or a superclass" % (
            self, target))

    # special case - findFirst and findAll
    if (opType in ('findFirst', 'findAll') and isinstance(target.valueType,
                                                          MetaDataType)):
      raise MemopsError(
        "%s: %s or operation has Datatype attribute target %s" % (
          self, opType, target))

    # check overriding of elements
    allSupertypes = self.container.getAllSupertypes()
    mayNotOverride = not (Base in allSupertypes)
    for supertype in allSupertypes[1:]:
      superElem = supertype._MetaModelElement__elementDict.get(self.name)
      if superElem is not None:

        if superElem.__class__ is not self.__class__:
          raise MemopsError(
            "%s overrides %s but types are different" % (superElem, self))

        # classes without supertype cannot override or be overridden
        if mayNotOverride and not superElem.isAbstract:
          raise MemopsError(
            "Name clash between %s and %s - classes do not descend from %s" % (
              superElem, self, Base))

        parameterData = self.parameterData
        for tag in parameterData.keys():

          if tag in (
            'codeStubs', 'isAbstract', 'container', 'documentation', 'guid'):
            continue

          if parameterData[tag].get('type') == 'content':
            continue

          val = getattr(self, tag)
          superval = getattr(superElem, tag)

          if val == superval:
            pass

          elif tag == 'target':
            if targetTag == 'container':
              pass
            elif targetTag == 'masterOp':
              pass
            elif targetTag == 'ChildClass':
              raise MemopsError(
                "%s overrides %s but %s operations may not be overridden" % (
                  self, superElem, self.opType))
            else:
              # ClassElement target - superval must be overridden by val
              if superval is not supertype.getElement(val.name):
                raise MemopsError(
                  "%s overrides %s but target %s does not override %s" % (
                    self, superElem, val, superval))

          elif tag == 'taggedValues':
            for tt, vv in superval.items():
              if val.get(tt) != vv:
                raise MemopsError(
                  "%s overrides %s but tagged value %s differs" % (
                    self, superElem, tt))

          else:
            raise MemopsError(
              "%s overrides %s but differs for %s" % (self, superElem, tag))

        if self.opType != 'init':
          # parameter inheritance
          if len(parameters) != len(superElem.parameters):
            raise MemopsError(
              "%s overrides %s but number of parameters is different" % (
                self, superElem))

    # checks on Parameters.
    if not self.isImplicit:
      # input parameters
      pars = [x for x in parameters if
              x.direction == metaConstants.in_direction]
      if len(pars) == 1 and not pars[0].isImplicit and pars[0].name != 'value':
        if self.container.container is not implPackage:
          # warn of unusual names, but exclude implPackage to keep number down
          print(
            "WARNING, %s: single input parameter is not named 'value' but %s" % (
              self, pars[0].name))

      foundOptional = None
      for par in pars:
        if par.taggedValues.get('isSubdivided'):
          if len(pars) >= 2 and par is pars[-2]:

            if pars[-1].taggedValues.get('isSubdivided'):
              if par.hicard == 1:
                raise MemopsError(
                  "%s: isSubdivided KeywordValue parameter %s is not the last input parameter" % (
                    self, par.name))
              elif pars[-1].hicard != 1:
                raise MemopsError(
                  "%s: isSubdivided Two KeywordValue parameters %s and %s" % (
                    self, par.name, pars[-1].name))

            else:
              raise MemopsError(
                "%s: isSubdivided parameter %s is not the last input parameter" % (
                  self, par.name))

          elif par is not pars[-1]:
            raise MemopsError(
              "%s: isSubdivided parameter %s is not the last input parameter" % (
                self, par.name))

        elif ((
                    par.locard == 0 and par.hicard == 1) or par.defaultValue is not None):
          # optional parameter. NB the or statement is currently superflous
          # but we might allow defaults for hicard!= 1 later
          foundOptional = par

        else:
          # mandatory parameter - must come first
          if foundOptional is not None:
            raise MemopsError(
              "%s: mandatory parameter %s appears after optional %s" % (
                self, par.name, foundOptional.name))

    # return parameters
    pars = [x for x in parameters if
            x.direction == metaConstants.return_direction]
    if pars:
      if opTypeInfo['group'] in ('modify', 'delete'):
        raise MemopsError("%s: modifier has return parameter" % (self,))
      elif len(pars) > 1:
        raise MemopsError("%s: more than one return parameter : %s" % (
          self, [x.name for x in pars]))


#############################################################################

class MetaRole(ClassElement):
  """ class for roles (link ends) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ClassElement.parameterData)
  parameterData['container']['type'] = MetaClass
  parameterData.update({
    'scope':{'type':'Token', 'enumeration':metaConstants.scope_enumeration,
             'default':metaConstants.instance_level, 'isFixed':True, },
    'valueType':{'type':MetaClass, },
    'aggregation':{'default':None, 'type':'Token',
                   'enumeration':metaConstants.aggregation_enumeration, },
    'hierarchy':{'default':None, 'type':'Token',
                 'enumeration':metaConstants.hierarchy_enumeration, },
    'otherRole':{'default':None, 'setterFunc':'setOtherRole', },
    'partitionsChildren':{'type':'Boolean', 'default':False, },
    'noDeleteIfSet':{'type':'Boolean', 'default':False, }, })

  # allowed tagged values
  allowedTags = ClassElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaRole'])

  def __init__(self, **params):

    ClassElement.__init__(self, **params)

    # finish link from container
    params['container']._MetaClass__roleNames.append(params['name'])

    if params.get('hierarchy') == metaConstants.parent_hierarchy:

      # set container parentRole
      params['container'].__dict__['parentRole'] = self

  def setOtherRole(self, value):
    """ set otherRole link
    """

    current = self.__dict__.get('otherRole')

    if value is None:
      if current:
        raise MemopsError(
          "%s - attempt to unset (partially) set otherRole" % (self,))
      else:
        self.__dict__['otherRole'] = None

    else:

      reverse = value.__dict__.get('otherRole')

      if current is value and reverse is self:
        #we are already set up
        return

      elif current is None and reverse is None:
        # NB value and self may be the same, but this still works
        self.__dict__['otherRole'] = value
        value.__dict__['otherRole'] = self

        # set container.container.topObjectClass
        if self.hierarchy in (
          metaConstants.parent_hierarchy, metaConstants.child_hierarchy):
          packages = (self.container.container, value.container.container)
          if packages[0] is not packages[1]:
            objs = (self, value)
            for ii in (0, 1):
              obj = objs[ii]
              if obj.hierarchy == metaConstants.parent_hierarchy:
                # out-of-package parent role - this must be the TopObject
                packages[ii].__dict__['topObjectClass'] = obj.container

      else:
        raise MemopsError(
          "%s - attempt to overwrite (partially) set otherRole with value %s" % (
            self, value))

  def removeOtherRole(self):
    """ remove otherRole link
    """

    current = self.__dict__.get('otherRole')

    if current is None:
      raise MemopsError(
        "%s - attempt to remove non-existing otherRole" % (self,))
    else:
      # NB current and self may be the same, but this still works
      self.__dict__['otherRole'] = None
      current.__dict__['otherRole'] = None

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    ClassElement.checkValid(self, complete=complete)

    valueType = self.valueType
    otherRole = self.otherRole
    hicard = self.hicard
    container = self.container
    constraints = self.constraints
    Impl = self.metaObjFromQualName('.'.join(
      [metaConstants.modellingPackageName,
       metaConstants.implementationPackageName]))
    DataRoot = Impl.getElement(metaConstants.dataRootName)
    Base = Impl.getElement(metaConstants.baseClassName)
    DataObject = Impl.getElement(metaConstants.dataObjClassName)
    TopObject = Impl.getElement(metaConstants.topObjClassName)

    # check package access
    if self.canAccess(valueType):
      # same package or other package is imported - no trouble
      pass

    elif valueType.canAccess(self):
      # other package imports this one

      if otherRole is None:
        # NBNB TBD this could be DANGEROUS - RECONSIDER later
        #if not (DataRoot is self.container and 
        #      TopObject in valueType.getAllSupertypes()):
        if not (DataObject is self.container or (
              DataRoot is self.container and TopObject in valueType.getAllSupertypes())):
          # MemopsRoot.currentTopObject has special handling.
          # any other case is illegal.
          raise MemopsError(
            "%s - one-way link to %s in non-imported package" % (
              self, valueType))

      elif self.isDerived:
        pass

      elif self.locard != 0:
        raise MemopsError(
          "%s - mandatory link to %s in non-imported package" % (
            self, valueType))
      elif self.changeability == metaConstants.frozen:
        raise MemopsError(
          "%s - frozen link to %s in non-imported package" % (self, valueType))
    else:
      raise MemopsError(
        "%s - link to %s in non-imported package" % (self, valueType))

    # check otherRole and constraint location
    if otherRole is not None:
      if constraints:
        if container.container is not otherRole.container.container:
          if not self.canAccess(otherRole):
            raise MemopsError(
              "%s: constraints on wrong side of interpackage link" % (self,))

        elif hicard != 1 and otherRole.hicard == 1:
          raise MemopsError(
            "%s: constraints on wrong side of one-to-many link" % (self,))

        if otherRole.constraints:
          raise MemopsError("%s: constraints on both sides of link" % (self,))

    # checks for parentRoles and composite aggregations 
    if self.hierarchy == metaConstants.parent_hierarchy:
      if (
                        hicard != 1 or self.locard != 1 or self.changeability != metaConstants.frozen or self.aggregation != metaConstants.composite_aggregation or self.isDerived or self.isAutomatic or self.isImplementation or (
              otherRole is None and not self.isAbstract)):
        raise MemopsError("""%s - invalid parentRole :
hicard:%s, locard:%s, changeability:%s, aggregation:%s
isDerived:%s, isAutomatic:%s, isImplementation:%s, otherRole:%s""" % (
          self, hicard, self.locard, self.changeability, self.aggregation,
          self.isDerived, self.isAutomatic, self.isImplementation, otherRole
        ))

      # check parentRole
      pr = self.container.parentRole
      if pr is not self:
        raise MemopsError("%s has hierarchy %s, but %s is class parent" %
          (self, metaConstants.parent_hierarchy, pr))

      # check package topObjectClass
      package = self.container.container
      if package is not self.valueType.container:
        # out-of-package parent role - this must be the TopObject
        if package.__dict__['topObjectClass'] is not self.container:
          raise MemopsError(
            "parentRole %s incompatible with package.topObjectClass %s" % (
              self, package.__dict__['topObjectClass']))

      if constraints:
        raise MemopsError("%s: constraints on parent role" % (self,))

    elif self.aggregation == metaConstants.composite_aggregation:
      raise MemopsError(
        "%s - non-parentRole has aggregation %s" % (self, self.aggregation))

    if self.hierarchy == metaConstants.child_hierarchy:
      if constraints:
        raise MemopsError("%s: constraints on child role" % (self,))
      if not otherRole:
        raise MemopsError("%s: child role lacks otherRole" % (self,))

    # check limits on partitioning roles
    if self.partitionsChildren:
      if self.hierarchy != metaConstants.no_hierarchy:
        raise MemopsError(
          "%s: only crosslinks can have partitionsChildren True" % (self,))

    if otherRole is None:
      if (
            not self.isAbstract and not self.isDerived and not self.isImplementation):
        # check that valueType does not have out-of-package subclasses
        # for two-way roles this is handled at the class level
        pp = valueType.container
        ll = [x for x in valueType.getAllSubtypes() if x.container is not pp]
        if ll:
          raise MemopsError(
            "%s: link to class %s with out-of-package subclasses :\n%s" % (
              self, valueType, ll))

    else:

      # check abstract association
      if self.isAbstract != otherRole.isAbstract:
        raise MemopsError(
          "%s: association has abstract and non-abstract role" % self.qualifiedName())

      # check coherence with otherRole
      if otherRole.otherRole is not self:
        raise MemopsError(
          "%s otherRole incoherent across Association" % self.qualifiedName())
      elif otherRole.container is not valueType:
        raise MemopsError(
          "%s valueType differs from otherRole.container" % self.qualifiedName())
      elif container is not otherRole.valueType:
        raise MemopsError(
          "%s otherRole.valueType differs from container" % self.qualifiedName())

      # check limits on cardinalities (NB may later be relaxed)

      # limit on bi-ordering:
      if (
              self.isOrdered and otherRole.isOrdered and not self.isDerived and not self.isImplementation):
        raise MemopsError(
          "%s: a link cannot be ordered in both directions, unless it is derived or implementation" % self.qualifiedName())

      # limit on non-unique two-way links
      if not self.isUnique and not self.isDerived and not self.isImplementation:
        raise MemopsError(
          "%s: a two-way link must be derived, implementation, or unique in both directions" % self.qualifiedName())

    # NB - Abstract roles are not allowed in non-abstract classes, but this
    # is checked in MetaClass.checkValid

    # check overriding
    allSupertypes = container.getAllSupertypes()

    if (
            Base not in allSupertypes and not self.isAbstract and not self.isImplementation):
      raise MemopsError(
        "%s: Non-abstract, non-implementation role in class that does not inherit from %s" % (
          self, Base))

    for supertype in allSupertypes[1:]:
      superElem = supertype._MetaModelElement__elementDict.get(self.name)
      if superElem is not None:

        superval = superElem.otherRole

        if otherRole is None:
          if superval is not None:
            raise MemopsError(
              "one-way link %s overrides two-way link %s:" % (self, superval))

        else:
          xx = otherRole.container.supertype
          if xx is not None:
            superOther = xx.getElement(otherRole.name)
          else:
            superOther = None
          if superOther is not superval:
            raise MemopsError(
              "%s overrides %s but otherRole %s does not override %s" % (
                self, superElem, otherRole, superval))

        break

# must be set here, after the class definition
MetaRole.parameterData['otherRole']['type'] = MetaRole
MetaClass.parameterData['parentRole']['type'] = MetaRole

#############################################################################

class MetaAttribute(ClassElement):
  """ class for roles (link ends) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(ClassElement.parameterData)
  parameterData['container']['type'] = ComplexDataType
  parameterData.update({
    'scope':{'type':'Token', 'enumeration':metaConstants.scope_enumeration,
             'default':metaConstants.instance_level, },
    'valueType':{'type':AbstractDataType, },
    'defaultValue':{'default':[], 'hicard':infinity, }, })

  # allowed tagged values
  allowedTags = ClassElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaAttribute'])

  def __init__(self, **params):

    ClassElement.__init__(self, **params)

    # finish link from container
    params['container']._ComplexDataType__attributeNames.append(params['name'])

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    ClassElement.checkValid(self, complete=complete)

    # default value requires a MetaDataType valueType
    defaultValue = self.defaultValue

    if not isinstance(self.valueType, MetaDataType) and defaultValue:
      raise MemopsError(
        "%s - default value only when valueType is a MetaDataType" % (self,))

    # default value must be valid
    if defaultValue:

      if not isinstance(self.valueType, MetaDataType):
        raise MemopsError(
          "%s - default value only when valueType is a MetaDataType" % (self,))

      if len(defaultValue) > self.hicard and self.hicard != infinity:
        raise MemopsError("%s - default value %s longer than hicard %s" % (
          self, self.defaultValue, self.hicard))

      if len(defaultValue) < self.locard:
        raise MemopsError("%s - default value %s shorter than locard %s" % (
          self, self.defaultValue, self.locard))

      #if self.locard == 0:
      #  # optional attribute with default value is not allowed 
      #  # there would be no way to set it to None or empty
      #  raise MemopsError(
      #   "%s - attribute with cardinality 0..%s has defaultValue (%s)"
      #   % (self, self.hicard, self.defaultValue)
      #  )


      for dv in defaultValue:
        if not self.valueType.isValid(dv):
          raise MemopsError("%s - default value %s from  %s is invalid" % (
            self, dv, self.defaultValue))

    # package access check
    if not self.canAccess(self.valueType):
      raise MemopsError(
        "%s - cannot access valueType %s" % (self, self.valueType))

    # special check:
    if isinstance(self.valueType, MetaClass):
      raise MemopsError("%s -attribute can not have class valueType: %s" % (
        self, self.valueType))


#############################################################################

class MetaParameter(AbstractValue):
  """ class for roles (link ends) 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(AbstractValue.parameterData)
  parameterData['container']['type'] = HasParameters
  parameterData['locard']['default'] = 1
  parameterData.update({'direction':{'type':'Token',
                                     'enumeration':metaConstants.direction_enumeration, },
                        'valueType':{'type':AbstractDataType, },
                        'defaultValue':{'default':None, }, })


  # allowed tagged values
  allowedTags = AbstractValue.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaParameter'])

  def __init__(self, **params):

    AbstractValue.__init__(self, **params)

    # finish link from container
    params['container']._HasParameters__parameterNames.append(params['name'])

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    AbstractValue.checkValid(self, complete=complete)

    valueType = self.valueType
    superValueTypes = valueType.getAllSupertypes()
    Base = None
    if isinstance(valueType, MetaClass):
      Base = self.metaObjFromQualName('.'.join(
        [metaConstants.modellingPackageName,
         metaConstants.implementationPackageName, metaConstants.baseClassName]))
    elif isinstance(valueType, MetaDataObjType):
      Base = self.metaObjFromQualName('.'.join(
        [metaConstants.modellingPackageName,
         metaConstants.implementationPackageName,
         metaConstants.baseDataTypeObjName]))
    if Base is not None and not Base in superValueTypes:
      #raise MemopsError("%s valueType %s does not descend from %s"
      #                  % (self, valueType, Base))
      #NBNB TBD tenporary HACK - test should be put back soonest
      print("WARNING - %s valueType %s does not descend from %s" % (
        self, valueType, Base))

    # package access check
    operationData = OpTypes.operationData
    if operationData[self.container.opType]['targetTag'] == 'masterOp':
      # Other operations have their parameters follow autogeneration rules
      # also, ops for e.g. interpackage links would fail this test
      if not self.canAccess(self.valueType):
        raise MemopsError(
          "%s - cannot access valueType %s" % (self, self.valueType))

    # default value checks
    if self.defaultValue:

      if self.direction != metaConstants.in_direction:
        raise MemopsError(
          "%s - non-input parameter has explicit default %s" % (
            self, self.defaultValue))

      if self.hicard != 1:
        raise MemopsError("%s - has explicit default %s and hicard %s" % (
          self, self.defaultValue, self.hicard))

      if self.locard != 0:
        raise MemopsError("%s - is mandatory but has explicit default %s" % (
          self, self.defaultValue))

      if not isinstance(self.valueType, MetaDataType):
        raise MemopsError(
          "%s: explicit default %s but valueType %s is not a MetaDataType" % (
            self, self.defaultValue, self.valueType))

      if not self.valueType.isValid(self.defaultValue):
        raise MemopsError(
          "%s - default value %s is invalid" % (self, self.defaultValue))

    # optional parameters
    if (
            self.locard == 0 and self.hicard == 1 and self.direction != metaConstants.in_direction):
      raise MemopsError(
        "%s - non-input parameter is optional (0..1)" % (self,))


    # check subdivided parameters
    # these are Dictionaries that are implemented as undefined keyword/value
    # input or lists implemented as undefined parameters 
    # for langauges that allow it.
    # In practice we are talking about Python *par and **par.
    if self.taggedValues.get('isSubdivided'):

      if self.direction != metaConstants.in_direction:
        raise MemopsError(
          "%s - isSubdivided and direction is not %s" % (self, self.direction))

      if self.hicard == 1:
        if self.locard != 1:
          raise MemopsError("%s: isSubdivided parameter is 1..0" % (self, ))
        skDict = self.metaObjFromQualName(
          'memops.Implementation.StringKeyDict')
        if skDict not in self.valueType.getAllSupertypes():
          raise MemopsError(
            "%s - isSubdivided, hicard == 1 and type is not %s" % (
              self, skDict))

      else:
        if self.locard != 0:
          raise MemopsError("%s: isSubdivided parameter is n..m" % (self, ))


    # check overiding of elements. NB special, as operations
    # override but do not have supertypes themselves
    container = self.container
    superContainer = None
    if isinstance(container, MetaOperation):
      for supertype in container.container.getAllSupertypes()[1:]:
        superContainer = supertype._MetaModelElement__elementDict.get(
          container.name)
        if superContainer is not None:
          break

    elif isinstance(container, MetaException):
      superContainer = container.supertype

    if superContainer is not None and superContainer.opType != 'init':
      superElem = superContainer.getElement(self.name)
      if superElem is None:
        raise MemopsError("%s: new parameter %s in overriding %s " % (
          container, self.name, superContainer.__class__.__name__))

      else:
        # check that parameters fit

        if not (self.isImplicit and superElem.isImplicit):
          # no need to police autogenerated parameters.

          parameterData = self.parameterData
          for tag in parameterData.keys():

            if tag in ('container', 'documentation', 'guid', 'defaultValue'):
              continue

            if parameterData[tag].get('type') == 'content':
              continue

            val = getattr(self, tag)
            superval = getattr(superElem, tag)

            if val == superval:
              pass

            elif tag == 'locard':
              if superval > val:
                raise MemopsError(
                  "%s: locard %s lower than in overridden %s %s" % (
                    self, val, self.__class__.__name__, superElem))

            elif tag == 'hicard':

              if (superval == 1) != (val == 1):
                raise MemopsError(
                  "%s overriding %s: hicard must be 1 in both or neither" % (
                    self, superElem))

              elif superval == infinity:
                pass

              elif val == infinity:
                raise MemopsError(
                  "%s: hicard infinity higher than in overridden %s %s" % (
                    self, self.__class__.__name__, superElem))
                pass

              elif superval < val:
                raise MemopsError(
                  "%s: hicard %s higher than in overridden %s %s" % (
                    self, val, self.__class__.__name__, superElem))

            elif tag == 'valueType':
              if superval not in val.getAllSupertypes():
                if superval.qualifiedName() != 'memops.Implementation.Any':
                  raise MemopsError(
                    "%s overrides %s, but valuetype %s is not a subtype of %s" % (
                      self, superElem, val, superval))

            elif tag == 'taggedValues':
              for tt, vv in superval.items():
                if val.get(tt) != vv:
                  raise MemopsError(
                    "%s overrides %s but tagged value %s differs" % (
                      self, superElem, tt))

            else:
              raise MemopsError(
                "%s overrides %s but differs for %s" % (self, superElem, tag))


#############################################################################

class MetaConstant(MetaModelElement):
  """ class for static constants
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(MetaModelElement.parameterData)
  parameterData['container']['type'] = MetaPackage
  parameterData.update({'value':{}, 'valueType':{'type':MetaDataType, }, })

  # allowed tagged values
  allowedTags = MetaModelElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaConstant'])

  def __init__(self, **params):

    MetaModelElement.__init__(self, **params)

    # finish link from container
    params['container']._MetaPackage__constantNames.append(params['name'])

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    MetaModelElement.checkValid(self, complete=complete)

    if not self.valueType.isValid(self.value):
      raise MemopsError("%s - value %s is invalid" % (self, self.value))

    # package access check
    if not self.canAccess(self.valueType):
      raise MemopsError(
        "%s - cannot access valueType %s" % (self, self.valueType))

    # name style
    if self.name[0] not in metaConstants.uppercase:
      print("WARNING, name of %s does not start with upper case" % self)


#############################################################################


class MetaConstraint(MetaModelElement):
  """ abstract class for elements 
  """

  # information for handling input parameters
  parameterData = memopsUtil.semideepcopy(MetaModelElement.parameterData)
  parameterData['container']['type'] = ConstrainedElement
  parameterData['codeStubs'] = {'type':'StringDict', 'default':{}, }

  # allowed tagged values
  allowedTags = MetaModelElement.allowedTags.copy()
  allowedTags.update(TaggedValues.allowedTags['MetaConstraint'])

  def __init__(self, **params):

    MetaModelElement.__init__(self, **params)

    # special case - MetaParameters cannot have constraints.
    if isinstance(self.container, MetaParameter):
      raise MemopsError("Attempt to add constraint to %s" % self.container)


  def addCodeStub(self, tag, value):
    """ Add codeStub
    """

    if type(tag) != StringType:
      raise MemopsError("%s codeStub tag %s is not a string" % (self, tag))

    if type(value) != StringType:
      raise MemopsError(
        "%s codeStub %s value %s is not a string" % (self, tag, value))

    if tag not in metaConstants.codeStubTags:
      raise MemopsError("%s : unsupported  codeStub tag %s " % (self, tag))

    self._MetaModelElement__dataDict['codeStubs'][tag] = value

  def removeCodeStub(self, tag):
    """Remove existing CodeStub
    """

    if self._MetaModelElement__dataDict['codeStubs'].get(tag,
                                                         sentinel) is not sentinel:
      del self._MetaModelElement__dataDict['codeStubs'][tag]
    else:
      raise MemopsError("%s has no CodeStub %s " % (self, tag))

  def checkValid(self, complete=False):
    """ Check that object is valid.
    """

    MetaModelElement.checkValid(self, complete=complete)

    # check if container is derived
    if isinstance(self.container, ClassElement) and self.container.isDerived:
      raise MemopsError(
        "MetaConstraint %s is attached to derived element" % self.qualifiedName())

    # check if container is Implementation
    if isinstance(self.container,
                  ClassElement) and self.container.isImplementation:
      raise MemopsError(
        "MetaConstraint %s is attached to Implementation element" % self.qualifiedName())

    # check code
    codeStubs = self._MetaModelElement__dataDict['codeStubs']
    codeTags = metaConstants.codeStubTags
    for codeTag in codeStubs.keys():

      # check code tags
      if codeTag not in codeTags:
        raise MemopsError("%s: Ilegal codeStub tag %s" % (self, codeTag))

      # check code content
      codeString = codeStubs.get(codeTag)
      if (codeString is not None and codeString.find('isValid') == -1 and len(
        codeString.split('\n')) != 1
      ):
        raise MemopsError("""MetaConstraint:
%s
has multiline %s code:

%s

that does not contains string 'isValid'
      """ % (self, codeTag, codeString))


#############################################################################
#
# classes
#
#############################################################################

# non-abstract classes. NB used in XmlModelGen
nonAbstractClasses = (
  MetaPackage, MetaClass, MetaDataObjType, MetaDataType, MetaException,
  MetaOperation, MetaRole, MetaAttribute, MetaParameter, MetaConstant,
  MetaConstraint
)

# check business rules for MetaClasses
for cls in nonAbstractClasses:
  finaliseMetaClass(cls)
