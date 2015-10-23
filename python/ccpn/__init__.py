"""CCPN data. High level interface for normal data access

The standard ways of starting a project are:

- myProject = :ref:`ccpn-loadProject-ref` (*path*, ...)
- myProject = :ref:`ccpn-newProject-ref` (*projectName*, ...)

Module Organisation
-------------------

Class Hierarchy
^^^^^^^^^^^^^^^

Classes are organised in a hierarchy, with all data objects ultimately contained within the Project::

  Project
  |       Spectrum
  |       |       PeakList
  |       |       |       Peak
  |       |       SpectrumReference
  |       |       PseudoDimension
  |       |       SpectrumHit
  |       Sample
  |       |       SampleComponent
  |       Substance
  |       Chain
  |       |       Residue
  |       |       |       Atom
  |       NmrChain
  |       |       NmrResidue
  |       |       |       NmrAtom
  |       ChemicalShiftList
  |       |       ChemicalShift
  |       RestraintSet
  |       |       RestraintList
  |       |       |       Restraint
  |       |       |       |       RestraintContribution
  |       Note


Common Class elements
^^^^^^^^^^^^^^^^^^^^^

All classes in this module are subclasses of the :ref:`ccpn-AbstractWrapperObject-ref`,
and inherit the following elements:

**project** - *ccpn.Project*

The Project (root)containing the object.

**pid** - *ccpncore.util.Pid.Pid*

Identifier for the object, unique within the project.
Set automatically from the short class name and object.id
E.g. 'NA:A.102.ALA.CA'

**longPid** - *ccpncore.util.Pid.Pid*

Identifier for the object, unique within the project.
Set automatically from the full class name and object.id
E.g. 'NmrAtom:A.102.ALA.CA'

**id** - *str*

Identifier for the object, used to generate the pid and longPid.
Generated by combining the id of the containing object, with the
value of one or more key attributes that uniquely identify the
object in context.
E.g. the id for an Atom, 'A.55.VAL.HA' is generated from::

    - 'A' *Chain.shortName*
    - '55' *Residue.sequenceCode*
    - 'VAL' *Residue.residueType*
    - 'HA' *Atom.name*

**delete()**

Delete object, with all contained objects and underlying data.

**getByPid(pidString)**

Get an arbitrary ccpn.Object from either its pid (e.g. 'SP:HSQC2') or its longPid
(e.g. 'Spectrum:HSQC2'

Returns None for invalid or unrecognised input strings.

**rename(newName)**

Change the object name or other key attribute(s), changing the object id, pid,
and all internal references to maintain consistency.
Some Objects (Chain, Residue, Atom) cannot be renamed

Data access
^^^^^^^^^^^

The data of objects are accessed with the normal Python syntax (x = object.value; object.value = x'.
There are no public getter and setter functions. For collections you will not get the internal
collection, but an unmodifiable copy, to prevent accidental modification fo the data
(e.g. myPeakList.peaks will return a tuple, not a list)

Each object has a link to the containing object (e.g. myPeakList.spectrum)

Each class has a link to contained objects,
and a function to get a contained object by relative id.
E.g. myProject.peaks, mySpectrum.peaks, and myPeakList.peaks will each get
all peaks contained within the relevant object, sorted by Peak id.
Similarly, a given peak can be found by either myProject.getPeak('HSQC2.1.593'),
mySpectrum.getPeak('1.593'), or myPeakList.getPeak('593')

Most objects can be created using a *newXyzObject* method on the parent.
E.g. you can create a new Restraint object with the myRestraintList.newRestraint(...) function.
'new' functions create a single objects, using the passed-in parameters.
There is no 'newSpectrum' function; spectra are created with 'loadSpectrum' as a complete spectrum
object requires an external file with the data.

More complex object creation is done with 'create...()' functions, that may create multiple
objects, and use heuristics to fill in missing parameters.
E.g. the myRestraintList.createRestraint(....) function creates a Restraint with the
contained RestraintContributions and restraintItems.

Functions whose names start with 'get' (e.g. getNmrAtom(...)) mostly take some kind of identifier
as an argument and returns the identified object if it exists, None otherwise.

Functions whose names start with 'fetch' (e.g. fetchNmrAtom(...)) also take some kind of identifier
as an argument.
These will return the identified object if it exists, but will create a new object otherwise.

Other common prefixes for function names include 'add' and 'remove' (which add and remove
pre-existing objects to collections), 'copy', 'clear', 'load', 'process' and 'toggle',
all of which should be self-explanatory.



.. currentmodule:: ccpn

Module level functions :
------------------------

.. _ccpn-loadProject-ref:

ccpn.loadProject
^^^^^^^^^^^^^^^^

.. autofunction:: ccpn.loadProject

.. _ccpn-newProject-ref:

ccpn.newProject
^^^^^^^^^^^^^^^

.. autofunction:: ccpn.newProject

"""

import importlib

from ccpncore.util import ApiFunc

# Import classes and set to this module
# All classes must be imported in correct order for subsequent code
# to work, as connections between classes are set when child class is imported
# _wrappedClassNames gives import order
_wrappedClasses = []
AbstractWrapperObject = cls = importlib.import_module(
  'ccpn._wrapper._AbstractWrapperObject').AbstractWrapperObject
