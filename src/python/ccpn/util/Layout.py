"""
Module Documentation Here
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:29 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import ntpath
import glob
from ccpn.util.Logging import getLogger
from ccpn.ui.gui.modules.GuiSpectrumDisplay import GuiSpectrumDisplay
from ccpn.util.AttrDict import AttrDict
import json
from collections import defaultdict
import sys, os



LayoutDirName = 'layout'
DefaultLayoutFileName = 'v3Layout.json'
Warning =  "warning"
WarningMessage =  "Warning. Any changes in this file will be overwritten when saving a new layout."
General = "general"
ApplicationName = "applicationName"
ApplicationVersion = "applicationVersion"
GuiModules = "guiModules"
FileNames = 'fileNames'
ClassNameModuleName = "class_And_Module_Names"
LayoutState =  "layoutState"

DefaultLayoutFile = {
                    Warning:  WarningMessage,
                    General:
                              {
                                ApplicationName: "",
                                ApplicationVersion: ""
                              },
                    GuiModules:
                              {
                                ClassNameModuleName: [()]
                              },

                    FileNames:
                              [
                              ]
                              ,
                    LayoutState:
                              {

                              }

                   }


def createLayoutDirectory(project):
  '''

  :param project:
  :return: creates a new folder : layout, where all the layout json files will be contained
  '''
  if project is not None:
    layoutDirectory = os.path.join(project.path, LayoutDirName)
    if not os.path.exists(layoutDirectory):
      os.makedirs(layoutDirectory)
      return layoutDirectory

def _createLayoutFile(project):
  try:
    path =  getLayoutDirectoryPath(project.path)+'/'+DefaultLayoutFileName
    file = open(path, "w")
    json.dump(DefaultLayoutFile, file, sort_keys=False, indent=4, separators=(',', ': '))
    file.close()
  except Exception as e:
    getLogger().warning('Impossible to create a layout File.', e)


def getLayoutDirectoryPath(projectPath):
  return os.path.join(projectPath, LayoutDirName)


def getLayoutFile(projectPath):
  if projectPath:
    fileType = '.json'
    layoutDirPath = getLayoutDirectoryPath(projectPath)
    if layoutDirPath:
      layoutFilepaths = glob.glob(layoutDirPath + "/*" + fileType)  # * means all if need specific format then *.fileType
      if len(layoutFilepaths)>0:
        latest_file = max(layoutFilepaths, key=os.path.getctime)
        getLogger().debug('Loaded User Layout')
        return latest_file

def _updateGeneral(mainWindow, layout):
  application = mainWindow.application
  applicationName = application.applicationName
  applicationVersion = application.applicationVersion
  if General in layout:
    if ApplicationName in layout.general:
      setattr(layout.general, ApplicationName, applicationName)
    if ApplicationVersion in layout.general:
      setattr(layout.general, ApplicationVersion, applicationVersion)


def _updateFilenNames(mainWindow, layout):
  """

  :param mainWindow:
  :param layout:
  :return: #updates the fileNames needed for importing the module. list of file name from the full path

  """
  guiModules = mainWindow.moduleArea.ccpnModules
  paths = []
  names = []
  for guiModule in guiModules:
    if not isinstance(guiModule, GuiSpectrumDisplay): #Don't Save spectrum Displays
      pyModule = sys.modules[guiModule.__module__]
      if pyModule:
        file = pyModule.__file__
        if file:
          path = os.path.abspath(file)
          basename = ntpath.basename(path)
          basenameList = os.path.splitext(basename)
          if len(basenameList)>0:
            names.append(basenameList[0])

    if len(names) > 0:
      if FileNames in layout:
        setattr(layout, FileNames, names)


def _updateGuiModules(mainWindow, layout):
  """
  
  :param mainWindow: 
  :param layout: 
  :return: #updates classNameModuleNameTupleList on layout with list of tuples [(className, ModuleName), (className, ModuleName)]
  list of tuples because a multiple modules of the same class type can exist. E.g. two peakListTable modules! 
  """
  guiModules = mainWindow.moduleArea.ccpnModules

  classNames_ModuleNames = [] #list of tuples [(className, ModuleName), (className, ModuleName)]
  for module in guiModules:
    if not isinstance(module, GuiSpectrumDisplay): # Displays are not stored here but in the DataModel
      classNames_ModuleNames.append((module.className, module.name()))

  if GuiModules in layout:
    if ClassNameModuleName in layout.guiModules:
        setattr(layout.guiModules, ClassNameModuleName, classNames_ModuleNames )

def _updateLayoutState(mainWindow, layout):
  if LayoutState in layout:
    setattr(layout, LayoutState, mainWindow.moduleArea.saveState())

def _updateWarning(mainWindow, layout):
  if Warning in layout:
    setattr(layout, Warning, WarningMessage)

def updateSavedLayout(mainWindow):
  """
  Updates the application.layout Dict
  :param mainWindow: needed to get application
  :return: an up to date layout dictionary with the current state of GuiModules
  """
  layout = mainWindow.application.layout
  
  _updateGeneral(mainWindow, layout)
  _updateFilenNames(mainWindow, layout)
  _updateGuiModules(mainWindow, layout)
  _updateLayoutState(mainWindow, layout)
  _updateWarning(mainWindow, layout)


def saveLayoutToJson(mainWindow, jsonFilePath=None):
  """

  :param application:
  :param jsonFilePath: User defined file path where to save the layout. Default is in .ccpn/layout/v3Layout.json
  :return: None
  """
  try:
    updateSavedLayout(mainWindow)
    layout = mainWindow.application.layout
    project = mainWindow.application.project
    if not jsonFilePath:
      jsonFilePath = getLayoutDirectoryPath(project.path) + '/' + DefaultLayoutFileName
    file = open(jsonFilePath, "w")
    json.dump(layout, file, sort_keys=False, indent=4, separators=(',', ': '))
    file.close()
  except Exception as e:
    getLogger().warning('Impossible to save Layout %s' %e)


def _ccpnModulesImporter(path, neededModules):
  """
  :param path: fullPath of the directory where are located the CcpnModules files
  :return: list of CcpnModule classes
  """
  _ccpnModules = []
  import pkgutil as _pkgutil
  import inspect as _inspect
  from ccpn.ui.gui.modules.CcpnModule import CcpnModule

  for loader, name, isPpkg in _pkgutil.walk_packages(path):
    # print ('>>>loading', name)
    # print(neededModules, name)
    if name in neededModules:

      try:
        findModule = loader.find_module(name)
        # for neededModule in neededModules:
        module = findModule.load_module(name)
      # print ('>>>found')
        for i, obj in _inspect.getmembers(module):
          if _inspect.isclass(obj):
            if issubclass(obj, CcpnModule):
              if hasattr(obj, 'className'):
                # print ('>>>     end')
                _ccpnModules.append(obj)
                # print ('>>>     append')
      except Exception as es:
        getLogger().warning('Error loading module: %s' % str(es))
  return _ccpnModules


def _openCcpnModule(mainWindow, ccpnModules, className, moduleName=None):
  for ccpnModule in ccpnModules:
    if ccpnModule is not None:
      if ccpnModule.className == className:
        try:
          newCcpnModule = ccpnModule(mainWindow=mainWindow, name=moduleName)
          newCcpnModule._restored = True
          # newCcpnModule.rename(newCcpnModule.name().split('.')[0])

          mainWindow.moduleArea.addModule(newCcpnModule)

        except Exception as e:
          getLogger().warning("Layout restore failed: %s" % e)


def _getApplicationSpecificModules(mainWindow, applicationName):
  '''init imports. try except as some applications may not be distribuited '''
  modules = []
  from ccpn.framework.Framework import AnalysisAssign, AnalysisMetabolomics, AnalysisStructure, AnalysisScreen

  if applicationName == AnalysisScreen:
    try:
      from ccpn.AnalysisScreen import modules as aS
      modules.append(aS)
    except Exception as e:
      getLogger().warning("Import Error for AnalysisScreen , %s" % e)

  if applicationName == AnalysisAssign:
    try:
      from ccpn.AnalysisAssign import modules as aA
      modules.append(aA)
    except Exception as e:
      getLogger().warning("Import Error for AnalysisAssign , %s" % e)

  if applicationName == AnalysisMetabolomics:
    try:
      from ccpn.AnalysisMetabolomics.ui.gui import modules as aM
      modules.append(aM)
    except Exception as e:
      getLogger().warning("Import Error for AnalysisMetabolomics , %s" % e)

  if applicationName == AnalysisStructure:
    try:
      from ccpn.AnalysisStructure import modules as aS
      modules.append(aS)
    except Exception as e:
      getLogger().warning("Import Error for AnalysisStructure , %s" % e)

  return modules


def _getAvailableModules(mainWindow, layout, neededModules):
  from ccpn.ui.gui import modules as gM
  if General in layout:
    if ApplicationName in layout.general:

      applicationName = getattr(layout.general, ApplicationName)
      modules = []
      if applicationName != mainWindow.application.applicationName:
        getLogger().debug('The layout was saved in a different application. Same of the modules might not be loaded.'
                          'If this happens,  start a new project with %s' %applicationName)
      else:
        modules = _getApplicationSpecificModules(mainWindow, applicationName)
      modules.append(gM)
      paths = [item.__path__ for item in modules]

      ccpnModules = [ccpnModule for path in paths for ccpnModule in _ccpnModulesImporter(path, neededModules)]
      return ccpnModules


def _traverse(o, tree_types=(list, tuple)):
  '''used to flat the state in a long list '''
  if isinstance(o, tree_types):
    for value in o:
      for subvalue in _traverse(value, tree_types):
        yield subvalue
  else:
    yield o

def _getModuleNamesFromState(layoutState):
  ''' '''
  names = []
  if not layoutState:
    return names

  lls = []
  if 'main' in layoutState:
   mains = layoutState['main']
   lls += list(_traverse(mains))
  if 'float' in layoutState:
   flts = layoutState['float']
   lls += list(_traverse(flts))
   for i in list(_traverse(flts)):
      if isinstance(i, dict):
        if 'main' in i:
          lls += list(_traverse(i['main']))

  excludingList = ['vertical', 'dock', 'horizontal','tab', 'main', 'sizes','float']
  names = [i for i in lls if i not in excludingList if isinstance(i, str)]


  return names

def restoreLayout(mainWindow, layout):
  ## import all the ccpnModules classes specific for the application.
  # mainWindow.moduleArea._closeAll()

  if FileNames in layout:
    neededModules = getattr(layout, FileNames)
    if len(neededModules)>0:
      if GuiModules in layout:
        if ClassNameModuleName in layout.guiModules:
          classNameGuiModuleNameList = getattr(layout.guiModules, ClassNameModuleName)
          # Checks if  modules  are present in the layout file. If not stops it
          if not list(_traverse(classNameGuiModuleNameList)):
            return

          try:
            ccpnModules = _getAvailableModules(mainWindow, layout, neededModules)
            for classNameGuiModuleName in classNameGuiModuleNameList:
              if len(classNameGuiModuleName) == 2:
                className, guiModuleName = classNameGuiModuleName
                neededModules.append(className)
                _openCcpnModule(mainWindow, ccpnModules, className, moduleName=guiModuleName)

          except Exception as e:
            getLogger().warning("Failed to restore Layout")

  if LayoutState in layout:
    # Very important step:
    # Checks if the all the modules opened are present in the layout state. If not, will not restore the geometries
    state = getattr(layout, LayoutState)
    if not state:
      return
    namesFromState = _getModuleNamesFromState(state)
    openedModulesName =[i.name() for i in mainWindow.moduleArea.ccpnModules]
    compare = list( set(namesFromState) & set(openedModulesName))

    if len(openedModulesName)>0:
      if len(compare) == len(openedModulesName):
        try:
          mainWindow.moduleArea.restoreState(state)
        except Exception as e:
            getLogger().warning("Layout error: %s" % e)
      else:
        getLogger().warning("Layout error: Some of the modules are missing. Geometries could not be restored")