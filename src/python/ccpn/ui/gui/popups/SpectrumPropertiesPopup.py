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
__dateModified__ = "$dateModified: 2017-07-07 16:32:50 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import os
from functools import partial

from PyQt5 import QtGui, QtWidgets, QtCore

from ccpn.core.lib import Util as ccpnUtil

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.ColourDialog import ColourDialog
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox, ScientificDoubleSpinBox
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.FilteringPulldownList import FilteringPulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.popups.ExperimentTypePopup import _getExperimentTypes
from ccpn.util.Colour import spectrumColours, addNewColour, fillColourPulldown, addNewColourString
from ccpn.ui.gui.popups.Dialog import CcpnDialog  # ejb
from ccpn.ui.gui.widgets.MessageDialog import showWarning
from ccpn.util.Logging import getLogger
from ccpn.util.Constants import DEFAULT_ISOTOPE_DICT

SPECTRA = ['1H', 'STD', 'Relaxation Filtered', 'Water LOGSY']


def _updateGl(self, spectrumList):
    from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier

    # # spawn a redraw of the contours
    # for spec in spectrumList:
    #     for specViews in spec.spectrumViews:
    #         specViews.buildContours = True

    GLSignals = GLNotifier(parent=self)
    GLSignals.emitPaintEvent()


class SpectrumPropertiesPopup(CcpnDialog):
    # The values on the 'General' and 'Dimensions' tabs are queued as partial functions when set.
    # The apply button then steps through each tab, and calls each function in the _changes dictionary
    # in order to set the parameters.

    def __init__(self, parent=None, mainWindow=None, spectrum=None,
                 title='Spectrum Properties', **kw):
        CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

        self.mainWindow = mainWindow
        self.application = mainWindow.application
        self.project = mainWindow.application.project
        self.current = mainWindow.application.current
        self.spectrum = spectrum

        # layout = QtWidgets.QGridLayout()
        # self.setLayout(layout)
        self.tabWidget = QtWidgets.QTabWidget()
        # tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        if spectrum.dimensionCount == 1:
            self._generalTab = GeneralTab(parent=self, mainWindow=self.mainWindow, spectrum=spectrum)
            self._dimensionsTab = DimensionsTab(parent=self, mainWindow=self.mainWindow,
                                                spectrum=spectrum, dimensions=spectrum.dimensionCount)

            self.tabWidget.addTab(self._generalTab, "General")
            self.tabWidget.addTab(self._dimensionsTab, "Dimensions")
            self._contoursTab = None
        else:
            self._generalTab = GeneralTab(parent=self, mainWindow=self.mainWindow, spectrum=spectrum)
            self._dimensionsTab = DimensionsTab(parent=self, mainWindow=self.mainWindow,
                                                spectrum=spectrum, dimensions=spectrum.dimensionCount)
            self._contoursTab = ContoursTab(parent=self, mainWindow=self.mainWindow, spectrum=spectrum)

            self.tabWidget.addTab(self._generalTab, "General")
            self.tabWidget.addTab(self._dimensionsTab, "Dimensions")
            self.tabWidget.addTab(self._contoursTab, "Contours")
        self.layout().addWidget(self.tabWidget, 0, 0, 2, 4)

        self.applyButtons = ButtonList(self, texts=['Cancel', 'Apply', 'Ok'],
                                       callbacks=[self.reject, self._applyChanges, self._okButton],
                                       tipTexts=['', '', '', None], direction='h',
                                       hAlign='r', grid=(2, 1), gridSpan=(1, 4))

        self._fillPullDowns()

    def _fillPullDowns(self):
        if self.spectrum.dimensionCount == 1:
            fillColourPulldown(self._generalTab.colourBox, allowAuto=False)
        else:
            fillColourPulldown(self._contoursTab.positiveColourBox, allowAuto=False)
            fillColourPulldown(self._contoursTab.negativeColourBox, allowAuto=False)

    def _keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            pass

    def _repopulate(self):
        if self._generalTab:
            self._generalTab._repopulate()
        if self._dimensionsTab:
            self._dimensionsTab._repopulate()
        if self._contoursTab:
            self._contoursTab._repopulate()

    def _applyAllChanges(self, changes):
        for v in changes.values():
            v()

    def _applyChanges(self):
        """
        The apply button has been clicked
        Define an undo block for setting the properties of the object
        If there is an error setting any values then generate an error message
          If anything has been added to the undo queue then remove it with application.undo()
          repopulate the popup widgets
        """
        tabs = (self._generalTab, self._dimensionsTab, self._contoursTab)

        applyAccept = False
        _undo = self.project._undo
        oldUndo = _undo.numItems()

        from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier

        GLSignals = GLNotifier(parent=self)

        self.project._startCommandEchoBlock('_applyChanges', quiet=True)
        try:
            spectrumList = []
            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        spectrumList.append(t.spectrum)

            _undo._newItem(undoPartial=partial(_updateGl, self, spectrumList))

            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        self._applyAllChanges(changes)

            _undo._newItem(redoPartial=partial(_updateGl, self, spectrumList))

            for spec in spectrumList:
                for specViews in spec.spectrumViews:
                    specViews.buildContours = True

            # repaint
            GLSignals.emitPaintEvent()

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
            if oldUndo != self.project._undo.numItems():
                self.project._undo.undo()
                getLogger().debug('>>>Undo.%s._applychanges' % errorName)
            else:
                getLogger().debug('>>>Undo.%s._applychanges nothing to remove' % errorName)

            # repopulate popup
            self._repopulate()
            return False
        else:
            return True

    def _okButton(self):
        if self._applyChanges() is True:
            self.accept()


class FilePathValidator(QtGui.QValidator):

    def __init__(self, spectrum, parent=None, validationType='exists'):
        QtGui.QValidator.__init__(self, parent=parent)
        self.spectrum = spectrum
        self.validationType = validationType

    def validate(self, p_str, p_int):
        if self.validationType != 'exists':
            raise NotImplemented('FilePathValidation only checks that the path exists')
        filePath = ccpnUtil.expandDollarFilePath(self.spectrum._project, p_str)

        if os.path.exists(filePath):
            try:
                self.parent().setStyleSheet('background-color: #f7ffff')
            except:
                pass
            state = QtGui.QValidator.Acceptable
        else:
            try:
                self.parent().setStyleSheet('background-color: #f7ffff')
            except:
                pass
            self.parent().setStyleSheet('background-color: #f7ffbe')  # TODO: use a yellow in our colour scheme
            state = QtGui.QValidator.Intermediate
        return state, p_str, p_int


