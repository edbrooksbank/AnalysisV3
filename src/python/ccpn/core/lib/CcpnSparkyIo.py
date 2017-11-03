"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = ""
__credits__ = ""
__licence__ = ("")
__reference__ = ("")
#=========================================================================================
# Last code modification:
#=========================================================================================
__modifiedBy__ = "$modifiedBy$"
__dateModified__ = "$dateModified$"
__version__ = "$Revision$"
#=========================================================================================
# Created:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

# import random
import os
# import sys
import time
# import typing
# import itertools
# import errno
import re
import collections
import pandas as pd

try:
  # Python 3
  from itertools import zip_longest
except:
  # python 2.7
  from itertools import izip_longest as zip_longest

# from datetime import datetime
from collections import OrderedDict
from ccpn.core.Project import Project

# from ccpn.core.Spectrum import Spectrum
# from ccpn.core.SpectrumGroup import SpectrumGroup
# from ccpn.core.Complex import Complex
# from ccpn.core.PeakList import PeakList
# from ccpn.core.IntegralList import IntegralList
# from ccpn.core.Integral import Integral
# from ccpn.core.Peak import Peak
# from ccpn.core.Sample import Sample
# from ccpn.core.SampleComponent import SampleComponent
# from ccpn.core.Substance import Substance
# from ccpn.core.Chain import Chain
# from ccpn.core.Residue import Residue
# from ccpn.core.Atom import Atom
# from ccpn.core.NmrChain import NmrChain
# from ccpn.core.NmrResidue import NmrResidue
# from ccpnmodel.ccpncore.lib.Io import Formats as ioFormats
from ccpn.util.Logging import getLogger

sparkyReadingOrder = [
  'sparky_nmr_meta_data',
  'sparky_molecular_system',
  'ccpn_sample',
  'ccpn_substance',
  'ccpn_assignment',
  'sparky_chemical_shift_list',
  'ccpn_dataset',
  'sparky_distance_restraint_list',
  'sparky_dihedral_restraint_list',
  'sparky_rdc_restraint_list',
  'sparky_nmr_spectrum',
  'sparky_peak_restraint_links',
  'ccpn_complex',
  'ccpn_spectrum_group',
  'ccpn_restraint_list',
  'ccpn_notes',
  'ccpn_additional_data'
]

# possibly for later
sparkyWritingOrder = ([x for x in sparkyReadingOrder if x.startswith('sparky_')] +
                         [x for x in sparkyReadingOrder if not x.startswith('sparky_')])

_isALoop = ()

# not sure how to use this yet
sparky2CcpnMap = {
  'sparky_nmr_meta_data':OrderedDict((
    ('format_name',None),
    ('format_version',None),
    ('program_name',None),
    ('program_version',None),
    ('creation_date',None),
    ('uuid',None),
    ('coordinate_file_name',None),
    ('ccpn_dataset_serial', None),
    ('ccpn_dataset_comment',None),
    ('sparky_related_entries',_isALoop),
    ('sparky_program_script',_isALoop),
    ('sparky_run_history',_isALoop),
  )),
  'sparky_related_entries':OrderedDict((
    ('database_name',None),
    ('database_accession_code',None),
  )),
  'sparky_program_script':OrderedDict((
    ('program_name',None),
    ('script_name',None),
    ('script',None),
  ))
}

