"""
Module Documentation here
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
__modifiedBy__ = "$modifiedBy: Wayne Boucher $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:41 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Wayne Boucher $"
__date__ = "$Date: 2017-03-16 18:20:01 +0000 (Thu, March 16, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import sys
import typing

from PyQt5 import QtWidgets, QtCore

from ccpn.core import _coreClassMap
from ccpn.core.Project import Project
from ccpn.core._implementation.AbstractWrapperObject import AbstractWrapperObject
from ccpn.core.lib.SpectrumLib import getExperimentClassifications
from ccpn.ui.Ui import Ui
from ccpn.ui.gui.popups.RegisterPopup import RegisterPopup
from ccpn.ui.gui.widgets.Application import Application
from ccpn.core.lib.Notifiers import Notifier

# This import initializes relative paths for QT style-sheets.  Do not remove!

from ccpn.util import Logging


def qtMessageHandler(*errors):
    for err in errors:
        Logging.getLogger().warning('QT error: %s' % err)


# un/suppress messages
QtCore.qInstallMessageHandler(qtMessageHandler)


class Gui(Ui):
    # Factory functions for UI-specific instantiation of wrapped graphics classes
    _factoryFunctions = {}

    def __init__(self, application):
        Ui.__init__(self, application)
        self._initQtApp()

    def _initQtApp(self):
        # On the Mac (at least) it does not matter what you set the applicationName to be,
        # it will come out as the executable you are running (e.g. "python3")

        # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)

        self.qtApp = Application(self.application.applicationName,
                                 self.application.applicationVersion,
                                 organizationName='CCPN', organizationDomain='ccpn.ac.uk')
        #self.qtApp.setStyleSheet(self.application.styleSheet)

        styles = QtWidgets.QStyleFactory()
        self.qtApp.setStyle(styles.create('fusion'))

    def initialize(self, mainWindow):
        """UI operations done after every project load/create"""

        # Set up mainWindow
        self.mainWindow = self._setupMainWindow(mainWindow)

        self.application.initGraphics()

        project = self.application.project

        # Wrapper Notifiers
        from ccpn.ui.gui.lib import GuiStrip

        notifier = project.registerNotifier('Strip', 'create', GuiStrip.GuiStrip._resetRemoveStripAction)
        project.duplicateNotifier('Strip', 'delete', notifier)

        project.registerNotifier('Axis', 'change', GuiStrip._axisRegionChanged)

        # TODO:ED not sure this is the best place
        project.registerNotifier('Mark', 'create', GuiStrip._updateDisplayedMarks)
        project.registerNotifier('Mark', 'change', GuiStrip._updateDisplayedMarks)
        project.registerNotifier('Mark', 'delete', GuiStrip._updateDisplayedMarks)

        # TODO:ED sorry - don't actually want _appBase
        self._currentPeakNotifier = Notifier(project._appBase.current, [Notifier.CURRENT], 'peaks', GuiStrip._updateSelectedPeaks)
        self._currentIntegralNotifier = Notifier(project._appBase.current, [Notifier.CURRENT], 'integrals', GuiStrip._updateSelectedIntegrals)
        self._currentMultipletNotifier = Notifier(project._appBase.current, [Notifier.CURRENT], 'multiplets', GuiStrip._updateSelectedMultiplets)

        from ccpn.ui.gui.lib import GuiSpectrumDisplay

        project.registerNotifier('Peak', 'delete', GuiSpectrumDisplay._deletedPeak)
        project.registerNotifier('Spectrum', 'change', GuiSpectrumDisplay._spectrumHasChanged)

        from ccpn.ui.gui.lib.GuiSpectrumView import GuiSpectrumView

        project.registerNotifier('SpectrumView', 'delete', GuiSpectrumView._deletedSpectrumView)
        project.registerNotifier('SpectrumView', 'create', GuiSpectrumView._createdSpectrumView)
        project.registerNotifier('SpectrumView', 'change', GuiSpectrumView._spectrumViewHasChanged)

        from ccpn.ui.gui.lib import GuiPeakListView

        # project.registerNotifier('PeakListView', 'create',
        #                          GuiPeakListView.GuiPeakListView._createdPeakListView)
        # project.registerNotifier('PeakListView', 'delete',
        #                          GuiPeakListView.GuiPeakListView._deletedStripPeakListView)
        # project.registerNotifier('PeakListView', 'change',
        #                          GuiPeakListView.GuiPeakListView._changedPeakListView)
        #
        # from ccpn.ui.gui.lib import GuiIntegralListView
        # project.registerNotifier('IntegralListView', 'create',
        #                          GuiIntegralListView.GuiIntegralListView._createdIntegralListView)
        # project.registerNotifier('IntegralListView', 'delete',
        #                          GuiIntegralListView.GuiIntegralListView._deletedStripIntegralListView)
        # project.registerNotifier('IntegralListView', 'change',
        #                          GuiIntegralListView.GuiIntegralListView._changedIntegralListView)
        #
        # from ccpn.ui.gui.lib import GuiMultipletListView
        # project.registerNotifier('MultipletListView', 'create',
        #                          GuiMultipletListView.GuiMultipletListView._createdMultipletListView)
        # project.registerNotifier('MultipletListView', 'delete',
        #                          GuiMultipletListView.GuiMultipletListView._deletedStripMultipletListView)
        # project.registerNotifier('MultipletListView', 'change',
        #                          GuiMultipletListView.GuiMultipletListView._changedMultipletListView)

        # TODO:ED need to unregister these notifiers on close
        self._updateNotifier1 = Notifier(project
                                         , triggers=[Notifier.RENAME]
                                         , targetName='NmrAtom'
                                         , callback=GuiPeakListView._updateAssignmentsNmrAtom)
        # self._updateNotifier2 = Notifier(project
        #                                 , triggers=[Notifier.CREATE]
        #                                 , targetName='NmrAtom'
        #                                 , callback=GuiPeakListView._editAssignmentsNmrAtom)

        project.registerNotifier('Peak', 'change', _coreClassMap['Peak']._refreshPeakPosition)

        # API notifiers - see functions for comments on why this is done this way
        project._registerApiNotifier(GuiPeakListView._upDateAssignmentsPeakDimContrib,
                                     'ccp.nmr.Nmr.AbstractPeakDimContrib', 'postInit')
        # project._registerApiNotifier(GuiPeakListView._deleteAssignmentsNmrAtomDelete,
        #                             'ccp.nmr.Nmr.AbstractPeakDimContrib', 'preDelete')

        # ejb - new notifier to catch the deletion of an nmrAtom and update peak labels
        project._registerApiNotifier(GuiPeakListView._deleteAssignmentsNmrAtomDelete,
                                     'ccp.nmr.Nmr.AbstractPeakDimContrib', 'delete')

        from ccpn.ui.gui.modules import SpectrumDisplayNd

        project._registerApiNotifier(SpectrumDisplayNd._changedBoundDisplayAxisOrdering,
                                     SpectrumDisplayNd.ApiBoundDisplay, 'axisOrder')

        # # TODO:ED remove if not needed
        # from ccpn.ui.gui.modules import SpectrumDisplay1d
        # project._registerApiNotifier(SpectrumDisplay1d._updateSpectrumPlotColour,
        #                              SpectrumDisplay1d.ApiDataSource, 'setSliceColour')
        #
        # project._registerApiNotifier(SpectrumDisplay1d._updateSpectrumViewPlotColour,
        #                              SpectrumDisplay1d.ApiSpectrumView, 'setSliceColour')

        project._registerApiNotifier(GuiStrip._rulerCreated, 'ccpnmr.gui.Task.Ruler', 'postInit')
        project._registerApiNotifier(GuiStrip._rulerDeleted, 'ccpnmr.gui.Task.Ruler', 'preDelete')
        project._registerApiNotifier(GuiStrip._setupGuiStrip, 'ccpnmr.gui.Task.Strip', 'postInit')

        project._registerApiNotifier(GuiSpectrumDisplay._deletedSpectrumView,
                                     'ccpnmr.gui.Task.SpectrumView', 'preDelete')

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # TODO:ED   added so that some modules are cleared on changing projects

        from ccpn.ui.gui.modules.SequenceModule import SequenceModule

        SequenceModule._alreadyOpened = False

    def start(self):
        self.mainWindow._fillRecentMacrosMenu()
        self.mainWindow._updateRestoreArchiveMenu()
        # self.mainWindow._setUserShortcuts(self.application.preferences, mainWindow=self.mainWindow)
        project = self.application.project
        self.application.experimentClassifications = getExperimentClassifications(project)

        # sys.stderr.write('==> Gui interface is ready\n')

        self.mainWindow.show()
        QtWidgets.QApplication.setActiveWindow(self.mainWindow)

        self.qtApp.start()

    def _showRegisterPopup(self):
        """Display registration popup"""

        popup = RegisterPopup(self.mainWindow, version=self.application.applicationVersion, modal=True)
        self.mainWindow.show()
        popup.exec_()
        self.qtApp.processEvents()

    def _setupMainWindow(self, mainWindow):
        # Set up mainWindow

        project = self.application.project

        # mainWindow = self.application.mainWindow
        mainWindow.sideBar.setProject(project)
        mainWindow.sideBar.fillSideBar(project)
        mainWindow.raise_()
        mainWindow.namespace['current'] = self.application.current
        return mainWindow

    def echoCommands(self, commands: typing.List[str]):
        """Echo commands strings, one by one, to logger
        and store them in internal list for perusal
        """
        console = self.application.ui.mainWindow.pythonConsole
        logger = self.application.project._logger

        for command in commands:
            console._write(command + '\n')
            logger.info(command)

    #TODO:RASMUS: should discuss how application should deal with it
    def getByGid(self, gid):
        return self.application.project.getByPid(gid)

    from ccpn.core.IntegralList import IntegralList
    from ccpn.ui.gui.modules.CcpnModule import CcpnModule

    def showIntegralTable(self, position: str = 'bottom', relativeTo: CcpnModule = None, selectedList: IntegralList = None):
        logParametersString = "position={position}, relativeTo={relativeTo}, selectedList={selectedList}".format(
                position="'" + position + "'" if isinstance(position, str) else position,
                relativeTo="'" + relativeTo + "'" if isinstance(relativeTo, str) else relativeTo,
                selectedList="'" + selectedList + "'" if isinstance(selectedList, str) else selectedList)
        # log = False
        # import inspect
        # i0, i1 = inspect.stack()[0:2]
        # if i0.function != i1.function:  # Caller function name matches, we don't log...
        #   code_context = i1.code_context[0]
        #   if 'ui.{}('.format(i0.function) in code_context:
        #     log = True
        # if log:
        #   self.application._startCommandBlock(
        #     'application.ui.showIntegralTable({})'.format(logParametersString))
        # try:
        #   from ccpn.ui.gui.modules.IntegralTable import IntegralTable
        #
        #   if 'INTEGRAL TABLE' in self.mainWindow.moduleArea.findAll()[1]:
        #     integralTable = self.mainWindow.moduleArea.findAll()[1]['INTEGRAL TABLE']
        #     if integralTable.isVisible():
        #       return
        #     else:
        #       self.mainWindow.moduleArea.moveModule(integralTable, position=position,
        #                                                 relativeTo=relativeTo)
        #   else:
        #    integralTable = IntegralTable(project=self.application.project, selectedList=selectedList)
        #    self.mainWindow.moduleArea.addModule(integralTable, position=position,
        #                                         relativeTo=relativeTo)
        #
        #   return integralTable
        #
        # finally:
        #   if log:
        #     self.application._endCommandBlock()

    def _execUpdates(self):
        sys.stderr.write('==> Gui update\n')
        from ccpn.framework.update.UpdatePopup import UpdatePopup

        updatePopup = UpdatePopup(parent=self.mainWindow, mainWindow=self.mainWindow)
        self.mainWindow.show()
        updatePopup.exec_()

#######################################################################################
#
#  Ui classes that map ccpn.ui._implementation
#
#######################################################################################

#TODO:RASMUS move to individual files containing the wrapped class and Gui-class
# Any Factory function to _implementation or abstractWrapper


## Window class
coreClass = _coreClassMap['Window']

#TODO:RASMUS move to individual files containing the wrapped class and Gui-class
# Any Factory function to _implementation or abstractWrapper
#
from ccpn.ui.gui.lib.GuiMainWindow import GuiMainWindow as _GuiMainWindow


class MainWindow(coreClass, _GuiMainWindow):
    """GUI main window, corresponds to OS window"""

    def __init__(self, project: Project, wrappedData: 'ApiWindow'):
        AbstractWrapperObject.__init__(self, project, wrappedData)

        logger = Logging.getLogger()

        logger.debug('MainWindow>> project: %s' % project)
        logger.debug('MainWindow>> project._appBase: %s' % project._appBase)

        application = project._appBase
        _GuiMainWindow.__init__(self, application=application)

        # hide the window here and make visible later
        self.hide()

        # patches for now:
        project._mainWindow = self
        logger.debug('MainWindow>> project._mainWindow: %s' % project._mainWindow)

        application._mainWindow = self
        application.ui.mainWindow = self
        logger.debug('MainWindow>> application from QtCore..: %s' % application)
        logger.debug('MainWindow>> application.project: %s' % application.project)
        logger.debug('MainWindow>> application._mainWindow: %s' % application._mainWindow)
        logger.debug('MainWindow>> application.ui.mainWindow: %s' % application.ui.mainWindow)


from ccpn.ui.gui.lib.GuiWindow import GuiWindow as _GuiWindow


#TODO:RASMUS: copy from MainWindow
class SideWindow(coreClass, _GuiWindow):
    """GUI side window, corresponds to OS window"""

    def __init__(self, project: Project, wrappedData: 'ApiWindow'):
        AbstractWrapperObject.__init__(self, project, wrappedData)
        _GuiWindow.__init__(self)


def _factoryFunction(project: Project, wrappedData) -> coreClass:
    """create Window, dispatching to subtype depending on wrappedData"""
    if wrappedData.title == 'Main':
        return MainWindow(project, wrappedData)
    else:
        return SideWindow(project, wrappedData)


Gui._factoryFunctions[coreClass.className] = _factoryFunction

## Task class
# There is no special GuiTask, so nothing needs to be done


## Mark class - put in namespace for documentation
Mark = _coreClassMap['Mark']

#TODO:RASMUS move to individual files containing the wrapped class and Gui-class
# Any Factory function to _implementation or abstractWrapper
# Also Rename
# SpectrumDisplay1d.py; contains SpectrumDisplay1d (formerly StripDisplay1d) and
#                       GuiStripDisplay
# SpectrumDisplayNd.py: likeWise


## SpectrumDisplay class
coreClass = _coreClassMap['SpectrumDisplay']
from ccpn.ui.gui.modules.SpectrumDisplay1d import SpectrumDisplay1d as _SpectrumDisplay1d


#TODO:RASMUS: also change for this class as done for the Nd variant below; this involves
#chaning the init signature of the SpectrumDisplay1d and passing the parameters along to
# GuiSpectrumDisplay

class StripDisplay1d(coreClass, _SpectrumDisplay1d):
    """1D bound display"""

    def __init__(self, project: Project, wrappedData: 'ApiBoundDisplay'):
        """Local override init for Qt subclass"""
        Logging.getLogger().debug('StripDisplay1d>> project: %s, project._appBase: %s' % (project, project._appBase))
        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack for now
        self.application = project._appBase

        _SpectrumDisplay1d.__init__(self, mainWindow=self.application.ui.mainWindow,
                                    name=self._longName('Spectrum Display'))
        if not project._isNew:
            # hack for now;  Needs to know this for restoring the GuiSpectrum Module. This has to be removed after decoupling Gui and Data!
            # This is a normal guiModule that should be opened in module area from the position
            # where is created. E.g. and not hardcoded on the "right" and coupled with api calls!
            self.application.ui.mainWindow.moduleArea.addModule(self, position='right',
                                                                relativeTo=self.application.ui.mainWindow.moduleArea)



from ccpn.ui.gui.modules.SpectrumDisplayNd import SpectrumDisplayNd as _SpectrumDisplayNd


#TODO:RASMUS Need to check on the consequences of hiding name from the wrapper
# NB: GWV had to comment out the name property to make it work
# conflicts existed between the 'name' and 'window' attributes of the two classes
# the pyqtgraph decendents need name(), GuiStripNd had 'window', but that could be replaced with
# mainWindow throughout

class SpectrumDisplayNd(coreClass, _SpectrumDisplayNd):
    """ND bound display"""

    def __init__(self, project: Project, wrappedData: 'ApiBoundDisplay'):
        """Local override init for Qt subclass"""
        Logging.getLogger().debug('SpectrumDisplayNd>> project: %s, project._appBase: %s' % (project, project._appBase))
        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack for now;
        self.application = project._appBase
        self._appBase = project._appBase

        _SpectrumDisplayNd.__init__(self, mainWindow=self.application.ui.mainWindow,
                                    name=self._longName('Spectrum Display'))

        if not project._isNew:
            # hack for now;  Needs to know this for restoring the GuiSpectrum Module. This has to be removed after decoupling Gui and Data!
            # This is a normal guiModule that should be opened in module area from the position
            # where is created. E.g. and not hardcoded on the "right" and coupled with api calls!
            self.application.ui.mainWindow.moduleArea.addModule(self, position='right',
                                                                relativeTo=self.application.ui.mainWindow.moduleArea)


#old name
StripDisplayNd = SpectrumDisplayNd


def _factoryFunction(project: Project, wrappedData) -> coreClass:
    """create SpectrumDisplay, dispatching to subtype depending on wrappedData"""
    if wrappedData.is1d:
        return StripDisplay1d(project, wrappedData)
    else:
        return StripDisplayNd(project, wrappedData)


Gui._factoryFunctions[coreClass.className] = _factoryFunction

## Strip class
coreClass = _coreClassMap['Strip']
from ccpn.ui.gui.lib.GuiStrip1d import GuiStrip1d as _GuiStrip1d


class Strip1d(coreClass, _GuiStrip1d):
    """1D strip"""

    def __init__(self, project: Project, wrappedData: 'ApiBoundStrip'):
        """Local override init for Qt subclass"""

        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack : Postpone SpectrumLoading and PlotWidget stuff until later
        self._finaliseDone = True

        Logging.getLogger().debug('Strip1d>> spectrumDisplay: %s' % self.spectrumDisplay)
        _GuiStrip1d.__init__(self, self.spectrumDisplay)

        stripIndex = self.spectrumDisplay.orderedStrips.index(self)
        self.spectrumDisplay.stripFrame.layout().addWidget(self, 0, stripIndex)


from ccpn.ui.gui.lib.GuiStripNd import GuiStripNd as _GuiStripNd


class StripNd(coreClass, _GuiStripNd):
    """ND strip """

    def __init__(self, project: Project, wrappedData: 'ApiBoundStrip'):
        """Local override init for Qt subclass"""

        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack : Postpone SpectrumLoading and PlotWidget stuff until later
        self._finaliseDone = True

        Logging.getLogger().debug('StripNd>> spectrumDisplay: %s' % self.spectrumDisplay)
        _GuiStripNd.__init__(self, self.spectrumDisplay)

        # cannot add the Frame until fully done
        stripIndex = self.spectrumDisplay.orderedStrips.index(self)
        self.spectrumDisplay.stripFrame.layout().addWidget(self, 0, stripIndex)

        return

        # these are not needed anymore
        self.spectrumDisplay.showAxes()
        self.spectrumDisplay.setColumnStretches(True)  # ejb - set the columns


def _factoryFunction(project: Project, wrappedData) -> coreClass:
    """create SpectrumDisplay, dispatching to subtype depending on wrappedData"""
    apiSpectrumDisplay = wrappedData.spectrumDisplay
    if apiSpectrumDisplay.is1d:
        return Strip1d(project, wrappedData)
    else:
        return StripNd(project, wrappedData)


Gui._factoryFunctions[coreClass.className] = _factoryFunction

## Axis class - put in namespace for documentation
Axis = _coreClassMap['Axis']

# TODO:RASMUS move to individual files containing the wrapped class and Gui-class
# Any Factory function to _implementation or abstractWrapper
#
## SpectrumView class
coreClass = _coreClassMap['SpectrumView']
from ccpn.ui.gui.lib.GuiSpectrumView1d import GuiSpectrumView1d as _GuiSpectrumView1d


class _SpectrumView1d(coreClass, _GuiSpectrumView1d):
    """1D Spectrum View"""

    def __init__(self, project: Project, wrappedData: 'ApiStripSpectrumView'):
        """Local override init for Qt subclass"""
        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack for now
        self._appBase = project._appBase
        self.application = project._appBase

        Logging.getLogger().debug('SpectrumView1d>> %s' % self)
        _GuiSpectrumView1d.__init__(self)


from ccpn.ui.gui.lib.GuiSpectrumViewNd import GuiSpectrumViewNd as _GuiSpectrumViewNd


class _SpectrumViewNd(coreClass, _GuiSpectrumViewNd):
    """ND Spectrum View"""

    def __init__(self, project: Project, wrappedData: 'ApiStripSpectrumView'):
        """Local override init for Qt subclass"""
        AbstractWrapperObject.__init__(self, project, wrappedData)

        # hack for now
        self._appBase = project._appBase
        self.application = project._appBase

        Logging.getLogger().debug('SpectrumViewNd>> %s %s' % (self, self.strip))
        _GuiSpectrumViewNd.__init__(self)


def _factoryFunction(project: Project, wrappedData) -> coreClass:
    """create SpectrumView, dispatching to subtype depending on wrappedData"""
    if 'intensity' in wrappedData.strip.spectrumDisplay.axisCodes:
        # 1D display
        return _SpectrumView1d(project, wrappedData)
    else:
        # ND display
        return _SpectrumViewNd(project, wrappedData)


Gui._factoryFunctions[coreClass.className] = _factoryFunction

# TODO:RASMUS move to individual files containing the wrapped class and Gui-class
# Any Factory function to _implementation or abstractWrapper
#

## PeakListView class
coreClass = _coreClassMap['PeakListView']
from ccpn.ui.gui.lib.GuiPeakListView import GuiPeakListView as _GuiPeakListView


class _PeakListView(coreClass, _GuiPeakListView):
    """Peak List View for 1D or nD PeakList"""

    def __init__(self, project: Project, wrappedData: 'ApiStripPeakListView'):
        """Local override init for Qt subclass"""
        AbstractWrapperObject.__init__(self, project, wrappedData)
        # hack for now
        self._appBase = project._appBase
        self.application = project._appBase
        _GuiPeakListView.__init__(self)


Gui._factoryFunctions[coreClass.className] = _PeakListView

## IntegralListView class
coreClass = _coreClassMap['IntegralListView']
from ccpn.ui.gui.lib.GuiIntegralListView import GuiIntegralListView as _GuiIntegralListView


class _IntegralListView(coreClass, _GuiIntegralListView):
    """Integral List View for 1D or nD IntegralList"""

    def __init__(self, project: Project, wrappedData: 'ApiStripIntegralListView'):
        """Local override init for Qt subclass"""
        AbstractWrapperObject.__init__(self, project, wrappedData)
        # hack for now
        self._appBase = project._appBase
        self.application = project._appBase
        _GuiIntegralListView.__init__(self)


Gui._factoryFunctions[coreClass.className] = _IntegralListView

## MultipletListView class
coreClass = _coreClassMap['MultipletListView']
from ccpn.ui.gui.lib.GuiMultipletListView import GuiMultipletListView as _GuiMultipletListView


class _MultipletListView(coreClass, _GuiMultipletListView):
    """Multiplet List View for 1D or nD MultipletList"""

    def __init__(self, project: Project, wrappedData: 'ApiStripMultipletListView'):
        """Local override init for Qt subclass"""
        AbstractWrapperObject.__init__(self, project, wrappedData)
        # hack for now
        self._appBase = project._appBase
        self.application = project._appBase
        _GuiMultipletListView.__init__(self)


Gui._factoryFunctions[coreClass.className] = _MultipletListView

# Delete what we do not want in namespace
del _factoryFunction
del coreClass