class GeneralTab(QtWidgets.QWidget, Base):
    def __init__(self, parent=None, mainWindow=None, spectrum=None, item=None, colourOnly=False):

        from ccpnmodel.ccpncore.lib.spectrum.NmrExpPrototype import priorityNameRemapping

        super(GeneralTab, self).__init__(parent)
        Base.__init__(self, setLayout=True)  # ejb

        self.parent = parent
        self.mainWindow = mainWindow
        self.application = self.mainWindow.application
        self.project = self.mainWindow.project

        self.item = item
        self.spectrum = spectrum
        self._changes = dict()
        self.atomCodes = ()

        self.experimentTypes = spectrum._project._experimentTypeMap
        Label(self, text="Spectrum name ", grid=(1, 0))
        self.nameData = LineEdit(self, vAlign='t', grid=(1, 1))
        self.nameData.setText(spectrum.name)
        self.layout().addItem(QtWidgets.QSpacerItem(0, 10), 0, 0)
        self.nameData.textChanged.connect(self._queueSpectrumNameChange)  # ejb - was editingFinished

        Label(self, text="Path", vAlign='t', hAlign='l', grid=(2, 0))
        self.pathData = LineEdit(self, vAlign='t', grid=(2, 1))
        self.pathData.setValidator(FilePathValidator(parent=self.pathData, spectrum=self.spectrum))
        self.pathButton = Button(self, grid=(2, 2), callback=self._getSpectrumFile, icon='icons/applications-system')

        self.pythonConsole = mainWindow.pythonConsole
        self.logger = getLogger()  # self.spectrum.project._logger

        self.setWindowTitle("Spectrum Properties")

        apiDataStore = spectrum._apiDataSource.dataStore
        if not apiDataStore:
            self.pathData.setText('<None>')
        elif apiDataStore.dataLocationStore.name == 'standard':
            dataUrlName = apiDataStore.dataUrl.name
            if dataUrlName == 'insideData':
                self.pathData.setText('$INSIDE/%s' % apiDataStore.path)
            elif dataUrlName == 'alongsideData':
                self.pathData.setText('$ALONGSIDE/%s' % apiDataStore.path)
            elif dataUrlName == 'remoteData':
                self.pathData.setText('$DATA/%s' % apiDataStore.path)
            else:
                self.pathData.setText(apiDataStore.fullPath)
        else:
            self.pathData.setText(apiDataStore.fullPath)
        self.pathData.editingFinished.connect(self._queueSetSpectrumPath)
        try:
            index = spectrum.project.chemicalShiftLists.index(spectrum.chemicalShiftList)
        except:
            index = 0
        Label(self, text="Chemical Shift List ", vAlign='t', hAlign='l', grid=(3, 0))
        self.chemicalShiftListPulldown = PulldownList(self, vAlign='t', grid=(3, 1), index=index,
                                                      texts=[csList.pid for csList in spectrum.project.chemicalShiftLists] + ['<New>'],
                                                      callback=self._queueChemicalShiftListChange)
        Label(self, text="PID ", vAlign='t', hAlign='l', grid=(5, 0))
        Label(self, text=spectrum.pid, vAlign='t', grid=(5, 1))

        Label(self, text="Sample", vAlign='t', hAlign='l', grid=(6, 0))
        self.samplesPulldownList = PulldownList(self, texts=['None'], objects=[None], vAlign='t', grid=(6, 1))
        for sample in spectrum.project.samples:
            self.samplesPulldownList.addItem(sample.name, sample)
        if spectrum.sample is not None:
            self.samplesPulldownList.select(spectrum.sample.name)
        self.samplesPulldownList.activated[str].connect(self._queueSampleChange)

        if spectrum.dimensionCount == 1:
            Label(self, text="Colour", vAlign='t', hAlign='l', grid=(7, 0))
            self.colourBox = PulldownList(self, vAlign='t', grid=(7, 1))

            # populate initial pulldown
            spectrumColourKeys = list(spectrumColours.keys())
            fillColourPulldown(self.colourBox, allowAuto=False)
            c = spectrum.sliceColour
            if c in spectrumColourKeys:
                self.colourBox.setCurrentText(spectrumColours[c])
            else:
                addNewColourString(c)
                fillColourPulldown(self.colourBox, allowAuto=False)
                spectrumColourKeys = list(spectrumColours.keys())
                self.colourBox.setCurrentText(spectrumColours[c])

            self.colourBox.currentIndexChanged.connect(partial(self._queueChangeSliceComboIndex, spectrum))
            colourButton = Button(self, vAlign='t', hAlign='l', grid=(7, 2), hPolicy='fixed',
                                  callback=partial(self._queueSetSpectrumColour, spectrum), icon='icons/colours')
            Label(self, text="Experiment Type ", vAlign='t', hAlign='l', grid=(8, 0))
            self.spectrumType = FilteringPulldownList(self, vAlign='t', grid=(8, 1))
            spButton = Button(self, grid=(8, 2),
                              callback=partial(self._raiseExperimentFilterPopup, spectrum),
                              hPolicy='fixed', icon='icons/applications-system')
            experimentTypes = _getExperimentTypes(spectrum.project, spectrum)
            self.spectrumType.setData(texts=list(experimentTypes.keys()), objects=list(experimentTypes.values()))

            # Added to account for renaming of experiments
            self.spectrumType.currentIndexChanged.connect(self._queueSetSpectrumType)
            if spectrum.experimentType is not None:
                self.spectrumType.select(spectrum.experimentType)

            Label(self, text='Spectrum Scaling', vAlign='t', hAlign='l', grid=(9, 0))
            self.spectrumScalingData = LineEdit(self, text=str(self.spectrum.scale), vAlign='t', hAlign='l', grid=(9, 1))

            self.spectrumScalingData.textChanged.connect(self._queueSpectrumScaleChange)

            Label(self, text="Date Recorded ", vAlign='t', hAlign='l', grid=(11, 0))
            Label(self, text='n/a', vAlign='t', hAlign='l', grid=(11, 1))

            Label(self, text="Noise Level ", vAlign='t', hAlign='l', grid=(12, 0))
            self.noiseLevelData = ScientificDoubleSpinBox(self, vAlign='t', hAlign='l', grid=(12, 1))

            self.noiseLevelData.valueChanged.connect(self._queueNoiseLevelDataChange)
            if spectrum.noiseLevel is not None:
                self.noiseLevelData.setValue(spectrum.noiseLevel)
            else:
                self.noiseLevelData.setValue(0)

            # self.noiseLevelData.textChanged.connect(self._queueNoiseLevelDataChange)
            # if spectrum.noiseLevel is not None:
            #     self.noiseLevelData.setText(str('%.3d' % spectrum.noiseLevel))
            # else:
            #     self.noiseLevelData.setText('None')

        else:
            Label(self, text="Experiment Type ", vAlign='t', hAlign='l', grid=(7, 0))
            self.spectrumType = FilteringPulldownList(self, vAlign='t', grid=(7, 1))
            spButton = Button(self, grid=(7, 2),
                              callback=partial(self._raiseExperimentFilterPopup, spectrum),
                              hPolicy='fixed', icon='icons/applications-system')
            experimentTypes = _getExperimentTypes(spectrum.project, spectrum)
            if experimentTypes:
                self.spectrumType.setData(texts=list(experimentTypes.keys()), objects=list(experimentTypes.values()))

            # axisCodes = []
            # for isotopeCode in spectrum.isotopeCodes:
            #   axisCodes.append(''.join([code for code in isotopeCode if not code.isdigit()]))
            #
            # self.atomCodes = tuple(sorted(axisCodes))
            # itemsList = list(self.experimentTypes[spectrum.dimensionCount].get(self.atomCodes).keys())
            # self.spectrumType.addItems(itemsList)
            # Get the text that was used in the pulldown from the refExperiment
            # NBNB This could possibly give unpredictable results
            # if there is an experiment with experimentName (user settable!)
            # that happens to match the synonym for a different experiment type.
            # But if people will ignore our defined vocabulary, on their head be it!
            # Anyway, tha alternative (discarded) is to look into the ExpPrototype
            # to compare RefExperiment names and synonyms
            # or (too ugly for words) to have a third attribute in parallel with
            # spectrum.experimentName and spectrum.experimentType
            text = spectrum.experimentName
            if experimentTypes and text not in experimentTypes:
                text = spectrum.experimentType
            # apiRefExperiment = spectrum._wrappedData.experiment.refExperiment
            # text = apiRefExperiment and (apiRefExperiment.synonym or apiRefExperiment.name)
            # Added to account for renaming of experiments
            text = priorityNameRemapping.get(text, text)
            self.spectrumType.setCurrentIndex(self.spectrumType.findText(text))

            self.spectrumType.currentIndexChanged.connect(self._queueSetSpectrumType)
            self.spectrumType.setMinimumWidth(self.pathData.width() * 1.95)
            self.spectrumType.setFixedHeight(25)

            spectrumScalingLabel = Label(self, text='Spectrum Scaling', vAlign='t', grid=(9, 0))
            self.spectrumScalingData = LineEdit(self, text=str(self.spectrum.scale), vAlign='t', grid=(9, 1))
            self.spectrumScalingData.textChanged.connect(self._queueSpectrumScaleChange)

            noiseLevelLabel = Label(self, text="Noise Level ", vAlign='t', hAlign='l', grid=(10, 0))
            self.noiseLevelData = ScientificDoubleSpinBox(self, vAlign='t', grid=(10, 1))
            self.noiseLevelData.valueChanged.connect(self._queueNoiseLevelDataChange)

            if spectrum.noiseLevel is None:
                self.noiseLevelData.setValue(spectrum.estimateNoise())
            else:
                self.noiseLevelData.setValue(spectrum.noiseLevel)

            # if spectrum.noiseLevel is None:
            #     self.noiseLevelData.setText(str('%.3d' % spectrum.estimateNoise()))
            # else:
            #     self.noiseLevelData.setText('%.3d' % spectrum.noiseLevel)

            doubleCrosshairLabel = Label(self, text="Show Second Cursor", grid=(11, 0), vAlign='t', hAlign='l')
            doubleCrosshairCheckBox = CheckBox(self, grid=(11, 1), checked=True, vAlign='t', hAlign='l')
            doubleCrosshairCheckBox.setChecked(spectrum.showDoubleCrosshair)
            self.layout().addItem(QtWidgets.QSpacerItem(0, 10), 0, 0)
            doubleCrosshairCheckBox.stateChanged.connect(self._queueChangeDoubleCrosshair)

    def _repopulate(self):
        from ccpnmodel.ccpncore.lib.spectrum.NmrExpPrototype import priorityNameRemapping

        self.nameData.setText(self.spectrum.name)
        self.pathData.setValidator(FilePathValidator(parent=self.pathData, spectrum=self.spectrum))

        try:
            index = self.spectrum.project.chemicalShiftLists.index(self.spectrum.chemicalShiftList)
        except:
            index = 0
        self.chemicalShiftListPulldown.setIndex(index)

        if self.spectrum.sample is not None:
            self.samplesPulldownList.select(self.spectrum.sample.name)

        if self.atomCodes:
            itemsList = list(self.experimentTypes[self.spectrum.dimensionCount].get(self.atomCodes).keys())
            self.spectrumType.addItems(itemsList)
            text = self.spectrum.experimentName
            if text not in itemsList:
                text = self.spectrum.experimentType
            text = priorityNameRemapping.get(text, text)
            self.spectrumType.setCurrentIndex(self.spectrumType.findText(text))

        if self.spectrum.scale is not None:
            self.spectrumScalingData.setText(str(self.spectrum.scale))

        if self.spectrum.noiseLevel is None:
            self.noiseLevelData.setValue(self.spectrum.estimateNoise())
        else:
            self.noiseLevelData.setValue(self.spectrum.noiseLevel)

        # if self.spectrum.noiseLevel is None:
        #     self.noiseLevelData.setText(str('%.3d' % self.spectrum.estimateNoise()))
        # else:
        #     self.noiseLevelData.setText('%.3d' % self.spectrum.noiseLevel)

    def _writeLoggingMessage(self, command):
        self.logger.info("spectrum = project.getByPid('%s')" % self.spectrum.pid)
        self.logger.info(command)

    def _queueSpectrumNameChange(self):
        if self.nameData.isModified():
            self._changes['spectrumName'] = partial(self._changeSpectrumName, self.nameData.text())

    def _changeSpectrumName(self, name):
        self.spectrum.rename(name)
        self._writeLoggingMessage("spectrum.rename('%s')" % self.nameData.text())

    def _queueSpectrumScaleChange(self):
        self._changes['spectrumScale'] = partial(self._setSpectrumScale, self.spectrumScalingData.text())

    def _setSpectrumScale(self, scale):
        self.spectrum.scale = float(scale)
        self._writeLoggingMessage("spectrum.scale = %s" % self.spectrumScalingData.text())
        self.pythonConsole.writeConsoleCommand("spectrum.scale = %s" % self.spectrumScalingData.text(), spectrum=self.spectrum)

    def _queueNoiseLevelDataChange(self):
        self._changes['spectrumNoiseLevel'] = partial(self._setNoiseLevelData, self.noiseLevelData.value())

    def _setNoiseLevelData(self, noise):
        self.spectrum.noiseLevel = float(noise)
        self._writeLoggingMessage("spectrum.noiseLevel = %s" % self.noiseLevelData.value())

    def _queueChangePositiveContourDisplay(self, state):
        self._changes['positiveContourDisplay'] = partial(self._changePositiveContourDisplay, state)

    def _queueChangeDoubleCrosshair(self, state):
        flag = (state == QtCore.Qt.Checked)
        self.spectrum.showDoubleCrosshair = flag
        self.logger.info("spectrum = ui.getByGid('%s')" % self.spectrum.pid)
        self.logger.info("spectrum.showDoubleCrosshair = %s" % flag)

    def _queueChemicalShiftListChange(self, item):
        if item == '<New>':
            listLen = len(self.chemicalShiftListPulldown.texts)
            self._changes['chemicalShiftList'] = partial(self._setNewChemicalShiftList, listLen)
        else:
            self._changes['chemicalShiftList'] = partial(self._setChemicalShiftList, item)

    def _raiseExperimentFilterPopup(self, spectrum):
        from ccpn.ui.gui.popups.ExperimentFilterPopup import ExperimentFilterPopup

        popup = ExperimentFilterPopup(parent=self.mainWindow, mainWindow=self.mainWindow, spectrum=spectrum)
        popup.exec_()
        self.spectrumType.select(popup.expType)

    def _setNewChemicalShiftList(self, listLen):
        newChemicalShiftList = self.spectrum.project.newChemicalShiftList()
        insertionIndex = listLen - 1
        self.chemicalShiftListPulldown.texts.insert(insertionIndex, newChemicalShiftList.pid)
        self.chemicalShiftListPulldown.setData(self.chemicalShiftListPulldown.texts)
        self.chemicalShiftListPulldown.setCurrentIndex(insertionIndex)
        self.spectrum.chemicalShiftList = newChemicalShiftList
        self._writeLoggingMessage("""newChemicalShiftList = project.newChemicalShiftList()
                                spectrum.chemicalShiftList = newChemicalShiftList""")
        self.pythonConsole.writeConsoleCommand('spectrum.chemicalShiftList = chemicalShiftList', chemicalShiftList=newChemicalShiftList, spectrum=self.spectrum)
        self.logger.info('spectrum.chemicalShiftList = chemicalShiftList')

    def _setChemicalShiftList(self, item):
        self.spectrum.chemicalShiftList = self.spectrum.project.getByPid(item)
        self.pythonConsole.writeConsoleCommand('spectrum.newChemicalShiftList = chemicalShiftList', chemicalShiftList=self.spectrum.chemicalShiftList,
                                               spectrum=self.spectrum)
        self._writeLoggingMessage("""chemicalShiftList = project.getByPid('%s')
                                  spectrum.chemicalShiftList = chemicalShiftList""" % self.spectrum.chemicalShiftList.pid)

    def _queueSampleChange(self):
        self._changes['sampleSpectrum'] = partial(self._changeSampleSpectrum, self.samplesPulldownList.currentObject())

    def _changeSampleSpectrum(self, sample):
        if sample is not None:
            sample.spectra += (self.spectrum,)
        else:
            if self.spectrum.sample is not None:
                self.spectrum.sample = None

    def _queueSetSpectrumType(self, value):
        self._changes['spectrumType'] = partial(self._setSpectrumType, value)

    def _setSpectrumType(self, value):

        # expType = self.experimentTypes[self.spectrum.dimensionCount].get(self.atomCodes).get(self.spectrumType.currentText())
        expType = self.spectrumType.getObject()
        print(expType)
        self.spectrum.experimentType = expType
        self.pythonConsole.writeConsoleCommand('spectrum.experimentType = experimentType', experimentType=expType, spectrum=self.spectrum)
        self._writeLoggingMessage("spectrum.experimentType = '%s'" % expType)

    def _getSpectrumFile(self):
        if os.path.exists('/'.join(self.pathData.text().split('/')[:-1])):
            currentSpectrumDirectory = '/'.join(self.pathData.text().split('/')[:-1])
        else:
            currentSpectrumDirectory = os.path.expanduser('~')
        dialog = FileDialog(self, text='Select Spectrum File', directory=currentSpectrumDirectory,
                            fileMode=1, acceptMode=0,
                            preferences=self.application.preferences.general)
        directory = dialog.selectedFiles()
        if len(directory) > 0:
            self.pathData.setText(directory[0])
            self.spectrum.filePath = directory[0]

            apiDataStore = self.spectrum._apiDataSource.dataStore
            if not apiDataStore:
                self.pathData.setText('<None>')
            elif apiDataStore.dataLocationStore.name == 'standard':
                dataUrlName = apiDataStore.dataUrl.name
                if dataUrlName == 'insideData':
                    self.pathData.setText('$INSIDE/%s' % apiDataStore.path)
                elif dataUrlName == 'alongsideData':
                    self.pathData.setText('$ALONGSIDE/%s' % apiDataStore.path)
                elif dataUrlName == 'remoteData':
                    self.pathData.setText('$DATA/%s' % apiDataStore.path)
                else:
                    self.pathData.setText(apiDataStore.fullPath)

    def _queueSetSpectrumPath(self):
        if self.pathData.isModified():
            filePath = self.pathData.text()

            # Convert from custom repository names to full names
            filePath = ccpnUtil.expandDollarFilePath(self.spectrum._project, filePath)

            if os.path.exists(filePath):
                self._changes['spectrumFilePath'] = partial(self._setSpectrumFilePath, filePath)
            else:
                self.logger.error('Cannot set spectrum path to %s. Path does not exist' % self.pathData.text())

    def _setSpectrumFilePath(self, filePath):
        self.spectrum.filePath = filePath
        self._writeLoggingMessage("spectrum.filePath = '%s'" % filePath)
        self.pythonConsole.writeConsoleCommand("spectrum.filePath('%s')" % filePath,
                                               spectrum=self.spectrum)

        # TODO: Find a way to convert to the shortened path without setting the value in the model,
        #       then move this back to _setSpectrumPath
        apiDataSource = self.spectrum._apiDataSource
        apiDataStore = apiDataSource.dataStore

        if not apiDataStore or apiDataStore.dataLocationStore.name != 'standard':
            raise NotImplemented('Non-standard API data store locations are invalid.')

        dataUrlName = apiDataStore.dataUrl.name
        apiPathName = apiDataStore.path
        if dataUrlName == 'insideData':
            shortenedPath = '$INSIDE/{}'.format(apiPathName)
        elif dataUrlName == 'alongsideData':
            shortenedPath = '$ALONGSIDE/{}'.format(apiPathName)
        elif dataUrlName == 'remoteData':
            shortenedPath = '$DATA/{}'.format(apiPathName)
        else:
            shortenedPath = apiDataStore.fullPath
        self.pathData.setText(shortenedPath)

    def _queueSetSpectrumColour(self, spectrum):
        dialog = ColourDialog(self)

        newColour = dialog.getColor()
        if newColour:
            addNewColour(newColour)
            self.parent._fillPullDowns()  #fillColourPulldown(self.colourBox, allowAuto=False)
            self.colourBox.setCurrentText(spectrumColours[newColour.name()])

            self._changes['spectrumColour'] = partial(self._setSpectrumColour, spectrum, newColour)

    def _setSpectrumColour(self, spectrum, newColour):
        spectrum._apiDataSource.setSliceColour(newColour.name())
        self._writeLoggingMessage("spectrum.sliceColour = '%s'" % newColour.name())
        self.pythonConsole.writeConsoleCommand("spectrum.sliceColour = '%s'" % newColour.name(), spectrum=self.spectrum)

    def _queueChangeSliceComboIndex(self, spectrum, value):
        self._changes['sliceComboIndex'] = partial(self._changedSliceComboIndex, spectrum, value)

    def _changedSliceComboIndex(self, spectrum, value):
        # newColour = list(spectrumColours.keys())[value]
        newColour = list(spectrumColours.keys())[list(spectrumColours.values()).index(self.colourBox.currentText())]
        if newColour:
            spectrum.sliceColour = newColour
            self._writeLoggingMessage("spectrum.sliceColour = '%s'" % newColour)
            self.pythonConsole.writeConsoleCommand("spectrum.sliceColour '%s'" % newColour, spectrum=self.spectrum)


