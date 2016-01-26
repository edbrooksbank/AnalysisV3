"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - : 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
               "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                 " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui, QtCore
from ccpncore.gui.Base import Base
from ccpncore.gui.Button import Button
from ccpncore.gui.CheckBox import CheckBox
from ccpncore.gui.DoubleSpinbox import DoubleSpinbox
from ccpncore.gui.Label import Label
from ccpncore.gui.ListWidget import ListWidget
from ccpncore.gui.PulldownList import PulldownList
from ccpncore.gui.Spinbox import Spinbox
import pyqtgraph as pg



class PolyBaseline(QtGui.QWidget, Base):


  def __init__(self, parent=None, current=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.current = current
    self.orderLabel = Label(self, 'Order ', grid=(0, 0))
    self.orderBox = Spinbox(self, grid=(0, 1))
    self.orderBox.setMinimum(2)
    self.orderBox.setMaximum(5)
    # self.orderBox.setValue(2)
    self.orderBox.valueChanged.connect(self.updateLayout)
    self.controlPointsLabel = Label(self, 'Control Points ', grid=(0, 2))
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 9), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    # self.mySignal1.connect(self.setSpinBoxSelected)
    self.currentBox = None
    self.linePoints = []


    self.updateLayout(self.orderBox.value())



  def updateLayout(self, value=None):
    if value < 6:
      for j in range(self.layout().rowCount()):
        for k in range(3, self.layout().columnCount()-1):
          item = self.layout().itemAtPosition(j, k)
          if item:
            if item.widget():
              item.widget().hide()
            self.layout().removeItem(item)
      self.controlPointBoxList = []
      self.controlPointBox1 = DoubleSpinbox(self, grid=(0, 3), showButtons=False)
      self.controlPointBoxList.append(self.controlPointBox1)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 4))
      self.controlPointBox2 = DoubleSpinbox(self, grid=(0, 5), showButtons=False)
      self.controlPointBoxList.append(self.controlPointBox2)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 6))
      self.controlPointBox3 = DoubleSpinbox(self, grid=(0, 7), showButtons=False)
      self.controlPointBoxList.append(self.controlPointBox3)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 8))
      if 2 < value <= 5:
        gridArray = [3+x for x in range(2*(value-2))]
        for i in range(0, len(gridArray), 2):
          self.controlPointBox = DoubleSpinbox(self, grid=(1, gridArray[i]), showButtons=False)
          self.controlPointBoxList.append(self.controlPointBox)
          self.ppmLabel = Label(self, 'ppm', grid=(1, gridArray[i+1]))
    else:
      pass


  def setValueInValueList(self):
    self.valueList = [controlPointBox.value() for controlPointBox in self.controlPointBoxList]


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')

  def setPositions(self, positions):
    if len(self.linePoints) < len(self.controlPointBoxList):
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      line.sigPositionChanged.connect(self.lineMoved)
      self.current.strip.plotWidget.addItem(line)
      self.linePoints.append(line)
      for i, line in enumerate(self.linePoints):
        self.controlPointBoxList[i].setValue(line.pos().x())
    else:
      print('No more lines can be added')


  def lineMoved(self, line):
    lineIndex = self.linePoints.index(line)
    self.controlPointBoxList[lineIndex].setValue(line.pos().x())


class NormaliseSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.project = project
    self.label = Label(self, 'Method ', grid=(0, 0))
    if spectra is None:
      spectra = [spectrum.pid for spectrum in project.spectra]
    self.lenSpectra = len(spectra)
    self.methodPulldownList = PulldownList(self, grid=(0, 1))
    self.coeffsLabel = Label(self, 'Coefficients', grid=(0, 2))
    self.coeffBoxes = []
    methods = ['Reference Peak',
               'Total Area',
               'PQN']
    self.methodPulldownList.setData(methods)

