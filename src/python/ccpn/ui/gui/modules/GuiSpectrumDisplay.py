"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================
__author__ = 'simon'

import importlib, os

from PyQt4 import QtGui, QtCore

from ccpn.core.Project import Project
from ccpn.core.Peak import Peak

# from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import DataSource as ApiDataSource
# from ccpnmodel.ccpncore.api.ccp.nmr.Nmr import Peak as ApiPeak

from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import SpectrumView as ApiSpectrumView
# from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import StripSpectrumView as ApiStripSpectrumView
# from ccpnmodel.ccpncore.api.ccpnmr.gui.Task import StripPeakListView as ApiStripPeakListView

# from ccpn.ui.gui.widgets.Frame import Frame as CoreFrame
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.ToolBar import ToolBar

import typing

from ccpn.ui.gui.DropBase import DropBase
from ccpn.ui.gui.base.Frame import Frame as GuiFrame
from ccpn.ui.gui.base.PhasingFrame import PhasingFrame
from ccpn.ui.gui.modules.GuiModule import GuiModule
from ccpn.ui.gui.widgets.SpectrumToolBar import SpectrumToolBar

# from ccpn.ui.gui.util.Svg import Svg

# def _findPpmRegion(spectrum, axisDim, spectrumDim):
#
#   pointCount = spectrum.pointCounts[spectrumDim]
#   if axisDim < 2: # want entire region
#     region = (0, pointCount)
#   else:
#     n = pointCount // 2
#     region = (n, n+1)
#
#   firstPpm, lastPpm = spectrum.getDimValueFromPoint(spectrumDim, region)
#
#   return 0.5*(firstPpm+lastPpm), abs(lastPpm-firstPpm)


