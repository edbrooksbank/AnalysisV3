#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:40:37 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from ccpn.framework.lib.Pipe import PandasPipe

class DemoExtension(PandasPipe):
  '''
  Demo auto-generated gui for pipeline
  '''
  METHODNAME = 'Demo'

  from collections import OrderedDict
  # TODO: Expand dictionary spec
  params = [{'variable' : 'param1',
             'value'    : ('Fast', 'Slow'),
             'label'    : 'Param #1',
             'default'  : 'Fast'},                        # List

            {'variable' : 'param2',
             'value'    : False,
             'default'  : 0},                              # checkbox 0 unchecked 2 checked

            {'variable': 'param43',
             'value': (('White 1',False),('Red 2',True)),  #  RadioButtons
             'default': 'Red 2'},

            {'variable' : 'param3',
             'value'    : ('0', '4'),
             'default'  : 4},                                # List

            {'variable' : 'param4',                         # Spinbox
             'value'    : (0, 4),
             'default'  : (3)},

            {'variable' : 'param5',                         # Spinbox with default
             'value'    : (0, 4),
             'default'  : 2},

            {'variable' : 'param6',                         # Spinbox with stepsize
             'value'    : (0, 4),
             'stepsize' : 2,
             'default'  : 3},

            {'variable' : 'param7',                         # Spinbox with default and stepsize
             'value'    : (0, 4),
             'stepsize' : 2,
             'default'  : 2},

            {'variable' : 'param8',                         # Double Spinbox
             'value'    : (0., 1),
             'default'  : 0.3},

            {'variable' : 'param9',                         # Double Spinbox with default
             'value'    : (0., 1.),
             'default'  : 0.2},

            {'variable' : 'param10',                         # Double Spinbox with stepsize
             'value'    : (0., 1.),
             'stepsize' : 0.1,
             'default'  : 0.2},

            {'variable' : 'param11',                         # Double Spinbox with default and stepsize
             'value'    : (0., 1),
             'stepsize' : 0.1,
             'default'  : 0.2},

            {'variable': 'param12',                         # LineEdit
             'value': '',
             'default'  : 'param12'},

            {'variable': 'param13',
             'value': (('Ford', 'Focus'),                    # Mapped list
                       ('BMW', '320'),
                       ('Fiat', '500')
                      ),
             'default'  : 'Focus'},
            ]

  def run(self, dataframe, test=None, **params):
    print('', str(test), params)
    return dataframe