_wrappedClasses.append(cls)
Project = cls = importlib.import_module('ccpn._wrapper._Project').Project
_wrappedClasses.append(cls)
Spectrum = cls = importlib.import_module('ccpn._wrapper._Spectrum').Spectrum
_wrappedClasses.append(cls)
PeakList = cls = importlib.import_module('ccpn._wrapper._PeakList').PeakList
_wrappedClasses.append(cls)
Peak = cls = importlib.import_module('ccpn._wrapper._Peak').Peak
_wrappedClasses.append(cls)
SpectrumReference = cls = importlib.import_module(
  'ccpn._wrapper._SpectrumReference').SpectrumReference
_wrappedClasses.append(cls)
PseudoDimension = cls = importlib.import_module('ccpn._wrapper._PseudoDimension').PseudoDimension
_wrappedClasses.append(cls)
SpectrumHit = cls = importlib.import_module('ccpn._wrapper._SpectrumHit').SpectrumHit
_wrappedClasses.append(cls)
Sample = cls = importlib.import_module('ccpn._wrapper._Sample').Sample
_wrappedClasses.append(cls)
SampleComponent = cls = importlib.import_module('ccpn._wrapper._SampleComponent').SampleComponent
_wrappedClasses.append(cls)
Substance = cls = importlib.import_module(
  'ccpn._wrapper._Substance').Substance
_wrappedClasses.append(cls)
Chain = cls = importlib.import_module('ccpn._wrapper._Chain').Chain
_wrappedClasses.append(cls)
Residue = cls = importlib.import_module('ccpn._wrapper._Residue').Residue
_wrappedClasses.append(cls)
Atom = cls = importlib.import_module('ccpn._wrapper._Atom').Atom
_wrappedClasses.append(cls)
NmrChain = cls = importlib.import_module('ccpn._wrapper._NmrChain').NmrChain
_wrappedClasses.append(cls)
NmrResidue = cls = importlib.import_module('ccpn._wrapper._NmrResidue').NmrResidue
_wrappedClasses.append(cls)
NmrAtom = cls = importlib.import_module('ccpn._wrapper._NmrAtom').NmrAtom
_wrappedClasses.append(cls)
ChemicalShiftList = cls = importlib.import_module(
  'ccpn._wrapper._ChemicalShiftList').ChemicalShiftList
_wrappedClasses.append(cls)
ChemicalShift = cls = importlib.import_module('ccpn._wrapper._ChemicalShift').ChemicalShift
_wrappedClasses.append(cls)
RestraintSet = cls = importlib.import_module('ccpn._wrapper._RestraintSet').RestraintSet
_wrappedClasses.append(cls)
RestraintList = cls = importlib.import_module('ccpn._wrapper._RestraintList').RestraintList
_wrappedClasses.append(cls)
Restraint = cls = importlib.import_module('ccpn._wrapper._Restraint').Restraint
_wrappedClasses.append(cls)
RestraintContribution = cls = importlib.import_module(
  'ccpn._wrapper._RestraintContribution').RestraintContribution
_wrappedClasses.append(cls)
StructureEnsemble = cls = importlib.import_module(
  'ccpn._wrapper._StructureEnsemble').StructureEnsemble
_wrappedClasses.append(cls)
Note = cls = importlib.import_module('ccpn._wrapper._Note').Note
_wrappedClasses.append(cls)

# Add class list for extended sphinx documentation to module
# putting AbstractWrapperObj3ct last
_sphinxWrappedClasses = _wrappedClasses[1:] + _wrappedClasses[:1]

# set main starting functions in namespace. Must be done after setting Project
# to avoid circular import problems
from ccpn.lib import Io as ccpnIo
loadProject = ccpnIo.loadProject
newProject = ccpnIo.newProject

# Make {shortClassName: className} map. NB may be added to by importing modules (ccpnmr wrapper)
_pluralPidTypeMap = {}
for cls in _wrappedClasses:
  className = cls.className if hasattr(cls, 'className') else cls.__class__.__name__
  _pluralPidTypeMap[cls.shortClassName] = className + 's'
#Special case, irregular plural
_pluralPidTypeMap['SP'] = _pluralPidTypeMap['Spectrum'] = 'Spectra'

# NBNB set function parameter annotations for AbstractBaseClass functions
# MUST be done here to get correct class type
AbstractWrapperObject.__init__.__annotations__['project'] = Project
AbstractWrapperObject.project.fget.__annotations__['return'] = Project


# Set up interclass links and related functions
Project._linkWrapperClasses()

# Load in additional utility functions int wrapper classes
# NB this does NOT pick up utility functions in non-child classes
# (e.g. AbstractWrapperObject or MainWindow) so these must be avoided
libModule = 'ccpn.lib._wrapper'
allActiveClasses = [Project]
for cls in allActiveClasses:
  # moduleName = '%s.%s' % (libModule, cls.__name__)
  ApiFunc._addModuleFunctionsToApiClass( cls.__name__, cls, rootModuleName=libModule)
  allActiveClasses.extend(cls._childClasses)

