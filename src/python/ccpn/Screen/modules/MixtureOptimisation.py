from PyQt4 import QtCore, QtGui
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Icon import Icon
# from ccpn.ui.gui.widgets.VerticalTab import VerticalTabWidget
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
# from ccpn.ui.gui.popups.SampleSetupPopup import ExcludeRegions


class MixtureOptimisation(CcpnModule):

  '''Creates a module to analyse the mixtures'''

  def __init__(self, parent=None, project=None):
    super(MixtureOptimisation, self)
    CcpnModule.__init__(self, name='Mixture Optimisation')

    self.project = project
    # if self._appBase.ui.mainWindow is not None:
    #   self.mainWindow = self._appBase.ui.mainWindow
    # else:
    #   self.mainWindow = self._appBase._mainWindow

    self.mainWindow = parent
    self.moduleArea = self.mainWindow.moduleArea
    self.framework = self.mainWindow.framework
    self.generalPreferences = self.framework.preferences.general
    self.colourScheme = self.generalPreferences.colourScheme
    # self.excludeRegions = ExcludeRegions
    print('This module is under implementation, not active yet')
    self.implementationLabel = Label(self, 'This module is under implementation, not active yet')

    ######## ======== Set Main Layout ====== ########
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QVBoxLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0)

    ######## ======== Set Secondary Layout ====== ########
    self.settingFrameLayout = QtGui.QHBoxLayout()
    self.buttonsFrameLayout = QtGui.QHBoxLayout()
    self.mainLayout.addLayout(self.settingFrameLayout)
    self.mainLayout.addLayout(self.buttonsFrameLayout)

    ######## ======== Set Tabs  ====== ########
    self.tabWidget = QtGui.QTabWidget()
    self.settingFrameLayout.addWidget(self.tabWidget)
    # self.tabWidget.setTabBar(VerticalTabWidget(width=130,height=25))
    # self.tabWidget.setTabPosition(QtGui.QTabWidget.West)

    ######## ======== Set Buttons  ====== ########
    self.panelButtons = ButtonList(self, texts=['Show Status', 'Show Graph', 'Cancel', 'Perform'],
                                   callbacks=[None, None, None, None],
                                   icons=[None, None, None, None],
                                   tipTexts=[None, None, None, None],
                                   direction='H')
    self.buttonsFrameLayout.addWidget(self.panelButtons)
    self._disableButtons()

    ######## ======== Set 1 Tab  ====== ########
    self.tab1Frame = QtGui.QFrame()
    self.tab1Layout = QtGui.QGridLayout()
    self.tab1Frame.setLayout(self.tab1Layout)
    self.tabWidget.addTab(self.tab1Frame, 'Iterations')

    self.selectNumberLabel = Label(self, 'Select Number of Iterations')
    self.iterationBox = Spinbox(self, value=1, min=1)
    # self.iterationBox.setFixedWidth(80)
    self.tab1Layout.addWidget(self.selectNumberLabel, 0,0)
    self.tab1Layout.addWidget(self.iterationBox, 0,1)
    self.tab1Layout.addWidget(self.implementationLabel, 1, 0, 1, 1)

    ######## ======== Set 2 Tab  ====== ########
    self.tab2Frame = QtGui.QFrame()
    self.tab2Layout = QtGui.QGridLayout()
    self.tab2Frame.setLayout(self.tab2Layout)
    self.tabWidget.addTab(self.tab2Frame, 'Minimal overlap')

    self.distanceLabel = Label(self, text="Minimal distance between peaks")
    self.ppmDistance = DoubleSpinbox(self)
    # self.ppmDistance.setFixedWidth(80)
    self.tab2Layout.addWidget(self.distanceLabel, 0,0)
    self.tab2Layout.addWidget(self.ppmDistance, 0,1)

    ######## ======== Set 3 Tab  ====== ########
    self.tab3Frame = QtGui.QFrame()
    self.tab3Layout = QtGui.QGridLayout()
    self.tab3Frame.setLayout(self.tab3Layout)
    self.tabWidget.addTab(self.tab3Frame, 'Exclude Regions')

    # self.excludeRegions = ExcludeRegions()
    # self.tab3Layout.addWidget(self.excludeRegions)


    ######## ======== Set 4 Tab  ====== ########
    self.tab4Frame = QtGui.QFrame()
    self.tab4Layout = QtGui.QGridLayout()
    self.tab4Frame.setLayout(self.tab4Layout)
    self.tabWidget.addTab(self.tab4Frame, 'Others')

    self.replaceMixtureLabel = Label(self, text="Replace Mixtures")
    self.replaceRadioButtons = RadioButtons(self,
                                            texts=['Yes', 'No'],
                                            selectedInd=0,
                                            callback=None,
                                            tipTexts=None)
    self.tab4Layout.addWidget(self.replaceMixtureLabel, 0,0)
    self.tab4Layout.addWidget(self.replaceRadioButtons, 0,1)

  def _disableButtons(self):
    for button in self.panelButtons.buttons:
      button.setEnabled(False)
      button.setStyleSheet("background-color:#868D9D; color: #000000")
