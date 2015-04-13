"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================
import numpy

from OpenGL import GL
from PyQt4 import QtCore, QtGui

from ccpncore.gui.ToolButton import ToolButton
from ccpncore.util import Colour

from ccpnc.contour import Contourer2d
###from ccpnc.peak import Peak

from ccpnmrcore.modules.GuiSpectrumView import GuiSpectrumView
###from ccpnmrcore.modules.spectrumPane.PeakListNdItem import PeakListNdItem

# TBD: for now ignore fact that apiSpectrumView can override contour colour and/or contour levels

def _getLevels(count, base, factor):
  
  base *= 100.0  # TEMP
  levels = []
  if count > 0:
    levels = [base]
    for n in range(count-1):
      levels.append(numpy.float32(factor * levels[-1]))

  return levels
       
class GuiSpectrumViewNd(GuiSpectrumView):
  
  ###PeakListItemClass = PeakListNdItem
  
  #sigClicked = QtCore.Signal(object, object)

  #def __init__(self, guiSpectrumDisplay, apiSpectrumView, dimMapping=None, region=None, **kw):
  def __init__(self):
    """ guiSpectrumDisplay is the parent
        apiSpectrumView is the (API) SpectrumView object
    """
    """ old comment
        region is in units of parent, ordered by spectrum dimensions
        dimMapping is from spectrum numerical dimensions to guiStrip numerical dimensions
        (for example, xDim is what gets mapped to 0 and yDim is what gets mapped to 1)
    """

    self.setAcceptedMouseButtons = QtCore.Qt.LeftButton

    #GuiSpectrumView.__init__(self, guiSpectrumDisplay, apiSpectrumView, dimMapping)
    GuiSpectrumView.__init__(self)
    # self.spectralData = self.getSlices()
    
    ###xDim, yDim = apiSpectrumView.dimensionOrdering[:2]
    ###xDim -= 1  # dimensionOrdering starts at 1
    ###yDim -= 1

    # TBD: this is not correct
    ##apiDataSource = self.apiDataSource
    # I think this fixes it - number of DISPLAY axes, rather than dataSource axes. RHF
    # dimensionCount = apiDataSource.numDim
    dimensionCount = len(self.dimensionOrdering)
    self.previousRegion = dimensionCount * [None]

    #self.setZValue(-1)  # this is so that the contours are drawn on the bottom
    """
    if dimMapping is not None:
      self.xDim = dimMapping[0]
      self.yDim = dimMapping[1]
"""
    """
    apiStrips = apiSpectrumView.strips
    if apiStrips:
      # just looks at first strip, is that correct idea??
      apiStrip = apiStrips[0]
      guiStrip = apiStrip.guiStrip
      viewBox = guiStrip.viewBox
    else:
      guiStrip = viewBox = None
"""
    """
    for guiStrip in guiSpectrumDisplay.guiStrips:
      viewBox = guiStrip.viewBox
      apiStrip = guiStrip.apiStrip
      for dim, axis in enumerate(apiStrip.getOrderedAxes()[:2]):
        position = axis.position
        width = axis.width
        region = (position-0.5*width, position+0.5*width)
        if dim == 0:
          viewBox.setXRange(*region)
        else: # dim == 1
          viewBox.setYRange(*region)
"""
    """
    if not region:
      # chicken and egg problem, can't know xDim until after dimMapping set up
      # and that is set up in SpectrumItem constructor, but that needs to know
      # region; similar problem with spectrum object itself, which is set up in
      # SpectrumItem constructor but need to have it to hand before that called
      region = guiSpectrumDisplay.region = self.defaultRegion()
      
      if viewBox:
        xDim = self.xDim
        yDim = self.yDim
        # TBD: below assumes axes inverted
        viewBox.setXRange(region[xDim][1], region[xDim][0])
        viewBox.setYRange(region[yDim][1], region[yDim][0])
    if guiStrip: # TBD: HACK, TEMP, should be using guiStrip.positions
      guiStrip.region = region
      """
      
    """
    self.posContoursVisible = True # this block of code TEMP
    self.negContoursVisibleContoursVisible = True
    self.baseLevel = 1000000.00
    self.multiplier = 1.4
    self.numberOfLevels = 20
    try:
      self.levels
    except AttributeError:
      self.levels = self.getLevels()
"""
    #self.contourDisplayIndexDict = {} # (xDim, yDim) -> level -> display list index
    
    self.colourIndex = 0
        
    apiDataSource = self.apiSpectrumView.dataSource
    if not self.positiveContourColour:
      apiDataSource.positiveContourColour = Colour.spectrumHexColours[self.colourIndex]
      self.colourIndex += 1
      self.colourIndex %= len(Colour.spectrumHexColours)

    if not self.negativeContourColour:
    # Changed to guiSpectrumView.negativeContourColour, which picks up from either
    # SpectrumView or DataSource
      apiDataSource.negativeContourColour = Colour.spectrumHexColours[self.colourIndex]
      self.colourIndex += 1
      self.colourIndex %= len(Colour.spectrumHexColours)

    self.spectrumItems = {} # strip --> associated QtGui.QGraphicsItem 
    for strip in self.strips:
      self.addSpectrumItem(strip)

    self.spectrumViewButton = ToolButton(self.spectrumDisplay, self)

    for strip in self.strips:
       item = self.spectrumItems[strip]
       print(item)
       self.newAction.toggled.connect(item.setVisible)
      #if self not in strip.plotWidget.items():
        # newItem = self
      #  strip.plotWidget.scene().addItem(self)

  def addSpectrumItem(self, strip):
    if strip not in self.spectrumItems:
      item = GuiSpectrumViewItemNd(self, strip)
      self.spectrumItems[strip] = item
      strip.plotWidget.scene().addItem(item)
    
  def removeSpectrumItem(self, strip):
    if strip in self.spectrumItems:
      item = self.spectrumItems[strip]
      strip.plotWidget.scene().removeItem(item)
      del self.spectrumItems[strip]
      
  """
  def getLevels(self):
    
    levels = [self.baseLevel]
    for n in range(int(self.numberOfLevels-1)):
      levels.append(self.multiplier*levels[-1])
      
    return tuple(numpy.array(levels, dtype=numpy.float32))
"""

  def zPlaneSize(self):  # TBD: Do we need this still?
    
    spectrum = self.spectrum
    dimensionCount = spectrum.dimensionCount
    if dimensionCount < 3:
      return None  # TBD
      
    zDim = self.apiSpectrumView.orderedDataDims[2].dim - 1
    point = (0.0, 1.0)
    value = spectrum.getDimValueFromPoint(zDim, point)
    size = abs(value[1] - value[0])
    
    return size
   
