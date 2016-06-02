#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2016-05-16 17:45:50 +0100 (Mon, 16 May 2016) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Luca Mureddu, Simon P Skinner & Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license "
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2016-05-16 17:45:50 +0100 (Mon, 16 May 2016) $"
__version__ = "$Revision: 9320 $"

#=========================================================================================
# Start of code
#=========================================================================================

import json
import os
import platform
import sys
from functools import partial

from ccpn.core.Project import Project
from ccpn.core._implementation import Io as coreIo
from ccpn.core.lib.Version import applicationVersion
from ccpn.framework.Translation import languages, defaultLanguage
from ccpn.framework.Translation import translator
from ccpn.ui import interfaces, defaultInterface
from ccpn.ui.gui.Current import Current
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.util import Path
from ccpn.util import Register
from ccpn.util.AttrDict import AttrDict
from ccpnmodel.ccpncore.api.memops import Implementation
from ccpnmodel.ccpncore.lib.Io import Api as apiIo
from ccpnmodel.ccpncore.memops.metamodel import Util as metaUtil

from PyQt4.QtGui import QKeySequence

_DEBUG = True

componentNames = ('Assignment', 'Screening', 'Structure')

interfaceNames = ('NoUi', 'Gui')

def printCreditsText(fp, programName, version):
  """Initial text to terminal """

  lines = []
  lines.append("%s, version: %s" % (programName, version))
  lines.append("")
  lines.append(__copyright__[0:__copyright__.index('-')] + '- 2016')
  lines.append(__license__)
  lines.append("Not to be distributed without prior consent!")
  lines.append("")
  lines.append("Written by: %s" % __credits__)

  # print with aligning '|'s
  maxlen = max(map(len,lines))
  fp.write('%s\n' % ('=' * (maxlen+8)))
  for line in lines:
    fp.write('|   %s ' % line + ' ' * (maxlen-len(line)) + '  |\n')
  fp.write('%s\n' % ('=' * (maxlen+8)))


def defineProgramArguments():
  """Define the arguments of the program
  return argparse instance
  """
  import argparse
  parser = argparse.ArgumentParser(description='Process startup arguments')
  for component in componentNames:
    parser.add_argument('--'+component.lower(), dest='include'+component, action='store_true',
                                                help='Show %s component' % component.lower())
  parser.add_argument('--language',
                      help=('Language for menus, etc.; valid options = (%s); default=%s' %
                            ('|'.join(languages) ,defaultLanguage)),
                      default=defaultLanguage)
  parser.add_argument('--interface',
                      help=('User interface, to use; one of  = (%s); default=%s' %
                            ('|'.join(interfaces) ,defaultInterface)),
                      default=defaultInterface)
  parser.add_argument('--skip-user-preferences', dest='skipUserPreferences', action='store_true',
                                                 help='Skip loading user preferences')
  parser.add_argument('--nologging', dest='nologging', action='store_true', help='Do not log information to a file')
  parser.add_argument('projectPath', nargs='?', help='Project path')

  return parser

class Arguments:
  """Class for setting FrameWork input arguments directly"""
  language = defaultLanguage
  interface = 'NoUi'
  nologging = True
  skipUserPreferences = True
  projectPath = None

  def __init__(self, projectPath=None, **kw):

    # Dummy values
    for component in componentNames:
      setattr(self, 'include' + component, None)

    self.projectPath = projectPath
    for tag, val in kw.items():
      setattr(self, tag, val)

def getFramework(projectPath=None, **kw):

  args = Arguments(projectPath=projectPath, **kw)
  result = Framework('CcpNmr', applicationVersion, args)
  result.start()
  #
  return result



