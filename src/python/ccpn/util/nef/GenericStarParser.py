"""Star-type file parser, agnostic between cif, mmcif, star, nef, etc.
Returns a nested data structure that matches the file,
with DataExtent, DataBlock, SaveFrame, and Loop objects.
Additional support for distinguishing between None, True, False, and int/float values
and the strings that match their representations.

Usage:

parse(text, mode) to parse a text representation

parseFile(fileName, mode) to load and parse a file


Reading behaviour
=================

follows the specification in
International Tables for Crystallography volume G section 2.1
with the following exceptions:

  - Nested loops are NOT supported

  - Global blocks are treated as simple data blocks. If the first data block in the file is
    a global_, is is named 'global_'; globals elsewhere are named global_1, global_2, etc.
    This may cause trouble downstream if there is a DataBlock named e.g. 'data_global_1'.

The object structure returned is:

::

    DataExtent
      DataBlock
        Item
        Loop
        SaveFrame
          Item
          Loop

DataExtent, DataBlock and SaveFrame are Python OrderedDict with an additional 'name' attribute
DataBlocks and SaveFrames are entered in their container using their name as the key.

Loop is an object with a 'columns' list, a 'data' list-of-row-OrderedDict, and a name attribute
set equal to the name of the first column. A loop is entered in its container under each
column name, so that e.g. aSaveFrame['_Loopx.loopcol1'] and aSaveFrame['_Loopx.loopcol2'] both
exist and both correspond to the same loop object.

Items are entered as a string key - string value pair.

All tags are preserved 'as is' (i.e. without stripping leading '_', 'data_', or 'save_'),
basically to avoid the theoretical risk that a SaveFrame name might clash with
an item name or loop column, or a DataBLock with a Global. Duplicate tags raise an error.

Quoted values are returned as str,
whereas unquoted values are returned as a str subtype UnquotedValue(str)
This allows later distinction between null, unknown, saveframe_reference and the
equivalent quoted strings.



Writing behaviour
=================

follows the specification in
International Tables for Crystallography volume G section 2.1
with the following exceptions and additions.

  - Strings of type UnquotedValue are written as-is, without quoting them.

  - Note that e.g. ' "say" 'what'?'    or    " 'say"'"what"?" are
    valid quoted strings according to the standard, since  the end-quote marker
    is a quotation marker FOLLOWED BY WHITESPACE.

  - Strings that cannot be quoted on one line (e.g.   ''' "say" 'what' '''   )
    are converted to  multiline strings by appending a newline

  - Strings with internal linebreaks but no terminal linebreak
    are converted by appending a linebreak

  - Strings that cannot be quoted as multiline strings because they contain
    a line starting with ';' are converted by prepending a space (' ') to each line

  - Values None, True, False, NaN, Infinity and -Infinity are converted to
    UNQUOTED strings '.', 'true', 'false', 'NaN', 'Infinity' and '-Infinity', respectively.

  - Normal (not unquoted) strings that evaluate to a float are written in quotes.
    Also the literal strings '.', 'true', 'false', 'NaN', 'Infinity' and '-Infinity'
    are always written in quotes.

    This makes it possible (but NOT mandatory) to distinguish the null,  boolean and float values
    from the equivalent strings

The toString functions in this module will work with loop rows implemented as
either tuples, lists, or OrderedDicts, and accept an optional tag prefix for
DataBlocks, SaveFrames, and Loops, to prepend to item and column names.

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                 " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================

import sys
import re
import math
from collections import OrderedDict
from .StarTokeniser import getTokenIterator

# Constants for converting values to string
# NB - these can be overridden by pre-converting all values to
# UnquotedValue containing proper quotation marks
_quoteStartStrings = [
  '_', '[', ']', '$', '"', "'", 'save_', 'loop_', 'stop_', 'data_', 'global_'
]
startComment = '#'
_quoteStrings = ['true', 'false', 'NaN', 'Infinity', '-Infinity']
_containsWhiteSpace = re.compile('\s').search
_containsSingleEndQuote =  re.compile("'\s").search
_containsDoubleEndQuote =  re.compile('"\s').search
# _floatingPointFormat = '%.3g'
_floatingPointFormat = '%.10g'
_defaultIndent = ' '  * 3
_defaultSeparator = ' '  * 2

# Options corresponding to the supported parser modes: 'standard', 'lenient', 'strict', and 'IUCr'
_parserModeOptions = {
  'lenient': {
    'enforceSaveFrameStop':False,
    'enforceLoopStop':False,
    'padIncompleteLoops':True,
    'allowSquareBracketStrings':True
  },
  'strict': {
    'enforceSaveFrameStop':True,
    'enforceLoopStop':True,
    'padIncompleteLoops':False,
    'allowSquareBracketStrings':False
  },
  'standard': {
    'enforceSaveFrameStop':True,
    'enforceLoopStop':False,
    'padIncompleteLoops':False,
    'allowSquareBracketStrings':True
  },
  'IUCr':{
    'enforceSaveFrameStop':True,
    'enforceLoopStop':False,
    'padIncompleteLoops':False,
    'allowSquareBracketStrings':False},
}


def parse(text, mode='standard'):
  """Parse STAR text string 'text'.
  Standard settings allow skipping 'stop_' tags and strings starting with '[' or ']',
  but require 'save_' termination of SaveFrames and throw an error if the number of loop
  values do not match the number of columns.

  'strict' and 'lenient' modes are available; mode='IUCr' follows the IUCr standard, which
  is like standard except that strings starting with '[' and ']' are not allowed

  See GeneralStarParser class for details and control of individual settings
  """

  try:
    options = _parserModeOptions[mode]
  except KeyError:
    raise ValueError(
      "illegal parser mode : %s  Only modes 'lenient', 'strict', 'standard', 'IUCr' allowed"
      %  repr(mode)
    )

  #
  return GeneralStarParser(text, **options).parse()


def parseFile(fileName:str, mode:str='standard'):
  """load generic STAR file"""

  text = open(fileName).read()
  return parse(text, mode=mode)

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


class StarSyntaxError(ValueError):
  pass

class NamedOrderedDict(OrderedDict):

  def __init__(self, name=None):
    super(NamedOrderedDict, self).__init__()
    self.name = name

  def __str__(self):
    return '%s(name=%s)' % (self.__class__.__name__, self.name)

  def __repr__(self):
    return '%s(%s, name=%s)' % (self.__class__.__name__, list(tt for tt in self.items()), self.name)

  def addItem(self, tag:str, value):
    if tag in self:
      raise ValueError("%s: duplicate key name %s" % (self, tag))
    else:
      self[tag] = value

class StarContainer(NamedOrderedDict):
  """DataBlock or SaveFrame containing items and loops"""

  def multiColumnValues(self, columns) -> list:
    """get tuple of orderedDict of values for columns.
    Will work whether columns are in a loop or single values
    If columns match a single loop or nothing, return the loop data.
    Otherwise return a tuple with a single OrderedDict.
    If no column matches return None
    If columns match more than one loop throw an error"""
    valueDict = OrderedDict((x, self.get(x)) for x in columns)
    testSet = set(x for x in valueDict.values() if x is not None)
    if not testSet:
      # None of the column names match
      return None
    elif any(isinstance(x,Loop) for x in testSet):
      if len(testSet) == 1:
        # All columns match a single loop (or nothing) return the loop data
        return tuple(testSet.pop().data)
      else:
        raise ValueError("%s columns %s must match either multiple items or a single loop"
        % (self, columns))
    else:
      # No column matches a loop. return a single dict
      return (valueDict,)

  def  _contentToString(self, indent:str=_defaultIndent, separator:str=_defaultSeparator) -> str:
    """Returns content of either DataBlock or SaveFrame"""

    lines = []

    # Set item formatting
    # tagwidth = max(len(tt[0]) for tt in self.items()
    #                if isinstance(tt[1], str) and '\n' not in tt[1])
    tagwidth = max((len(tt[0]) for tt in self.items() if isinstance(tt[1], str) ), default=1)
    tagPrefix = self.tagPrefix
    if tagPrefix:
      # tagwidth += len(tagPrefix)
      itemFormat = '%s%s%%-%ss%s%%s\n' % (indent, tagPrefix, tagwidth, separator)
    else:
      itemFormat = '%s%%-%ss%s%%s\n' % (indent, tagwidth, separator)

    # convert contents
    for tag, obj in self.items():

      if isinstance(obj, SaveFrame):
        lines.append(obj.toString(indent=indent+_defaultIndent, separator=separator))

      elif isinstance(obj, Loop):
        if tag == obj.name:
          # NB Loops can be contained in self once for each column.
          # This if statement ensures we only get them once
          lines.append(obj.toString(indent=indent, separator=separator))

      else:
        lines.append(itemFormat % (tag, valueToString(obj)))
    #
    return ''.join(lines)

class DataExtent(NamedOrderedDict):
  """Top level container for general STAR object tree"""
  def __init__(self, name='Root'):
    super(DataExtent, self).__init__(name=name)

  def toString(self, indent:str='', separator:str=_defaultSeparator) -> str:
    blockSeparator = '\n\n\n\n'
    return blockSeparator.join(x.toString(indent=indent, separator=separator) for x in self.values())

# We insert these afterwards as we want the functions at the top of the file
# but can only annotate after DataExtent is created
parse.__annotations__['return'] = DataExtent
parseFile.__annotations__['return'] = DataExtent

class DataBlock(StarContainer):
  """DataBlock for general STAR object tree"""

  # Tag prefix for string output, which is prefixed to item names before writing.
  # Can be set in subclass instances
  tagPrefix = None


  def toString(self, indent:str='', separator:str=_defaultSeparator) -> str:

    name = self.name
    if not name.startswith('data_'):
      name = 'data_' + name
    return ('%s\n\n%s\n# End of %s\n'
            % (name, self._contentToString(indent=indent,
                                           separator=separator), name))

class SaveFrame(StarContainer):
  """SaveFrame for general STAR object tree"""

  # Tag prefix for string output, which is prefixed to item names before writing.
  # Can be set in subclass instances
  tagPrefix = None


  def toString(self, indent:str=_defaultIndent, separator:str=_defaultSeparator) -> str:


    name = self.name
    if not name.startswith('save_'):
      name = 'save_' + name
    return ('\n%s%s\n\n%s%ssave_\n\n'
            % (indent, name, self._contentToString(indent=indent+_defaultIndent,
                                                   separator=separator), indent))

class LoopRow(OrderedDict):
  """Loop row - OrderedDict with additional functionality"""

  def _get(self, name:str):
    """Returns value of attribute 'name', or None if attribute is not defined

    Will treat a series of attributes 'foo_1', 'foo_2', 'foo_3', etc. as a single
    tuple attribute 'foo' """

    if  not name in self and (name + '_1') in self:
      tags = extractMatchingNameSequence(name, list(self.keys()))
      if tags:
        return tuple(self.get(x) for x in tags)
    #
    return self.get(name)

  def _set(self, name:str, value:object):
    """Sets attribute 'name' to value

    Will treat a series of attributes 'foo_1', 'foo_2', 'foo_3', etc. as a single
    tuple attribute 'foo' """

    if name in self:
      self[name] = value
      return

    elif (name + '_1') in self:
      tags = extractMatchingNameSequence(name, list(self.keys()))
      if tags and len(tags) == len(value):
        for ii, val in enumerate(value):
          self[tags[ii]] = val
        return
      else:
        raise ValueError("tag %s, values %s do not match columns: %s" % (name, value, tags))
    else:
      #
      raise KeyError("%s has no attribute(s) matching %s" % (self.__class__.__name__, name))

class Loop:
  """Loop for general STAR object tree
  Attributes are:

  - name: string

  - columns:  List of string column headers

  - data: List-of-rows, where rows are OrderedDicts """

  # Tag prefix for string output, which is prefixed to column names before writing.
  # Can be set in subclass instances.
  tagPrefix = None

  def __init__(self, name:str=None, columns:list=None):

    self.name = name
    self.data = []

    if columns:
      # print ('@~~@~', type(columns), list(columns), list(columns) == list(x for x in columns))
      self._columns = list(columns)
    else:
      self._columns = []

  def __str__(self):
    return '<%s:%s>' % (self.__class__.__name__, self.name)

  @property
  def columns(self) -> list:
    """Column names"""
    return tuple(self._columns)

  def newRow(self, values=None) -> LoopRow:
    """Add new row, initialised from values"""

    if values is None:
      row = LoopRow((x,None) for x in self.columns)

    elif isinstance(values, dict):
      ll = tuple(x for x in values if x not in self.columns)
      if ll:
        raise ValueError("Illegal fields in row input: %s" % ll)
      else:
        row = LoopRow((x,values.get(x)) for x in self.columns)

    else:
      if len(values) > len(self.columns):
        raise ValueError("Row passed %s values for %s columns" % (len(values), len(self.columns)))
      row = LoopRow(zip(self.columns,values))
    #
    self.data.append(row)
    return row

  def _addValue(self, value:str):
    """Put value in first slot in current row where previous value is None
    Add new row if necessary"""
    data = self.data

    if data and None in data[-1].values():
      row = data[-1]
      index = list(row.values()).index(None)
    else:
      row = self.newRow()
      index = 0
    #
    row[self.columns[index]] = value

  def addColumn(self, value:str, extendData=False):
    columns = self._columns
    if value in columns:
      raise ValueError("%s: duplicate column name: %s" % (self, value))
    elif self.data:
      if extendData:
        columns.append(value)
        for row in self.data:
          row[value] = None
      else:
        raise ValueError("%s: Cannot add columns when loop contains data" % self)
    else:
      columns.append(value)

  def removeColumn(self, value:str, removeData=False):
    columns = self._columns
    if value not in columns:
      raise ValueError("%s: column named %s does not exist" % (self, value))
    elif self.data:
      if removeData:
        for row in self.data:
          del row[value]
        columns.remove(value)
      else:
        raise ValueError("%s: Cannot remove columns when loop contains data" % self)
    else:
      columns.remove(value)

  def toString(self, indent:str=_defaultIndent, separator:str=_defaultSeparator) -> str:
    """Stringifier function for loop.

    Accepts (subtypes of) Loop with data as sequence of rows,
    where rows can be tuples, lists, or OrderedDicts.
    In all cases the values must be in the order given by the columns attribute"""

    # main body format
    lineFormat = indent + _defaultIndent + '%s\n'

    # Start tag
    lines = ['\n' + indent + 'loop_\n']

    # Write column headers
    if self.tagPrefix:
      for col in self.columns:
        lines.append(lineFormat % (self.tagPrefix + col))
    else:
      for col in self.columns:
        lines.append(lineFormat % col)
    lines.append('\n')

    # write data
    data = self.data
    if data:

      # First convert to strings to get correct columns widths
      if isinstance((data[0]), OrderedDict):
        data = [[valueToString(y) for y in list(x.values())] for x in self.data]
      else:
        # Must be a sequence of some kind. This will break for non-ordered dicts
        data = [[valueToString(y) for y in x] for x in self.data]

      columnWidths = [max(len(x) for x in col) for col in zip(*data)]
      for row in data:
        lines.append(lineFormat %
          separator.join('%-*s' % (wdth, row[ii]) for ii,wdth in enumerate(columnWidths))
        )

    # Add stop_
    lines.append( indent + 'stop_\n')

    return ''.join(lines)


def valueToString(value, quoteNumberStrings=False):
  """ Convert value to properly quoted STAR string

  if quoteNumberStrings, strings that evaluate to a float (e.g. '1', '2.7e5', ...)
  are put in quotes"""

  if value is None:
    return NULLSTRING

  elif value is True:
    return TRUESTRING

  elif value is False:
    return FALSESTRING

  elif isinstance(value, UnquotedValue):
    return value

  elif isinstance(value, float):

    if math.isnan(value):
      return NANSTRING

    elif math.isinf(value):
      if value > 0:
        return PLUSINFINITYSTRING
      else:
        return MINUSINFINITYSTRING

    else:
      return _floatingPointFormat % value

  elif isinstance(value, int):
    return str(value)

  else:
    value = str(value)

    # if quoteNumberStrings is true: quote, depending on content
    #
    if quoteNumberStrings:
      try:
        junk = float(value)
      except ValueError:
        matchesNumber = False
      else:
        matchesNumber = True
    else:
      matchesNumber = False

    if '\n' not in value:

      if (_containsWhiteSpace(value) or matchesNumber or value in _quoteStrings or
            startComment in value or any(value.startswith(x) for x in _quoteStartStrings)):
        if not "'" in value:
          value = "'%s'" % value
        elif not '"' in value:
          value = '"%s"' % value
        elif not _containsSingleEndQuote(value):
          # E.g. string like """ "say" 'what'?"""
          value = "'%s'" % value
        elif not _containsDoubleEndQuote(value):
          # E.g. string like """ 'say' "what"?"""
          value = '"%s"' % value
        else:
          # Cannot be quoted on one line (e.g. """ 'say' "what" """)
          # CHANGE VALUE to make it writable as multiline quote
          value += '\n'

    if '\n' in value:
      # Multiline quote. Done at the end to allow for modified values
      if ';' in value:
        # Fix strings with ';' starting line
        lines = value.splitlines()
        if any (x and x[0] == ';' for x in lines):
          # NB CHANGES VALUE
          value =  '\n'.join(' ' + x for x in lines)
      if value[-1] == '\n':
        value = '\n;%s; '  % value
      else:
        value = '\n;%s\n; '  % value
    #
    return value



class GeneralStarParser:
  """ Parser for text corresponding to a STAR file with one or more data blocks,
  producing a nested object structure matching the file (see module documentation for details:

  ::

    DataExtent
      DataBlock
        Loop
        Item
      SaveFrame
        Loop
        Item

  Parameters (default values correspond to the International Tables for Crystallography standard):

  - *text* Text to parse

  - *enforceSaveFrameStop* : True. Raise an error for missing 'save_' terminators - Yes/No

  - *enforceLoopStop* : False. Raise an error for missing 'stop_' terminators - Yes/No

  - *padIncompleteLoops* : False.  Pad final loop row with '.' for missing values - Yes/No

  - *allowSquareBracketStrings* : False.  Allow values starting '[' or ']' - Yes/No

  - *lowerCaseTags* : True. Convert all data and object names to lower case

  """

  def __init__(self, text:str, enforceSaveFrameStop:bool=True, enforceLoopStop:bool=False,
               padIncompleteLoops:bool=False, allowSquareBracketStrings=False, lowerCaseTags=True):

    self.enforceSaveFrameStop = enforceSaveFrameStop
    self.enforceLoopStop = enforceLoopStop
    self.padIncompleteLoops = padIncompleteLoops
    self.allowSquareBracketStrings = allowSquareBracketStrings
    self.lowerCaseTags = lowerCaseTags

    self.tokeniser = getTokenIterator(text)
    self.text = text

    self.stack = []
    self.globalsCounter = 0

  def _addDataBlock(self, name):
    container = self.stack[-1]
    obj = DataBlock(name)
    container.addItem(name, obj)
    self.stack.append(obj)

  def _addSaveFrame(self, name):
    container = self.stack[-1]
    obj = SaveFrame(name)
    container.addItem(name, obj)
    self.stack.append(obj)

  def _closeLoop(self, value):
    loop = self.stack[-1]
    if not isinstance(loop, Loop):
      raise StarSyntaxError(self._errorMessage("Loop stop_ %s outside loop" % value, value))

    columns = loop.columns
    data = loop.data
    if not columns:
      raise StarSyntaxError(self._errorMessage(" loop lacks column names" , value))

    if data:
      row = data[-1]
      if None in row.values():
        missingValueCount = len([x for x in row.values() if x is None])
        if self.padIncompleteLoops:
          print("WARNING Token %s: %s in %s is missing %s values. Last row was: %s"
                % (self.counter, loop, self.stack[-2], missingValueCount, data[-1]))
          # for row in data:
          #   print( ' - ', *row)
          for key,val in row.items():
            if val is None:
              row[key] = NULLSTRING
        else:
          raise StarSyntaxError(
            self._errorMessage("loop %s is missing %s values" % (loop, missingValueCount), value)
          )

    else:
      # empty loops appear here. We allow them, but that could change
      pass

    self.stack.pop()

  def _addLoopField(self, value):

    stack = self.stack
    loop = stack[-1]
    if loop.data:
      if self.enforceLoopStop:
        raise StarSyntaxError(
          self._errorMessage("Illegal token %s in unclosed loop" % value, value)
        )
      else:
        # Dataname among loop values. Interpreted as loop stop followed by new item start
        self._closeLoop(value)
        stack.append(value)
    else:
      if not loop.columns:
        # name loop after first column
        loop.name = value
      loop.addColumn(value)
      stack[-2].addItem(value, loop)

  def _processComment(self, value:str):
    # Comments are ignored
   return

  def _processGlobal(self, value:str):
    if self.globalsCounter:
      name = "global_%s" % self.globalsCounter
      self.globalsCounter += 1
    else:
      # NB globalsCounter is incremented in _processDataBlock for the first increment
      name = "global_"
    self._processDataBlock(name)

  def _processDataBlock(self, value:str):

    stack = self.stack

    if not self.globalsCounter:
      # to ensure the name global_ is only used if a global is the first dataBlock
      self.globalsCounter = 1

    # Terminate open elements
    if isinstance(stack[-1], Loop):
      if self.enforceLoopStop:
        raise StarSyntaxError(
          self._errorMessage("Loop terminated by %s instead of stop_" % value, value)
        )
      else:
        # Close loop and pop it off the stack
        self._closeLoop(value)

    if isinstance(stack[-1], SaveFrame):
      if self.enforceSaveFrameStop:
        raise StarSyntaxError(
          self._errorMessage("SaveFrame terminated by %s instead of save_" % value, value)
        )
      else:
        stack.pop()

    if isinstance(stack[-1], DataBlock):
      stack.pop()

    # Add new DataBlock
    if isinstance(stack[-1], DataExtent):
      if self.lowerCaseTags:
        value = value.lower()
      self._addDataBlock(value)
    else:
      raise StarSyntaxError(self._errorMessage("Parser error at token %s" % value, value))


  def _closeSaveFrame(self, value:str):

    stack =  self.stack

    lowerValue = value.lower()

    # Terminate loop
    if isinstance(stack[-1], Loop):
      if self.enforceLoopStop:
        raise StarSyntaxError(
          self._errorMessage("Loop terminated by %s instead of stop_" % value, value)
        )
      else:
        # Close loop and pop it off the stack
        self._closeLoop(value)

    # terminate saveframe
    if isinstance(stack[-1], SaveFrame):
      if lowerValue == 'save_':
        # Simple terminator. Close save frame
          stack.pop()#

      elif self.enforceSaveFrameStop:
        self._errorMessage("SaveFrame terminated by %s instead of save_" % value, value)

      else:
        # New saveframe start. We are missing the terminator, but close and continue anyway
        stack.pop()

    if not isinstance((stack[-1]), DataBlock):
      if lowerValue == 'save_':
        raise StarSyntaxError(self._errorMessage("'%s' found out of context" % value, value))

  def _openSaveFrame(self, value:str):

    stack = self.stack

    # Add new SaveFrame
    if self.lowerCaseTags:
      value = value.lower()
    if isinstance(stack[-1], DataBlock):
      self._addSaveFrame(value)
    else:
      raise StarSyntaxError(
        self._errorMessage("saveframe start out of context: %s" % value, value)
      )

  def _openLoop(self, value:str):

    stack = self.stack

    # Terminate open elements
    if isinstance(stack[-1], Loop):
      if not stack[-1].data:
        # NB, nested loops are not supported
        raise StarSyntaxError(
          self._errorMessage("Loop terminated by %s instead of stop_" % value, value)
        )
      elif self.enforceLoopStop:
        raise StarSyntaxError(
          self._errorMessage("Loop terminated by %s instead of stop_"%  value, value)
        )
      else:
        # Close loop and pop it off the stack
        self._closeLoop(value)

    if isinstance(stack[-1], (SaveFrame, DataBlock)):
      # NB Loop naming and adding to container is done when first column name is read
      stack.append(Loop(name='loop_'))

    else:
      raise StarSyntaxError(self._errorMessage("loop_ out of context", value))

  def _processBadToken(self, value, typ):
    raise StarSyntaxError(self._errorMessage("Illegal token of type% s:  %s" % (typ, value), value))

  def processDataName(self, value):

    stack = self.stack

    useValue = value.lower() if self.lowerCaseTags else value
    if isinstance(stack[-1], (SaveFrame, DataBlock)):
      stack.append(useValue)
    elif isinstance(stack[-1], Loop):
      self._addLoopField(useValue)
    else:
      raise StarSyntaxError(self._errorMessage(
        "Found item name %s: Must be in DataBlock, SaveFrame, or Loop header)"% value, value)
      )


  def processValue(self, value):
    stack = self.stack
    last = stack[-1]
    if isinstance(last, str):
      # Value half of tag, value pair
      stack.pop()
      stack[-1].addItem(last, value)
    elif isinstance(last, Loop):
      last._addValue(value)
    else:
      raise StarSyntaxError(self._errorMessage("Data value %s must be in item or loop_" % value,
                                               value))

  def parse(self):

    stack = self.stack

    result = DataExtent()
    stack.append(result)

    self.counter = 0   # Token counter
    try:
      for tk in self.tokeniser:
        typ = tk.type
        value = tk.value
        self.counter += 1

        if typ == 'COMMENT':
          self._processComment(value)
        elif typ == 'GLOBAL':
          self._processGlobal(value)
        elif typ == 'DATA_BLOCK':
          self._processDataBlock(value)
        elif typ == 'SAVE_FRAME':
          # save_ string
          self._closeSaveFrame(value)
          if value.lower() != 'save_':
            self._openSaveFrame(value)
        elif typ == 'LOOP':
          self._openLoop(value)
        elif typ == 'LOOP_STOP':
            self._closeLoop(value)
        elif typ in ('BAD_CONSTRUCT', 'BAD_TOKEN'):
          self._processBadToken(value, typ)
        elif typ == 'SQUARE_BRACKET':
          if self.allowSquareBracketStrings:
            self.processValue(UnquotedValue(value))
          else:
            self._processBadToken(value, typ)
        elif typ == 'DATA_NAME':
          self.processDataName(value)
        else:
          if typ in ('NULL', 'UNKNOWN', 'SAVE_FRAME_REF', 'STRING'):
            # Set to 'UnquotedValue string subtype
            value = UnquotedValue(value)
          else:
            pass
            assert (typ in ('SQUOTE_STRING', 'DQUOTE_STRING', 'MULTILINE')), "Unknown type string: %s" % typ
          self.processValue(value)

      # End of data - clean up stack
      if isinstance(stack[-1], str):
        raise StarSyntaxError(self._errorMessage("File ends with item name", value))

      if isinstance(stack[-1], Loop):
        self._closeLoop('<End-of-File>')

      if isinstance(stack[-1], SaveFrame):
        stack.pop()

      if isinstance(stack[-1], DataBlock):
        stack.pop()

      if isinstance(stack[-1], DataExtent):
        stack.pop()

      if stack:
        raise RuntimeError(self._errorMessage("stack not empty at end of file", value))
    except:
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


def extractMatchingNameSequence(name:str, matchNames:list) -> list:
  """Get list of matchNames matching 'name_1', 'name_2', ..., in order."""

  ll =[]
  for tag in matchNames:
    tt = tag.rsplit('_',1)
    if name == tt[0] and tt[-1].isdigit():
      ll.append((int(tt[1]), tag))
  ll.sort()

  if [tt[0] for tt in ll] == list(range(1, len(ll)+1)):
    return [tt[1] for tt in ll]
  else:
    return None


if __name__ == "__main__":

    print(sys.argv)
    cif = sys.argv[1]
    result = parse(cif.read())