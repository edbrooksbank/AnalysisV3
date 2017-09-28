from functools import partial

import pyqtgraph as pg
from PyQt4 import QtCore, QtGui

from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.modules.NmrResidueTable import NmrResidueTable
from ccpn.ui.gui.widgets.BarGraph import BarGraph, CustomViewBox
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.SpectraSelectionWidget import SpectraSelectionWidget
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.widgets.Base import Base
from ccpn.core.lib.Notifiers import Notifier
from ccpn.util.Colour import spectrumColours
from ccpn.ui.gui.widgets.Table import ObjectTable, Column
from ccpn.core.lib.peakUtils import getDeltaShiftsNmrResidue
from ccpn.core.lib import CcpnSorting

DefaultAtoms = ['H', 'N']

class CustomNmrResidueTable(NmrResidueTable):
  ''' Custon nmrResidue Table with extra Delta Shifts column'''
  deltaShiftsColumn = ('Delta Shifts', lambda nmrResidue: nmrResidue._deltaShift, '', None)

  columnDefs = [
    ('#', lambda nmrResidue: nmrResidue.serial, 'NmrResidue serial number', None),
    ('Index', lambda nmrResidue: NmrResidueTable._nmrIndex(nmrResidue), 'Index of NmrResidue in the NmrChain', None),
    ('Sequence', lambda nmrResidue: nmrResidue.sequenceCode, 'Sequence code of NmrResidue', None),
    ('Type', lambda nmrResidue: nmrResidue.residueType, 'NmrResidue type', None),
    ('Selected NmrAtoms', lambda nmrResidue: CustomNmrResidueTable._getSelectedNmrAtomNames(nmrResidue), 'NmrAtoms selected in NmrResidue', None),
    ('Selected Spectra count', lambda nmrResidue: CustomNmrResidueTable._getNmrResidueSpectraCount(nmrResidue)
     , 'Number of spectra selected for calculating the delta shift', None),
    ('Delta Shifts', lambda nmrResidue: nmrResidue._deltaShift, '', None),
    ('Comment', lambda nmr: NmrResidueTable._getCommentText(nmr), 'Notes', lambda nmr, value: NmrResidueTable._setComment(nmr, value))
  ]

  # columnDefs = NmrResidueTable.columnDefs+[deltaShiftsColumn,]
  # columnDefs[-1], columnDefs[-2] = columnDefs[-2], columnDefs[-1]

  def __init__(self, parent, application, actionCallback=None, selectionCallback=None, nmrChain=None, **kwds):

    NmrResidueTable.__init__(self, parent=parent, application=application,
                             actionCallback=actionCallback, selectionCallback=selectionCallback, nmrChain=nmrChain, **kwds)
    self.NMRcolumns = [Column(colName, func, tipText=tipText, setEditValue=editValue) for
                       colName, func, tipText, editValue in self.columnDefs]



  @staticmethod
  def _getNmrResidueSpectraCount(nmrResidue):

    """
    CCPN-INTERNAL: Insert an index into ObjectTable
    """
    try:
      return nmrResidue.spectraCount
    except:
      return None

  @staticmethod
  def _getSelectedNmrAtomNames(nmrResidue):

    """
    CCPN-INTERNAL: Insert an index into ObjectTable
    """
    try:
      return ', '.join(nmrResidue.selectedNmrAtomNames)
    except:
      return None

