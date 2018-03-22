"""

This module implemented a Frame and a ScrollableFrame

Frame(parent=None, showBorder=False, fShape=None, fShadow=None, **kwds)
  NB: Until now: fShape and fShadow do not seem to alter the appearance on OSX
  
ScrollableFrame(parent=None, showBorder=False, fShape=None, fShadow=None,
                minimumSizes=(50,50), scrollBarPolicies=('asNeeded','asNeeded'), **kwds)

  From: http://pyqt.sourceforge.net/Docs/PyQt5/qframe.html#details

  The QFrame class is the base class of widgets that can have a frame. More...

  Inherits QWidget.

  Inherited by QAbstractScrollArea, QLabel, QLCDNumber, QSplitter, QStackedWidget and QToolBox.

  Types

  enum Shadow { Plain, Raised, Sunken }
  enum Shape { NoFrame, Box, Panel, WinPanel, ..., StyledPanel }
  enum StyleMask { Shadow_Mask, Shape_Mask }
  Methods

  __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
  changeEvent (self, QEvent)
  drawFrame (self, QPainter)
  bool event (self, QEvent e)
  QRect frameRect (self)
  Shadow frameShadow (self)
  Shape frameShape (self)
  int frameStyle (self)
  int frameWidth (self)
  int lineWidth (self)
  int midLineWidth (self)
  paintEvent (self, QPaintEvent)
  setFrameRect (self, QRect)
  setFrameShadow (self, Shadow)
  setFrameShape (self, Shape)
  setFrameStyle (self, int)
  setLineWidth (self, int)
  setMidLineWidth (self, int)
  QSize sizeHint (self)

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
__dateModified__ = "$dateModified: 2017-07-07 16:32:53 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Geerten Vuister $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.Widget import Widget


class Frame(QtWidgets.QFrame, Base):

  FRAME_DICT = {
      # Shadow
      'plain':       QtWidgets.QFrame.Plain,
      'raised':      QtWidgets.QFrame.Raised,
      'sunken':      QtWidgets.QFrame.Sunken,
      # Shapes
      'noFrame':     QtWidgets.QFrame.NoFrame,
      'box':         QtWidgets.QFrame.Box,
      'panel':       QtWidgets.QFrame.Panel,
      'styledPanel': QtWidgets.QFrame.StyledPanel,
      'hLine':       QtWidgets.QFrame.HLine,
      'vLine':       QtWidgets.QFrame.VLine,
  }

  def __init__(self, parent=None, showBorder=False, fShape=None, fShadow=None,
                     setLayout=False, **kwds):
    """
    Initialise a Frame with optional border and layout

    :param fShape:   frame shape options: noFrame, box, styledPanel, hLine, vLine
    :param fShadow:  frame shadow options: plain, raised, sunken

    """

    QtWidgets.QFrame.__init__(self, parent)

    #TODO: replace with proper stylesheet routines once inplemented
    styleSheet = ''
    if 'bgColor' in kwds:
      #rgb = QtGui.QColor(kwds["bgColor"]).getRgb()[:3]
      styleSheet += "background-color: rgb(%d, %d, %d); " % kwds["bgColor"]
      del(kwds['bgColor'])
    if 'fgColor' in kwds:
      styleSheet += "foreground-color: rgb(%d, %d, %d); " % kwds["fgColor"]
      del (kwds['fgColor'])
    if showBorder:
      styleSheet += "border: 1px solid black; "
    else:
      styleSheet += "border: 0px; "
    if len(styleSheet) > 0:
      #print('>>', styleSheet)
      self.setStyleSheet('QFrame {' + styleSheet + '}')

    Base.__init__(self, setLayout=setLayout, **kwds)
    self.setContentsMargins(0, 0, 0, 0)

    # define frame styles
    if fShape or fShadow:
      """
      Define frame properties:
      """
      #TODO:GEERTEN: routine is called but appears not to change much in the appearance on OSX
      shape = self.FRAME_DICT.get(fShape, QtWidgets.QFrame.NoFrame)
      shadow = self.FRAME_DICT.get(fShadow, 0)
      #print('>>', shape, shadow)
      #print('Frame.framestyle>', shape | shadow)
      #self.setFrameStyle(shape | shadow)
      self.setFrameShape(shape)
      self.setFrameShadow(shadow)
      #self.setLineWidth(3)
      self.setMidLineWidth(3)

class ScrollableFrame(Frame):
  "A scrollable frame"

  def __init__(self, parent=None,
                     setLayout=False, showBorder=False, fShape=None, fShadow=None,
                     minimumSizes=(50,50), scrollBarPolicies=('asNeeded','asNeeded'), **kwds):

    # define a scroll area; check kwds if these apply to gridding
    kw1 = {}
    for key in 'grid gridSpan stretch hAlign vAlign'.split():
      if key in kwds:
        kw1[key] = kwds[key]
        del(kwds[key])
    kw1['setLayout'] = True ## always assure a layout for the scrollarea

    self.scrollArea = ScrollArea(parent=parent,
                                 scrollBarPolicies=scrollBarPolicies, minimumSizes=minimumSizes,
                                 **kw1
                                )

    # initialise the frame
    Frame.__init__(self, parent=self.scrollArea, setLayout=setLayout,
                         showBorder=showBorder, fShape = fShape, fShadow = fShadow,
                         **kwds
                  )
    # add it to the _sequenceGraphScrollArea
    self.scrollArea.setWidget(self)
    self.scrollArea.getLayout().addWidget(self)

    # configure the scroll area to allow all available space without margins
    self.scrollArea.setContentsMargins(0, 0, 0, 0)
    self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #self._sequenceGraphScrollArea.setWidgetResizable(True)
    self.setScrollBarPolicies(scrollBarPolicies)
    # GWV: tried for GuiSpectrumDisplay scrolling error on strip: no effect
    # self._sequenceGraphScrollArea.ensureWidgetVisible(self, xMargin=200, yMargin=200)
    self.show()

  def setScrollBarPolicies(self, scrollBarPolicies=('asNeeded','asNeeded')):
    "Set the scrolbar policy: always, never, asNeeded"
    self.scrollArea.setScrollBarPolicies(scrollBarPolicies)

  def getScrollArea(self):
    "Return the scrollbar widget; for external usage"
    return self.scrollArea


class ScrollableFrame2(Widget):
  "A scrollable frame"

  def __init__(self, parent=None,
                     setLayout=False, showBorder=False, fShape=None, fShadow=None,
                     minimumSizes=(50,50), scrollBarPolicies=('asNeeded','asNeeded'), **kwds):

    # check kwds if these apply to gridding
    kw1 = {}
    for key in 'grid gridSpan stretch hAlign vAlign'.split():
      if key in kwds:
        kw1[key] = kwds[key]
        del(kwds[key])

    Widget.__init__(self, parent=parent, **kw1)

    # define a scroll area;
    self._scrollArea = ScrollArea(parent=self, setLayout=True,
                                  scrollBarPolicies=scrollBarPolicies, minimumSizes=minimumSizes,
                                 )

    # initialise a frame
    self._frame = Frame(parent=self._scrollArea, setLayout=setLayout, grid=(0,0),
                                       showBorder=showBorder, fShape = fShape, fShadow = fShadow,
                                       **kwds
                       )

    print('>>', self._frame)
    # add it to the _sequenceGraphScrollArea
    self._scrollArea.setWidget(self._frame)
    # self._settingsScrollArea.setWidgetResizable(True)

    # configure the scroll area to allow all available space without margins
    self._scrollArea.setContentsMargins(0, 0, 0, 0)
    self._scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    self.setScrollBarPolicies(scrollBarPolicies)
    # self._sequenceGraphScrollArea.ensureWidgetVisible(self, xMargin=200, yMargin=200)
    #self.show()

  def setScrollBarPolicies(self, scrollBarPolicies=('asNeeded','asNeeded')):
    "Set the scrolbar policy: always, never, asNeeded"
    self._scrollArea.setScrollBarPolicies(scrollBarPolicies)

  def getScrollArea(self):
    "Return the scrollbar widget; for external usage"
    return self._scrollArea

  def getFrame(self):
    "Return the frame widget; for external usage"
    return self._frame


if __name__ == '__main__':

  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.BasePopup import BasePopup
  from ccpn.ui.gui.widgets.Label import Label

  class TestPopup(BasePopup):
    def body(self, parent):
      widget = Widget(parent, setLayout=True)
      policyDict = dict(
        hAlign='c',
        stretch=(1,0),
        #hPolicy = 'center',
        #vPolicy = 'center'
      )

      #TODO: find the cause of the empty space between the widgets
      #frame3 = ScrollableFrame(parent=parent, showBorder=True, bgColor=(255, 0, 255), grid=(2,0))
      frame1 = Frame(parent=widget, setLayout=True, grid=(0,0), showBorder=False, bgColor=(255, 255, 0), **policyDict)
      label1 = Label(parent=frame1, grid=(0,0), text="FRAME-1", bold=True,textColour='black', textSize='32')

      frame2 = Frame(parent=widget, setLayout=True, grid=(1,0), showBorder=True, bgColor=(255, 0, 0),
                     fShape='styledPanel', fShadow='raised', **policyDict)
      label2 = Label(parent=frame2, grid=(0,0), text="FRAME-2", bold=True,textColour='black', textSize='32')

 #     scroll4 = ScrollableFrame2(parent=widget, grid=(2,0), setLayout=True)
      scroll4 = ScrollArea(scrollBarPolicies=('always','always'))
      print(scroll4)
      label4 = Label(
                     text="ScrollableFrame",  bold=True,textColour='black', textSize='32',
                     **policyDict,
                   )
      scroll4.setWidget(label4)
      widget.getLayout().addWidget(scroll4, 2,0)

  app = TestApplication()
  popup = TestPopup(title='Test Frame')
  popup.resize(200, 400)
  app.start()

