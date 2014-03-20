from PySide import QtCore, QtGui

from ccpncore.gui.Base import Base
from ccpncore.gui.Icon import Icon

CHECKED = QtCore.Qt.Checked
UNCHECKED = QtCore.Qt.Unchecked

class Button(QtGui.QPushButton, Base):

  def __init__(self, parent, text='', callback=None, icon=None,
               toggle=None, **kw):
    
    QtGui.QPushButton.__init__(self, parent)
    Base.__init__(self, **kw)
    
    self.setText(text)

    if icon: # filename or pixmap
      self.setIcon(Icon(icon))
      self.setIconSize(QtCore.QSize(22,22))
    
    if toggle is not None:
      self.setCheckable(True)
      self.setSelected(toggle)
      
    self.callback = None
    self.setCallback(callback)

  def setSelected(self, selected):
    
    if self.isCheckable(): 
      if selected:
        self.setChecked(CHECKED)
      else:
        self.setChecked(UNCHECKED)

  def setCallback(self, callback):
  
    if self.callback:
      self.disconnect(self, QtCore.SIGNAL('clicked()'), self.callback)
    
    if callback:
      self.connect(self, QtCore.SIGNAL('clicked()'), callback)
      # self.clicked.connect doesn't work with lambda, yet...
    
    self.callback = callback

  def setText(self, text):

    QtGui.QPushButton.setText(self, self.translate(text))

if __name__ == '__main__':

  from ccpncore.gui.Application import TestApplication

  app = TestApplication()

  window = QtGui.QWidget()
  
  def click():
    print("Clicked")
  
  b1 = Button(window, text='Click Me', callback=click,
             tipText='Click for action',
             grid=(0, 0))

  b2 = Button(window, text='I am inactive', callback=click,
             tipText='Cannot click',
             grid=(0, 1))
  
  b2.setEnabled(False)

  b3 = Button(window, text='I am green', callback=click,
             tipText='Mmm, green', bgColor='#80FF80',
             grid=(0, 2))

  b4 = Button(window, icon='icons/system-help.png', callback=click,
             tipText='A toggled icon button', toggle=True, 
             grid=(0, 3))

  window.show()
  
  app.start()

