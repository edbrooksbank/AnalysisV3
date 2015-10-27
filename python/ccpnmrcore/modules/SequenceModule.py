__author__ = 'simon1'


from ccpn import Chain
from ccpn import Residue

from ccpncore.gui.Dock import CcpnDock
from ccpncore.gui.Font import Font
from ccpncore.util import Types

from ccpnmrcore.DropBase import DropBase
from PyQt4 import QtCore, QtGui

class SequenceModule(CcpnDock):

  def __init__(self, project):
    CcpnDock.__init__(self, name='Sequence')

    self.project=project
    self.colourScheme = project._appBase.preferences.general.colourScheme
    self.label.hide()
    self.setAcceptDrops(True)
    self.scrollArea = QtGui.QScrollArea()
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.scene = QtGui.QGraphicsScene(self)
    self.project = project
    self.scrollContents = QtGui.QGraphicsView(self.scrollArea.scene, self)
    self.scrollContents.setAcceptDrops(True)
    self.scrollContents.setAlignment(QtCore.Qt.AlignLeft)
    # self.scrollContents.setInteractive(True)
    self.scrollContents.setGeometry(QtCore.QRect(0, 0, 380, 1000))
    self.horizontalLayout2 = QtGui.QHBoxLayout(self.scrollContents)
    self.scrollArea.setWidget(self.scrollContents)
    self.setStyleSheet("""QScrollArea QScrollBar::horizontal {max-height: 10px;}
                          QScrollArea QScrollBar::vertical{max-width:10px;}
                      """)
    self.residueCount = 0
    self.layout.addWidget(self.scrollArea)

    self.scrollArea.scene.dragMoveEvent = self.dragMoveEvent
    self.chainLabels = []
    self.widgetHeight = 0
    for chain in project.chains:
      self._addChainLabel(chain)

    self.setFixedHeight(2*self.widgetHeight)
    self.scrollContents.setFixedHeight(2*self.widgetHeight)
    # for chainLabel in self.chainLabels:
    #   self.highlightPossibleStretches(chainLabel)

  def highlightPossibleStretches(self, residues:Types.List[Residue]):
    """
    Highlights regions on the sequence specified by the list of residues passed in.
    """
    if self.project._appBase.preferences.general.colourScheme == 'dark':
      colour = '#e4e15b'
    elif self.project._appBase.preferences.general.colourScheme == 'light':
      colour = '#009a00'
    for residue in residues:
      guiResidue = self.chainLabels[0].residueDict[residue.sequenceCode]
      guiResidue.setHtml('<div style="color: %s;text-align: center;">' % colour+
                           residue.shortName+'</div>')


  def _addChainLabel(self, chain:Chain):
    """
    Creates and adds a GuiChainLabel to the sequence module.
    """
    chainLabel = GuiChainLabel(self.project, self.scrollArea.scene, chain, position=[0, self.widgetHeight])
    self.scrollArea.scene.addItem(chainLabel)
    self.chainLabels.append(chainLabel)
    self.widgetHeight+=(0.8*(chainLabel.boundingRect().height()))


class GuiChainLabel(QtGui.QGraphicsTextItem):

  def __init__(self, project, scene, chain, position):
    QtGui.QGraphicsTextItem.__init__(self)
    self.chain = chain
    self.setPos(QtCore.QPointF(position[0], position[1]))
    self.text=chain.compoundName
    self.setHtml('<div style=><strong>'+chain.compoundName+': </strong></div>')
    self.setFont(Font(size=20, bold=True))
    if project._appBase.preferences.general.colourScheme == 'dark':
      colour = '#bec4f3'
    elif project._appBase.preferences.general.colourScheme == 'light':
      colour = '#bd8413'
    self.setDefaultTextColor(QtGui.QColor(colour))
    self.residueDict = {}
    i = 0
    for residue in chain.residues:
      newResidue = GuiChainResidue(self, project, residue, scene, self.boundingRect().width(), i, position[1])
      scene.addItem(newResidue)
      self.residueDict[residue.sequenceCode] = newResidue
      i+=1