# STAR parsing REGEX, following International Tables for Crystallography volume G section 2.1
_SPARKY_REGEX = r"""(?xmi) # $Revision$  # No 'u' flag for perl 5.8.8/RHEL5 compatibility
  ^;([\S\s]*?)(?:\r\n|\s)^;(?:(?=\s)|$)  # 1  Multi-line string
  |(?:^|(?<=\s))(\#.*?)\r?$              # 2  Comment
  |(?:^|(?<=\s))(?:(global_)             # 3  
  |<sparky\s(.*?)>                       # 4  Sparky project start
  |(\$\S+)                               # 5  STAR save frame reference
  |<end\s(.*?)>                          # 6  block terminator
  |<(version\s.*?)>                      # 7  block start
  |<(.*?)>                               # 8  block header   - shouldn't need the leading whitespace
  |((?:global_\S+)|(?:stop_\S+)|(?:data_)|(?:loop_\S+))  # 9 Invalid privileged construct
  |(_\S+)                                # 10 Data name
  |'(.*?)'                               # 11 Single-quoted string
  |"(.*?)"                               # 12 Double-quoted string
  |(\.)                                  # 13 CIF null
  |(\?)                                  # 14 CIF unknown/missing
  |((?:[^'";_$\s]|(?!^);).*)(?<![ ])     # 15 Non-quoted string - exclude pre/post whitespace
  |([\[\]]\S*)                           # 16 Square bracketed constructs (reserved)
  |(\S+)                                 # 17 Catch-all bad token
)
(?:(?=\s)|$)"""

# Compiled form of _REGEX
_sparky_pattern = re.compile(_SPARKY_REGEX, re.UNICODE)

# Token types. NB numbers must be synced to regex - these are used directly!!!
SP_TOKEN_MULTILINE        = 1
SP_TOKEN_COMMENT          = 2
SP_TOKEN_GLOBAL           = 3
SP_TOKEN_SPARKY_PROJECT   = 4
SP_TOKEN_SAVE_FRAME_REF   = 5
SP_TOKEN_END_SPARKY_BLOCK = 6
SP_TOKEN_VERSION          = 7
SP_TOKEN_SPARKY_BLOCK     = 8
SP_TOKEN_BAD_CONSTRUCT    = 9
SP_TOKEN_DATA_NAME        = 10
SP_TOKEN_SQUOTE_STRING    = 11
SP_TOKEN_DQUOTE_STRING    = 12
SP_TOKEN_NULL             = 13
SP_TOKEN_UNKNOWN          = 14
SP_TOKEN_STRING           = 15
SP_TOKEN_SQUARE_BRACKET   = 16
SP_TOKEN_BAD_TOKEN        = 17

SparkyToken = collections.namedtuple('SparkyToken', ('type', 'value'))

class UnquotedValue(str):
  """A plain string - the only difference is the type: 'UnquotedValue'.
  Used to distinguish values from STAR files that were not quoted.
  STAR special values (like null,  unknown, ...) are only recognised if unquoted strings"""
  pass

# Constants for I/O of standard values
NULLSTRING = UnquotedValue('.')
UNKNOWNSTRING = UnquotedValue('?')
TRUESTRING = UnquotedValue('true')
FALSESTRING = UnquotedValue('false')
NANSTRING = UnquotedValue('NaN')
PLUSINFINITYSTRING = UnquotedValue('Infinity')
MINUSINFINITYSTRING = UnquotedValue('-Infinity')


def getSparkyTokenIterator(text):
  """Iterator that returns an iterator over all STAR tokens in a generic STAR file"""
  return (SparkyToken(x.lastindex, x.group(x.lastindex))
          for x in _sparky_pattern.finditer(text))

class SparkySyntaxError(ValueError):
  pass

class NamedOrderedDict(OrderedDict):
  def __init__(self, name=None):
    super(NamedOrderedDict, self).__init__()
    self.name = name

  def __str__(self):
    return '%s(name=%s)' % (self.__class__.__name__, self.name)

  def __repr__(self):
    return '%s(%s, name=%s)' % (self.__class__.__name__, list(tt for tt in self.items()), self.name)

  def addItem(self, tag, value):
    if tag in self:
      raise ValueError("%s: duplicate key name %s" % (self, tag))
    else:
      self[tag] = value


