#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:04 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon1 $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore

from ccpn.ui.gui.modules.GuiTableGenerator import GuiTableGenerator
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.widgets.Spacer import Spacer
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.CompoundWidgets import CheckBoxCompoundWidget
from ccpn.ui.gui.widgets.CompoundWidgets import ListCompoundWidget
from ccpn.ui.gui.widgets.Table import ObjectTable, Column, ColumnViewSettings,  ObjectTableFilter
from ccpn.core.lib.Notifiers import Notifier
from ccpn.ui.gui.widgets.PulldownListsForObjects import RestraintsPulldown
from ccpn.core.RestraintList import RestraintList

from ccpn.util.Logging import getLogger
logger = getLogger()
ALL = '<all>'


class RestraintTableModule(CcpnModule):
  """
  This class implements the module by wrapping a restaintsTable instance
  """
  includeSettingsWidget = True
  maxSettingsState = 2  # states are defined as: 0: invisible, 1: both visible, 2: only settings visible
  settingsOnTop = True

  className = 'RestraintTableModule'

  # we are subclassing this Module, hence some more arguments to the init
  def __init__(self, mainWindow, name='Restraint Table', restraintLists=None):
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name)

    # Derive application, project, and current from mainWindow
    self.mainWindow = mainWindow
    self.application = mainWindow.application
    self.project = mainWindow.application.project
    self.current = mainWindow.application.current

    # if not restraintLists:
    #   if self.project is None:
    #     restraintLists = []
    #   else:
    #     restraintLists = self.project.restraintLists
    #
    # self.restraintLists = restraintLists
    self.itemPid = itemPid = restraintLists

    # Put all of the NmrTable settings in a widget, as there will be more added in the PickAndAssign, and
    # backBoneAssignment modules
    self._NTSwidget = Widget(self.settingsWidget, setLayout=True,
                             grid=(0,0), vAlign='top', hAlign='left')
    #self._NTSwidget = self.settingsWidget

    # cannot set a notifier for displays, as these are not (yet?) implemented and the Notifier routines
    # underpinning the addNotifier call do not allow for it either

    #FIXME:ED - need to check label text and function of these
    colwidth = 140
    self.displaysWidget = ListCompoundWidget(self._NTSwidget,
                                             grid=(0,0), vAlign='top', stretch=(0,0), hAlign='left',
                                             vPolicy='minimal',
                                             #minimumWidths=(colwidth, 0, 0),
                                             fixedWidths=(colwidth, colwidth, colwidth),
                                             orientation = 'left',
                                             labelText='Display(s):',
                                             tipText = 'SpectrumDisplay modules to respond to double-click',
                                             texts=[ALL] + [display.pid for display in self.application.ui.mainWindow.spectrumDisplays]
                                             )
    self.displaysWidget.setFixedHeigths((None, None, 40))

    self.sequentialStripsWidget = CheckBoxCompoundWidget(
                                             self._NTSwidget,
                                             grid=(1,0), vAlign='top', stretch=(0,0), hAlign='left',
                                             #minimumWidths=(colwidth, 0),
                                             fixedWidths=(colwidth, 30),
                                             orientation = 'left',
                                             labelText = 'Show sequential strips:',
                                             checked = False
                                            )

    self.markPositionsWidget = CheckBoxCompoundWidget(
                                             self._NTSwidget,
                                             grid=(2,0), vAlign='top', stretch=(0,0), hAlign='left',
                                             #minimumWidths=(colwidth, 0),
                                             fixedWidths=(colwidth, 30),
                                             orientation = 'left',
                                             labelText = 'Mark positions:',
                                             checked = True
                                            )
    self.autoClearMarksWidget = CheckBoxCompoundWidget(
                                             self._NTSwidget,
                                             grid=(3,0), vAlign='top', stretch=(0,0), hAlign='left',
                                             #minimumWidths=(colwidth, 0),
                                             fixedWidths=(colwidth, 30),
                                             orientation = 'left',
                                             labelText = 'Auto clear marks:',
                                             checked = True
                                            )

    self.restraintTable = RestraintTable(parent=self.mainWidget
                                        , setLayout=True
                                        , application=self.application
                                        , moduleParent=self
                                        , grid=(0,0))
    # settingsWidget
    self.displayColumnWidget = ColumnViewSettings(parent=self._NTSwidget, table=self.restraintTable, grid=(4, 0))
    self.searchWidget = ObjectTableFilter(parent=self._NTSwidget, table=self.restraintTable, grid=(5, 0))

  def _getDisplays(self):
    "return list of displays to navigate; done so BackboneAssignment module can subclass"
    displays = []
    # check for valid displays
    gids = self.displaysWidget.getTexts()
    if len(gids) == 0: return displays
    if ALL in gids:
        displays = self.application.ui.mainWindow.spectrumDisplays
    else:
        displays = [self.application.getByGid(gid) for gid in gids if gid != ALL]
    return displays

  def _getDisplayColumnWidget(self):
    " CCPN-INTERNAL: used to get displayColumnWidget"
    return self.displayColumnWidget

  def _getSearchWidget(self):
    " CCPN-INTERNAL: used to get searchWidget"
    return self.searchWidget


