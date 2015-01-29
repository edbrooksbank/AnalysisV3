"""
Version 2/3 Pid routines
"""
try:
  from cing import __version__
except ImportError:
  __version__ = '???'

# set separators
PREFIXSEP = ':'
IDSEP = '.'

# Set translation between IDSEP and alternative character
altCharacter = '^'
remapSeparators = str.maketrans(IDSEP,altCharacter)
unmapSeparators = str.maketrans(altCharacter, IDSEP)

def makePid(head, *args):
  """make pid from head and list of successive keys.
  Head may be an existing pid, or a naked string
  Keys are converted to string, and illegal characters are converted to altCharacter
  The head is  not checked - it should be either a valid pid or a class code"""

  # map args to corrected strings
  ll = [val.translate(remapSeparators) for val in args]

  if head[-1] == PREFIXSEP:
      sep = ''
  elif PREFIXSEP in head:
      sep = IDSEP
  else:
      sep = PREFIXSEP
  #
  return sep.join((head, IDSEP.join(*ll)))

def makeId(*args):
  """make id from list of successive keys.
  Keys are converted to string, and illegal characters are converted to altCharacter"""

  # map args to corrected strings
  return IDSEP.join(val.translate(remapSeparators) for val in args)

def splitId(idString):
  """Split idString into tuple of component elements,
  mapping altCharacter back to separator
  Keys are converted to string, and illegal characters are converted to altCharacter"""

  # map args to corrected strings
  return tuple(val.translate(unmapSeparators) for val in idString.split(IDSEP))


def decodePid(sourceObject, thePid):
    """
    try to decode thePid relative to sourceObject
    return decoded pid object or None on not found or Error
    """

    # REFACTOR. This DOES decode PID parts. TBD NBNB

    import cing.Libs.io as io

    if thePid is None:
        return None

    # assure a Pid object
    if not isinstance(thePid, Pid):
        strPid = str(thePid)

        # Modified by Rasmus to match new isValid behaviour)
        # thePid = Pid(str(thePid))
        # NB Assumes that asPid wi;ll raise VALUEeRROR (as Pid does) if something goes wrong
        try:
            if hasattr(thePid, 'asPid'):
                # we probably did get passed an object
                thePid = thePid.asPid

            else:
                # just try it as a string
                thePid = Pid(strPid)
        except ValueError:
            io.error('decodePid: pid "{0}" is invalid', thePid)


        #end if
    #end if

    if not thePid.isValid:
        io.error('decodePid: pid "{0}" is invalid', thePid)
        return None
    #end if

    # check if thePid describes the source object
    if hasattr(sourceObject,'asPid'):
        if sourceObject.asPid == thePid:
            return sourceObject
    #end if
    # apparently not, let try to traverse down to find the elements of thePid
    obj = sourceObject
    for p in thePid:
        #print( 'decodePid>>', p, object)
        if p not in obj:
            return None
        obj = obj[p]
    #end for
    # found an object, check if it is the right kind
    if thePid.type != obj.__class__.__name__:
        io.error('decodePid: type "{0}" does not match object type "{1}"',
                 thePid.type, obj.__class__.__name__)
        return None
    return obj
#end def


