"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = "$Revision: 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtCore, QtGui

from application.core.DropBase import DropBase
from application.core.modules.CreateSequence import CreateSequence
from application.core.modules.NotesEditor import NotesEditor
from application.core.popups.NmrAtomPopup import NmrAtomPopup
from application.core.popups.NmrChainPopup import NmrChainPopup
from application.core.popups.NmrResiduePopup import NmrResiduePopup
from application.core.popups.PeakListPropertesPopup import PeakListPropertiesPopup
from application.core.popups.RestraintTypePopup import RestraintTypePopup
from application.core.popups.SpectrumPropertiesPopup import SpectrumPropertiesPopup
from application.core.popups.SamplePropertiesPopup import SamplePropertiesPopup, EditSampleComponentPopup


from ccpn import Project
from ccpn import Spectrum
from ccpn import AbstractWrapperObject

from ccpncore.util import Pid
from ccpncore.util.Types import Sequence

NEW_ITEM_DICT = {
  'SP': 'newPeakList',
  'NC': 'newNmrResidue',
  'NR': 'newNmrAtom',
  'RS': 'newRestraintList',
  'RL': 'newRestraint',
  'SE': 'newModel',
  'Notes': 'newNote',
  'Structures': 'newStructureEnsemble',
  'Samples': 'newSample',
  'NmrChains': 'newNmrChain',
  'Chains': 'CreateSequence',
  'Substances': 'newSubstance',
  'Chemical Shift Lists': 'newChemicalShiftList',
  'Restraint Sets': 'newRestraintSet',
}
### Flag example code removed in revision 7686