class GuiSpectrumDisplay(DropBase, GuiModule):

  def __init__(self):
    GuiModule.__init__(self)
    # DropBase.__init__(self, self._appBase, self.dropCallback)
    self.setAcceptDrops(True)
    self.closeDock = self._closeDock
    self.spectrumToolBar = SpectrumToolBar(self.dock, widget=self)#, grid=(0, 0), gridSpan=(1, 2))
    self.dock.addWidget(self.spectrumToolBar, 0, 0, 1, 2)#, grid=(0, 0), gridSpan=(1, 2))
    self.dock.label.closeButton.clicked.connect(self.closeDock)
    self.spectrumToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    # screenWidth = QtGui.QApplication.desktop().screenGeometry().width()
    # self.spectrumToolBar.setFixedWidth(screenWidth*0.5)
    self.resize(self.sizeHint())


    self.spectrumUtilToolBar = ToolBar(self.dock)#, grid=(0, 2), gridSpan=(1, 2))
    # self.spectrumUtilToolBar.setFixedWidth(screenWidth*0.4)
    self.spectrumUtilToolBar.setFixedHeight(self.spectrumToolBar.height())
    # grid=(0, 2), gridSpan=(1, 1))
    self.dock.addWidget(self.spectrumUtilToolBar, 0, 2)
    if self._appBase.preferences.general.toolbarHidden is True:
      self.spectrumUtilToolBar.hide()
    else:
      self.spectrumUtilToolBar.show()
    # toolBarColour = QtGui.QColor(214,215,213)
    self.positionBox = Label(self.dock)
    self.dock.addWidget(self.positionBox, 0, 3)
    self.scrollArea = ScrollArea(self.dock, grid=(1, 0), gridSpan=(1, 4))
    self.scrollArea.setWidgetResizable(True)
    self.stripFrame = GuiFrame(self.scrollArea, grid=(0, 0), appBase=self._appBase)
    self.stripFrame.guiSpectrumDisplay = self
    self.stripFrame.setAcceptDrops(True)
    self.scrollArea.setWidget(self.stripFrame)

    
    self.setEnabled(True)

    includeDirection = not self._wrappedData.is1d
    self.phasingFrame = PhasingFrame(self.dock, includeDirection=includeDirection, callback=self._updatePhasing, returnCallback=self._updatePivot,
                                     directionCallback=self._changedPhasingDirection, grid=(2, 0), gridSpan=(1, 3))
    self.phasingFrame.setVisible(False)


  def printToFile(self, path, width=800, height=800):

    #generator = QtSvg.QSvgGenerator()
    #generator.setFileName(path)
    #generator.setSize(QtCore.QSize(1600, 1600)) # TBD
    #generator.setViewBox(QtCore.QRect(0, 0, 1600, 1600))
    #if title:
    #  generator.setTitle(title)

    #painter = QtGui.QPainter()
    #painter.begin(generator)
    #self.plotWidget.scene().render(painter)
    #painter.end()
    
    nstrips = len(self.strips)
    if nstrips == 0:
      return
    # with open(path, 'wt') as fp:
    #   printer = Svg(fp, width, height) # TBD: more general
    #
    #   # box
    #   printer.writeLine(0, 0, width, 0)
    #   printer.writeLine(width, 0, width, height)
    #   printer.writeLine(width, height, 0, height)
    #   printer.writeLine(0, height, 0, 0)
    #
    #   for n, strip in enumerate(self.strips):
    #     # TBD need to calculate offset, etc., for coords, and pass those along
    #     if self.stripDirection == 'X':
    #       xOutputRegion = (0, width)
    #       yOutputRegion = (n*height/nstrips, (n+1)*height/nstrips)
    #       if n > 0:
    #         # strip separator
    #         printer.writeLine(0, yOutputRegion[0], width, yOutputRegion[0])
    #     else:
    #       xOutputRegion = (n*width/nstrips, (n+1)*width/nstrips)
    #       yOutputRegion = (0, height)
    #       if n > 0:
    #         # strip separator
    #         printer.writeLine(xOutputRegion[0], 0, xOutputRegion[0], height)
    #     printer.startRegion(xOutputRegion, yOutputRegion)
    #     strip.printToFile(printer)
    #   printer.close()
      
  def _updatePivot(self):
    """Updates pivot in all strips contained in the spectrum display."""
    for strip in self.strips:
      strip._updatePivot()
    
  def _updatePhasing(self):
    """Updates phasing in all strips contained in the spectrum display."""
    for strip in self.strips:
      strip._updatePhasing()
    
  def _changedPhasingDirection(self):
    """Changes direction of phasing from horizontal to vertical or vice versa."""
    for strip in self.strips:
      strip._changedPhasingDirection()
    
  def togglePhaseConsole(self):
    """
    Toggles whether phasing console is displayed.
    """
    isVisible = not self.phasingFrame.isVisible()
    self.phasingFrame.setVisible(isVisible)
    for strip in self.strips:
      if isVisible:
        strip.turnOnPhasing()
      else:
        strip.turnOffPhasing()
         
    self._updatePhasing()

  def _closeDock(self):
    """
    Closes spectrum display and deletes it from the project.
    """
    if len(self._appBase.project.spectrumDisplays) == 1:
      self._appBase.mainWindow.addBlankDisplay()
    # self.dock.close()
    self.delete()


  def _fillToolBar(self):
    """
    # CCPN INTERNAL - called in _fillToolBar methods of GuiStripDisplay1d and GuiStripDisplayNd
    Puts icons for addition and removal of strips into the spectrum utility toolbar.
    """
    addStripAction = self.spectrumUtilToolBar.addAction('Add Strip', self.duplicateStrip) #self.orderedStrips[0].clone()) # clone first strip
    addStripIcon = Icon('icons/plus')
    addStripAction.setIcon(addStripIcon)
    removeStripAction = self.spectrumUtilToolBar.addAction('Remove Strip', self.removeStrip) # remove last strip
    removeStripIcon = Icon('icons/minus')
    removeStripAction.setIcon(removeStripIcon)
    self.removeStripAction = removeStripAction


  def removeStrip(self):
    self.orderedStrips[-1]._unregisterStrip()
    self.orderedStrips[-1].delete()

  def duplicateStrip(self):
    """
    Creates a new strip identical to the last one created and adds it to right of the display.
    """
    newStrip = self.strips[-1].clone()

  def _hideUtilToolBar(self):
    """
    # CCPN INTERNAL - called in __init__ of GuiStripDisplayNd.
    Hides the spectrum utility toolbar
    """
    self.spectrumUtilToolBar.hide()


  def resetYZooms(self):
    """Zooms Y axis of current strip to show entire region"""
    for strip in self.strips:
      strip.resetYZoom()

  def resetXZooms(self):
    """Zooms X axis of current strip to show entire region"""
    for strip in self.strips:
      strip.resetXZoom()

  def _restoreZoom(self):
    """Restores last saved zoom of current strip."""
    self._appBase.current.strip._restoreZoom()

  def _storeZoom(self):
    """Saves zoomed region of current strip."""
    self._appBase.current.strip._storeZoom()
    
  def toggleCrossHair(self):
    """Toggles whether cross hair is displayed in all strips of spectrum display."""
    # toggle crosshairs for strips in this spectrumDisplay
    for strip in self.strips:
      strip._toggleCrossHair()
    
  def toggleGrid(self):
    """Toggles whether grid is displayed in all strips of spectrum display."""
    # toggle grid for strips in this spectrumDisplay
    for strip in self.strips:
      strip.toggleGrid()
    
  def _setCrossHairPosition(self, axisPositionDict:typing.Dict[str, float]):
    """
    #CCPN INTERNAL
    Sets the position of the cross in all strips of spectrum display."""
    for strip in self.strips:
      strip._setCrossHairPosition(axisPositionDict)
  #
  # def _setActionIconColour(self, apiDataSource):
  #   action = self.spectrumActionDict.get(apiDataSource)
  #   if action:
  #     pix=QtGui.QPixmap(QtCore.QSize(60, 10))
  #     if apiDataSource.numDim < 2:
  #       pix.fill(QtGui.QColor(apiDataSource.sliceColour))
  #     else:
  #       pix.fill(QtGui.QColor(apiDataSource.positiveContourColour))
  #     action.setIcon(QtGui.QIcon(pix))

  def _deletedPeak(self, peak):
    apiPeak = peak._wrappedData
    # NBNB TBD FIXME rewrite this to not use API peaks
    # ALSO move this machinery from subclasses to this class.
    for peakListView in self.activePeakItemDict:
      peakItemDict = self.activePeakItemDict[peakListView]
      peakItem = peakItemDict.get(apiPeak)
      if peakItem:
        peakListView.spectrumView.strip.plotWidget.scene().removeItem(peakItem)
        del peakItemDict[apiPeak]
        inactivePeakItems = self.inactivePeakItemDict.get(peakListView)
        if inactivePeakItems:
          inactivePeakItems.add(peakItem)