class Pid(str):
    """Pid routines, adapted from path idea in: Python Cookbook, A. Martelli and D. Ascher (eds), O'Reilly 2002, pgs 140-142
    Features:
    - newpid = pid1 + id1 
    - slicing to address elements of pid
    - loop over elements of pid
    - modify an element
    - copy a pid
    - incrementation and decrementation
    - check validity
    - return as string (convenience)
    
    pid = Pid.new('Residue','mol1','A', 502) # elements need not be strings; but will be converted
    -> Residue:mol1.A.502   (Pid instance)

    which is equivalent to:

    pid = Pid('Residue:mol1.A.502')
    -> Residue:mol1.A.502   (Pid instance)

    Behaves as a string:
    pid == 'Residue:mol1.A.502'
    -> True

    pid.str
    -> 'Residue:mol1.A.502' (str instance)

    pid.type
    -> 'Residue' (str instance)

    pid.id
    -> 'mol1.A.502' (str instance)

    len(pid)
    -> 3

    pid[0]
    -> 'mol1' (str instance)

    pid[0:2]
    -> 'mol1.A' (str instance)
    
    for id in pid:
        print id
    ->
    'mol1' (str instance)
    'A'  (str instance)
    '502'  (str instance)
    
    pid2 = pid.modify(1, 'B', type='Atom') + 'N'
    -> Atom:mol1.B.502.N  (Pid instance)
    
    but also:
    pid3 = Pid('Residue') + 'mol2'
    -> Residue:mol2  (Pid instance)
    
    pid4 = pid.decrement(2,1)
    -> Residue:mol1.A.501  (Pid instance)
    or
    pid4 = pid.increment(2,-1)
    NB fails on elements that cannot be converted to int's
    
    pid5 = pid.copy()   # equivalent to pid5 = Pid(pid.str)
    -> Residue:mol1.A.502  (Pid instance)
    
    pid==pid5
    -> True
    
    '502' in pid
    -> True

    502 in pid
    -> False    # all pid elements are strings
    """
    
    # name mapping dictionary
    nameMap = dict(
        MO = 'Molecule'
    )

    def __init__(self, string, *args):
        """First argument ('string' must be a valid pid string with at least one, non-initial PREFIXSEP
        Additional arguments are converted to string with disallowed characters changed to altCharacter"""
        str.__init__(string)

        # inlining this here is 1) faster, 2) guarantees that we never get invalid Pids.
        # We can then assume validity for the rest of the functions
        if PREFIXSEP not in self or self[0] == PREFIXSEP:
            raise ValueError("String %s is not a valid Pid" % str.__repr__(self))

        self._version = 'cing:%s' % __version__

    @property
    def type(self):
        """
        return type part of pid
        """
        # parts = self._split()
        # if len(parts) > 0:
        #     return parts[0]
        # else:
        #     return ''

        return self.split(PREFIXSEP,1)[0]
    
    @property
    def id(self):
        """
        return id part of pid
        """
        # parts = self._split()
        # if len(parts) > 1:
        #     return IDSEP.join(parts[1:])
        # else:
        #     return ''

        return self.split(PREFIXSEP,1)[1]

    #end def

    @staticmethod
    def isValid(text):
        # tests here
        # if self.find(PREFIXSEP) < 0:
        #     return False
        # parts = self._split()
        # if len(parts) < 2:
        #     return False

        # Comment 1:    Do we allow multiline strings here?

        # Comment 2: When we check for validity in __init__, it will be impossible to create
        # invalid PIds. A static function allows yo to check for validity before creating.
        # Even so, is it necessary? It is no longer used above

         return PREFIXSEP in text and text[0] != PREFIXSEP

    @property
    def str(self):
        """
        Convenience: return as string rather than object;
        allows to do things as obj.asPid.str rather then str(obj.asPid)
        """
        return str(self)

    def __add__(self, other):
        tmp = self._split() + [other]
        #print 'Pid.__add__', tmp
        return Pid.new(*tmp)
    #end def
    
    def __len__(self):
        ll = len(self._split())-1
        if ll < 0:
            ll=0
        return ll
    #end def
    
    def __getslice__(self, start, stop):
        # NB using parts [1:] instead of modifying indices allows negative indices to work normally
        parts = self._split()[1:][start:stop]
        # if len(parts) > 0:
        #     return IDSEP.join(*parts)
        # else:
        #     return ''

        return IDSEP.join(parts)
    #end def
    
    def __getitem__(self, i):
        return self._split()[i+1]
    #end def
    
    def __iter__(self):
        for f in self._split()[1:]:
            yield f
        #end for
    #end def
    
    # Unecessary: __str__ is inherited
    # def __str__(self):
    #     return str.__str__(self)
    # #end def

    # I like that one. We could activate it. Rasmus
    # def __repr__(self):
    #     return 'Pid(%s)' % str.__repr__(self)
    # #end def

    def _split(self):
        """
        Return a splitted pid as list or empty list on error
        # """
        # allParts = []
        #
        # parts = self.split(PREFIXSEP)
        # if len(parts) > 0:
        #     allParts.append(parts[0])
        # if len(parts) > 1:
        #     for p in parts[1].split(IDSEP):
        #         allParts.append(p)
        # return allParts

        parts = self.split(PREFIXSEP, 1)
        result = [parts[0]]

        if parts[1]:
            result.extend(parts[1].split(IDSEP))

        return result

    #end def

    @staticmethod
    def new( *args ):
        """
        Return Pid object from arguments
        Apply str() on all arguments
        Have to use this as intermediate as str baseclass of Pid only accepts one argument
        """
        # use str operator on all arguments
        args = map(str, args)
        # could implement mapping here
        if (len(args) > 0) and (args[0] in Pid.nameMap):
            #args = list(args) # don't know why I have to use the list operator
            args[0] = Pid.nameMap[args[0]]
        #end if
        return Pid( Pid._join(*args) )
    #end def

    @staticmethod
    def _join(*args):
        """Join args using the rules for constructing a pid
        """
        # if len(args) >= 2:
        #     tmp =PREFIXSEP.join( args[0:2] )
        #     tmp2 = [tmp] + list(args[2:]) # don't know why args is tuple and thus I have to use
        #                                   # the list operator to avoid TypeError:
        #                                   # can only concatenate list (not "tuple") to list?
        #     return IDSEP.join(tmp2)
        # elif len(args) >= 1:
        #     return args[0]
        # else:
        #     return ''

        # NB the behaviour is len(args) == 1 is correct (return "type:")
        if args:
            return PREFIXSEP.join((args[0], IDSEP.join(args[1:])))
        else:
            return ''

    #end def

    def modify(self, index, newId, type=None):
        """
        Return new pid with position index modified by newId
        """
        # parts = self._split()
        # if index+1 >= len(parts):
        #     io.error('Pid.modify: invalid index ({0})\n', index+1)
        # parts[index+1] = newId
        # if type is not None:
        #     parts[0] = type
        # return Pid.new(*parts)


        parts = self._split()

        idparts = parts[1:]
        try:
            # NB this allows negative indices also, according to normal Python rules
            idparts[index] = newId
        except IndexError:
            import cing.Libs.io as io
            io.error('Pid.modify: invalid index ({0})\n', index+1)
        parts[1:] = idparts

        if type is not None:
            parts[0] = type

        return Pid.new(*parts)


    #end def

    def increment(self, index, value):
        """Return new pid with position index incremented by value
        Assumes integer valued id at position index
        """

        # NBNB do you want to set value=1 as parameter, so self.increment(index) increments by 1?

        parts = self._split()
        parts[index+1] = int(parts[index+1]) + value
        return Pid.new(*parts)
    #end def

    def decrement(self, index, value):
        """Return new pid with position index decremented by value
        Assumes integer valued id at position index
        """

        # NBNB do you want to set value=11 as parameter, so self.decrement(index) decrements by 1?

        return self.increment(index, -value)
    #end def
    
    def copy(self):
        """Return copy of pid
        """
        # Use Pid.new to pass it by any 'translater/checking routine'
        parts = self._split()
        return Pid.new(*parts)
    #end def
#end class
#--------------------------------------------------------------------------------------------------------------