class SparkyBlock(NamedOrderedDict):
  """Top level container for general STAR object tree"""
  def __init__(self, name='Root'):
    super(SparkyBlock, self).__init__(name=name)

  def getData(self):
    dataBlocks = [self[db] for db in self.keys() if 'data' in db]
    return [ll for x in dataBlocks for ll in x]     # concaternate data lists

  def getDataValues(self, value, firstOnly=False):
    dataBlocks = [self[db] for db in self.keys() if 'data' in db]
    spList = []
    for spType in dataBlocks:
      if spType:
        spType = [re.findall(r'%s\s?(.*)\s*' % value, sT) for sT in spType]
        spList.extend([ll for x in spType for ll in x])

    if spList:
      if firstOnly:
        return spList[0]
      else:
        return spList
    else:
      return None

  def _getBlocks(self, value, list=[]):
    if value in self.name:
      list.append(self)

    for ky in self.keys():
      if isinstance(self[ky], SparkyBlock):
        self[ky]._getBlocks(value, list)

    return list

  def getBlocks(self, value, firstOnly=False):
    list = self._getBlocks(value, list=[])
    if list:
      if firstOnly:
        return list[0]
      else:
        return list
    else:
      return None

# class SparkyProjectBlock(NamedOrderedDict):
#   """Top level container for general STAR object tree"""
#   def __init__(self, name='Root'):
#     super(SparkyProjectBlock, self).__init__(name=name)
#