# def _createdStripSpectrumView(project:Project, apiStripSpectrumView:ApiStripSpectrumView):
#   """Update interface when a strip is created"""
#
#   spectrumDisplay = project._data2Obj[apiStripSpectrumView.strip.spectrumDisplay]
#   enabled = len(spectrumDisplay.strips) > 1
#   spectrumDisplay.removeStripAction.setEnabled(enabled)
  
# def _deletedStripSpectrumView(project:Project, apiStripSpectrumView:ApiStripSpectrumView):
#   """Update interface when a strip is deleted"""
#
#   spectrumView = project._data2Obj[apiStripSpectrumView]
#   strip = spectrumView.strip
#   spectrumDisplay = strip.spectrumDisplay
#   scene = strip.plotWidget.scene()
#   scene.removeItem(spectrumView)
#   if hasattr(spectrumView, 'plot'):  # 1d
#     scene.removeItem(spectrumView.plot)
#
#   enabled = len(spectrumDisplay.strips) > 2  # 2 not 1 because this strip has not been deleted yet
#   spectrumDisplay.removeStripAction.setEnabled(enabled)
#
#
# Project._setupApiNotifier(_createdStripSpectrumView, ApiStripSpectrumView, 'postInit')
# Project._setupApiNotifier(_deletedStripSpectrumView, ApiStripSpectrumView, 'preDelete')


#
# def _createdStripPeakListView(project:Project, apiStripPeakListView:ApiStripPeakListView):
#   apiDataSource = apiStripPeakListView.stripSpectrumView.spectrumView.dataSource
#   getDataObj = project._data2Obj.get
#   peakListView = getDataObj(apiStripPeakListView)
#   spectrumView = peakListView.spectrumView
#   action = spectrumView.strip.spectrumDisplay.spectrumActionDict.get(apiDataSource)
#   if action:
#     action.toggled.connect(peakListView.setVisible) # TBD: need to undo this if peakListView removed
#
#   strip = spectrumView.strip
#   for apiPeakList in apiDataSource.sortedPeakLists():
#     strip.showPeaks(getDataObj(apiPeakList))
#
# Project._setupApiNotifier(_createdStripPeakListView, ApiStripPeakListView, 'postInit')

# def _setActionIconColour(project:Project, apiDataSource:ApiDataSource):
#
#   # TBD: the below might not be the best way to get hold of the spectrumDisplays
#   for task in project.tasks:
#     if task.status == 'active':
#       for spectrumDisplay in task.spectrumDisplays:
#         spectrumDisplay._setActionIconColour(apiDataSource)
#
# for apiFuncName in ('setPositiveContourColour', 'setSliceColour'):
#   Project._setupApiNotifier(_setActionIconColour, ApiDataSource, apiFuncName)


# def _deletedPeak(project:Project, apiPeak:ApiPeak):
#
#   # TBD: the below might not be the best way to get hold of the spectrumDisplays
#   for task in project.tasks:
#     if task.status == 'active':
#       for spectrumDisplay in task.spectrumDisplays:
#         spectrumDisplay._deletedPeak(apiPeak)
#
# Project._setupApiNotifier(_deletedPeak, ApiPeak, 'preDelete')


def _deletedPeak(peak:Peak):

  for spectrumView in peak.peakList.spectrum.spectrumViews:
    spectrumView.strip.spectrumDisplay._deletedPeak(peak)
Peak.setupCoreNotifier('delete', _deletedPeak)

def _deletedSpectrumView(project:Project, apiSpectrumView:ApiSpectrumView):
  """tear down SpectrumDisplay when new SpectrumView is deleted - for notifiers"""
  spectrumDisplay = project._data2Obj[apiSpectrumView.spectrumDisplay]
  apiDataSource = apiSpectrumView.dataSource

  # remove toolbar action (button)
  # NBNB TBD FIXME get rid of API object from code
  action = spectrumDisplay.spectrumActionDict.get(apiDataSource)  # should always be not None
  if action:
    spectrumDisplay.spectrumToolBar.removeAction(action)
    del spectrumDisplay.spectrumActionDict[apiDataSource]
Project._setupApiNotifier(_deletedSpectrumView, ApiSpectrumView, 'preDelete')