class AlignToReference(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.windowBoxes = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 0), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.region1 = DoubleSpinbox(self, grid=(0, 1))
    self.region2 = DoubleSpinbox(self, grid=(0, 2))
    self.regionBoxes = [self.region1, self.region2]
    self.linePoints = []
    self.lr = None


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    if self.lr:
      self.current.strip.plotWidget.addItem(self.lr)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    self.current.strip.plotWidget.removeItem(self.lr)

  def setPositions(self, positions):
    if len(self.linePoints) < 2:
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      self.current.strip.plotWidget.addItem(line)
      self.linePoints.append(line)
      for i, line in enumerate(self.linePoints):
        self.regionBoxes[i].setValue(line.pos().x())
    if len(self.linePoints) == 2:
      if not self.lr:
        self.lr = pg.LinearRegionItem(values=[self.linePoints[0].pos().x(), self.linePoints[1].pos().x()])

        self.current.strip.plotWidget.addItem(self.lr)
        self.lr.sigRegionChanged.connect(self.updateRegion)

  def updateRegion(self):
    region = self.lr.getRegion()
    self.regionBoxes[0].setValue(region[1])
    self.regionBoxes[1].setValue(region[0])


class AlignSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    spectrumLabel = Label(self, 'Spectrum', grid=(0, 0))
    spectrumPulldown = PulldownList(self, grid=(0, ))
    spectra = [spectrum.pid for spectrum in project.spectra]
    spectra.insert(0, '<All>')
    spectrumPulldown.setData(spectra)

class WhittakerBaseline(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    self.points = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 0), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.checkBoxLabel = Label(self, 'Auto', grid=(0, 1))
    self.checkBox = CheckBox(self, grid=(0, 2))
    self.checkBox.setChecked(False)
    self.aLabel = Label(self, 'a ', grid=(0, 3))
    self.aBox = DoubleSpinbox(self, grid=(0, 4))
    self.lamLabel = Label(self, 'lam ', grid=(0, 5))
    self.lamBox = DoubleSpinbox(self, grid=(0, 6))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    self.points.append(line.pos().x())

class SegmentalAlign(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    self.points = []
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 0), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    line.sigPositionChanged.connect(self.lineMoved)
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    self.points.append(line.pos().x())

class ExcludeBaselinePoints(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.pointLabel = Label(self, 'Exclusion Point ', grid=(0, 0))
    self.pointBox = Spinbox(self, grid=(0, 1), max=100000000000, min=-100000000000)
    self.pointBox.valueChanged.connect(self.setLinePosition)
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 2), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.multiplierLabel = Label(self, 'Baseline Multipler', grid=(0, 3))
    self.multiplierLabel = DoubleSpinbox(self, grid=(0, 4))
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.linePoint = pg.InfiniteLine(angle=0, pos=self.pointBox.value(), movable=True, pen=(255, 0, 100))
    self.current.strip.plotWidget.addItem(self.linePoint)
    self.pointBox.setValue(self.linePoint.pos().y())
    self.linePoint.hide()
    self.linePoint.sigPositionChanged.connect(self.lineMoved)


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.linePoint.show()

  def turnOffPositionPicking(self):
    print('picking off')
    self.linePoint.hide()

  def lineMoved(self):
    self.pointBox.setValue(self.linePoint.pos().y())

  def setLinePosition(self):
    self.linePoint.setPos(self.pointBox.value())

  def getParams(self):
    pass


class AlignSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.targetLabel = Label(self, 'Target Spectrum ', grid=(0, 0))
    self.targetPulldown = PulldownList(self, grid=(0, 1))
    spectra = [spectrum.pid for spectrum in project.spectra]
    spectra.insert(0, '<All>')
    self.targetPulldown.setData(spectra)


class Bin(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.binWidthLabel = Label(self, 'Bin Width (ppm) ', grid=(0, 0))
    self.binWidth = DoubleSpinbox(self, grid=(0, 1))


class Scale(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.methodLabel = Label(self, 'Method ', grid=(0, 0))
    self.methodPulldown = PulldownList(self, grid=(0, 1))
    methods = ['Unit Variance', 'Pareto']
    self.targetPulldown.setData(methods)

class ExcludeSignalFreeRegions(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.lamLabel = Label(self, 'lam ', grid=(0, 0))
    self.lamBox = DoubleSpinbox(self, grid=(0, 1))

class WhittakerSmooth(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    self.points = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, 'pick', grid=(0, 0), toggle=True)
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.checkBoxLabel = Label(self, 'Auto', grid=(0, 1))
    self.checkBox = CheckBox(self, grid=(0, 2))
    self.checkBox.setChecked(False)
    self.aLabel = Label(self, 'a ', grid=(0, 3))
    self.aBox = DoubleSpinbox(self, grid=(0, 4))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    self.points.append(line.pos().x())