class CcpnSparkyReader:

  def __init__(self, application:str, specificationFile:str=None, mode:str='standard',
               testing:bool=False):

    # just copied from Rasmus for the minute
    self.application = application
    self.mode=mode
    self.saveFrameName = None
    self.warnings = []
    self.errors = []
    self.testing = testing
    self.text = None
    self.tokeniser = None
    self.allowSquareBracketStrings = False
    self.lowerCaseTags = True
    self.enforceSaveFrameStop = False
    self.enforceLoopStop = False

    self.stack = []
    self.globalsCounter = 0
    self.columns = ['ResidueType', 'ResidueCode', 'FirstAtomName', 'SecondAtomName']

  def _processVersion(self, value):
    # next token must be version
    stack = self.stack
    last = stack[-1]

    if isinstance(last, SparkyBlock):
      try:
        func = last
      except AttributeError:
        raise SparkySyntaxError(self._errorMessage("Error inserting version num" % value,
                                                 value))
      func['version'] = value

    elif isinstance(last, list):
      try:
        func = last.append
      except AttributeError:
        raise SparkySyntaxError(self._errorMessage("Error inserting version num" % value,
                                                   value))
      func(value)

    return

  def _processComment(self, value):
    # Comments are ignored
    return

  def processValue(self, value):
    stack = self.stack
    last = stack[-1]

    # if isinstance(last, SparkyProjectBlock):
    #   # currently ignore until we have a SparkyBlock
    #   return

    if isinstance(last, SparkyBlock):
      return

    if isinstance(last, str):
      # Value half of tag, value pair
      stack.pop()
      stack[-1].addItem(last, value)
    else:
      try:
        func = last.append
      except AttributeError:
        raise SparkySyntaxError(self._errorMessage("Data value %s must be in item or loop_" % value,
                                                 value))
      func(value)

  def _processBadToken(self, value, typ):
    raise SparkySyntaxError(self._errorMessage("Illegal token of type% s:  %s" % (typ, value), value))

  def _addSparkyBlock(self, name):
    container = self.stack[-1]

    currentNames = [ky for ky in container.keys() if name in ky]

    if currentNames:
      name = name+str(len(currentNames))   # add an incremental number to the name

    # name is the new named block
    obj = SparkyBlock(name)
    container.addItem(name, obj)
    self.stack.append(obj)
    self.stack.append(list())     # put a list on as well

  def _closeSparkyBlock(self, value):

    stack =  self.stack
    lowerValue = value.lower()

    # Terminate loop
    if isinstance(stack[-1], list):
      if self.enforceLoopStop:
        raise SparkySyntaxError(
          self._errorMessage("Loop terminated by %s instead of stop_" % value, value)
        )
      else:
        # Close loop and pop it off the stack
        self._closeList(value)

    # terminate SparkyBlock
    if isinstance(stack[-1], SparkyBlock):
      blockName = value[5:-1]
      if lowerValue.startswith('<end') and stack[-1].name == blockName:
        # Simple terminator. Close save frame
        stack.pop()

      elif self.enforceSaveFrameStop:
        self._errorMessage("SaveFrame terminated by %s instead of save_" % value, value)

      else:
        # New saveframe start. We are missing the terminator, but close and continue anyway
        stack.pop()

    stack.append(list())          # in case there are more data items to add

    if not isinstance((stack[-1]), SparkyBlock):
      if lowerValue.startswith('<end '):
        raise SparkySyntaxError(self._errorMessage("'%s' found out of context" % value, value))

  def _openSparkyBlock(self, value):
    # start a new sparky block, which is everything
    stack = self.stack

    # Add new SparkyBlock
    if self.lowerCaseTags:
      value = value.lower()
    if isinstance(stack[-1], SparkyBlock):
      self._addSparkyBlock(value)

    elif isinstance(stack[-1], list):
      self._closeList(value)                                  # close the list and store
      self._addSparkyBlock(value)

    else:
      raise SparkySyntaxError(
        self._errorMessage("SparkyBlock start out of context: %s" % value, value)
      )

  def _closeList(self, value):

    stack = self.stack
    data = stack.pop()        # remove the list from the end
    block = stack[-1]         # point to the last block
    if not isinstance(block, SparkyBlock):
      if isinstance(data, SparkyBlock):
        raise TypeError("Implementation error, loop not correctly put on stack")
      else:
        raise SparkySyntaxError(self._errorMessage("Loop stop_ %s outside loop" % value, value))

    # columnCount = len(loop._columns)
    # if not columnCount:
    #   raise SparkySyntaxError(self._errorMessage(" loop lacks column names" , value))

    if data:

      dataName = 'data'
      currentNames = [ky for ky in block.keys() if 'data' in ky]
      if currentNames:
        dataName = 'data' + str(len(currentNames))  # add an incremental number to the name

      block[dataName] = data

      # if len(data) % columnCount:
      #   if self.padIncompleteLoops:
      #     print("WARNING Token %s: %s in %s is missing %s values. Last row was: %s"
      #           % (self.counter, loop, self.stack[-2],
      #              columnCount - (len(data) % columnCount), data[-1]))
      #   else:
      #     raise SparkySyntaxError(
      #       self._errorMessage("loop %s is missing %s values"
      #                          % (loop, (columnCount - (len(data) % columnCount))), value)
      #     )
      #
      # # Make rows:
      # args = [iter(data)] * columnCount
      # for tt in zip_longest(*args, fillvalue=NULLSTRING):
      #   loop.newRow(values=tt)

    else:
      # empty loops appear here. We allow them, but that could change
      pass

  def parseSparkyFile(self, path):

    with open(path, 'r') as fileName:
      self.text = fileName.read()

    self.tokeniser = getSparkyTokenIterator(self.text)

    processValue = self.processValue
    processFunctions = [None] * 20
    processFunctions[SP_TOKEN_SQUOTE_STRING] = self.processValue
    processFunctions[SP_TOKEN_DQUOTE_STRING] = self.processValue
    # processFunctions[SP_TOKEN_MULTILINE] = self.processValue
    processFunctions[SP_TOKEN_VERSION] = self._processVersion
    processFunctions[SP_TOKEN_COMMENT] = self._processComment

    # processFunctions[SP_TOKEN_LOOP] = self._openLoop
    # processFunctions[SP_TOKEN_LOOP_STOP] = self._closeLoop
    # processFunctions[SP_TOKEN_GLOBAL] = self._processGlobal
    # processFunctions[SP_TOKEN_DATA_BLOCK] = self._processDataBlock

    unquotedValueTags = (SP_TOKEN_STRING, SP_TOKEN_NULL, SP_TOKEN_UNKNOWN, SP_TOKEN_SAVE_FRAME_REF)
    # quotedValueTags = (TOKEN_SQUOTE_STRING, TOKEN_DQUOTE_STRING, TOKEN_MULTILINE)

    stack = self.stack

    name = os.path.splitext(os.path.basename(path))[0]
    # result = SparkyProjectBlock(name=name)
    # stack.append(result)

    # now process the file

    value = None
    self.counter = 0   # Token counter
    try:
      for tk in self.tokeniser:
        self.counter += 1
        typ, value = tk

        if typ in unquotedValueTags:
          value = UnquotedValue(value)
          processValue(value)

        else:
          func = processFunctions[typ]

          if func is None:

            if typ == SP_TOKEN_SPARKY_PROJECT:
              # put the first element on the stack
              result = SparkyBlock(name=name)           # result is the actually object, which SHOULD contain all
              stack.append(result)
              stack.append(list())  # put an empty list on the stack

              processValue("sparky %s" % value)     # put the type on the stack
              processValue("name %s" % name)
              processValue("pathname %s" % os.path.dirname(path))

            elif typ == SP_TOKEN_SPARKY_BLOCK:
              # save_ string
              self._openSparkyBlock(value)

            elif typ == SP_TOKEN_END_SPARKY_BLOCK:
                self._closeSparkyBlock(value)

            elif typ in (SP_TOKEN_BAD_CONSTRUCT, SP_TOKEN_BAD_TOKEN):
              self._processBadToken(value, typ)

            elif typ == SP_TOKEN_SQUARE_BRACKET:
              if self.allowSquareBracketStrings:
                processValue(UnquotedValue(value))
              else:
                self._processBadToken(value, typ)

            else:
              raise SparkySyntaxError("Unknown token type: %s" % typ)
          else:
            func(value)


      # End of data - clean up stack
      if isinstance(stack[-1], str):
        raise SparkySyntaxError(self._errorMessage("File ends with item name", value))

      if isinstance(stack[-1], list):
        self._closeList('<End-of-File>')

      if isinstance(stack[-1], SparkyBlock):
        stack.pop()

      if stack:
        raise RuntimeError(self._errorMessage("stack not empty at end of file", value))
    except Exception as es:
      print("ERROR at token %s" % self.counter)
      raise
    #
    return result

  def _errorMessage(self, msg, value):
    """Make standard error message"""
    template = "Error in context: %s, at token %s, line: %s\n%s"
    tags = [(x if isinstance(x, str) else x.name) for x in self.stack[1:]] + [value]

    lines = self.text.splitlines()
    lineCount = len(lines)
    ii = 0
    if tags:
      jj = 0
      tag = tags[jj]
      while ii < lineCount:
        if tag in lines[ii].lower().split():
          # This line contains the current tag - go to the next tag
          jj += 1
          if jj < len(tags):
            tag = tags[jj]
          else:
            # This line contains the last of the tags - it is the line we want
            break
        else:
          # nothing found here - try next line
          ii += 1
    #
    return template % (tags[:-1], tags[-1], ii+1, msg)#

  def _getSparkyDataList(self, sparkyBlock, value):
    if 'data' in sparkyBlock and sparkyBlock['data']:
      spType = sparkyBlock['data']
      if spType:
        spType = [re.findall(r'%s\s?(.*)\s*' % value, sT) for sT in spType]
        spType = [ll for x in spType for ll in x]
        if spType:
          return spType

    return None

  def _getSparkyBlock(self, sparkyBlock, name, list=[]):
    if name in sparkyBlock.name:
      list.append(sparkyBlock)

    for ky in sparkyBlock.keys():
      if isinstance(sparkyBlock[ky], SparkyBlock):
        self._getSparkyBlock(sparkyBlock[ky], name, list)

    return list

  def importSaveFile(self, project, saveBlock):
    pathName = saveBlock.getDataValues('pathname', firstOnly=True)

    spectra = saveBlock.getBlocks('spectrum', firstOnly=True)
    fileName = spectra.getDataValues('name', firstOnly=True)
    filePath = spectra.getDataValues('pathname', firstOnly=True)

    spectrumPath = os.path.abspath(os.path.join(pathName, filePath))
    workshopPath = os.path.abspath(
      os.path.join(pathName, '../lists/' + fileName + '.list.workshop'))

    self.project.loadData(spectrumPath)  # load the spectrum

    self.initParser(self.project, workshopPath, project.spectra[-1])

  def importSparkyProject(self, project, sparkyBlock):
    """Import entire project from dataBlock into empty Project"""
    t0 = time.time()

    self.warnings = []
    self.project = project

    # traverse the sparkyBlock and insert into project
    sparkyType = sparkyBlock.getDataValues('sparky', firstOnly=True)

    if sparkyType == 'project file':
      # load project file
      fileName = sparkyBlock.getDataValues('name', firstOnly=True)
      filePath = sparkyBlock.getDataValues('pathname', firstOnly=True)

      saveFiles = sparkyBlock.getBlocks('savefiles', firstOnly=True)
      loadedBlocks = []
      for sp in saveFiles.getData():
        savefilePath = os.path.abspath(os.path.join(filePath, sp))
        loadedBlocks.append(self.parseSparkyFile(savefilePath))

      # test
      self.importSaveFile(project, loadedBlocks[0])   # modify to load from the project

    elif sparkyType == 'save file':
      self.importSaveFile(project, sparkyBlock)
      # pathName = sparkyBlock.getDataValues('pathname', firstOnly=True)
      #
      # spectra = sparkyBlock.getBlocks('spectrum', firstOnly=True)
      # fileName = spectra.getDataValues('name', firstOnly=True)
      # filePath = spectra.getDataValues('pathname', firstOnly=True)
      #
      # spectrumPath = os.path.abspath(os.path.join(pathName, filePath))
      # workshopPath = os.path.abspath(os.path.join(pathName, '../lists/'+fileName+'.list.workshop'))
      #
      # self.project.loadData(spectrumPath)     # load the spectrum
      #
      # self.initParser(self.project, workshopPath, project.spectra[-1])

    else:
        getLogger().warning('Unknown Sparky File Type')

    t2 = time.time()
    getLogger().debug('Imported Sparky file into project, time = %.2fs' %(t2-t0))

    for msg in self.warnings:
      print ('====> ', msg)
    self.project = None

  def _createDataFrame(self, input_path):
    return pd.read_table(input_path, delim_whitespace=True, )

  def _splitAssignmentColumn(self, dataFrame):
    ''' parses the assignment column.
    Splits the column assignment in  four columns: ResidueName ResidueCode AtomName1 AtomName2.
    '''
    assignments = [re.findall('\d+|\D+', s) for s in dataFrame.iloc[:, 0]]
    assignmentsColumns = []
    for a in assignments:
      try:
        i,j,*args = a
        atoms = (''.join(args)).split('-')
        if len(atoms) == 2:
            firstAtom, secondAtom = atoms
            assignmentsColumns += ((i,j,firstAtom, secondAtom),)
      except:
        getLogger().warning('Undefined atom assignment %s' % str(a))

    return pd.DataFrame(assignmentsColumns,columns=self.columns)

  def _mergeDataFrames(self, generalDF, assignmentDF):
    '''
    :param generalDF: first dataframe with assignments all in on column
    :param assignmentDF: assignments dataframe  in  4 columns
    :return: new dataframe with four assignment columns + the original without the first column
    '''
    partialDf = generalDF.drop(generalDF.columns[0], axis=1)
    return pd.concat([assignmentDF, partialDf], axis=1, join_axes=[partialDf.index])

  def _correctChainResidueCodes(self, chain, ccpnDataFrame):
    ''' renames Chain residueCodes correctly according with the dataFrame, if duplicates, deletes them.
    '''
    for residue,resNumber, in zip(chain.residues, ccpnDataFrame.ResidueCode):
      try:
        residue.rename(str(resNumber))
      except:
        residue.delete()
    return chain

  def _createCcpnChain(self, project, ccpnDataFrame):
    '''makes a chain from the ResidueTypes.
    CCPN wants a long list of  one Letter Codes without spaces'''
    residueTypes = ''.join([i for i in ccpnDataFrame.ResidueType])
    newChain = project.createChain(residueTypes,molType='protein')
    self._correctChainResidueCodes(newChain, ccpnDataFrame)
    return newChain

  def _fetchAndAssignNmrAtom(self, peak, nmrResidue, atomName):
    atom = nmrResidue.fetchNmrAtom(name=str(atomName))
    peak.assignDimension(axisCode=atomName[0], value=[atom])

  def _connectNmrResidues(self, nmrChain):
    updatingNmrChain = None
    nrs = nmrChain.nmrResidues
    for i in range(len(nrs) - 1):
      currentItem, nextItem = nrs[i], nrs[i + 1]
      if currentItem or nextItem is not None:
        updatingNmrChain = currentItem.connectNext(nextItem, )
    return updatingNmrChain

  def _assignNmrResiduesToResidues(self, connectedNmrChain, ccpnChain):
    for nmrResidue, residue in zip(connectedNmrChain.nmrResidues, ccpnChain.residues):
      nmrResidue.residue = residue

  def _parseDataFrame(self, ccpnDataFrame, spectrum, nmrChain):

    lastNmrResidue = None
    newPeakList = spectrum.newPeakList()
    foundResNumber = list(ccpnDataFrame.iloc[:,1])
    for i, resType, resNumber, atom1, atom2, pos1, pos2, in zip(range(len(ccpnDataFrame.iloc[:,0]) -1), ccpnDataFrame.iloc[:,0],
                                                              ccpnDataFrame.iloc[:,1], ccpnDataFrame.iloc[:,2],
                                                              ccpnDataFrame.iloc[:,3], ccpnDataFrame.iloc[:,4],
                                                              ccpnDataFrame.iloc[:,5]):

      peak = newPeakList.newPeak(position=(float(pos2), float(pos1)))

      if resNumber in foundResNumber[:i]:  # in case of duplicated Residues Eg sideChain W2023N-H H and W2023NE1-HE1, don't need to create a new nmrResidue, just add the atoms to the previous one.
        nmrResidue = lastNmrResidue
        if nmrResidue:
          self._fetchAndAssignNmrAtom(peak, nmrResidue, atom2)
          self._fetchAndAssignNmrAtom(peak, nmrResidue, atom1)

      else:
        nmrResidue = nmrChain.fetchNmrResidue(sequenceCode=str(resNumber))
        lastNmrResidue = nmrResidue
        if nmrResidue:
          self._fetchAndAssignNmrAtom(peak, nmrResidue, atom2)
          self._fetchAndAssignNmrAtom(peak, nmrResidue, atom1)

    return nmrChain

  def initParser(self, project, input_path, spectrum):
    generalDF = self._createDataFrame(input_path)
    assignmentDF = self._splitAssignmentColumn(generalDF)
    ccpnDataFrame = self._mergeDataFrames(generalDF, assignmentDF)
    ccpnChain = self._createCcpnChain(project, ccpnDataFrame)
    nmrChain = project.fetchNmrChain('A')
    newNmrChain = self._parseDataFrame(ccpnDataFrame, spectrum, nmrChain)
    connectedNmrChain = self._connectNmrResidues(newNmrChain)
    self._assignNmrResiduesToResidues(connectedNmrChain, ccpnChain)


class CcpnSparkyWriter:
  # ejb - won't be implemented yet
  def __init__(self, project:Project, specificationFile:str=None, mode:str='strict',
               programName:str=None, programVersion:str=None):
    self.project = project
    self.mode=mode