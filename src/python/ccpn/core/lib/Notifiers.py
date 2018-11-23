"""
Notifier extensions, wrapping it into a class that also acts as the called 
function, displatching the 'user' callback if required.

The Notifier can be defined relative to any valid V3 core object, as well as the current
object as it first checks if the triggered signature is valid.

The triggers CREATE, DELETE, RENAME and CHANGE can be combined in the call signature,
preventing unnecessary code duplication. They are translated into multiple notifiers
of the 'Project V3-machinery' (i.e., the Rasmus callbacks)

The callback function is passed a callback dictionary with relevant info (see
docstring of Notifier class. This idea was copied from the Traitlets package.

April 2017: First design by Geerten Vuister

"""

#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================

__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
                 "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:32 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Geerten Vuister $"
__date__ = "$Date: 2017-04-18 15:19:30 +0100 (Tue, April 18, 2017) $"

#=========================================================================================
# Start of code
#=========================================================================================

import sys

from functools import partial
from collections import OrderedDict
from typing import Callable, Any
from ccpn.framework.Current import Current
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject

from ccpn.util.Logging import getLogger


logger = getLogger()


def skip(*args, **kwargs):
    "Do nothing"
    pass


class NotifierABC(object):
    """
    Abstract base class for Notifier and GuiNotifier classes
    """
    _currentIndex = 0

    # needs subclassing
    _triggerKeywords = ()

    def __init__(self, theObject, triggers, targetName, callback, debug=False, **kwargs):

        # Sanity checks
        if len(self._triggerKeywords) == 0:
            raise RuntimeError('Not trigger keywords defined; assure proper subclassing definitions')

        # initialisations
        self._id = NotifierABC._currentIndex
        NotifierABC._currentIndex += 1

        self._theObject = theObject  # The object we are monitoring

        if triggers is not None:
            if not (isinstance(triggers, list) or isinstance(triggers, tuple)) \
                    or len(triggers) == 0:
                raise RuntimeError('Invalid triggers (%r); should be a list or tuple' % triggers)
        for trigger in triggers:
            if not trigger in self._triggerKeywords:
                raise ValueError('Invalid trigger "%s" for <%s>' % (trigger, self.__class__.__name__))
        self._triggers = tuple(triggers)

        self._targetName = targetName

        self._callback = callback
        self._kwargs = kwargs

        self._debug = debug  # ability to report on individual instances
        self._isBlanked = False  # ability to blank notifier

    @property
    def id(self):
        return self._id

    def setDebug(self, flag: bool):
        "Set debug output on/off"
        self._debug = flag

    def setBlanking(self, flag: bool):
        "Set blanking on/off"
        self._isBlanked = flag

    def triggersOn(self, trigger) -> bool:
        """Return True if notifier triggers on trigger"""
        return trigger in self._triggers

    def __str__(self) -> str:
        return '<%s (%d): theObject=%s, triggers=%s targetName=%r>' % \
               (self.__class__.__name__, self.id, self._theObject, self._triggers, self._targetName)