class ChemicalShiftsMapping(CcpnModule):

  includeSettingsWidget = True
  maxSettingsState = 2  # states are defined as: 0: invisible, 1: both visible, 2: only settings visible
  settingsPosition = 'left'
  className = 'ChemicalShiftsMapping'

  def __init__(self, mainWindow, name='Chemical Shift Mapping', nmrChain= None, **kw):
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name, settingButton=True)

    BarGraph.mouseClickEvent = self._mouseClickEvent
    BarGraph.mouseDoubleClickEvent = self._mouseDoubleClickEvent


    self.mainWindow = mainWindow
    self.application = None
    self.atoms = set()
    self.atomCheckBoxes = []
    if self.mainWindow is not None:
      self.project = self.mainWindow.project
      self.application = self.mainWindow.application
      self.current = self.application.current

      if len(self.project.nmrResidues):

        for i in self.project.nmrResidues:
          for j in i.nmrAtoms:
            self.atoms.add(j.name)

    if nmrChain is not None:
      self.setNmrChain(nmrChain)

    self._setWidgets()
    self._setSettingsWidgets()

    self._selectCurrentNmrResiduesNotifier = Notifier(self.current , [Notifier.CURRENT] , targetName='nmrResidues'
                                                     , callback=self._selectCurrentNmrResiduesNotifierCallback)



  def _setWidgets(self):
    # self.barGraphWidget = BarGraphWidget(self.mainWidget, xValues=None, yValues=None, objects=None, grid=(0, 0))
    if self.application:

      self.nmrResidueTable = CustomNmrResidueTable(parent=self.mainWidget, application=self.application,  setLayout=True, grid=(1, 0))
      self.nmrResidueTable.displayTableForNmrChain = self._displayTableForNmrChain




  def _setSettingsWidgets(self):
    # self.settingsWidget.getLayout().setAlignment(QtCore.Qt.AlignTop)
    i = 0
    self.inputLabel = Label(self.settingsWidget, text='Select input', grid=(i, 0), vAlign='t')
    self.spectraSelectionWidget = SpectraSelectionWidget(self.settingsWidget, mainWindow=self.mainWindow, grid=(i,1), gridSpan=(i,1))
    i += 1
    self.atomLabel = Label(self.settingsWidget,text='Select atoms', grid=(i,0))
    for atom in sorted(self.atoms, key=CcpnSorting.stringSortKey):
      self.atomCheckBox = CheckBox(self.settingsWidget, text=atom, checked=True, grid=(i,1))
      if atom in DefaultAtoms:
        self.atomCheckBox.setChecked(True)
      else:
        self.atomCheckBox.setChecked(False)
      self.atomCheckBoxes.append(self.atomCheckBox)
      i += 1

    # i += 1
    self.aboveThresholdColourLabel =  Label(self.settingsWidget,text='Above Threshold Colour', grid=(i,0))
    self.aboveThresholdColourBox = PulldownList(self.settingsWidget,  grid=(i, 1))
    for item in spectrumColours.items():
      pix = QtGui.QPixmap(QtCore.QSize(20, 20))
      pix.fill(QtGui.QColor(item[0]))
      self.aboveThresholdColourBox.addItem(icon=QtGui.QIcon(pix), text=item[1])

    i += 1
    self.belowThresholdColourLabel = Label(self.settingsWidget, text='Below Threshold Colour', grid=(i, 0))
    self.belowThresholdColourBox = PulldownList(self.settingsWidget, grid=(i, 1))
    for item in spectrumColours.items():
      pix = QtGui.QPixmap(QtCore.QSize(20, 20))
      pix.fill(QtGui.QColor(item[0]))
      self.belowThresholdColourBox.addItem(icon=QtGui.QIcon(pix), text=item[1])

    i += 1
    self.updateButton = Button(self.settingsWidget, text='refresh', callback=self.updateModule, grid=(i, 0))

  def updateTable(self, nmrChain):
    self.nmrResidueTable.ncWidget.select(nmrChain.pid)
    self.nmrResidueTable.setColumns(self.nmrResidueTable.NMRcolumns)

    self.nmrResidueTable.setObjects([nr for nr in nmrChain.nmrResidues if nr._deltaShift])
    self.nmrResidueTable._selectOnTableCurrentNmrResidues(self.current.nmrResidues)

  def _displayTableForNmrChain(self, nmrChain):
    self.updateModule()
    self.updateTable(nmrChain)


  def updateModule(self):

    selectedAtomNames = [cb.text() for cb in self.atomCheckBoxes if cb.isChecked()]


    if self.nmrResidueTable.nmrChain:
      for nmrResidue in self.nmrResidueTable.nmrChain.nmrResidues:
        spectra = self.spectraSelectionWidget.getSelections()
        nmrResidue.spectraCount = len(spectra)
        nmrResidueAtoms = [atom.name for atom in nmrResidue.nmrAtoms]
        nmrResidue.selectedNmrAtomNames =  [atom for atom in nmrResidueAtoms if atom in selectedAtomNames]
        nmrResidue._deltaShift = getDeltaShiftsNmrResidue(nmrResidue, selectedAtomNames, spectra=spectra)
      self.updateTable(self.nmrResidueTable.nmrChain)

  def setNmrChain(self, nmrChain):
    if nmrChain:
      shifts = []
      sequenceCode = []
      nmrResidues = []
      for nmrResidue in nmrChain.nmrResidues:
        shifts += [nmrResidue._deltaShift,]
        sequenceCode += [int(nmrResidue.sequenceCode), ]
        nmrResidues += [nmrResidue, ]

      self.barGraphWidget = BarGraphWidget(self.mainWidget, xValues=sequenceCode, yValues=shifts, objects=nmrResidues, grid=(0, 0))

  def _selectCurrentNmrResiduesNotifierCallback(self, data):
    for bar in self.barGraphWidget.barGraphs:
      for label in bar.labels:
        if label.data(int(label.text())) is not None:
          if self.application is not None:

            if label.data(int(label.text())) in self.current.nmrResidues:
              label.setSelected(True)
            else:
              label.setSelected(False)


  def _mouseClickEvent(self, event):

    position = event.pos().x()
    self.clicked = int(position)
    if event.button() == QtCore.Qt.LeftButton:
      for bar in self.barGraphWidget.barGraphs:
        for label in bar.labels:
          if label.text() == str(self.clicked):
            print(label.data(self.clicked))
            self.current.nmrResidue = label.data(self.clicked)
            label.setSelected(True)

      event.accept()

  def _mouseDoubleClickEvent(self, event):
    from ccpn.ui.gui.lib.Strip import navigateToNmrResidueInDisplay

    self.application.ui.mainWindow.clearMarks()
    position = event.pos().x()
    self.doubleclicked = int(position)
    if event.button() == QtCore.Qt.LeftButton:
      for bar in self.barGraphWidget.barGraphs:
        for label in bar.labels:
          if label.text() == str(self.doubleclicked):
           nmrResidue =  label.data(self.doubleclicked)
           if nmrResidue:

             if self.current.strip is not None:
               strip = self.current.strip
               navigateToNmrResidueInDisplay(nmrResidue, strip.spectrumDisplay, stripIndex=0,
                                             widths=['default'] * len(strip.axisCodes))

             else:
               print('Impossible to navigate to peak position. Set a current strip first')



  def close(self):
    """
    Close the table from the commandline
    """
    self._closeModule()

  def _closeModule(self):
    """
    Re-implementation of closeModule function from CcpnModule to unregister notification on current
    """
    if self._selectCurrentNmrResiduesNotifier is not None:
      self._selectCurrentNmrResiduesNotifier.unRegister()

    super(ChemicalShiftsMapping, self)._closeModule()



