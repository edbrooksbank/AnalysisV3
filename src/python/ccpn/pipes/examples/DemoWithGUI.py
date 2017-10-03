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
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:39 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


#### GUI IMPORTS
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, PipelineDropArea , AutoGeneratedGuiPipe
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Label import Label

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import Pipe
from ccpn.pipes.examples.DemoWithAutoGUI import AutoGeneratedGuiPipeDemo

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

ReferenceSpectrum = 'referenceSpectrum'
PipeName = 'AlignSpectra'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################


def myAlgorithm(data):
    # do something
    return data



########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################

class DemoGuiPipe(GuiPipe):
  preferredPipe = True
  pipeName = PipeName

  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(DemoGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    ## add widgets to pipeFrame using Base grid=(i,ii) or self.pipeLayout.addWidget(widgetName)
    ## suggested to use setattr to give the same variable name as the one used in the pipe _kwarg.
    ## the guiPipe _kwarg is autogenerated from the variable name of widget and value.

    self.spectrumLabel = Label(self.pipeFrame, 'Reference Spectrum', grid=(0, 0))
    setattr(self, ReferenceSpectrum, PulldownList(self.pipeFrame, texts=['spectrum1', 'spectrum2'], grid=(0, 1)))




########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class DemoPipe1(Pipe):

  guiPipe = DemoGuiPipe
  pipeName = PipeName

  _kwargs = {
            ReferenceSpectrum: 'spectrum2'
            }

  def runPipe(self, data):
    output = myAlgorithm(data)
    return output




########################################################################################################################
##########################################      RUN TEST GUI PIPE     ##################################################
########################################################################################################################

if __name__ == '__main__':
  from PyQt5 import QtGui, QtWidgets
  from ccpn.ui.gui.widgets.Application import TestApplication

  app = TestApplication()
  win = QtWidgets.QMainWindow()

  pipeline = PipelineDropArea()
  demoGuiPipe = DemoGuiPipe(parent=pipeline)
  pipeline.addDock(demoGuiPipe)

  win.setCentralWidget(pipeline)
  win.resize(1000, 500)
  win.show()

  app.start()