class Framework:
  """
  The Framework class is the base class for all applications
  It's currently broken, so don't use this if you want your application to actually work!
  """

  def __init__(self, applicationName, applicationVersion, args):

    self.args = args
    self.applicationName = applicationName
    self.applicationVersion = applicationVersion

    printCreditsText(sys.stderr, applicationName, applicationVersion)

    self.setupComponents(args)

    self.useFileLogger = not self.args.nologging

    self.current = None

    self.preferences = None
    self.styleSheet = None

    # Necessary as attribute is queried during initialisation:
    self._mainWindow = None

    # This is needed to make project available in NoUi (if nothing else)
    self.project = None

    # NBNB TODO The following block should maybe be moved into _getUi
    self._getUserPrefs()
    self._registrationDict = {}   # Default - overridden elsewhere
    self._setLanguage()
    self.styleSheet = self.getStyleSheet(self.preferences)

    self.ui = self._getUI()

    self._setupMenus()



  def getStyleSheet(self, preferences=None):
    if preferences is None:
      preferences = self.preferences

    colourScheme = preferences.general.colourScheme
    colourScheme = metaUtil.upperFirst(colourScheme)

    styleSheet = open(os.path.join(Path.getPathToImport('ccpn.ui.gui.widgets'),
                                   '%sStyleSheet.qss' % colourScheme)).read()
    if platform.system() == 'Linux':
      additions = open(os.path.join(Path.getPathToImport('ccpn.ui.gui.widgets'),
                                    '%sAdditionsLinux.qss' % colourScheme)).read()
      styleSheet += additions
    return styleSheet


  def setupComponents(self, args):
    # components (for menus)
    self.components = set()
    for component in componentNames:
      if getattr(args, 'include' + component):
        self.components.add(component)


  def _getUserPrefs(self):
    # user preferences
    if not self.args.skipUserPreferences:
      sys.stderr.write('==> Getting user preferences\n')
    self.preferences = getPreferences(self.args.skipUserPreferences)

  def _setLanguage(self):
    # Language, check for command line override, or use preferences
    if self.args.language:
      language = self.args.language
    else:
      language = self.preferences.general.language
    if not translator.setLanguage(language):
      self.preferences.general.language = language
    # translator.setDebug(True)
    sys.stderr.write('==> Language set to "%s"\n' % translator._language)


  def _isRegistered(self):
    """return True if registered"""
    self._registrationDict = Register.loadDict()
    return not Register.isNewRegistration(self._registrationDict)


  def register(self):
    """
    Display registration popup if there is a gui
    return True on error
    """
    if self.ui is None:
        return True

    popup = RegisterPopup(version=self.applicationVersion, modal=True)
    popup.show()
    popup.raise_()
    popup.exec_()
    self.gui.processEvents()

    if not self._isRegistered():
      return True

    Register.updateServer(self._registrationDict, self.applicationVersion)
    return False


  def _getUI(self):
    if self.args.interface == 'Gui':
      from ccpn.ui.gui.Gui import Gui
      ui = Gui(self)
    else:
      from ccpn.ui.Ui import NoUi
      ui = NoUi(self)

    # Connect UI classes for chosen ui
    ui.setUp()

    return ui


  def start(self):
    """Start the program execution"""

    # Load / create project
    projectPath = self.args.projectPath
    if projectPath:
      project = self.loadProject(projectPath)

    else:
      project = self.newProject()


    sys.stderr.write('==> Done, %s is starting\n' % self.applicationName)

    # TODO: Add back in registration ???

    # self.project = project
    self.ui.start()

    project._resetUndo(debug=_DEBUG)


  def _recentProjectsMenuItems(self):
    """
    Populates recent projects menu with 10 most recently loaded projects
    specified in the preferences file.
    """
    l = []
    for recentFile in self.preferences.recentFiles:
      if (recentFile.startswith('/var/') is False):
        l.append((recentFile, partial(self.loadProject, recentFile), (('translate', False),)))
    return l

  def _setupMenus(self):
    self._menuSpec = ms = []
      # TODO: move callbacks over from GuiMainWindow
      # TODO: remove QKeySequence
    # ms.append(('Project', [("New", self.newProject, [('shortcut', 'pn')]),
    #                        ("Open...", self.loadProject, [('shortcut', 'po')]),
    #                        ("Open Recent", self._recentProjectsMenuItems()),
    #                        (),
    #                        ("Load Spectrum", self.newProject, [('shortcut', 'ls')]),
    #                        ("Load Data", self.newProject, [('shortcut', 'ld')]),
    #                        (),
    #                        ("Save", self.newProject, [('shortcut', 'ps')]),
    #                        ("Save As...", self.newProject, [('shortcut', 'sa')]),
    #                        (),
    #                        ("Undo", self.newProject, [('shortcut', QKeySequence("Ctrl+z"))]),
    #                        ("Redo", self.newProject, [('shortcut', QKeySequence("Ctrl+y"))]),
    #                        (),
    #                        ("Summary", self.newProject),
    #                        ("Archive", self.newProject),
    #                        ("Backup...", self.newProject),
    #                        (),
    #                        ("Preferences", self.newProject),
    #                        (),
    #                        ("Close Program", self.newProject, [('shortcut', 'qt')]),
    #                       ]
    #    )
    #   )
    ms.append(('Spectrum', [("Spectrum Groups...", self.showSpectrumGroupsPopup, [('shortcut', 'ss')]),
                            ("Set Experiment Types...", self.showExperimentTypePopup, [('shortcut', 'et')]),
                            (),
                            ("Pick Peaks...", self.showPeakPickPopup, [('shortcut', 'pp')]),
                            ("Integration", self.showIntegrationModule, [('shortcut', 'it')]),
                            (),
                            ("Make Projection...", self.showProjectionPopup, [('shortcut', 'pj')]),
                            ("Phasing Console", self.togglePhaseConsole, [('shortcut', 'pc')])
                           ]
               )
              )
    ms.append(('Molecules', [("Create Molecule...", self.showMoleculePopup),
                             ("Show Sequence", self.toggleSequenceModule, [('shortcut', 'sq'),
                                                                           ('checkable', True),
                                                                           ('checked', False)
                                                                          ]),
                             ("Inspect...", self.inspectMolecule),
                             (),
                             ("Reference Chemical Shifts", self.showRefChemicalShifts,
                                                           [('shortcut', 'rc')])
                            ]
              )
             )

  def loadData(self, paths=None, text=None):
    """
    Opens a file dialog box and loads data from selected file.
    """
    from ccpn.ui.gui.widgets.FileDialog import FileDialog

    if text is None:
      text='Load Data'
    if paths is None:
      dialog = FileDialog(self, fileMode=0, text=text, preferences=self.preferences.general)
      paths = dialog.selectedFiles()[0]

    # NBNB TBD I assume here that path is either a string or a list lf string paths.
    # NBNB FIXME if incorrect

    if not paths:
      return
    elif isinstance(paths,str):
      paths = [paths]

    self.ui.mainWindow.processDropData(paths, dataType='urls')

  def addApplicationMenuSpec(self, spec, position=3):
    self._menuSpec.insert(position, spec)


  def showSpectrumGroupsPopup(self):
    pass

  def showProjectionPopup(self):
    pass

  def togglePhaseConsole(self):
    self.ui.mainWindow.togglePhaseConsole(self.ui.mainWindow)

  def showExperimentTypePopup(self):
    """
    Displays experiment type popup.
    """
    from ccpn.ui.gui.popups.ExperimentTypePopup import ExperimentTypePopup
    popup = ExperimentTypePopup(self.ui.mainWindow, self.project)
    popup.exec_()

  def showPeakPickPopup(self):
    """
    Displays Peak Picking Popup.
    """
    from ccpn.ui.gui.popups.PeakFind import PeakFindPopup
    popup = PeakFindPopup(parent=self.ui.mainWindow, project=self.project)
    popup.exec_()

  def showIntegrationModule(self, position:str='bottom', relativeTo:CcpnModule=None):
    spectrumDisplay = self.ui.mainWindow.createSpectrumDisplay(self.project.spectra[0])
    from ccpn.Metabolomics.Integration import IntegrationTable, IntegrationWidget
    spectrumDisplay.integrationWidget = IntegrationWidget(spectrumDisplay.module,
                                                          project=self.project, grid=(2, 0), gridSpan=(1, 4))
    spectrumDisplay.integrationTable = IntegrationTable(spectrumDisplay.module,
                                                        project=self.project, grid=(0, 4), gridSpan=(3, 1))
    self.current.strip = spectrumDisplay.strips[0]
    if self.ui.mainWindow.blankDisplay:
      self.ui.mainWindow.blankDisplay.setParent(None)
      self.ui.mainWindow.blankDisplay = None


  def inspectMolecule(self):
    from ccpn.ui.gui.widgets import MessageDialog
    info = MessageDialog.showInfo('Not implemented yet!',
          'This function has not been implemented in the current version',
          colourScheme=self.ui.mainWindow.colourScheme)

  def showRefChemicalShifts(self):
    """Displays Reference Chemical Shifts module."""
    from ccpn.ui.gui.modules.ReferenceChemicalShifts import ReferenceChemicalShifts
    self.refChemShifts = ReferenceChemicalShifts(self.project, self.ui.mainWindow.moduleArea)

  def showMoleculePopup(self):
    """
    Displays sequence creation popup.
    """
    from ccpn.ui.gui.modules.CreateSequence import CreateSequence
    popup = CreateSequence(self.ui.mainWindow, project=self.project).exec_()
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showMoleculePopup()")
    self.project._logger.info("application.showMoleculePopup()")


  def toggleSequenceModule(self):
    """Toggles whether Sequence Module is displayed or not"""
    if hasattr(self, 'sequenceModule'):
      if self.sequenceModule.isVisible():
        self.hideSequenceModule()
    else:
      self.showSequenceModule()
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.toggleSequenceModule()")
    self.project._logger.info("application.toggleSequenceModule()")

  def showSequenceModule(self, position='top', relativeTo=None):
    """
    Displays Sequence Module at the top of the screen.
    """
    from ccpn.ui.gui.modules.SequenceModule import SequenceModule

    self.sequenceModule = SequenceModule(self.project)
    self.ui.mainWindow.moduleArea.addModule(self.sequenceModule,
                                            position=position, relativeTo=relativeTo)
    return self.sequenceModule

  def hideSequenceModule(self):
    """Hides sequence module"""
    self.sequenceModule.close()
    delattr(self, 'sequenceModule')



  def _initialiseProject(self, project:Project):
    """Initialise project and set up links and objects that involve it"""

    self.project = project

    # Pass an instance of framework to project so the UI instantiation can happen
    project._appBase = self

    # Set up current
    self.current = Current(project=project)

    # This wraps the underlying data, including the wrapped graphics data
    #  - the project is now ready to use
    project._initialiseProject()

    # Adapt project to preferences
    self.applyPreferences(project)

    self.project = project
    self.ui.initialize(self._mainWindow)

    # Get the mainWindow out of the framework once it's been transferred to ui
    del self._mainWindow

  def applyPreferences(self, project):
    """Apply user preferences

    NBNB project should be impliclt rather than a parameter (once reorganisation is finished)
    """
    # Reset remoteData DataStores to match preferences setting
    dataPath = self.preferences.general.dataPath
    if not dataPath or not os.path.isdir(dataPath):
      dataPath = os.path.expanduser('~')
    memopsRoot = project._wrappedData.root
    dataUrl = memopsRoot.findFirstDataLocationStore(name='standard').findFirstDataUrl(
      name='remoteData'
    )
    dataUrl.url = Implementation.Url(path=dataPath)


  def initGraphics(self):
    """Set up graphics system after loading - to be overridden in subclasses"""
    # for window in self.project.windows:
    #   window.initGraphics()
    pass


  def _closeProject(self):
    """Close project and clean up - when opening another or quitting application"""

    # NB: this function must clan up both wrapper and ui/gui

    if self.project is not None:
      # Cleans up wrapper project, including graphics data objects (Window, Strip, etc.)
      self.project._close()
      self.project._appBase = None
    if self.ui.mainWindow:
      # ui/gui cleanup
      self.ui.mainWindow.deleteLater()
    self.ui.mainWindow = None
    self.current = None
    self.project = None


  def loadProject(self, path):
    """Open new project from path"""

    if self.project is not None:
      self._closeProject()

    sys.stderr.write('==> Loading "%s" project\n' % path)
    project = coreIo.loadProject(path)

    self._initialiseProject(project)

    project._resetUndo(debug=_DEBUG)

    return project


  def newProject(self, name='default'):
    # """Create new, empty project"""

    # NB _closeProject includes a gui cleanup call

    if self.project is not None:
      self._closeProject()

    sys.stderr.write('==> Creating new, empty project\n')
    project = coreIo.newProject(name=name)

    self._initialiseProject(project)

    project._resetUndo(debug=_DEBUG)

    return project


  def saveProject(self, newPath=None, newProjectName=None, createFallback=True):
    # TODO: convert this to a save and call self.project.save()
    pass
    apiIo.saveProject(self.project._wrappedData.root, newPath=newPath, newProjectName=newProjectName, createFallback=createFallback)
    layout = self.mainWindow.moduleArea.saveState()
    layoutPath = os.path.join(self.project.path, 'layouts')
    if not os.path.exists(layoutPath):
      os.makedirs(layoutPath)
    import yaml
    with open(os.path.join(layoutPath, "layout.yaml"), 'w') as stream:
      yaml.dump(layout, stream)
      stream.close()
    saveIconPath = os.path.join(Path.getPathToImport('ccpn.ui.gui.widgets'), 'icons', 'save.png')

    sys.stderr.write('==> Project successfully saved\n')
    # MessageDialog.showMessage('Project saved', 'Project successfully saved!',
    #                           colourScheme=self.preferences.general.colourScheme, iconPath=saveIconPath)

  def getByPid(self, pid):
    return self.project.getByPid(pid)


###################################


def getPreferences(skipUserPreferences=False, defaultPreferencesPath=None,
                   userPreferencesPath=None):

  def _readPreferencesFile(preferencesPath):
    fp = open(preferencesPath)
    preferences = json.load(fp, object_hook=AttrDict) ##TBD find a better way ?!?
    fp.close()
    return preferences

  def _updateDict(d, u):
    import collections
    # recursive update of dictionary
    # this deletes every key in u that is not in d
    # if we want every key regardless, then remove first if check below
    for k, v in u.items():
      if k not in d:
        continue
      if isinstance(v, collections.Mapping):
        r = _updateDict(d.get(k, {}), v)
        d[k] = r
      else:
        d[k] = u[k]
    return d

  preferencesPath = (defaultPreferencesPath if defaultPreferencesPath else
                     os.path.join(Path.getTopDirectory(), 'config', 'defaultv3settings.json'))
  preferences = _readPreferencesFile(preferencesPath)

  if not skipUserPreferences:
    preferencesPath = userPreferencesPath if userPreferencesPath else os.path.expanduser('~/.ccpn/v3settings.json')
    if os.path.exists(preferencesPath):
      _updateDict(preferences, _readPreferencesFile(preferencesPath))

  return preferences