class RestraintTable(ObjectTable):
  columnDefs = [('#', '_key', 'Restraint Id', None),
                 ('Atoms', lambda restraint:RestraintTable._getContributions(RestraintTable, restraint),
                  'Atoms involved in the restraint', None),
                 ('Target Value.', 'targetValue', 'Target value for the restraint', None),
                 ('Upper Limit', 'upperLimit', 'Upper limit for the restraint', None),
                 ('Lower Limit', 'lowerLimit', 'Lower limit or the restraint', None),
                 ('Error', 'error', 'Error on the restraint', None),
                 ('Peaks', lambda restraint:'%3d ' % RestraintTable._getRestraintPeakCount(RestraintTable, restraint),
                  'Number of peaks used to derive this restraint', None),
                 # ('Peak count', lambda chemicalShift: '%3d ' % self._getShiftPeakCount(chemicalShift))
                ('Comment', lambda restraint:RestraintTable._getCommentText(restraint), 'Notes',
                 lambda restraint, value:RestraintTable._setComment(restraint, value))
                ]

  className = 'RestraintTable'
  attributeName = 'restraintLists'

  def __init__(self, parent, application, moduleParent, itemPid=None, **kwds):
    self.moduleParent = moduleParent
    self._application = application
    self._project = application.project
    self._current = application.current
    kwds['setLayout'] = True  ## Assure we have a layout with the widget
    self._widget = Widget(parent=parent, **kwds)
    self.restraintList = None

    # create the column objects
    columns = [Column(colName, func, tipText=tipText, setEditValue=editValue) for colName, func, tipText, editValue in self.columnDefs]

    # create the table; objects are added later via the displayTableForRestraints method
    self.spacer = Spacer(self._widget, 5, 5
                         , QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
                         , grid=(0, 0), gridSpan=(1, 1))
    self.stWidget = RestraintsPulldown(parent=self._widget
                                     , project=self._project, default=0
                                     , grid=(1,0), gridSpan=(1,1), minimumWidths=(0,100)
                                     , showSelectName=True
                                     , callback=self._selectionPulldownCallback)
    self.spacer = Spacer(self._widget, 5, 5
                         , QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
                         , grid=(2, 0), gridSpan=(1, 1))
    ObjectTable.__init__(self, parent=self._widget, setLayout=True,
                         columns=columns, objects=[],
                         autoResize=True,
                         selectionCallback=self._selectionCallback,
                         actionCallback=self._actionCallback,
                         grid=(3, 0), gridSpan=(1, 6)
                         )

    self._restraintNotifier = Notifier(self._project
                                   , [Notifier.CREATE, Notifier.DELETE, Notifier.RENAME]
                                   , RestraintList.__name__
                                   , self._updateCallback)
    #TODO: see how to handle peaks as this is too costly at present
    # Notifier object to update the table if the peaks change
    self._peaksNotifier = None
    # self._peaksNotifier = Notifier(self._project,
    #                                [Notifier.CREATE, Notifier.DELETE, Notifier.RENAME], 'Peak',
    #                                 self._updateCallback
    #                                )
    self._updateSilence = False  # flag to silence updating of the table

    # if self.itemPid:
    #   self.thisObj = self._project.getByPid(self.itemPid)
    #   self.displayTableForRestraint(self.thisObj)

  # def addWidgetToTop(self, widget, col=2, colSpan=1):
  #   "Convenience to add a widget to the top of the table; col >= 2"
  #   if col < 2:
  #     raise RuntimeError('Col has to be >= 2')
  #   self._widget.getLayout().addWidget(widget, 0, col, 1, colSpan)

  def displayTableForRestraint(self, restraintList):
    "Display the table for all Restraints"

    # if self._restraintNotifier is not None:
    #   # we have a new nmrChain and hence need to unregister the previous notifier
    #   self._restraintNotifier.unRegister()
    # # register a notifier for this structureEnsemble
    # self._restraintNotifier = Notifier(restraint,
    #                                [Notifier.CREATE, Notifier.DELETE, Notifier.RENAME], 'Restraint',
    #                                 self._updateCallback
    #                               )

    self.stWidget.select(restraintList.pid)
    self._update(restraintList)

  def _updateCallback(self, data):
    "callback for updating the table"
    thisRestraintList = getattr(data[Notifier.THEOBJECT], self.attributeName)   # get the restraintList
    if self.restraintList in thisRestraintList:
      self.displayTableForRestraint(self.restraintList)
    else:
      self.clearTable()

  def _update(self, RestraintList):
    "Update the table"
    if not self._updateSilence:
      self.clearTable()
      self._silenceCallback = True
      self.setObjects(RestraintList.restraints)
      self._updateSettingsWidgets()
      self._silenceCallback = False
      self.show()

  def setUpdateSilence(self, silence):
    "Silences/unsilences the update of the table until switched again"
    self._updateSilence = silence

  def _selectionCallback(self, restraint, row, col):
    "Callback for selecting a row in the table"
    self._current.restraint = restraint

  def _actionCallback(self, atomRecordTuple, row, column):
    print(atomRecordTuple, row, column)

  def _selectionPulldownCallback(self, item):
    "Callback for selecting Restraint"
    self.restraintList = self._project.getByPid(item)
    # print('>selectionPulldownCallback>', item, type(item), nmrChain)
    if self.restraintList is not None:
      # self.thisDataSet = self._getAttachedDataSet(item)
      self.displayTableForRestraint(self.restraintList)
    else:
      self.clearTable()

  def destroy(self):
    "Cleanup of self"
    if self._restraintNotifier is not None:
      self._restraintNotifier.unRegister()
    if self._peaksNotifier is not None:
      self._peaksNotifier.unRegister()

  def navigateToRestraintInDisplay(restraint, display, stripIndex=0, widths=None,
                                    showSequentialStructures=False, markPositions=True):

    getLogger().debug('display=%r, nmrResidue=%r, showSequentialResidues=%s, markPositions=%s' %
                      (display.id, restraint.id, showSequentialStructures, markPositions)
                      )
    return None

  def _getContributions(self, restraint):
    """return number of peaks assigned to NmrAtom in Experiments and PeakLists
    using ChemicalShiftList"""
    if restraint.restraintContributions[0].restraintItems:
      return ' - '.join(restraint.restraintContributions[0].restraintItems[0])

  def _getRestraintPeakCount(self, restraint):
    """return number of peaks assigned to NmrAtom in Experiments and PeakLists
    using ChemicalShiftList"""
    peaks = restraint.peaks
    if peaks:
      return len(peaks)
    else:
      return 0

  def _callback(self):
    pass

  def _updateSettingsWidgets(self):
    ''' update settings Widgets according with the new displayed table '''
    displayColumnWidget = self.moduleParent._getDisplayColumnWidget()
    displayColumnWidget.updateWidgets(self)
    searchWidget = self.moduleParent._getSearchWidget()
    searchWidget.updateWidgets(self)

  @staticmethod
  def _getCommentText(chemicalShift):
    if chemicalShift.comment == '' or not chemicalShift.comment:
      return ' '
    else:
      return chemicalShift.comment

  @staticmethod
  def _setComment(chemicalShift, value):
    chemicalShift.comment = value

