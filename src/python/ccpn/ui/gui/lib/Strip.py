"""
Module Documentation.
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
__dateModified__ = "$dateModified: 2017-07-07 16:32:41 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import typing

from ccpn.util import Common as commonUtil
from ccpn.core.ChemicalShift import ChemicalShift
from ccpn.core.NmrAtom import NmrAtom
from ccpn.ui.gui.modules.GuiStrip import GuiStrip
from ccpn.ui.gui.lib import Window

from ccpn.util.Logging import getLogger


def _getCurrentZoomRatio(viewRange):
  xRange, yRange = viewRange
  xMin, xMax = xRange
  xRatio = (xMax - xMin)
  yMin, yMax = yRange
  yRatio = (yMax - yMin)
  return xRatio, yRatio


def navigateToPositionInStrip(strip, positions:typing.List[float], axisCodes:typing.List[str]=None,
                              widths:typing.List[float]=None):
  """
  Takes a strip, a list of positions and optionally, a parallel list of axisCodes.
  Navigates to specified positions in strip using axisCodes, if specified, otherwise it navigates
  to the positions in the displayed axis order of the strip.
  """

  if not axisCodes:
    axisCodes = strip.axisCodes

  # below does not work for the Navigate To right mouse menu option because in the width
  # setting further down, stripAxisIndex is not necessarily the same as ii
  # so the width in the z axis can be set to some huge number by mistake
  # if widths is None:
  #   widths = _getCurrentZoomRatio(strip.viewBox.viewRange())

  # _undo = strip.project._undo     # ejb - just a temporary fix
  # if _undo is not None:
  #   _undo.increaseBlocking()

  for ii, axisCode in enumerate(axisCodes):
    try:
      stripAxisIndex = strip.axisCodes.index(axisCode)
    except ValueError as e:
      continue
    if len(positions)>ii: # this used to say 1 rather than ii (coupled with the else below)
      if positions[ii]:
        strip.orderedAxes[stripAxisIndex].position = positions[ii]

    #else: # what in the world is the case this is trying to deal with??
           # why would you want to set all the positions to the same thing??
    #  strip.orderedAxes[stripAxisIndex].position = positions[0]

    if widths is not None:
      try:
        if widths[ii]: # FIXME this can be out of range
          # if this item in the list contains a float, set the axis width to that float value
          if isinstance(widths[ii], float):
            strip.orderedAxes[stripAxisIndex].width = widths[ii]
          elif isinstance(widths[ii], str):
            # if the list item is a str with value, full, reset the corresponding axis
            if widths[ii] == 'full':
              strip.resetAxisRange(stripAxisIndex)
            if widths[ii] == 'default' and stripAxisIndex < 2:
              # if the list item is a str with value, default, set width to 5ppm for heteronuclei and 0.5ppm for 1H
              if (commonUtil.name2IsotopeCode(axisCode) == '13C' or
                  commonUtil.name2IsotopeCode(axisCode) == '15N'):
                strip.orderedAxes[stripAxisIndex].width = 5
              else:
                strip.orderedAxes[stripAxisIndex].width = 0.5
      except:
        continue

  # if _undo is not None:
  #   _undo.decreaseBlocking()


def matchAxesAndNmrAtoms(strip:GuiStrip, nmrAtoms:typing.List[NmrAtom]):

  shiftDict = {}
  shiftList = strip.spectra[0].chemicalShiftList
  for axis in strip.orderedAxes:
    shiftDict[axis.code] = []
    for atom in nmrAtoms:
      if atom.isotopeCode == commonUtil.name2IsotopeCode(axis.code):
        shift = shiftList.getChemicalShift(atom.id)
        if shift is not None and isPositionWithinfBounds(strip, shift, axis):
          shiftDict[axis.code].append(shift)

  return shiftDict


def isPositionWithinfBounds(strip:GuiStrip, shift:ChemicalShift, axis:object):
  """
  Determines whether a given shift is within the bounds of the specified axis of the specified
  strip.

  NBNB Bug Fixed by Rasmus 13/3/2016.
  This was not used then. Maybe it should be?

  Modified to use aliasingLimits instead of spectrumLimits. Rasmus, 24/7/2016

  """
  minima = []
  maxima = []

  axisIndex = strip.axisOrder.index(axis.code)

  for spectrumView in strip.spectrumViews:
    spectrumIndices = spectrumView._displayOrderSpectrumDimensionIndices
    index = spectrumIndices[axisIndex]
    if index:
      minima.append(spectrumView.spectrum.aliasingLimits[index][0])
      maxima.append(spectrumView.spectrum.aliasingLimits[index][1])

  if len(maxima) < 1:
    return True
  else:
    return min(minima) < shift.value <= max(maxima)


def navigateToNmrAtomsInStrip(strip:GuiStrip, nmrAtoms:typing.List[NmrAtom], widths=None,
                              markPositions:bool=False, setNmrResidueLabel=False):
  """
  Takes an NmrResidue and optional spectrum displays and strips and navigates the strips
  and spectrum displays to the positions specified by the peak.
  """
  getLogger().debug('strip: %r, nmrAtoms:%s, widths=%s, markPositions:%s, setSpinSystemLabel:%s' %
                    (strip.pid, nmrAtoms, widths, markPositions, setNmrResidueLabel)
                   )

  if not strip:
    getLogger().warning('navigateToNmrAtomsInStrip: no strip specified')
    return

  if len(nmrAtoms) == 0:
    getLogger().warning('navigateToNmrAtomsInStrip: no atoms specified')

  shiftDict = matchAxesAndNmrAtoms(strip, nmrAtoms)
  # atomPositions = shiftDict[strip.axisOrder[2]]
  atomPositions = [[x.value for x in shiftDict[axisCode]] for axisCode in strip.axisOrder]
  positions = []
  for atomPos in atomPositions:
    if atomPos:
      if len(atomPos) < 2:
        positions.append(atomPos[0])
      else:
        positions.append(max(atomPos)-min(atomPos)/2)
    else:
      positions.append('')
  navigateToPositionInStrip(strip, positions, widths=widths)

  if markPositions:
    strip.spectrumDisplay.mainWindow.markPositions(list(shiftDict.keys()), list(shiftDict.values()))

  if setNmrResidueLabel:
    strip.setStripLabelText(nmrAtoms[0].nmrResidue.pid)
    strip.showStripLabel()


def navigateToNmrResidueInDisplay(nmrResidue, display, stripIndex=0, widths=None,
                                  showSequentialResidues=False, markPositions=True):
  """
  Navigate in to nmrResidue in strip[stripIndex] of display, with optionally-1, +1 residues in
  strips[stripIndex-1] and strips[stripIndex+1]
  return list of strips
  
  :param nmrResidue: 
  :param display:
  :param stripIndex: location of strip in display (assumed 0 if connected and showSequentialResidues)
  :param widths: ignored (for now)
  :param showSequentialResidues: boolean selecting if sequential strips are displayed
  :param markPositions: boolean selecting if marks are displayed
  :return list of strips 
  """

  getLogger().debug('display=%r, nmrResidue=%r, showSequentialResidues=%s, markPositions=%s' %
               (display.id, nmrResidue.id, showSequentialResidues, markPositions)
               )

  nmrResidue = nmrResidue.mainNmrResidue
  strips = []
  if showSequentialResidues and (nmrResidue.nmrChain.isConnected
                                 or nmrResidue.residue is not None):
    # showing sequential strips

    # NB Rasmus 11/7/2017.
    # For showSequentialResidues we want to show the exact number of strips,
    # resetting what was there earlier, rather than keeping old ones around
    # NB if we go back to showing long stretches, this will have to be changed.
    # Meanwhile we ignore stripINdex in this branch of the 'if' statement

    # Previous code, kept for comparison :
    # stripIndex = 0  # for now enforce this, o/w below would be more complicated
    #
    # previousNmrResidue = nmrResidue.previousNmrResidue
    # nextNmrResidue = nmrResidue.nextNmrResidue
    # minNumStrips = 1
    # if previousNmrResidue:
    #   minNumStrips += 1
    # if nextNmrResidue:
    #   minNumStrips += 1
    #
    # # showing sequential strips
    # while len(display.strips) < minNumStrips:
    #     display.addStrip()
    #
    # # display the previousNmrResidue if not None
    # if previousNmrResidue is not None:
    #   navigateToNmrAtomsInStrip(display.strips[stripIndex], previousNmrResidue.nmrAtoms,
    #                             widths=None, markPositions=False, setNmrResidueLabel=True)
    #   strips.append(display.strips[stripIndex])
    #   stripIndex += 1
    #
    # if nmrResidue is not None: # this better be true or would hit Exception long before you get here
    #   navigateToNmrAtomsInStrip(display.strips[stripIndex], nmrResidue.nmrAtoms,
    #                             widths=None, markPositions=markPositions, setNmrResidueLabel=True)
    #   strips.append(display.strips[stripIndex])
    #   stripIndex += 1
    #
    # # display the nextNmrResidue if not None
    # if nextNmrResidue is not None:
    #   navigateToNmrAtomsInStrip(display.strips[stripIndex], nextNmrResidue.nmrAtoms,
    #                             widths=None, markPositions=False, setNmrResidueLabel=True)
    #   strips.append(display.strips[stripIndex]) now enforce this, o/w below would be more complicated



    # show the three connected nmrResidues in the strip
    # but alqways show the end three if connected and the strip long enough

    allNmrResidues = nmrResidue._getAllConnectedList()
    if len(allNmrResidues) < 3:
      nmrResidues = allNmrResidues                          # display those that we have
    else:
      nmrMid = allNmrResidues.index(nmrResidue)             # get the index of the required element
      nmrMid = min(max(nmrMid, 1), len(allNmrResidues)-2)
      nmrResidues = allNmrResidues[nmrMid-1:nmrMid+2]

    # nmrResidues = []
    # previousNmrResidue = nmrResidue.previousNmrResidue
    # if previousNmrResidue:
    #   nmrResidues.append(previousNmrResidue)
    # nmrResidues.append(nmrResidue)
    # nextNmrResidue = nmrResidue.nextNmrResidue
    # if nextNmrResidue:
    #   nmrResidues.append(nextNmrResidue)

    stripCount = len(nmrResidues)
    while len(display.strips) < stripCount:
        display.addStrip()
    for strip in display.strips[stripCount:]:
      display.removeStrip(strip)
    strips = display.strips

    # widths = ['default'] * len(display.strips)
    for ii,nr in enumerate(nmrResidues):
      navigateToNmrAtomsInStrip(strips[ii], nr.nmrAtoms,
                                widths=widths, markPositions=markPositions, setNmrResidueLabel=True)

  else:
    # not showing sequential strips
    # widths = ['default'] * len(display.strips)
    for strip in display.strips[stripIndex+1:]:
      display.removeStrip(strip)
    navigateToNmrAtomsInStrip(display.strips[stripIndex], nmrResidue.nmrAtoms,
                              widths=widths, markPositions=markPositions, setNmrResidueLabel=True)
    strips.append(display.strips[stripIndex])

  return strips