class Notifier(NotifierABC):
    """
    Notifier class:

    triggers callback function with signature:  callback(callbackDict [, *args] [, **kwargs])

    ____________________________________________________________________________________________________________________

    trigger             targetName           callbackDict keys          Notes
    ____________________________________________________________________________________________________________________

     Notifier.CREATE    className             theObject, object,        targetName: valid child className of theObject
                                              targetName, trigger       (any for project instances)
                                              notifier

     Notifier.DELETE    className             theObject, object,        targetName: valid child className of theObject
                                              targetName, trigger       (any for project instances)
                                              notifier

     Notifier.RENAME    className             theObject, object         targetName: valid child className of theObject
                                              targetName, oldPid,       (any for project instances)
                                              trigger

     Notifier.CHANGE    className             theObject, object         targetName: valid child className of theObject
                                              targetName,               (any for project instances)
                                              trigger, notifier

     Notifier.OBSERVE   attributeName         theObject,targetName      targetName: valid attribute name of theObject
                        or ANY                value, previousValue,     NB: should only be used in isolation; i.e. not
                                              trigger, notifier         combined with other triggers

     Notifier.CURRENT   attributeName         theObject,targetName      theObject should be current object
                                              value, previousValue,     targetName: valid attribute name of current
                                              trigger, notifier         NB: should only be used in isolation; i.e. not
                                                                        combined with other triggers

    Implemention:

      Uses current notifier system from Project and Current;filters for child objects of type targetName in theObject.
      TargetName does need to denote a valid child-class or attribute of theObject, except for Project instances
      which can be triggered by all classes (see Table).

      The callback provides a dict with several key, value pairs and optional arguments and/or keyword arguments if
      defined in the instantiation of the Notifier object. (idea following the Trailtlets concept).
      Note that this dict also contains a reference to the Notifier object itself; this way it can be used
      to pass-on additional implementation specfic information to the callback function.

    """

    # Trigger keywords
    CREATE = 'create'
    DELETE = 'delete'
    RENAME = 'rename'
    CHANGE = 'change'
    OBSERVE = 'observe'
    CURRENT = 'current'

    ANY = '<Any>'

    NOTIFIER = 'notifier'
    THEOBJECT = 'theObject'
    TRIGGER = 'trigger'
    OBJECT = 'object'
    GETPID = 'pid'
    OLDPID = 'oldPid'
    VALUE = 'value'
    PREVIOUSVALUE = 'previousValue'
    TARGETNAME = 'targetName'

    _triggerKeywords = (CREATE, DELETE, RENAME, CHANGE, OBSERVE, CURRENT)

    def __init__(self, theObject: Any,
                 triggers: list,
                 targetName: str,
                 callback: Callable[..., str],
                 onceOnly=False,
                 debug=False,
                 **kwargs):
        """
        Create Notifier object;
        The triggers CREATE, DELETE, RENAME and CHANGE can be combined in the call signature

        :param theObject: valid V3 core object or current object to watch
        :param triggers: list of trigger keywords callback
        :param targetName: valid className, attributeName or None
        :param callback: callback function with signature: callback(obj, parameter2 [, *args] [, **kwargs])
        :param debug: set debug
        :param *args: optional arguments to callback
        :param **kwargs: optional keyword,value arguments to callback
        """
        super().__init__(theObject=theObject, triggers=triggers, targetName=targetName, debug=debug,
                         callback=callback, **kwargs
                         )

        # bit of a clutch for now
        if isinstance(theObject, Current):
            # assume we have current
            self._project = None
            self._isProject = False
            self._isCurrent = True
        elif isinstance(theObject, AbstractWrapperObject):
            self._project = theObject.project  # toplevel Project instance for theObject
            self._isProject = (theObject == self._project)  # theObject is the toplevel Project instance
            self._isCurrent = False
        else:
            raise RuntimeError('Invalid object (%s)', theObject)

        self._value = None  # used to store the value of attribute to observe for change

        self._notifiers = []  # list of tuples defining Notifier call signature;
        self._unregister = []  # list of tuples needed for unregistering

        # some sanity checks
        if len(triggers) > 1 and Notifier.OBSERVE in triggers:
            raise RuntimeError('Notifier: trigger "%s" only to be used in isolation' % Notifier.OBSERVE)
        if len(triggers) > 1 and Notifier.CURRENT in triggers:
            raise RuntimeError('Notifier.__init__: trigger "%s" only to be used in isolation' % Notifier.CURRENT)
        if triggers[0] == Notifier.CURRENT and not self._isCurrent:
            raise RuntimeError('Notifier.__init__: invalid object "%s" for trigger "%s"' % (theObject, triggers[0]))

        if targetName is None:
            raise ValueError('Invalid None targetName')

        # register the callbacks
        for trigger in self._triggers:

            # CURRENT special case; has its own callback mechanism
            if trigger == Notifier.CURRENT:

                if not hasattr(theObject, targetName):
                    raise RuntimeWarning(
                            'Notifier.__init__: invalid targetName "%s" for class "%s"' % (targetName, theObject))

                self._value = getattr(theObject, targetName)
                notifier = (trigger, targetName)
                # current has its own notifier system

                #TODO:RASMUS: change this and remove this hack
                # to register strip, the keywords is strips!
                tName = targetName + 's' if targetName == 'strip' else targetName
                func = theObject.registerNotify(partial(self, notifier=notifier), tName)
                self._notifiers.append(notifier)
                self._unregister.append((tName, Notifier.CURRENT, func))

            # OBSERVE special case, as the current underpinning implementation does not allow this directly
            # Hence, we track all changes to the object class, filtering those that apply
            elif trigger == Notifier.OBSERVE:
                if targetName != self.ANY and not hasattr(theObject, targetName):
                    raise RuntimeWarning(
                            'Notifier.__init__: invalid targetName "%s" for class "%s"' % (targetName, theObject.className))

                if targetName != self.ANY:
                    self._value = getattr(theObject, targetName)

                notifier = (trigger, targetName)
                func = self._project.registerNotifier(theObject.className,
                                                      Notifier.CHANGE,
                                                      partial(self, notifier=notifier),
                                                      onceOnly=onceOnly)
                self._notifiers.append(notifier)
                self._unregister.append((theObject.className, Notifier.CHANGE, func))

            # All other triggers;
            else:
                # Projects allow all registering of all classes
                allowedClassNames = [c.className for c in theObject._getChildClasses(recursion=self._isProject)]
                if targetName not in allowedClassNames:
                    raise RuntimeWarning('Notifier.__init__: invalid targetName "%s" for class "%s"' % (targetName, theObject.className))

                notifier = (trigger, targetName)
                func = self._project.registerNotifier(targetName,
                                                      trigger,
                                                      partial(self, notifier=notifier),
                                                      onceOnly=onceOnly)
                self._notifiers.append(notifier)
                self._unregister.append((targetName, trigger, func))

        if len(self._notifiers) == 0:
            raise RuntimeWarning('Notifier.__init__: no notifiers intialised for theObject=%s, targetName=%r, triggers=%s ' % \
                                 (theObject, targetName, triggers))

        if self._debug:
            # logger.info
            sys.stderr.write('>>> registered %s\n' % self)

    def unRegister(self):
        """
        unregister the notifiers
        """
        if not self.isRegistered():
            return

        if self._debug:
            # logger.info # logger apears not to work
            sys.stderr.write('>>> unregister Notifier (%d): %r, triggers=%r, target=%r, callback=%r\n' % \
                             (self._index, self._theObject, self._triggers,
                              self._targetName, self._callback)
                             )
        for targetName, trigger, func in self._unregister:
            if trigger == Notifier.CURRENT:
                self._theObject.unRegisterNotify(func, targetName)
            else:
                self._project.unRegisterNotifier(targetName, trigger, func)
        self._theObject = None
        self._callback = None
        self._notifiers = []
        self._unregister = []
        self._theObject = None
        self._callback = None
        self._triggers = None

    def isRegistered(self):
        "Return True if notifier is still registered; i.e. active"
        return len(self._notifiers) > 0

    def __call__(self, obj: Any, parameter2: Any = None, notifier: tuple = None):
        """
        wrapper, accomodating the different triggers before firing the callback
        """

        if not self.isRegistered():
            logger.warning('Trigering unregistered notifier %s' % self)
            return

        if self._isBlanked:
            return

        trigger, targetName = notifier

        if self._debug:
            sys.stderr.write('>>> Notifier.__call__: %s \n--> notifier=%s obj=%r parameter2=%r\n' % \
                             (self, notifier, obj, parameter2)
            )

        callbackDict = dict(
                notifier=self,
                trigger=trigger,
                theObject=self._theObject,
                object=obj,
                targetName=targetName,
                previousValue=None,
                value=None,
        )

        # CURRENT special case
        if trigger == Notifier.CURRENT:
            value = getattr(self._theObject, targetName)
            if value != self._value:
                callbackDict[self.OBJECT] = self._theObject
                callbackDict[self.PREVIOUSVALUE] = self._value
                callbackDict[self.VALUE] = value
                self._callback(callbackDict, **self._kwargs)
                self._value = value

        # OBSERVE ANY special case
        elif trigger == Notifier.OBSERVE and targetName == self.ANY:
            if obj.pid == self._theObject.pid:
                callbackDict[self.OBJECT] = self._theObject
                self._callback(callbackDict, **self._kwargs)

        # OBSERVE targetName special case
        elif trigger == Notifier.OBSERVE and targetName != self.ANY:
            # The check below catches all changes to obj that do not involve targetName, as only when it has changed
            # its value will we trigger the callback
            value = getattr(self._theObject, targetName)
            if obj.pid == self._theObject.pid and value != self._value:
                callbackDict[self.OBJECT] = self._theObject
                callbackDict[self.PREVIOUSVALUE] = self._value
                callbackDict[self.VALUE] = value
                self._callback(callbackDict, **self._kwargs)
                self._value = value

        # check if the trigger applies for all other cases
        elif self._isProject or obj._parent.pid == self._theObject.pid:
            if trigger == self.RENAME and parameter2 is not None:
                callbackDict[self.OLDPID] = parameter2
            self._callback(callbackDict, **self._kwargs)

        return

    # convenience methods

    # @staticmethod
    # def _getChildClasses(obj: AbstractWrapperObject, recursion: bool) -> list:
    #     """
    #     :param obj: valid V3 object
    #     :param recursion: use recursion to also add child objects
    #     :return: list of valid child classes of obj
    #     """
    #     #if not isinstance(obj, AbstractWrapperObject):
    #     #  raise RuntimeError('Ivalid object type (%s)' % obj)
    #
    #     cls = []
    #     for child in obj._childClasses:
    #         cls.append(child)
    #         if recursion:
    #             for grandchild in Notifier._getChildClasses(child, recursion=True):
    #                 cls.append(grandchild)
    #     return cls

    # @staticmethod
    # def _getChildObjects(obj: AbstractWrapperObject, recursion: bool = False) -> list:
    #     """
    #     depth-first extraction of all child objects, optionally using recursion
    #     :param obj: valid V3 object
    #     :return: list of child objects
    #     """
    #     #if not isinstance(obj, AbstractWrapperObject):
    #     #  raise RuntimeError('Invalid object type (%s)' % obj)
    #
    #     children = []
    #     for cls in obj._childClasses:
    #         if hasattr(obj, cls._pluralLinkName):
    #             for child in getattr(obj, cls._pluralLinkName):
    #                 children.append(child)
    #                 if recursion:
    #                     for grandchild in Notifier._getChildObjects(child, recursion=True):
    #                         children.append(grandchild)
    #     return children