class DimensionsTab(QtWidgets.QWidget, Base):
    def __init__(self, parent=None, mainWindow=None, spectrum=None, dimensions=None):
        super(DimensionsTab, self).__init__(parent)
        Base.__init__(self, setLayout=True)  # ejb

        self.parent = parent
        self.mainWindow = mainWindow
        self.spectrum = spectrum
        self.dimensions = dimensions
        self._changes = dict()

        self.pythonConsole = mainWindow.pythonConsole
        self.logger = getLogger()  # self.spectrum.project._logger

        Label(self, text="Dimension ", grid=(1, 0), hAlign='l', vAlign='t', )

        self.layout().addItem(QtWidgets.QSpacerItem(0, 10), 0, 0)
        for i in range(dimensions):
            dimLabel = Label(self, text='%s' % str(i + 1), grid=(1, i + 1), vAlign='t', hAlign='l')

        self.axisCodes = [i for i in range(dimensions)]
        self.isotopeCodePullDowns = [i for i in range(dimensions)]
        self.spectralReferencingData = [i for i in range(dimensions)]
        self.spectralReferencingDataPoints = [i for i in range(dimensions)]
        self.spectralAssignmentToleranceData = [i for i in range(dimensions)]
        self.spectralDoubleCursorOffset = [i for i in range(dimensions)]

        row = 2
        Label(self, text="Axis Code ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Isotope Code ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Point Counts ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Dimension Type ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Spectrum Width (ppm) ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Spectral Width (Hz) ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Spectrometer Frequency (Hz) ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Referencing (ppm) ", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Referencing (points)", grid=(row, 0), vAlign='t', hAlign='l')

        row += 1
        Label(self, text="Assignment Tolerance ", grid=(row, 0), hAlign='l')

        row += 1
        Label(self, text="Second cursor offset (Hz) ", grid=(row, 0), hAlign='l')

        for i in range(dimensions):
            row = 2
            # Label(self, text=str(spectrum.axisCodes[i]), grid=(row, i+1),  hAlign='l', vAlign='t',)

            value = spectrum.axisCodes[i]
            self.axisCodes[i] = LineEdit(self,
                                         text='<None>' if value is None else str(value),
                                         grid=(row, i + 1), vAlign='t', hAlign='l')
            self.axisCodes[i].textChanged.connect(partial(self._queueSetAxisCodes,
                                                          self.axisCodes[i].text, i))

            row += 1
            # Label(self, text=str(spectrum.isotopeCodes[i]), grid=(row, i + 1), hAlign='l', vAlign='t', )

            self.isotopeCodePullDowns[i] = PulldownList(self, grid=(row, i+1), vAlign='t')
            isotopeList = [code for code in DEFAULT_ISOTOPE_DICT.values()]
            self.isotopeCodePullDowns[i].setData(isotopeList)
            if spectrum.isotopeCodes[i] in isotopeList:
                index = isotopeList.index(spectrum.isotopeCodes[i])
                self.isotopeCodePullDowns[i].setIndex(index)

            self.isotopeCodePullDowns[i].currentIndexChanged.connect(partial(self._queueSetIsotopeCodes, self.isotopeCodePullDowns[i].getText, i))

            row += 1
            Label(self, text=str(spectrum.pointCounts[i]), grid=(row, i + 1), vAlign='t', hAlign='l')

            row += 1
            Label(self, text=spectrum.dimensionTypes[i], grid=(row, i + 1), vAlign='t', hAlign='l')

            row += 1
            Label(self, text=str("%.3f" % (spectrum.spectralWidths[i] or 0.0)), grid=(row, i + 1),
                  vAlign='t', hAlign='l')

            row += 1
            Label(self, text=str("%.3f" % (spectrum.spectralWidthsHz[i] or 0.0)), grid=(row, i + 1),
                  vAlign='t', hAlign='l')

            row += 1
            Label(self, text=str("%.3f" % (spectrum.spectrometerFrequencies[i] or 0.0)), grid=(row, i + 1),
                  vAlign='t', hAlign='l')

            row += 1
            value = spectrum.referenceValues[i]
            self.spectralReferencingData[i] = LineEdit(self,
                                                       text='<None>' if value is None else str("%.3f" % value),
                                                       grid=(row, i + 1), vAlign='t', hAlign='l')
            self.spectralReferencingData[i].textChanged.connect(partial(self._queueSetDimensionReferencing,
                                                                        self.spectralReferencingData[i].text, i))
            # self.spectralReferencingDataList.append(spectralReferencingData)

            row += 1
            # Label(self, text="Referencing (points)", grid=(8, 0), vAlign='t', hAlign='l')
            value = spectrum.referencePoints[i]
            self.spectralReferencingDataPoints[i] = LineEdit(self,
                                                             text='<None>' if value is None else str("%.3f" % value),
                                                             # text=str("%.3f" % (spectrum.referencePoints[i] or 0.0)),
                                                             grid=(row, i + 1), vAlign='t', hAlign='l')
            self.spectralReferencingDataPoints[i].textChanged.connect(partial(self._queueSetPointDimensionReferencing,
                                                                              self.spectralReferencingDataPoints[i].text, i))
            # self.spectralReferencingDataPointsList.append(spectralReferencingDataPoints)

            row += 1
            # Label(self, text="Assignment Tolerance ", grid=(row, 0),  hAlign='l')
            value = spectrum.assignmentTolerances[i]
            self.spectralAssignmentToleranceData[i] = LineEdit(self,
                                                               text='<None>' if value is None else str("%.3f" % value),
                                                               grid=(row, i + 1), hAlign='l')
            self.spectralAssignmentToleranceData[i].textChanged.connect(partial(self._queueSetAssignmentTolerances,
                                                                                self.spectralAssignmentToleranceData[i].text, i))

            row += 1
            # Label(self, text="Second cursor offset (Hz) ", grid=(10, 0), hAlign='l')
            value = spectrum.doubleCrosshairOffsets[i]
            self.spectralDoubleCursorOffset[i] = LineEdit(self,
                                                          text='0' if value is None else str("%.3f" % value),
                                                          grid=(row, i + 1), hAlign='l')
            self.spectralDoubleCursorOffset[i].textChanged.connect(partial(self._queueSetDoubleCursorOffset,
                                                                           self.spectralDoubleCursorOffset[i].text, i))

    def _repopulate(self):
        for i in range(self.dimensions):
            value = self.spectrum.referenceValues[i]
            self.spectralReferencingData[i].setText('<None>' if value is None else str("%.3f" % value))

            value = self.spectrum.referencePoints[i]
            self.spectralReferencingDataPoints[i].setText('<None>' if value is None else str("%.3f" % value))

            value = self.spectrum.assignmentTolerances[i]
            self.spectralAssignmentToleranceData[i].setText('<None>' if value is None else str("%.3f" % value))

    def _writeLoggingMessage(self, command):
        self.logger.info("spectrum = project.getByPid('%s')" % self.spectrum.pid)
        self.logger.info(command)

    def _queueSetAssignmentTolerances(self, valueGetter, dim):
        self._changes['assignmentTolerances{}'.format(dim)] = partial(self._setAssignmentTolerances,
                                                                      self.spectrum, dim, valueGetter())

    def _setAssignmentTolerances(self, spectrum, dim, value):
        assignmentTolerances = list(spectrum.assignmentTolerances)
        assignmentTolerances[dim] = float(value)
        spectrum.assignmentTolerances = assignmentTolerances
        self.pythonConsole.writeConsoleCommand("spectrum.assignmentTolerances = {0}".format(assignmentTolerances), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.assignmentTolerances = {0}".format(assignmentTolerances))

    def _queueSetDoubleCursorOffset(self, valueGetter, dim):
        self._changes['doubleCursorOffset{}'.format(dim)] = partial(self._setDoubleCursorOffset,
                                                                    self.spectrum, dim, valueGetter())

    def _setDoubleCursorOffset(self, spectrum, dim, value):
        doubleCrosshairOffsets = list(spectrum.doubleCrosshairOffsets)
        doubleCrosshairOffsets[dim] = float(value)
        spectrum.doubleCrosshairOffsets = doubleCrosshairOffsets
        self.pythonConsole.writeConsoleCommand("spectrum.doubleCrosshairOffsets = {0}".format(doubleCrosshairOffsets), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.doubleCrosshairOffsets = {0}".format(doubleCrosshairOffsets))

    def _queueSetAxisCodes(self, valueGetter, dim):
        self._changes['AxisCodes{}'.format(dim)] = partial(self._setAxisCodes,
                                                           self.spectrum, dim, valueGetter())

    def _setAxisCodes(self, spectrum, dim, value):
        axisCodes = list(spectrum.axisCodes)
        axisCodes[dim] = str(value)
        spectrum.axisCodes = axisCodes
        showWarning('Change Axis Code', 'Caution is advised when changing axis codes\n'
                                        'It can adversely affect spectrumDisplays and peak/integral/multiplet lists.')

        self.pythonConsole.writeConsoleCommand("spectrum.axisCodes = {0}".format(axisCodes), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.referenceValues = {0}".format(axisCodes))

    def _queueSetIsotopeCodes(self, valueGetter, dim):
        self._changes['IsotopeCodes{}'.format(dim)] = partial(self._setIsotopeCodes,
                                                           self.spectrum, dim, valueGetter())

    def _setIsotopeCodes(self, spectrum, dim, value):
        isotopeCodes = list(spectrum.isotopeCodes)
        isotopeCodes[dim] = str(value)
        spectrum.isotopeCodes = isotopeCodes
        showWarning('Change Isotope Code', 'Caution is advised when changing isotope codes\n'
                                        'It can adversely affect spectrumDisplays and peak/integral/multiplet lists.')

        self.pythonConsole.writeConsoleCommand("spectrum.isotopeCodes = {0}".format(isotopeCodes), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.referenceValues = {0}".format(isotopeCodes))

    def _queueSetDimensionReferencing(self, valueGetter, dim):
        self._changes['dimensionReferencing{}'.format(dim)] = partial(self._setDimensionReferencing,
                                                                      self.spectrum, dim, valueGetter())

    def _setDimensionReferencing(self, spectrum, dim, value):
        spectrumReferencing = list(spectrum.referenceValues)
        spectrumReferencing[dim] = float(value)
        spectrum.referenceValues = spectrumReferencing
        self.pythonConsole.writeConsoleCommand("spectrum.referenceValues = {0}".format(spectrumReferencing), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.referenceValues = {0}".format(spectrumReferencing))

    def _queueSetPointDimensionReferencing(self, valueGetter, dim):
        self._changes['dimensionReferencingPoint{}'.format(dim)] = partial(self._setPointDimensionReferencing,
                                                                           self.spectrum, dim, valueGetter())

    def _setPointDimensionReferencing(self, spectrum, dim, value):
        spectrumReferencing = list(spectrum.referencePoints)
        spectrumReferencing[dim] = float(value)
        spectrum.referencePoints = spectrumReferencing
        self.pythonConsole.writeConsoleCommand("spectrum.referencePoints = {0}".format(spectrumReferencing), spectrum=spectrum)
        self._writeLoggingMessage("spectrum.referencePoints = {0}".format(spectrumReferencing))


class ContoursTab(QtWidgets.QWidget, Base):

    def __init__(self, parent=None, mainWindow=None, spectrum=None):
        super(ContoursTab, self).__init__(parent)
        Base.__init__(self, setLayout=True)  # ejb

        self.parent = parent
        self.mainWindow = mainWindow
        self.spectrum = spectrum

        self.pythonConsole = mainWindow.pythonConsole
        self.logger = getLogger()  # self.spectrum.project._logger

        # TODO self._changes looks unused, as do all the functions put in it
        # Check if the lot can be removed
        self._changes = dict()

        positiveContoursLabel = Label(self, text="Show Positive Contours", grid=(1, 0), vAlign='t', hAlign='l')
        positiveContoursCheckBox = CheckBox(self, grid=(1, 1), checked=True, vAlign='t', hAlign='l')
        # for spectrumView in self.spectrum.spectrumViews:
        #     if spectrumView.displayPositiveContours:
        #         positiveContoursCheckBox.setChecked(True)
        #     else:
        #         positiveContoursCheckBox.setChecked(False)
        positiveContoursCheckBox.setChecked(self.spectrum.includePositiveContours)

        self.layout().addItem(QtWidgets.QSpacerItem(0, 10), 0, 0)
        positiveContoursCheckBox.stateChanged.connect(self._queueChangePositiveContourDisplay)

        positiveBaseLevelLabel = Label(self, text="Positive Base Level", grid=(2, 0), vAlign='c', hAlign='l')
        positiveBaseLevelData = ScientificDoubleSpinBox(self, grid=(2, 1), vAlign='t')
        positiveBaseLevelData.setMaximum(1e12)
        positiveBaseLevelData.setMinimum(0.1)
        positiveBaseLevelData.setValue(self.spectrum.positiveContourBase)
        positiveBaseLevelData.valueChanged.connect(partial(self._queueChangePositiveBaseLevel, self.spectrum))
        # positiveBaseLevelData.setSingleStep(positiveBaseLevelData.value()*(positiveMultiplierData.value()-1))
        # Changed to get less quickly to zero - but DoubleSpinBox is NOT right for this
        positiveBaseLevelData.setSingleStep(positiveBaseLevelData.value() * 0.1)

        positiveMultiplierLabel = Label(self, text="Positive Multiplier", grid=(3, 0), vAlign='c', hAlign='l')
        positiveMultiplierData = DoubleSpinbox(self, grid=(3, 1), vAlign='t')
        positiveMultiplierData.setSingleStep(0.1)
        positiveMultiplierData.setValue(float(self.spectrum.positiveContourFactor))
        positiveMultiplierData.valueChanged.connect(partial(self._queueChangePositiveContourMultiplier, self.spectrum))

        positiveContourCountLabel = Label(self, text="Number of positive contours", grid=(4, 0), vAlign='c', hAlign='l')
        positiveContourCountData = Spinbox(self, grid=(4, 1), vAlign='t')
        positiveContourCountData.setValue(int(self.spectrum._apiDataSource.positiveContourCount))
        positiveContourCountData.valueChanged.connect(partial(self._queueChangePositiveContourCount, self.spectrum))
        positiveContourColourLabel = Label(self, text="Positive Contour Colour", grid=(5, 0), vAlign='c', hAlign='l')

        self.positiveColourBox = PulldownList(self, grid=(5, 1), vAlign='t')
        self.negativeColourBox = PulldownList(self, grid=(10, 1), vAlign='t')

        # populate initial pulldown
        spectrumColourKeys = list(spectrumColours.keys())
        fillColourPulldown(self.positiveColourBox, allowAuto=False)
        fillColourPulldown(self.negativeColourBox, allowAuto=False)

        c = self.spectrum.positiveContourColour
        if c in spectrumColourKeys:
            col = spectrumColours[c]
            self.positiveColourBox.setCurrentText(col)
        else:
            addNewColourString(c)
            fillColourPulldown(self.positiveColourBox, allowAuto=False)
            fillColourPulldown(self.negativeColourBox, allowAuto=False)
            spectrumColourKeys = list(spectrumColours.keys())
            col = spectrumColours[c]
            self.positiveColourBox.setCurrentText(col)

        self.positiveColourBox.currentIndexChanged.connect(partial(self._queueChangePosColourComboIndex, self.spectrum))

        self.positiveColourButton = Button(self, grid=(5, 2), vAlign='t', hAlign='l',
                                           icon='icons/colours', hPolicy='fixed')
        self.positiveColourButton.clicked.connect(partial(self._queueChangePosSpectrumColour, self.spectrum))

        negativeContoursLabel = Label(self, text="Show Negative Contours", grid=(6, 0), vAlign='c', hAlign='l')
        negativeContoursCheckBox = CheckBox(self, grid=(6, 1), checked=True, vAlign='t', hAlign='l')
        # for spectrumView in self.spectrum.spectrumViews:
        #     if spectrumView.displayNegativeContours:
        #         negativeContoursCheckBox.setChecked(True)
        #     else:
        #         negativeContoursCheckBox.setChecked(False)
        negativeContoursCheckBox.setChecked(self.spectrum.includeNegativeContours)

        negativeContoursCheckBox.stateChanged.connect(self._queueChangeNegativeContourDisplay)

        negativeBaseLevelLabel = Label(self, text="Negative Base Level", grid=(7, 0), vAlign='c', hAlign='l')
        negativeBaseLevelData = ScientificDoubleSpinBox(self, grid=(7, 1), vAlign='t')
        negativeBaseLevelData.setMaximum(-0.1)
        negativeBaseLevelData.setMinimum(-1e12)
        negativeBaseLevelData.setValue(self.spectrum.negativeContourBase)
        negativeBaseLevelData.valueChanged.connect(partial(self._queueChangeNegativeBaseLevel, self.spectrum))
        # negativeBaseLevelData.setSingleStep((negativeBaseLevelData.value()*-1)*negativeMultiplierData.value()-1)
        # Changed to get less quickly to zero - but DoubleSpinBox is NOT right for this
        negativeBaseLevelData.setSingleStep((negativeBaseLevelData.value() * -1) * 0.1)

        negativeMultiplierLabel = Label(self, text="Negative Multiplier", grid=(8, 0), vAlign='c', hAlign='l')
        negativeMultiplierData = DoubleSpinbox(self, grid=(8, 1), vAlign='t')
        negativeMultiplierData.setValue(self.spectrum.negativeContourFactor)
        negativeMultiplierData.setSingleStep(0.1)
        negativeMultiplierData.valueChanged.connect(partial(self._queueChangeNegativeContourMultiplier, self.spectrum))

        negativeContourCountLabel = Label(self, text="Number of negative contours", grid=(9, 0), vAlign='c', hAlign='l')
        negativeContourCountData = Spinbox(self, grid=(9, 1), vAlign='t')
        negativeContourCountData.setValue(self.spectrum.negativeContourCount)
        negativeContourCountData.valueChanged.connect(partial(self._queueChangeNegativeContourCount, self.spectrum))
        negativeContourColourLabel = Label(self, text="Negative Contour Colour", grid=(10, 0), vAlign='c', hAlign='l')

        # self.negativeColourBox = PulldownList(self, grid=(10, 1), vAlign='t')
        c = self.spectrum.negativeContourColour
        if c in spectrumColourKeys:
            self.negativeColourBox.setCurrentText(spectrumColours[c])
        else:
            addNewColourString(c)
            fillColourPulldown(self.positiveColourBox, allowAuto=False)
            fillColourPulldown(self.negativeColourBox, allowAuto=False)
            spectrumColourKeys = list(spectrumColours.keys())
            self.negativeColourBox.setCurrentText(spectrumColours[c])

        self.negativeColourBox.currentIndexChanged.connect(
                partial(self._queueChangeNegColourComboIndex, self.spectrum)
                )
        self.negativeColourButton = Button(self, grid=(10, 2), icon='icons/colours', hPolicy='fixed',
                                           vAlign='t', hAlign='l')
        self.negativeColourButton.clicked.connect(partial(self._queueChangeNegSpectrumColour, self.spectrum))

    def _repopulate(self):
        # don't need anything here as can't generate any errors
        pass

    def _writeLoggingMessage(self, command):
        self.logger.info("spectrum = project.getByPid('%s')" % self.spectrum.pid)
        self.logger.info(command)

    def _queueChangePositiveContourDisplay(self, state):
        self._changes['positiveContourDisplay'] = partial(self._changePositiveContourDisplay, state)

    def _changePositiveContourDisplay(self, state):
        if state == QtCore.Qt.Checked:
            self.spectrum.includePositiveContours = True
            for spectrumView in self.spectrum.spectrumViews:
                spectrumView.displayPositiveContours = True
                self.logger.info("spectrumView = ui.getByGid('%s')" % spectrumView.pid)
                self.logger.info("spectrumView.displayPositiveContours = True")
        else:
            self.spectrum.includePositiveContours = False
            for spectrumView in self.spectrum.spectrumViews:
                spectrumView.displayPositiveContours = False
                self.logger.info("spectrumView = ui.getByGid('%s')" % spectrumView.pid)
                self.logger.info("spectrumView.displayPositiveContours = False")

    def _queueChangeNegativeContourDisplay(self, state):
        self._changes['negativeContourDisplay'] = partial(self._changeNegativeContourDisplay, state)

    def _changeNegativeContourDisplay(self, state):
        if state == QtCore.Qt.Checked:
            self.spectrum.includeNegativeContours = True
            for spectrumView in self.spectrum.spectrumViews:
                spectrumView.displayNegativeContours = True
                self.logger.info("spectrumView = ui.getByGid('%s')" % spectrumView.pid)
                self.logger.info("spectrumView.displayNegativeContours = True")
        else:
            self.spectrum.includeNegativeContours = False
            for spectrumView in self.spectrum.spectrumViews:
                spectrumView.displayNegativeContours = False
                self.logger.info("spectrumView = ui.getByGid('%s')" % spectrumView.pid)
                self.logger.info("spectrumView.displayNegativeContours = False")

    def _queueChangePositiveBaseLevel(self, spectrum, value):
        self._changes['positiveContourBaseLevel'] = partial(self._changePositiveBaseLevel, spectrum, value)

    def _changePositiveBaseLevel(self, spectrum, value):
        spectrum.positiveContourBase = float(value)
        self._writeLoggingMessage("spectrum.positiveContourBase = %f" % float(value))
        self.pythonConsole.writeConsoleCommand("spectrum.positiveContourBase = %f" % float(value), spectrum=spectrum)

    def _queueChangePositiveContourMultiplier(self, spectrum, value):
        self._changes['positiveContourMultiplier'] = partial(self._changePositiveContourMultiplier, spectrum, value)

    def _changePositiveContourMultiplier(self, spectrum, value):
        spectrum.positiveContourFactor = float(value)
        self._writeLoggingMessage("spectrum.positiveContourFactor = %f" % float(value))
        self.pythonConsole.writeConsoleCommand("spectrum.positiveContourFactor = %f" % float(value), spectrum=spectrum)

    def _queueChangePositiveContourCount(self, spectrum, value):
        self._changes['positiveContourCount'] = partial(self._changePositiveContourCount, spectrum, value)

    def _changePositiveContourCount(self, spectrum, value):
        spectrum.positiveContourCount = int(value)
        self._writeLoggingMessage("spectrum.positiveContourCount = %d" % int(value))
        self.pythonConsole.writeConsoleCommand("spectrum.positiveContourCount = %d" % int(value), spectrum=spectrum)

    def _queueChangeNegativeBaseLevel(self, spectrum, value):
        self._changes['negativeContourBaseLevel'] = partial(self._changeNegativeBaseLevel, spectrum, value)

    def _changeNegativeBaseLevel(self, spectrum, value):
        spectrum.negativeContourBase = float(value)
        self._writeLoggingMessage("spectrum.negativeContourBase = %f" % float(value))
        self.pythonConsole.writeConsoleCommand("spectrum.negativeContourBase = %f" % float(value), spectrum=spectrum)

    def _queueChangeNegativeContourMultiplier(self, spectrum, value):
        self._changes['negativeContourMultiplier'] = partial(self._changeNegativeContourMultiplier, spectrum, value)

    def _changeNegativeContourMultiplier(self, spectrum, value):
        spectrum.negativeContourFactor = float(value)
        self._writeLoggingMessage("spectrum.negativeContourFactor = %f" % float(value))
        self.pythonConsole.writeConsoleCommand("spectrum.negativeContourFactor = %f" % float(value), spectrum=spectrum)

    def _queueChangeNegativeContourCount(self, spectrum, value):
        self._changes['negativeContourCount'] = partial(self._changeNegativeContourCount, spectrum, value)

    def _changeNegativeContourCount(self, spectrum, value):
        spectrum.negativeContourCount = int(value)
        self._writeLoggingMessage("spectrum.negativeContourCount = %d" % int(value))
        self.pythonConsole.writeConsoleCommand("spectrum.negativeContourCount = %d" % int(value), spectrum=spectrum)

    # change colours using comboboxes and colour buttons
    def _queueChangePosSpectrumColour(self, spectrum):
        dialog = ColourDialog(self)
        newColour = dialog.getColor()
        if newColour is not None:
            addNewColour(newColour)
            self.parent._fillPullDowns()  #fillColourPulldown(self.positiveColourBox, allowAuto=False)
            self.positiveColourBox.setCurrentText(spectrumColours[newColour.name()])

    def _queueChangeNegSpectrumColour(self, spectrum):
        dialog = ColourDialog(self)
        newColour = dialog.getColor()
        if newColour is not None:
            addNewColour(newColour)
            self.parent._fillPullDowns()  #fillColourPulldown(self.positiveColourBox, allowAuto=False)
            # fillColourPulldown(self.negativeColourBox, allowAuto=False)
            self.negativeColourBox.setCurrentText(spectrumColours[newColour.name()])

    def _queueChangePosColourComboIndex(self, spectrum, value):
        self._changes['positiveColourComboIndex'] = partial(self._changePosColourComboIndex, spectrum, value)

    def _changePosColourComboIndex(self, spectrum, value):
        # newColour = list(spectrumColours.keys())[value]
        newColour = list(spectrumColours.keys())[list(spectrumColours.values()).index(self.positiveColourBox.currentText())]
        if newColour:
            spectrum.positiveContourColour = newColour
            self._writeLoggingMessage("spectrum.positiveContourColour = '%s'" % newColour)
            self.pythonConsole.writeConsoleCommand("spectrum.positiveContourColour = '%s'" % newColour, spectrum=spectrum)

    def _queueChangeNegColourComboIndex(self, spectrum, value):
        self._changes['negativeColourComboIndex'] = partial(self._changeNegColourComboIndex, spectrum, value)

    def _changeNegColourComboIndex(self, spectrum, value):
        # newColour = list(spectrumColours.keys())[value]
        newColour = list(spectrumColours.keys())[list(spectrumColours.values()).index(self.negativeColourBox.currentText())]
        if newColour:
            spectrum._apiDataSource.negativeContourColour = newColour
            self._writeLoggingMessage("spectrum.negativeContourColour = %s" % newColour)
            self.pythonConsole.writeConsoleCommand("spectrum.negativeContourColour = '%s'" % newColour, spectrum=spectrum)


class SpectrumDisplayPropertiesPopupNd(CcpnDialog):
    """All spectra in the current display are added as tabs
    The apply button then steps through each tab, and calls each function in the _changes dictionary
    in order to set the parameters.
    """
    MINIMUM_WIDTH_PER_TAB = 120
    MINIMUM_WIDTH = 400

    def __init__(self, parent=None, mainWindow=None, orderedSpectrumViews=None,
                 title='Spectrum Display Properties', **kw):
        CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

        self.mainWindow = mainWindow
        self.application = mainWindow.application
        self.project = mainWindow.application.project
        self.current = mainWindow.application.current
        self.orderedSpectrumViews = orderedSpectrumViews
        self.orderedSpectra = set([spec.spectrum for spec in self.orderedSpectrumViews])

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setMinimumWidth(
                max(self.MINIMUM_WIDTH, self.MINIMUM_WIDTH_PER_TAB * len(self.orderedSpectra)))

        self._contoursTab = []
        for specNum, thisSpec in enumerate(self.orderedSpectra):
            self._contoursTab.append(ContoursTab(parent=self, mainWindow=self.mainWindow, spectrum=thisSpec))
            self.tabWidget.addTab(self._contoursTab[specNum], thisSpec.name)

        self.layout().addWidget(self.tabWidget, 0, 0, 2, 4)

        self.applyButtons = ButtonList(self, texts=['Cancel', 'Apply', 'Ok'],
                                       callbacks=[self.reject, self._applyChanges, self._okButton],
                                       tipTexts=['', '', '', None], direction='h',
                                       hAlign='r', grid=(2, 1), gridSpan=(1, 4))

        self._fillPullDowns()

        # clear the changes dict in each tab
        tabs = self._contoursTab
        for t in tabs:
            t._changes = dict()

    def _fillPullDowns(self):
        for aTab in self._contoursTab:
            fillColourPulldown(aTab.positiveColourBox, allowAuto=False)
            fillColourPulldown(aTab.negativeColourBox, allowAuto=False)

    def _keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            pass

    def _repopulate(self):
        if self._contoursTab:
            self._contoursTab._repopulate()

    def _applyAllChanges(self, changes):
        for v in changes.values():
            v()

    def _applyChanges(self):
        """
        The apply button has been clicked
        Define an undo block for setting the properties of the object
        If there is an error setting any values then generate an error message
          If anything has been added to the undo queue then remove it with application.undo()
          repopulate the popup widgets
        """
        tabs = self._contoursTab

        applyAccept = False
        _undo = self.project._undo
        oldUndo = _undo.numItems()

        from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier

        GLSignals = GLNotifier(parent=self)

        self.project._startCommandEchoBlock('_applyChanges', quiet=True)
        try:
            spectrumList = []
            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        spectrumList.append(t.spectrum)

            _undo._newItem(undoPartial=partial(_updateGl, self, spectrumList))

            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        self._applyAllChanges(changes)

            _undo._newItem(redoPartial=partial(_updateGl, self, spectrumList))

            for spec in spectrumList:
                for specViews in spec.spectrumViews:
                    specViews.buildContours = True

            # repaint
            GLSignals.emitPaintEvent()

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
            if oldUndo != self.project._undo.numItems():
                self.project._undo.undo()
                getLogger().debug('>>>Undo.%s._applychanges' % errorName)
            else:
                getLogger().debug('>>>Undo.%s._applychanges nothing to remove' % errorName)

            # repopulate popup
            self._repopulate()
            return False
        else:
            return True

    def _okButton(self):
        if self._applyChanges() is True:
            self.accept()


class SpectrumDisplayPropertiesPopup1d(CcpnDialog):
    """All spectra in the current display are added as tabs
    The apply button then steps through each tab, and calls each function in the _changes dictionary
    in order to set the parameters.
    """

    MINIMUM_WIDTH_PER_TAB = 120
    MINIMUM_WIDTH = 400

    def __init__(self, parent=None, mainWindow=None, orderedSpectrumViews=None,
                 title='Spectrum Display Properties', **kw):
        CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

        self.mainWindow = mainWindow
        self.application = mainWindow.application
        self.project = mainWindow.application.project
        self.current = mainWindow.application.current
        self.orderedSpectrumViews = orderedSpectrumViews
        self.orderedSpectra = [spec.spectrum for spec in self.orderedSpectrumViews]

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setMinimumWidth(
                max(self.MINIMUM_WIDTH, self.MINIMUM_WIDTH_PER_TAB * len(self.orderedSpectra)))

        self._generalTab = []
        # for specNum, thisSpec in enumerate(self.orderedSpectra):
        for specNum, thisSpec in enumerate(self.orderedSpectra):
            self._generalTab.append(ColourTab(parent=self, mainWindow=self.mainWindow, spectrum=thisSpec))
            self.tabWidget.addTab(self._generalTab[specNum], thisSpec.name)

        self.layout().addWidget(self.tabWidget, 0, 0, 2, 4)

        self.applyButtons = ButtonList(self, texts=['Cancel', 'Apply', 'Ok'],
                                       callbacks=[self.reject, self._applyChanges, self._okButton],
                                       tipTexts=['', '', '', None], direction='h',
                                       hAlign='r', grid=(2, 1), gridSpan=(1, 4))

        self._fillPullDowns()

        # clear the changes dict in each tab
        tabs = self._generalTab
        for t in tabs:
            t._changes = dict()

    def _fillPullDowns(self):
        for aTab in self._generalTab:
            fillColourPulldown(aTab.colourBox, allowAuto=False)

    def _keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            pass

    def _repopulate(self):
        pass
        # if self._generalTab:
        #   self._generalTab._repopulate()

    def _applyAllChanges(self, changes):
        for v in changes.values():
            v()

    def _applyChanges(self):
        """
        The apply button has been clicked
        Define an undo block for setting the properties of the object
        If there is an error setting any values then generate an error message
          If anything has been added to the undo queue then remove it with application.undo()
          repopulate the popup widgets
        """
        # tabs = self.tabWidget.findChildren(QtGui.QStackedWidget)[0].children()
        # tabs = [t for t in tabs if not isinstance(t, QtGui.QStackedLayout)]

        # ejb - error above, need to set the tabs explicitly
        tabs = self._generalTab

        applyAccept = False
        _undo = self.project._undo
        oldUndo = _undo.numItems()

        from ccpn.ui.gui.lib.OpenGL.CcpnOpenGL import GLNotifier

        GLSignals = GLNotifier(parent=self)

        self.project._startCommandEchoBlock('_applyChanges', quiet=True)
        try:
            spectrumList = []
            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        spectrumList.append(t.spectrum)

            _undo._newItem(undoPartial=partial(_updateGl, self, spectrumList))

            for t in tabs:
                if t is not None:
                    changes = t._changes
                    if changes:
                        self._applyAllChanges(changes)

            _undo._newItem(redoPartial=partial(_updateGl, self, spectrumList))

            # for specNum, thisSpec in enumerate(self.orderedSpectra):
            #   for specViews in thisSpec.spectrumViews:
            #
            #     specViews.buildContours = True

            for spec in spectrumList:
                for specViews in spec.spectrumViews:
                    specViews.buildContours = True

            # repaint
            GLSignals.emitPaintEvent()

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
            if oldUndo != self.project._undo.numItems():
                self.project._undo.undo()
                getLogger().debug('>>>Undo.%s._applychanges' % errorName)
            else:
                getLogger().debug('>>>Undo.%s._applychanges nothing to remove' % errorName)

            # repopulate popup
            self._repopulate()
            return False
        else:
            return True

    def _okButton(self):
        if self._applyChanges() is True:
            self.accept()


class ColourTab(QtWidgets.QWidget, Base):
    def __init__(self, parent=None, mainWindow=None, spectrum=None, item=None, colourOnly=False):

        from ccpnmodel.ccpncore.lib.spectrum.NmrExpPrototype import priorityNameRemapping

        super(ColourTab, self).__init__(parent)
        Base.__init__(self, setLayout=True)  # ejb

        self.parent = parent
        self.mainWindow = mainWindow
        self.application = self.mainWindow.application
        self.project = self.mainWindow.project

        self.item = item
        self.spectrum = spectrum
        self._changes = dict()
        self.atomCodes = ()

        self.pythonConsole = mainWindow.pythonConsole
        self.logger = getLogger()  # self.spectrum.project._logger

        Label(self, text="Colour", vAlign='t', hAlign='l', grid=(7, 0))
        self.colourBox = PulldownList(self, vAlign='t', grid=(7, 1))

        # populate initial pulldown
        spectrumColourKeys = list(spectrumColours.keys())
        fillColourPulldown(self.colourBox, allowAuto=False)
        c = self.spectrum.sliceColour
        if c in spectrumColourKeys:
            self.colourBox.setCurrentText(spectrumColours[c])
        else:
            addNewColourString(c)
            fillColourPulldown(self.colourBox, allowAuto=False)
            spectrumColourKeys = list(spectrumColours.keys())
            self.colourBox.setCurrentText(spectrumColours[c])

        self.colourBox.currentIndexChanged.connect(partial(self._queueChangeSliceComboIndex, self.spectrum))
        colourButton = Button(self, vAlign='t', hAlign='l', grid=(7, 2), hPolicy='fixed',
                              callback=partial(self._queueSetSpectrumColour, self.spectrum), icon='icons/colours')

    def _repopulate(self):
        pass

    def _writeLoggingMessage(self, command):
        self.logger.info("spectrum = project.getByPid('%s')" % self.spectrum.pid)
        self.logger.info(command)

    def _queueSetSpectrumColour(self, spectrum):
        dialog = ColourDialog(self)

        newColour = dialog.getColor()
        if newColour:
            # pix = QtGui.QPixmap(QtCore.QSize(20, 20))
            # pix.fill(QtGui.QColor(newColour))
            # newIndex = str(len(spectrumColours.items())+1)
            # self.colourBox.addItem(icon=QtGui.QIcon(pix), text='Colour %s' % newIndex)
            # # spectrumColours[newColour.name()] = 'Colour %s' % newIndex
            # addNewColour(newColour)
            #
            # self.colourBox.setCurrentIndex(int(newIndex)-1)

            addNewColour(newColour)
            self.parent._fillPullDowns()  #fillColourPulldown(self.colourBox, allowAuto=False)
            self.colourBox.setCurrentText(spectrumColours[newColour.name()])

            self._changes['spectrumColour'] = partial(self._setSpectrumColour, spectrum, newColour)

    def _setSpectrumColour(self, spectrum, newColour):
        spectrum._apiDataSource.setSliceColour(newColour.name())
        self._writeLoggingMessage("spectrum.sliceColour = '%s'" % newColour.name())
        self.pythonConsole.writeConsoleCommand("spectrum.sliceColour = '%s'" % newColour.name(), spectrum=self.spectrum)

    def _queueChangeSliceComboIndex(self, spectrum, value):
        self._changes['sliceComboIndex'] = partial(self._changedSliceComboIndex, spectrum, value)

    def _changedSliceComboIndex(self, spectrum, value):
        # newColour = list(spectrumColours.keys())[value]
        newColour = list(spectrumColours.keys())[list(spectrumColours.values()).index(self.colourBox.currentText())]
        if newColour:
            spectrum.sliceColour = newColour
            self._writeLoggingMessage("spectrum.sliceColour = '%s'" % newColour)
            self.pythonConsole.writeConsoleCommand("spectrum.sliceColour '%s'" % newColour, spectrum=self.spectrum)