#
#     tipTexts = ['Restraint Id',
#                 'Atoms involved in the restraint',
#                 'Target value for the restraint',
#                 'Upper limit for the restraint',
#                 'Lower limitf or the restraint',
#                 'Error on the restraint',
#                 'Number of peaks used to derive this restraint'
#                 ]

# class RestraintTable(CcpnModule):
#   def __init__(self, mainWindow=None, name='Restraint Table', restraintLists=None, **kw):
#     CcpnModule.__init__(self, mainWindow=mainWindow, name=name)
# 
#     self.mainWindow = mainWindow
#     self.application = mainWindow.application
#     self.project = mainWindow.application.project
#     self.current = mainWindow.application.current
# 
#     project = kw.get('project')
# 
#     if not restraintLists:
#       if project is None:
#         restraintLists = []
#       else:
#         restraintLists = project.restraintLists
# 
#     self.restraintLists = restraintLists
# 
#     self._NTSwidget = Widget(self.settingsWidget, setLayout=True,
#                              grid=(0,0), vAlign='top', hAlign='left')
# 
#     # cannot set a notifier for displays, as these are not (yet?) implemented and the Notifier routines
#     # underpinning the addNotifier call do not allow for it either
# 
#     #FIXME:ED - need to check label text and function of these
#     colwidth = 140
#     self.displaysWidget = ListCompoundWidget(self._NTSwidget,
#                                              grid=(0,0), vAlign='top', stretch=(0,0), hAlign='left',
#                                              vPolicy='minimal',
#                                              #minimumWidths=(colwidth, 0, 0),
#                                              fixedWidths=(colwidth, colwidth, colwidth),
#                                              orientation = 'left',
#                                              labelText='Display(s):',
#                                              tipText = 'ResidueList modules to respond to double-click',
#                                              texts=[ALL] + [display.pid for display in self.application.ui.mainWindow.spectrumDisplays]
#                                              )
#     self.displaysWidget.setFixedHeigths((None, None, 40))
# 
#     self.sequentialStripsWidget = CheckBoxCompoundWidget(
#                                              self._NTSwidget,
#                                              grid=(1,0), vAlign='top', stretch=(0,0), hAlign='left',
#                                              #minimumWidths=(colwidth, 0),
#                                              fixedWidths=(colwidth, 30),
#                                              orientation = 'left',
#                                              labelText = 'Show sequential strips:',
#                                              checked = False
#                                             )
# 
#     self.markPositionsWidget = CheckBoxCompoundWidget(
#                                              self._NTSwidget,
#                                              grid=(2,0), vAlign='top', stretch=(0,0), hAlign='left',
#                                              #minimumWidths=(colwidth, 0),
#                                              fixedWidths=(colwidth, 30),
#                                              orientation = 'left',
#                                              labelText = 'Mark positions:',
#                                              checked = True
#                                             )
#     self.autoClearMarksWidget = CheckBoxCompoundWidget(
#                                              self._NTSwidget,
#                                              grid=(3,0), vAlign='top', stretch=(0,0), hAlign='left',
#                                              #minimumWidths=(colwidth, 0),
#                                              fixedWidths=(colwidth, 30),
#                                              orientation = 'left',
#                                              labelText = 'Auto clear marks:',
#                                              checked = True
#                                             )
# 
# 
# 
# 
#     label = Label(self, "Restraint List:")
#     widget1 = QtGui.QWidget(self)
#     widget1.setLayout(QtGui.QGridLayout())
#     widget1.layout().addWidget(label, 0, 0, QtCore.Qt.AlignLeft)
#     self.restraintListPulldown = PulldownList(self, grid=(0, 1))
#     widget1.layout().addWidget(self.restraintListPulldown, 0, 1)
#     self.layout.addWidget(widget1, 0, 0)
# 
#     columns = [('#', '_key'),
#                ('Atoms', lambda restraint: self._getContributions(restraint)),
#                ('Target Value.', 'targetValue'),
#                ('Upper Limit', 'upperLimit'),
#                ('Lower Limit', 'lowerLimit'),
#                ('Error', 'error'),
#                ('Peaks', lambda restraint: '%3d ' % self._getRestraintPeakCount(restraint))
#                # ('Peak count', lambda chemicalShift: '%3d ' % self._getShiftPeakCount(chemicalShift))
#                ]
# 
#     tipTexts = ['Restraint Id',
#                 'Atoms involved in the restraint',
#                 'Target value for the restraint',
#                 'Upper limit for the restraint',
#                 'Lower limitf or the restraint',
#                 'Error on the restraint',
#                 'Number of peaks used to derive this restraint '
#                 ]
# 
#     self.restraintTable = GuiTableGenerator(self.mainWidget, restraintLists,
#                                                 actionCallback=self._callback, columns=columns,
#                                                 selector=self.restraintListPulldown,
#                                                 tipTexts=tipTexts, objectType='restraints')
# 
#     newLabel = Label(self, '', grid=(2, 0))
#     self.layout.addWidget(self.restraintTable, 3, 0, 1, 4)
# 
#     self.mainWidget.setContentsMargins(5, 5, 5, 5)    # ejb - put into CcpnModule?
# 
# 
#   def _getContributions(self, restraint):
#     """return number of peaks assigned to NmrAtom in Experiments and PeakLists
#     using ChemicalShiftList"""
#     if restraint.restraintContributions[0].restraintItems:
#       return ' - '.join(restraint.restraintContributions[0].restraintItems[0])
#
#
#   def _getRestraintPeakCount(self, restraint):
#     """return number of peaks assigned to NmrAtom in Experiments and PeakLists
#     using ChemicalShiftList"""
#     peaks = restraint.peaks
#     if peaks:
#       return len(peaks)
#     else:
#       return 0
#
#   def _callback(self):
#     pass
# 