# def currentNotifier(attributeName, callback, onlyOnce=False, debug=False):
#     """Convienience method: Return a Notifier instance for current.attributeName
#     """
#     app = getApplication()
#     notifier = Notifier(app.current, [Notifier.CURRENT], targetName=attributeName,
#                         callback=callback, onlyOnce=onlyOnce, debug=debug)
#     return notifier



class NotifierBase(object):
    """
    A class confering notifier management routines;
    """
    NOTIFIERSDICT = '_ccpNmrV3notifiersDict'  # attribute name for storing notifiers in Ccpn objects

    # def _init(self):
    #     """Method to call at intialisation; deliberately different from __init__"""
    #     setattr(self, self.NOTIFIERSDICT, OrderedDict())

    def _getObjectNotifiersDict(self):
        """Internal routine to get the object notifiers dict"""
        if not hasattr(self, self.NOTIFIERSDICT):
            setattr(self, self.NOTIFIERSDICT, OrderedDict())
        objNotifiers = getattr(self, self.NOTIFIERSDICT)
        # Need to implement a check
        return objNotifiers

    def setNotifier(self, theObject:AbstractWrapperObject, triggers: list, targetName: str, callback: Callable[..., str], *args, **kwargs) -> Notifier:
        """
        Set Notifier for Ccpn V3 object theObject
        :param theObject: V3 object to register a notifier with
        :param triggers: list of triggers to trigger callback
        :param targetName: valid className, attributeName or None (See Notifier doc string for details)
        :param callback: callback function with signature: callback(obj, parameter2 [, *args] [, **kwargs])
        :param *args: optional arguments
        :param **kwargs: optional keyword,value arguments
        :returns Notifier instance
        """
        objNotifiers = self._getObjectNotifiersDict()
        notifier = Notifier(theObject=theObject, triggers=triggers, targetName=targetName,
                            callback=callback, *args, **kwargs)
        id = notifier.id
        # this should never happen; hence just a check
        if id in objNotifiers:
            raise RuntimeError('%s: a notifier with id "%s" already exists (%s)' % (self, id, objNotifiers[id]))
        # add the notifier
        objNotifiers[id] = notifier
        return notifier

    def setGuiNotifier(self, theObject:AbstractWrapperObject, triggers: list, targetName: str, callback: Callable[..., str], *args, **kwargs) -> Notifier:
        """
        Set Notifier for Ccpn V3 object theObject
        :param theObject: V3 object to register a notifier with
        :param triggers: list of triggers to trigger callback
        :param targetName: valid className, attributeName or None (See Notifier doc string for details)
        :param callback: callback function with signature: callback(obj, parameter2 [, *args] [, **kwargs])
        :param *args: optional arguments
        :param **kwargs: optional keyword,value arguments

        :returns GuiNotifier instance
        """
        from ccpn.ui.gui.lib.GuiNotifier import GuiNotifier  # To avoid circular imports

        objNotifiers = self._getObjectNotifiersDict()
        notifier = GuiNotifier(theObject=theObject, triggers=triggers, targetName=targetName,
                               callback=callback, *args, **kwargs)
        id = notifier.id
        # this should never happen; hence just a check
        if id in objNotifiers:
            raise RuntimeError('%s: a notifier with id "%s" already exists (%s)' % (self, id, objNotifiers[id]))
        # add the notifier
        objNotifiers[id] = notifier
        return notifier

    def deleteNotifier(self, notifier: Notifier):
        """
        unregister notifier; remove it from the list and delete it
        :param notifier: Notifier instance
        """
        if not self.hasNotifier(notifier):
            raise RuntimeWarning('"%s" is not a (valid) notifier of "%s"' % (notifier, self))

        objNotifiers = self._getObjectNotifiersDict()
        notifier.unregister()
        del(objNotifiers[notifier.id])
        del(notifier)

    def hasNotifier(self, notifier: Notifier=None) -> bool:
        """
        Checks if object has notifier; return True if it has notifier or has any notifier when notifier=None

        :param notifier: Notifier instance or None
        :return: True or False
        """
        if not hasattr(self, self.NOTIFIERSDICT):
            return False

        objNotifiers = self._getObjectNotifiersDict()
        if len(objNotifiers) == 0:
            return False

        if notifier is None and len(objNotifiers) > 0:
            return True

        if not isinstance(notifier, NotifierABC):
           raise ValueError('"%s" is not a valid notifier instance' % notifier)

        if notifier.id in objNotifiers:
            return True

        return False

    def deleteAllNotifiers(self):
        """Unregister all the notifiers"""
        if not self.hasNotifier(None):
            # there are no notifiers
            return
        objNotifiers = self._getObjectNotifiersDict()
        for notifier in list(objNotifiers.values()):
            self.deleteNotifier(notifier)

    def setBlankingAllNotifiers(self, flag):
        """Set blanking of all the notifiers to flag"""
        if not self.hasNotifier(None):
            return
        objNotifiers = self._getObjectNotifiersDict()
        for notifier in list(objNotifiers.values()):
            notifier.setBlanking(flag)

