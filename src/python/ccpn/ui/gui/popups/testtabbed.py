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
__dateModified__ = "$dateModified: 2017-04-10 15:35:09 +0100 (Mon, April 10, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: simon $"
__date__ = "$Date: 2017-03-30 11:28:58 +0100 (Thu, March 30, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtCore, QtGui
from ccpn.ui.gui.popups.Dialog import CcpnDialog      # ejb


class TabDialog(CcpnDialog):
    def __init__(self, fileName, parent=None, title='Tab Dialog', **kw):
        CcpnDialog.__init__(self, parent, setLayout=True, windowTitle=title, **kw)

        fileInfo = QtCore.QFileInfo(fileName)

        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(GeneralTab(fileInfo), "General")
        tabWidget.addTab(PermissionsTab(fileInfo), "Permissions")
        tabWidget.addTab(ApplicationsTab(fileInfo), "Applications")

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Tab Dialog")


class GeneralTab(QtGui.QWidget):
    def __init__(self, fileInfo, parent=None):
        super(GeneralTab, self).__init__(parent)

        fileNameLabel = QtGui.QLabel("File Name:")
        fileNameEdit = QtGui.QLineEdit(fileInfo.fileName())

        pathLabel = QtGui.QLabel("Path:")
        pathValueLabel = QtGui.QLabel(fileInfo.absoluteFilePath())
        pathValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        sizeLabel = QtGui.QLabel("Size:")
        size = fileInfo.size() // 1024
        sizeValueLabel = QtGui.QLabel("%d K" % size)
        sizeValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        lastReadLabel = QtGui.QLabel("Last Read:")
        lastReadValueLabel = QtGui.QLabel(fileInfo.lastRead().toString())
        lastReadValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        lastModLabel = QtGui.QLabel("Last Modified:")
        lastModValueLabel = QtGui.QLabel(fileInfo.lastModified().toString())
        lastModValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(fileNameLabel)
        mainLayout.addWidget(fileNameEdit)
        mainLayout.addWidget(pathLabel)
        mainLayout.addWidget(pathValueLabel)
        mainLayout.addWidget(sizeLabel)
        mainLayout.addWidget(sizeValueLabel)
        mainLayout.addWidget(lastReadLabel)
        mainLayout.addWidget(lastReadValueLabel)
        mainLayout.addWidget(lastModLabel)
        mainLayout.addWidget(lastModValueLabel)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class PermissionsTab(QtGui.QWidget):
    def __init__(self, fileInfo, parent=None):
        super(PermissionsTab, self).__init__(parent)

        permissionsGroup = QtGui.QGroupBox("Permissions")

        readable = QtGui.QCheckBox("Readable")
        if fileInfo.isReadable():
            readable.setChecked(True)

        writable = QtGui.QCheckBox("Writable")
        if fileInfo.isWritable():
            writable.setChecked(True)

        executable = QtGui.QCheckBox("Executable")
        if fileInfo.isExecutable():
            executable.setChecked(True)

        ownerGroup = QtGui.QGroupBox("Ownership")

        ownerLabel = QtGui.QLabel("Owner")
        ownerValueLabel = QtGui.QLabel(fileInfo.owner())
        ownerValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        groupLabel = QtGui.QLabel("Group")
        groupValueLabel = QtGui.QLabel(fileInfo.group())
        groupValueLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        permissionsLayout = QtGui.QVBoxLayout()
        permissionsLayout.addWidget(readable)
        permissionsLayout.addWidget(writable)
        permissionsLayout.addWidget(executable)
        permissionsGroup.setLayout(permissionsLayout)

        ownerLayout = QtGui.QVBoxLayout()
        ownerLayout.addWidget(ownerLabel)
        ownerLayout.addWidget(ownerValueLabel)
        ownerLayout.addWidget(groupLabel)
        ownerLayout.addWidget(groupValueLabel)
        ownerGroup.setLayout(ownerLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(permissionsGroup)
        mainLayout.addWidget(ownerGroup)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class ApplicationsTab(QtGui.QWidget):
    def __init__(self, fileInfo, parent=None):
        super(ApplicationsTab, self).__init__(parent)

        topLabel = QtGui.QLabel("Open with:")

        applicationsListBox = QtGui.QListWidget()
        applications = []

        for i in range(1, 31):
            applications.append("Application %d" % i)

        applicationsListBox.insertItems(0, applications)

        alwaysCheckBox = QtGui.QCheckBox()

        if fileInfo.suffix():
            alwaysCheckBox = QtGui.QCheckBox("Always use this application to "
                    "open files with the extension '%s'" % fileInfo.suffix())
        else:
            alwaysCheckBox = QtGui.QCheckBox("Always use this application to "
                    "open this type of file")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(topLabel)
        layout.addWidget(applicationsListBox)
        layout.addWidget(alwaysCheckBox)
        self.setLayout(layout)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    if len(sys.argv) >= 2:
        fileName = sys.argv[1]
    else:
        fileName = "."

    tabdialog = TabDialog(fileName)
    sys.exit(tabdialog.exec_())