class GuiSpectrumViewItemNd(QtGui.QGraphicsItem):
  
  def __init__(self, spectrumView, strip):
    
    self.spectrumView = spectrumView
    self.strip = strip
    QtGui.QGraphicsItem.__init__(self)  
    
    self.setZValue(-1)  # this is so that the contours are drawn on the bottom
    self.posLevelsPrev = []
    self.negLevelsPrev = []
    self.xyDataDimsPrev = None
    self.posDisplayLists = []
    self.negDisplayLists = []
    
    #for peakListView in spectrumView._wrappedData.sortedPeakListViews():
    #  peakListItem = GuiPeakListItemNd(self, peakListView)
 
  ##### override of superclass function

  def paint(self, painter, option, widget=None):
    
    ##if not widget:
    ##  return

    ##guiStrip = self.spectrumDisplay.viewportDict[widget]
    ##self.drawContours(painter, guiStrip)
    self.drawContours(painter)
    
  def boundingRect(self):  # seems necessary to have


    return QtCore.QRectF(-2000, -2000, 2000, 2000)  # TBD: remove hardwiring
  
  ##### functions not to be used externally #####

  #def drawContours(self, painter, guiStrip):
  def drawContours(self, painter):
    
    apiDataSource = self.spectrumView.apiDataSource
    if self.spectrumView._wrappedData.displayPositiveContours is True:
      posLevels = _getLevels(apiDataSource.positiveContourCount, apiDataSource.positiveContourBase, apiDataSource.positiveContourFactor)
    else:
      posLevels = []
    if self.spectrumView._wrappedData.displayNegativeContours is True:
      negLevels = _getLevels(apiDataSource.negativeContourCount, apiDataSource.negativeContourBase, apiDataSource.negativeContourFactor)
    else:
      negLevels = []
    if not posLevels and not negLevels:
      return
      
    #contourDict = self.constructContours(guiStrip, posLevels, negLevels)
    self.constructContours(posLevels, negLevels)


    posColour = Colour.scaledRgba(apiDataSource.positiveContourColour) # TBD: for now assume only one colour
    negColour = Colour.scaledRgba(apiDataSource.negativeContourColour)

    painter.beginNativePainting()  # this puts OpenGL back in its default coordinate system instead of Qt one

    try:
      
      #spectrum = self.spectrum
      xyDataDims = self.spectrumView.apiSpectrumView.orderedDataDims[:2]
      #xTranslate, xScale = self.getTranslateScale(guiStrip, xyDataDims[0].dim-1) # -1 because API dims start at 1
      #yTranslate, yScale = self.getTranslateScale(guiStrip, xyDataDims[1].dim-1)
      xTranslate, xScale = self.getTranslateScale(xyDataDims[0].dim-1, 0) # -1 because API dims start at 1
      yTranslate, yScale = self.getTranslateScale(xyDataDims[1].dim-1, 1)
      
      GL.glLoadIdentity()
      GL.glPushMatrix()
      ### do not need the below and if you have them then the axes get zapped as well unless it has positive Z values
      ###GL.glClearColor(1.0, 1.0, 1.0, 1.0)
      ###GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    
      ###apiStrips = self.apiSpectrumView.strips
      ###apiStrip = apiStrips[0]
      ###guiStrip = apiStrip.guiStrip
    
      # the below is because the y axis goes from top to bottom
      GL.glScale(1.0, -1.0, 1.0)
      GL.glTranslate(0.0, -self.strip.plotWidget.height(), 0.0)
      
      # the below makes sure that spectrum points get mapped to screen pixels correctly
      GL.glTranslate(xTranslate, yTranslate, 0.0)
      GL.glScale(xScale, yScale, 1.0)
      
      for (colour, levels, displayLists) in ((posColour, posLevels, self.posDisplayLists), (negColour, negLevels, self.negDisplayLists)):
        for n, level in enumerate(levels):
          GL.glColor4f(*colour)
          # TBD: scaling, translating, etc.
          GL.glCallList(displayLists[n])
      GL.glPopMatrix()

    finally:
      
      painter.endNativePainting()
      
  #def constructContours(self, guiStrip, posLevels, negLevels):
  def constructContours(self, posLevels, negLevels):
    """ Construct the contours for this spectrum using an OpenGL display list
        The way this is done here, any change in contour level or color needs to call this function.
    """
    
    xyDataDims = self.spectrumView.apiSpectrumView.orderedDataDims[:2]
    
    if xyDataDims is not self.xyDataDimsPrev:
      self.releaseDisplayLists(self.posDisplayLists)
      self.releaseDisplayLists(self.negDisplayLists)
      doPosLevels = doNegLevels = True
    else:
      if posLevels == self.posLevelsPrev:
        doPosLevels = False
      else:
        self.releaseDisplayLists(self.posDisplayLists)
        doPosLevels = posLevels and True
      if negLevels == self.negLevelsPrev:
        doNegLevels = False
      else:
        self.releaseDisplayLists(self.negDisplayLists)
        doNegLevels = negLevels and True
      
    ###self.previousRegion = self.guiSpectrumDisplay.region[:]  # TBD: not quite right, should be looking at the strip(s)
    
    # do the contouring and store results in display list
    if doPosLevels:
      posLevels = numpy.array(posLevels, numpy.float32)
      self.createDisplayLists(posLevels, self.posDisplayLists)
      
    if doNegLevels:
      negLevels = numpy.array(negLevels, numpy.float32)
      self.createDisplayLists(negLevels, self.negDisplayLists)
      
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    
    #for position, dataArray in self.getPlaneData(guiStrip):
    for position, dataArray in self.getPlaneData():
      
      if doPosLevels:
        posContours = Contourer2d.contourer2d(dataArray, posLevels)
        for n, contourData in enumerate(posContours):
          self.addContoursToDisplayList(self.posDisplayLists[n], contourData, posLevels[n])
        
      if len(negLevels):
        negContours = Contourer2d.contourer2d(dataArray, negLevels)
        for n, contourData in enumerate(negContours):
          self.addContoursToDisplayList(self.negDisplayLists[n], contourData, negLevels[n])
        
    GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
    
    self.posLevelsPrev = posLevels[:]
    self.negLevelsPrev = negLevels[:]
    self.xyDataDimsPrev = xyDataDims
    
  def releaseDisplayLists(self, displayLists):

    for displayList in displayLists:
      GL.glDeleteLists(displayList, 1)
    displayLists[:] = []

  def createDisplayLists(self, levels, displayLists):

    # could create them in one go but more likely to get fragmentation that way
    for level in levels:
      displayLists.append(GL.glGenLists(1))

  #def getPlaneData(self, guiStrip):
  def getPlaneData(self):
    
    strip = self.strip
    spectrum = self.spectrumView.spectrum
    dimensionCount = spectrum.dimensionCount
    apiSpectrumView = self.spectrumView.apiSpectrumView
    """ dimensionOrdering not working yet so for now hardwire
    xDim, yDim = apiSpectrumView.dimensionOrdering[:2]
    xDim -= 1  # dimensionOrdering starts at 1
    yDim -= 1
    """
    dataDims = apiSpectrumView.orderedDataDims
    xDim = dataDims[0].dim - 1  # -1 because dataDim.dim starts at 1
    yDim = dataDims[1].dim - 1
    if dimensionCount == 2: # TBD
      # below does not work yet
      #planeData = spectrum.getPlaneData(xDim=xDim, yDim=yDim)
      planeData = spectrum.getPlaneData(xDim=xDim, yDim=yDim)
      position = [0, 0]
      yield position, planeData
    elif dimensionCount == 3: # TBD
      apiStrip = strip.apiStrip
      zAxis = apiStrip.orderedAxes[2]
      position = zAxis.position
      width = zAxis.width
      zregionValue = (position+0.5*width, position-0.5*width) # Note + and - (axis backwards)
      zDim = dataDims[2].dim - 1
      zregionPoint = spectrum.getDimPointFromValue(zDim, zregionValue)
      zregionPoint = (int(numpy.round(zregionPoint[0])), int(numpy.round(zregionPoint[1])))
      strip.planeLabel.setText('%.3f' % position)
      position = dimensionCount * [0]
      for z in range(*zregionPoint):  # TBD
        position[zDim] = z
        # below does not work yet
        #planeData = spectrum.getPlaneData(position, xDim, yDim)
        planeData = spectrum.getPlaneData(position, xDim=xDim, yDim=yDim)
        yield position, planeData

  def addContoursToDisplayList(self, displayList, contourData, level):
    """ contourData is list of [NumPy array with ndim = 1 and size = twice number of points] """
    
    GL.glNewList(displayList, GL.GL_COMPILE)

    for contour in contourData:
      GL.glVertexPointer(2, GL.GL_FLOAT, 0, contour)
      GL.glDrawArrays(GL.GL_LINE_LOOP, 0, len(contour)//2)
      
    GL.glEndList()

  """
  def defaultRegion(self):
    
    spectrum = self.spectrum
    dimensionCount = spectrum.dimensionCount
    pointCounts = spectrum.pointCounts
    pntRegion = dimensionCount * [None]
    for dim in range(dimensionCount):
      if dim in (self.xDim, self.yDim):
        region = (0, pointCounts[dim])
      else:
        n = pointCounts[dim] // 2
        region = (n, n+1)
      pntRegion[dim] = region
    ppmRegion = []
    for dim in range(dimensionCount):
      (firstPpm, lastPpm) = spectrum.getDimValueFromPoint(dim, pntRegion[dim])
      ppmRegion.append((firstPpm, lastPpm))
      
    return ppmRegion
  """
  
  #def getTranslateScale(self, guiStrip, dim):
  def getTranslateScale(self, dim, ind):
        
    strip = self.strip
    plotWidget = strip.plotWidget
    plotItem = plotWidget.plotItem
    viewBox = strip.viewBox
    viewRegion = plotWidget.viewRange()
    region1, region0 = viewRegion[ind]  # TBD: relies on axes being backwards

    if ind == 0:
      pixelCount = plotWidget.width()
      pixelViewBox0 = plotItem.getAxis('left').width()
      pixelViewBox1 = pixelViewBox0 + viewBox.width()
    else:
      pixelCount = plotWidget.height()
      pixelViewBox0 = plotItem.getAxis('bottom').height()
      pixelViewBox1 = pixelViewBox0 + viewBox.height()
    
    (firstPoint, lastPoint) = self.spectrumView.spectrum.getDimPointFromValue(dim, (region0, region1))

    scale = (pixelViewBox1-pixelViewBox0) / (lastPoint-firstPoint)
    translate = pixelViewBox0 - firstPoint * scale
    
    return translate, scale

  """
  def raiseBaseLevel(self):
    self.baseLevel*=1.4
    self.levels = self.getLevels()

  def lowerBaseLevel(self):
    self.baseLevel/=1.4
    self.levels = self.getLevels()
  """     
    
class GuiPeakListItemNd(QtGui.QGraphicsItem):
  
  def __init__(self, spectrumViewItem, apiPeakListView):
    """ spectrumViewItem is the QGraphicsItem parent
        apiPeakListView is the API object
    """

    QtGui.QGraphicsItem.__init__(self, spectrumViewItem)

    self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, True)

    self.apiPeakListView = apiPeakListView
    self.peakItems = {}  # CCPN peak -> Qt peakItem
    self.displayed = False
    self.symbolColour = None
    self.symbolStyle = None
    self.isSymbolDisplayed = False
    self.textColour = None
    self.isTextDisplayed = False

    #for peak in peakList.peaks:
    #  self.peakItems[peak.pid] = PeakItem(self, peak)