class SideBar(DropBase, QtGui.QTreeWidget):
  def __init__(self, parent=None ):
    QtGui.QTreeWidget.__init__(self, parent)

    self._typeToItem = dd = {}

    self.setFont(QtGui.QFont('Lucida Grande', 12))
    self.header().hide()
    self.setDragEnabled(True)
    self._appBase = parent._appBase
    self.setExpandsOnDoubleClick(False)
    self.setDragDropMode(self.InternalMove)
    self.setMinimumWidth(200)
    self.projectItem = dd['PR'] = QtGui.QTreeWidgetItem(self)
    self.projectItem.setText(0, "Project")
    self.projectItem.setExpanded(True)
    self.spectrumItem = dd['SP'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.spectrumItem.setText(0, "Spectra")
    self.spectrumGroupItem = dd['SG'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.spectrumGroupItem.setText(0, "Spectrum Groups")
    self.samplesItem = dd['SA'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.samplesItem.setText(0, 'Samples')
    self.newSample = QtGui.QTreeWidgetItem(self.samplesItem)
    self.newSample.setText(0, "<New>")
    self.substancesItem = dd['SU'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.substancesItem.setText(0, "Substances")
    self.newSubstanceItem = QtGui.QTreeWidgetItem(self.substancesItem)
    self.newSubstanceItem.setText(0, '<New>')
    self.chainItem = dd['MC'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.chainItem.setText(0, "Chains")
    self.newChainItem = QtGui.QTreeWidgetItem(self.chainItem)
    self.newChainItem.setText(0, '<New>')
    self.nmrChainItem = dd['NC'] =  QtGui.QTreeWidgetItem(self.projectItem)
    self.nmrChainItem.setText(0, "NmrChains")
    self.newNmrChainItem = QtGui.QTreeWidgetItem(self.nmrChainItem)
    self.newNmrChainItem.setText(0, '<New>')
    self.chemicalShiftListsItem = dd['CL'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.chemicalShiftListsItem.setText(0, "Chemical Shift Lists")
    self.newChemicalShiftListItem = QtGui.QTreeWidgetItem(self.chemicalShiftListsItem)
    self.newChemicalShiftListItem.setText(0, '<New>')
    self.structuresItem = dd['SE'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.structuresItem.setText(0, "Structures")
    self.restraintSetsItem = dd['RS'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.restraintSetsItem.setText(0, "Datasets")
    self.newRestraintSetItem = QtGui.QTreeWidgetItem(self.restraintSetsItem)
    self.newRestraintSetItem.setText(0, '<New>')
    self.notesItem = dd['NO'] = QtGui.QTreeWidgetItem(self.projectItem)
    self.notesItem.setText(0, "Notes")
    self.newNoteItem = QtGui.QTreeWidgetItem(self.notesItem)
    self.newNoteItem.setText(0, '<New>')



  def setProject(self, project:Project):
    """
    Sets the specified project as a class attribute so it can be accessed from elsewhere
    """
    self.project = project

  def addItem(self, item:QtGui.QTreeWidgetItem, pid:str):
    """
    Adds a QTreeWidgetItem as a child of the item specified, which corresponds to the data object
    passed in.
    """
    newItem = QtGui.QTreeWidgetItem(item)
    newItem.setFlags(newItem.flags() & ~(QtCore.Qt.ItemIsDropEnabled))
    newItem.setData(0, QtCore.Qt.DisplayRole, pid)
    newItem.mousePressEvent = self.mousePressEvent
    return newItem

  def renameItem(self, pid):
    # item = FindItem
    pass



  def mousePressEvent(self, event):
    """
    Re-implementation of the mouse press event so right click can be used to delete items from the
    sidebar.
    """
    if event.button() == QtCore.Qt.RightButton:
      self.raiseContextMenu(event, self.itemAt(event.pos()))
    else:
      QtGui.QTreeWidget.mousePressEvent(self, event)

  def raiseContextMenu(self, event:QtGui.QMouseEvent, item:QtGui.QTreeWidgetItem):
    """
    Creates and raises a context menu enabling items to be deleted from the sidebar.
    """
    from ccpncore.gui.Menu import Menu
    contextMenu = Menu('', self, isFloatWidget=True)
    from functools import partial
    # contextMenu.addAction('Delete', partial(self.removeItem, item))
    contextMenu.addAction('Delete', partial(self._deleteItemObject, item))
    contextMenu.popup(event.globalPos())

  # NBNB TBD FIXME. Sorry, but this will need refactoring.
  # 1) semantically, removeItem should only remove the item, not delete the underlying object
  # 2) If deleting the object triggers item removal, item removal cannot trigger item deletion
  # I think I have refactored this by changing raiseContextMenu, but you need to double check
  #
  # You can rename the new functions (probably remove the underscore)
  # I just wanted to give them distinctive names to avoid confusion

  # RHF: Removed and replaced by _deleteItemObject
  # def removeItem(self, item:QtGui.QTreeWidgetItem):
  #   """
  #   Removes the specified item from the sidebar and the project.
  #
  #    NBNB TBD this function should be retired and replaced by the new _deleteItemObject
  #    Note that _removeItem does SOMETHInG ELSE
  #   """
  #   import sip
  #   self.project.getByPid(item.data(0, QtCore.Qt.DisplayRole)).delete()
  #   sip.delete(item)

  def _deleteItemObject(self,  item:QtGui.QTreeWidgetItem):
    """Removes the specified item from the sidebar and deletes it from the project.
    NB, the clean-up of the side bar is done through notifiers
    """
    self.project.getByPid(item.data(0, QtCore.Qt.DisplayRole)).delete()

  def _createItem(self, obj:AbstractWrapperObject):
    """Create a new sidebar item from a new object.
    Called by notifier when a new object is created or undeleted (so need to check for duplicates).
    NB Obj may be of a type that does not have an item"""

    if not isinstance(obj, AbstractWrapperObject):
      return

    shortClassName = obj.shortClassName

    if shortClassName == 'SP':
      # Spectrum - special behaviour - appear under SpectrumGroups, if any
      spectrumGroups = obj.spectrumGroups
      if spectrumGroups:
        for sg in spectrumGroups:
          for sgitem in self._findItems(sg.pid):
            self.addItem(sgitem, obj.pid)

        return

    # If we get to here we have only one object to deal with
    # get itemType from passed-in object
    itemParent = self._typeToItem.get(shortClassName)
    if itemParent is not None:
      self.addItem(itemParent, obj.pid)

  def _renameItem(self, oldPid:str, newPid:str):
    """rename item(s) from object pdi oldPid to object pid newPid"""
    for item in self._findItems(oldPid):
      item.setData(0, QtCore.Qt.DisplayRole, str(newPid))

  def _removeItem(self, objPid):
    """Removes sidebar item(s) for objec with pid objPid, but does NOT delete the object.
    Called when objects are deleted"""
    import sip
    for item in self._findItems(objPid):
      sip.delete(item)

  def _findItems(self, objPid:str) -> QtGui.QTreeWidgetItem:
    """Find items that match objPid - returns empty list if no matches"""

    acceptableObjects = set(('SP', 'PL', 'SG', 'SA' 'SC', 'SU', 'MC', 'NC', 'NR', 'NA', 'CL', 'SE',
                         'MO', 'DS', 'NO'))
    if objPid[:2] in acceptableObjects:
      result = self.findItems(objPid, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)

    else:
      result = []

    return result

  def fillSideBar(self, project:Project):
    """
    Fills the sidebar with the relevant data from the project.
    """
    self.projectItem.setText(0, project.name)
    for spectrum in project.spectra:
      newItem = self.addItem(self.spectrumItem, spectrum.pid)
      if spectrum is not None:
        anItem = QtGui.QTreeWidgetItem(newItem)
        anItem.setText(0, '<New>')
        for peakList in spectrum.peakLists:
          peakListItem = QtGui.QTreeWidgetItem(newItem)
          peakListItem.setText(0, peakList.pid)

    for spectrumGroup in project.spectrumGroups:
      newItem = self.addItem(self.spectrumGroupItem, spectrumGroup.pid)

    for chain in project.chains:
      newItem = self.addItem(self.chainItem, chain.pid)
    for nmrChain in project.nmrChains:
      newItem = self.addItem(self.nmrChainItem, nmrChain.pid)
      for nmrResidue in nmrChain.nmrResidues:
        newItem3 = self.addItem(newItem, nmrResidue.pid)
        for nmrAtom in nmrResidue.nmrAtoms:
          newItem5 = self.addItem(newItem3, nmrAtom.pid)
    for chemicalShiftList in project.chemicalShiftLists:
      newItem = self.addItem(self.chemicalShiftListsItem, chemicalShiftList.pid)

    for restraintSet in project.restraintSets:
      newItem = self.addItem(self.restraintSetsItem, restraintSet.pid)
      newItem2 = QtGui.QTreeWidgetItem(newItem)
      newItem2.setText(0, '<New>')
      for restraintList in restraintSet.restraintLists:
        newItem4 = self.addItem(newItem, restraintList.pid)
        newItem3 = QtGui.QTreeWidgetItem(newItem4)
        newItem3.setText(0, '<New>')
        for restraint in restraintList.restraints:
          newItem5 = self.addItem(newItem4, restraint.pid)

    for structureEnsemble in project.structureEnsembles:
      newItem = self.addItem(self.structuresItem, structureEnsemble.pid)
      for model in structureEnsemble.models:
        newItem3 = self.addItem(newItem, model.pid)

    for note in project.notes:
      newItem = self.addItem(self.notesItem, note.pid)



  def clearSideBar(self):
    """
    Clears all data from the sidebar.
    """
    self.projectItem.setText(0, "Project")
    self.spectrumItem.setText(0, "Spectra")
    self.spectrumItem.setText(0, "Reference")
    self.spectrumItem.takeChildren()

  def dragEnterEvent(self, event, enter=True):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      import json
      item = self.itemAt(event.pos())
      if item:
        itemData = json.dumps({'pids':[item.text(0)]})
        event.mimeData().setData('ccpnmr-json', itemData)
        event.mimeData().setText(itemData)

  def dragMoveEvent(self, event:QtGui.QMouseEvent):
    """
    Required function to enable dragging and dropping within the sidebar.
    """
    event.accept()

  # RHF 9/2/2016: Function no longer used
  # def addSpectrum(self, spectrum:(Spectrum,Pid)):
  #   """
  #   Adds the specified spectrum to the sidebar.
  #   """
  #   peakList = spectrum.newPeakList()
  #   newItem = self.addItem(self.spectrumItem, spectrum)
  #   peakListItem = QtGui.QTreeWidgetItem(newItem)
  #   peakListItem.setText(0, peakList.pid)

  # RHF 9/2/2016: Function no longer used
  # def processNotes(self, pids:Sequence[str], event):
  #   """Display notes defined by list of Pid strings"""
  #   for ss in pids:
  #     note = self.project.getByPid(ss)
  #     self.addItem(self.notesItem, note)

  def raisePopup(self, obj, item):
    if obj.shortClassName == 'SP':
      popup = SpectrumPropertiesPopup(obj)
      popup.exec_()
      popup.raise_()
    elif obj.shortClassName == 'PL':
      popup = PeakListPropertiesPopup(peakList=obj)
      popup.exec_()
      popup.raise_()

    elif obj.shortClassName == 'SA':
      popup = SamplePropertiesPopup(obj, project=self.project)
      popup.exec_()
      popup.raise_()

    elif obj.shortClassName == 'SC':
      popup = EditSampleComponentPopup(sampleComponent=obj)
      popup.exec_()
      popup.raise_()
    elif obj.shortClassName == 'SU':
      pass
    elif obj.shortClassName == 'NC':
      popup = NmrChainPopup(nmrChain=obj)
      popup.exec_()
      popup.raise_()
    elif obj.shortClassName == 'NR':
      popup = NmrResiduePopup(nmrResidue=obj)
      popup.exec_()
      popup.raise_()
    elif obj.shortClassName == 'NA':
      popup = NmrAtomPopup(nmrAtom=obj)
      popup.exec_()
      popup.raise_()
    elif obj.shortClassName == 'CS':
      pass
    elif obj.shortClassName == 'SE':
      pass #to be decided when we design structure
    elif obj.shortClassName == 'MD':
      pass #to be decided when we design structure
    elif obj.shortClassName == 'RS':
      pass #to be decided when we design structure
    elif obj.shortClassName == 'RL':
      pass #to be decided when we design structure
    elif obj.shortClassName == 'RE':
      pass #to be decided when we design structure
    elif obj.shortClassName == 'NO':
      self.notesEditor = NotesEditor(self._appBase.mainWindow.dockArea, self.project, name='Notes Editor', note=obj)

  def createNewObject(self, item):

    itemParent = self.project.getByPid(item.parent().text(0))
    if itemParent is not None:
      if itemParent.shortClassName == 'RS':
        popup = RestraintTypePopup()
        popup.exec_()
        popup.raise_()
        restraintType = popup.restraintType
        funcName = NEW_ITEM_DICT.get(itemParent.shortClassName)
        # Naughty - this is a wrapper object, not an item
        # newItem = getattr(itemParent, funcName)(restraintType)
        getattr(itemParent, funcName)(restraintType)
        # No longer necessary
        # self.addItem(item.parent(), newItem)
      elif item.parent.shortClassName == 'SA':
        newComponent = itemParent.newSampleComponent()
        popup = EditSampleComponentPopup(sampleComponent=newComponent)
        popup.exec_()
        popup.raise_()
        return
      else:
        funcName = NEW_ITEM_DICT.get(itemParent.shortClassName)

    else:
      if item.parent().text(0) == 'Chains':
        popup = CreateSequence(project=self.project)
        popup.exec_()
        popup.raise_()
        return
      else:
        itemParent = self.project
        funcName = NEW_ITEM_DICT.get(item.parent().text(0))

    # Naughty - this is a wrapper object, not an item
    # newItem = getattr(itemParent, funcName)()
    getattr(itemParent, funcName)()
    # No longer necessary
    # self.addItem(item.parent(), newItem)
