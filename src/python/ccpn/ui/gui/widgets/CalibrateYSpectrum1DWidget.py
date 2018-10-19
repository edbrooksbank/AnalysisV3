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
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:47 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-07-25 11:28:58 +0100 (Tue, July 25, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets, QtCore
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.DoubleSpinbox import ScientificDoubleSpinBox
from ccpn.core.lib.SpectrumLib import _calibrateY1D
# import pyqtgraph as pg
from ccpn.util.Logging import getLogger
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier


OP = 'Calibrate Y - Original Position: '
NP = 'New Position: '

ToolTip = 'Click the line to select. Hold left click and drag. Release the mouse to set the original ' \
          'position to the new position '


class CalibrateY1DWidgets(Frame):
    def __init__(self, parent=None, mainWindow=None, strip=None, **kw):
        Frame.__init__(self, parent, setLayout=True, **kw)

        if mainWindow is None:  # This allows opening the popup for graphical tests
            self.mainWindow = None
            self.project = None
        else:
            self.mainWindow = mainWindow
            self.project = self.mainWindow.project
            self.application = self.mainWindow.application
            self.current = self.application.current

        self.strip = strip
        self.newPosition = None
        self.targetLineVisible = False

        try:
            self.GLWidget = self.current.strip._CcpnGLWidget
        except Exception as es:
            getLogger().debugGL('OpenGL widget not instantiated')

        i = 0
        self.labelOriginalPosition = Label(self, OP, grid=(0, i), hAlign='r')
        i += 1
        self.boxOriginalPosition = ScientificDoubleSpinBox(self, step=0.001, decimals=3, grid=(0, i))
        i += 1
        self.labelNewPosition = Label(self, NP, grid=(0, i), hAlign='r')
        i += 1
        self.boxNewPosition = ScientificDoubleSpinBox(self, step=0.001, decimals=3, grid=(0, i))
        i += 1
        # self.okButtons = ButtonList(self, ['Apply', 'Close'], callbacks=[self._apply, self._close],
        #                             grid=(0, i))
        self.okButtons = ButtonList(self, ['Apply'], callbacks=[self._apply],
                                    grid=(0, i))

        # self.infiniteLine = pg.InfiniteLine(movable=True, angle=0)
        # self.originalPosInfiniteLine = pg.InfiniteLine(movable=False, angle=0, pen='g')
        #
        # # self.infiniteLine.sigPositionChangeFinished.connect(self._calibrateSpectra)
        # self.infiniteLine.sigPositionChanged.connect(self._newPositionLineCallback)

        self.labelOriginalPosition.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.boxOriginalPosition.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.labelNewPosition.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.boxNewPosition.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.okButtons.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        if self.GLWidget:
            self.infiniteLine = self.GLWidget.addInfiniteLine(colour='highlight', movable=True, lineStyle='solid', orientation='h')
            self.originalPosInfiniteLine = self.GLWidget.addInfiniteLine(colour='highlight', movable=True, lineStyle='dashed', orientation='h')

            # openGL callbacks
            self.infiniteLine.valuesChanged.connect(self._newPositionLineCallback)
            self.originalPosInfiniteLine.valuesChanged.connect(self._originalPositionLineCallback)

        self.boxOriginalPosition.valueChanged.connect(self._originalPositionBoxCallback)
        self.boxNewPosition.valueChanged.connect(self._newPositionBoxCallback)

        self._initLines()
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Minimum)

        self.GLSignals = GLNotifier(parent=None)

    def _initLines(self):
        if self.mainWindow is not None:
            # if self.strip is not None:
            #   self.strip.plotWidget.addItem(self.infiniteLine)
            #   self.strip.plotWidget.addItem(self.originalPosInfiniteLine)

            if self.strip.plotWidget.viewBox.contextMenuPosition is not None:
                self.originalPosition = self.strip.plotWidget.viewBox.contextMenuPosition[1]
                self.infiniteLine.setValue(self.originalPosition)
                self.originalPosInfiniteLine.setValue(self.originalPosition)
                self.boxOriginalPosition.setValue(round(self.originalPosition, 3))

                self.infiniteLine.visible = True and self.targetLineVisible
                self.originalPosInfiniteLine.visible = True

    def _newBoxCallback(self):
        spinboxValue = self.sender().value()
        self.infiniteLine.setValue(spinboxValue)

    def _newPositionLineCallback(self):
        # self.newPosition = self.infiniteLine.pos().y()

        self.newPosition = self.infiniteLine.values[0]
        self.boxNewPosition.setValue(round(self.newPosition, 3))

    def _newPositionBoxCallback(self):
        box = self.sender()
        if box.hasFocus():
            self.newPosition = round(box.value(), 3)
            self.infiniteLine.setValue(self.newPosition)

    def _originalPositionLineCallback(self):
        self.originalPosition = self.originalPosInfiniteLine.values[0]
        self.boxOriginalPosition.setValue(round(self.originalPosition, 3))

    def _originalPositionBoxCallback(self):
        box = self.sender()
        if box.hasFocus():
            self.originalPosition = round(box.value(), 3)
            self.originalPosInfiniteLine.setValue(self.originalPosition)

    def _removeLines(self):
        if self.mainWindow is not None:
            # if self.strip is not None:
            #   self.strip.plotWidget.removeItem(self.infiniteLine)
            #   self.strip.plotWidget.removeItem(self.originalPosInfiniteLine)

            if self.GLWidget:
                self.infiniteLine.visible = False
                self.originalPosInfiniteLine.visible = False

    def resetUndos(self):
        """Set the number of undos to enable cancelling
        """
        self.numUndos = self.project._undo.numItems()

    def _toggleLines(self):
        if self.isVisible():
            self._initLines()
        else:
            self._removeLines()

    def _apply(self):
        applyAccept = False
        self.project._startCommandEchoBlock('_applyChanges', quiet=True)
        _undo = self.project._undo
        oldUndo = _undo.numItems()
        fromPos = self.originalPosition
        toPos = self.newPosition
        try:
            self._calibrateSpectra(fromPos, toPos)

            # add an undo item to the stack
            if _undo is not None:
                _undo.newItem(self._calibrateSpectra, self._calibrateSpectra,
                              undoArgs=(toPos, fromPos),
                              redoArgs=(fromPos, toPos))

            applyAccept = True
        except Exception as es:
            showWarning(str(self.windowTitle()), str(es))
        finally:
            self.project._endCommandEchoBlock()

        if applyAccept is False:
            # should only undo if something new has been added to the undo deque
            # may cause a problem as some things may be set with the same values
            # and still be added to the change list, so only undo if length has changed
            errorName = str(self.__class__.__name__)
            while oldUndo < self.project._undo.numItems():
                self.project._undo.undo()
            getLogger().debug('>>>Undo.%s._applychanges' % errorName)

    def _calibrateSpectra(self, fromPos, toPos):

        if self.mainWindow is not None:
            if self.strip is not None:
                for spectrumView in self.strip.spectrumViews:
                    if spectrumView.plot.isVisible():
                        spectrum = spectrumView.spectrum
                        _calibrateY1D(spectrum, fromPos, toPos)

                        spectrumView.buildContours = True

        if self.GLWidget:
            # spawn a redraw of the GL windows
            self.GLWidget._moveAxes((0.0, toPos-fromPos))
            self.GLSignals.emitPaintEvent()

    def _cancel(self):
        """Cancel has been pressed, undo all items since the widget was opened
        Dangerous as other stuff may have happened
        """
        pass

    def _close(self):
        self.setVisible(False)
        self.strip.calibrateYAction.setChecked(False)
        self._toggleLines()


if __name__ == '__main__':
    from ccpn.ui.gui.widgets.Application import TestApplication
    from ccpn.ui.gui.popups.Dialog import CcpnDialog


    app = TestApplication()
    popup = CcpnDialog()
    f = CalibrateY1DWidgets(popup)

    popup.show()
    popup.raise_()

    app.start()