class GuiChainResidue(DropBase, QtGui.QGraphicsTextItem):

  fontSize = 20

  def __init__(self, parent, project, residue, scene, labelPosition, index, yPosition):

    QtGui.QGraphicsTextItem.__init__(self)
    DropBase.__init__(self, project._appBase)
    self.setPlainText(residue.shortName)
    position = labelPosition+(20*index)
    self.setFont(Font(size=GuiChainResidue.fontSize, normal=True))
    if project._appBase.preferences.general.colourScheme == 'dark':
      colour1 = '#bec4f3'
      colour2 = '#f7ffff'
    elif project._appBase.preferences.general.colourScheme == 'light':
      colour1 = '#bd8413'
      colour2 = '#666e98'
    self.setDefaultTextColor(QtGui.QColor(colour1))
    self.setPos(QtCore.QPointF(position, yPosition))
    self.residueNumber = residue.sequenceCode
    if residue.nmrResidue is not None:
      self.setHtml('<div style="color: %s; text-align: center;"><strong>' % colour2 +
                   residue.shortName+'</strong></div>')
    else:
      self.setHtml('<div style:"text-align: center;">'+residue.shortName+'</div')
    self.project = project
    self.residue = residue
    self.setAcceptDrops(True)
    self.parent=parent
    scene.dragLeaveEvent = self._dragLeaveEvent
    scene.dragEnterEvent = self._dragEnterEvent
    scene.dropEvent = self.dropEvent
    self.scene = scene
    self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | self.flags())


  def _setFontBold(self):
    """
    Sets font to bold, necessary as QtGui.QGraphicsTextItem are used for display of residue
    one letter codes.
    """
    format = QtGui.QTextCharFormat()
    format.setFontWeight(75)
    self.textCursor().mergeCharFormat(format)


  def _dragEnterEvent(self, event:QtGui.QMouseEvent):

    if self.project._appBase.preferences.general.colourScheme == 'dark':
      colour = '#e4e15b'
    elif self.project._appBase.preferences.general.colourScheme == 'light':
      colour = '#009a00'
    item = self.scene.itemAt(event.scenePos())
    if isinstance(item, GuiChainResidue):
      item.setDefaultTextColor(QtGui.QColor(colour))
    event.accept()

  def _dragLeaveEvent(self, event:QtGui.QMouseEvent):
    if self.project._appBase.preferences.general.colourScheme == 'dark':
      colour = '#f7ffff'
    elif self.project._appBase.preferences.general.colourScheme == 'light':
      colour = '#666e98'
    item = self.scene.itemAt(event.scenePos())
    if isinstance(item, GuiChainResidue):
      item.setDefaultTextColor(QtGui.QColor(colour))
    event.accept()


  def processNmrResidues(self, data:Types.List[str], event:QtGui.QMouseEvent):
    """
    Process a list of NmrResidue Pids and assigns the residue onto which the data is dropped and
    all succeeding residues according to the length of the list.
    """
    if self.project._appBase.preferences.general.colourScheme == 'dark':
      colour = '#f7ffff'
    elif self.project._appBase.preferences.general.colourScheme == 'light':
      colour = '#666e98'
    res = self.scene.itemAt(event.scenePos())
    nmrResidue = self.project.getByPid(data[0])
    res.setHtml('<div style="color: %s; text-align: center;"><strong>' % colour +
                  res.residue.shortName+'</strong></div>')
    nmrResidue.residue = res.residue

    for assignableResidue in data[1:]:
      res = nmrResidue.residue.nextResidue
      guiResidue = self.parent.residueDict.get(res.sequenceCode)
      guiResidue.setHtml('<div style="color: %s; text-align: center;"><strong>' % colour+
                         res.shortName+'</strong></div>')
      nmrResidue = self.project.getByPid(assignableResidue)
      nmrResidue.residue = res