#
#
# def deleteAllNotifiers(project):
#   """
#   remove all notifiers from project object using depth-first recursion, i.e. the
#   deepest objects in the tree are handled first.
#
#   :param project: valid V3 project
#   """
#
#   def _deleteNotifiers(obj):
#     if not hasattr(obj, NOTIFIERSDICT) or len() == 0:
#       return
#     objNotifiers = getattr(obj, NOTIFIERSDICT)
#     if len(objNotifiers) == 0:
#       return
#     for notifier in objNotifiers.values():
#       obj.deleteNotifier(notifier)
#     return
#
#   def _handleObj(obj):
#     for cls in obj._childClasses:
#       if hasattr(obj, cls._pluralLinkName):
#         for child in getattr(obj, cls._pluralLinkName):
#           _handleObj(child)
#     _deleteNotifiers(obj)
#
#   _handleObj(project)
#   return
#
# # class Test(object):
# #   "testing __del__"
# #   def __init__(self):
# #     print('__init__')
# #
# #   def __del__(self):
# #     print('__del__')
#
#
# # some testing in console
# if False:
#   r = project.nmrResidues[10]
#   n0 = r.setNotifier([Notifier.CREATE, Notifier.DELETE, Notifier.RENAME], 'NmrAtom', print)
#   n1 = r.setNotifier([Notifier.RENAME], None, print, 'renaming')
#   n2 = project.setNotifier([Notifier.CREATE, Notifier.DELETE], 'NmrAtom', print)
#   n4 = r.setNotifier([Notifier.OBSERVE], 'comment', print)
#
#   a = r.newNmrAtom()
#   project.deleteObjects(a)
#   r.rename('test')
#   r.comment = 'new comment'
#
#   n0.delete()
#   a = r.newNmrAtom()