class BarGraphWidget(Widget, Base):

  def __init__(self, parent, xValues=None, yValues=None, colour='r', objects=None, **kw):
    Widget.__init__(self, parent)
    Base.__init__(self, **kw)
    self._setViewBox()
    self._setLayout()

    self.xLine = None
    self.barGraphs = []

    self.xValues = xValues
    self.yValues = yValues
    self.objects = objects
    self.colour = colour
    self.setData(xValues=xValues,yValues=yValues, objects=objects,colour=colour,replace=True)


    self._addExtraItems()
    self.updateViewBoxLimits()

  def _setViewBox(self):
    self.customViewBox = CustomViewBox()
    self.customViewBox.setMenuEnabled(enableMenu=False)  # override pg default context menu
    self.plotWidget = pg.PlotWidget(viewBox=self.customViewBox, background='w')
    self.customViewBox.setParent(self.plotWidget)

  def _setLayout(self):
    hbox = QtGui.QHBoxLayout()
    self.setLayout(hbox)
    hbox.addWidget(self.plotWidget)

  def _addExtraItems(self):
    # self.addLegend()
    self.addThresholdLine()


  def setData(self, xValues, yValues, objects, colour, replace=True):
    if replace:
      self.barGraphs = []
      self.customViewBox.clear()

    self.barGraph = BarGraph(viewBox=self.customViewBox, xValues=xValues, yValues=yValues, objects=objects,
                  brush=colour)
    self.barGraphs.append(self.barGraph)
    self.customViewBox.addItem(self.barGraph)
    self.xValues = xValues
    self.yValues = yValues
    self.objects = objects

    # self._lineMoved()

  def setViewBoxLimits(self, xMin, xMax, yMin, yMax):
    self.customViewBox.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)

  def updateViewBoxLimits(self):
    '''Updates with default paarameters. Minimum values to show the data only'''
    if self.xValues and self.yValues:
      self.customViewBox.setLimits(xMin=min(self.xValues)/2, xMax=max(self.xValues) + (max(self.xValues) * 0.5),
                                   yMin=min(self.yValues)/2 ,yMax=max(self.yValues) + (max(self.yValues) * 0.5))



  def clearBars(self):
    self.barGraphs = []
    for item in self.customViewBox.addedItems:
      if not isinstance(item, pg.InfiniteLine):
        self.customViewBox.removeItem(item)

  def addThresholdLine(self):

    self.xLine = pg.InfiniteLine(angle=0, movable=True, pen='b')
    self.customViewBox.addItem(self.xLine)
    if self.yValues is not None:
      if len(self.yValues)>0:
        self.xLine.setPos(min(self.yValues))
    self.showThresholdLine(False)
    self._lineMoved()
    self.xLine.sigPositionChangeFinished.connect(self._lineMoved)

  def showThresholdLine(self, value=True):
    if value:
      self.xLine.show()
    else:
      self.xLine.hide()

  def _lineMoved(self):
    self.clearBars()

    aboveX = []
    aboveY = []
    aboveObjects = []
    belowX = []
    belowY = []
    belowObjects = []

    pos = self.xLine.pos().y()
    if self.xValues:
      for x,y,obj in zip(self.xValues, self.yValues, self.objects):
        if y > pos:
          aboveY.append(y)
          aboveX.append(x)
          aboveObjects.append(obj)
        else:
          belowX.append(x)
          belowY.append(y)
          belowObjects.append(obj)



      self.aboveThreshold = BarGraph(viewBox=self.customViewBox, xValues=aboveX, yValues=aboveY, objects=aboveObjects,
                    brush='g')
      self.belowTrheshold = BarGraph(viewBox=self.customViewBox, xValues=belowX, yValues=belowY, objects=belowObjects,
                    brush='r')
      self.customViewBox.addItem(self.aboveThreshold)
      self.customViewBox.addItem(self.belowTrheshold)
      self.barGraphs.append(self.aboveThreshold)
      self.barGraphs.append(self.belowTrheshold)
      self.updateViewBoxLimits()

    for bar in self.barGraphs:
      bar.viewBox.showAboveThreshold()

  def addLegend(self):
    self.legendItem = pg.LegendItem((100, 60), offset=(70, 30))  # args are (size, offset)
    self.legendItem.setParentItem(self.customViewBox.graphicsItem())

  def addLegendItem(self, pen='r', name=''):
    c = self.plotWidget.plot(pen=pen, name=name)
    self.legendItem.addItem(c, name)

  def showLegend(self, value:False):
    if value:
      self.legendItem.show()
    else:
     self.legendItem.hide()

  def _updateGraph(self):
    self.customViewBox.clear()





#######################################################################################################
####################################      Mock DATA TESTING    ########################################
#######################################################################################################

from collections import namedtuple
import random

nmrResidues = []
for i in range(30):
  nmrResidue = namedtuple('nmrResidue', ['sequenceCode','peaksShifts'])
  nmrResidue.__new__.__defaults__ = (0,)
  nmrResidue.sequenceCode = i
  nmrResidue.peaksShifts = random.uniform(1.5, 3.9)
  nmrResidues.append(nmrResidue)

nmrChain = namedtuple('nmrChain', ['nmrResidues'])
nmrChain.nmrResidues = nmrResidues




if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea

  app = TestApplication()
  win = QtGui.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None, )
  chemicalShiftsMapping = ChemicalShiftsMapping(mainWindow=None, nmrChain=nmrChain)
  moduleArea.addModule(chemicalShiftsMapping)




  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % chemicalShiftsMapping.moduleName)
  win.show()

  app.start()
