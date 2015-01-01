"""NEF (Nmr Exchange Format) exporter code
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date$"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon Skinner, Geerten Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
               "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                 " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
__version__ = "$Revision$"

#=========================================================================================
# Start of code
#=========================================================================================

import os
import sys
import operator
import datetime
import itertools

from ccpn.lib.nef import Util as nefUtil
from ccpncore.lib.Bmrb import bmrb


nefExtension = 'nef'

# potential tags to use depending on potential type - underscore version
# NBNB TBD move to more appropriate location?
# NB target+value and target_value_error are not included as they are used each time
nefTagsByPotentialType = {
  'log-normal' : (),
  'parabolic' : (),
  'square-well-parabolic' : ( 'lower_limit', 'upper_limit'),
  'upper-bound-parabolic' : ('upper_limit',),
  'lower-bound-parabolic' : ('lower_limit',),
  'square-well-parabolic-linear' : ('lower_linear_limit', 'lower_limit','upper_limit',
                                    'upper_linear_limit'),
  'upper_bound-parabolic-linear' : ('upper_limit','upper_linear_limit'),
  'lower_bound-parabolic-linear' : ('lower_linear_limit', 'lower_limit'),
  'unknown' : ('lower_linear_limit', 'lower_limit','upper_limit', 'upper_linear_limit'),
}
ccpnTagsByPotentialType = {
  'log-normal' : (),
  'parabolic'  :(),
  'square-well-parabolic' : ('lowerLimit', 'upperLimit'),
  'upper-bound-parabolic' : ('upperLimit',),
  'lower-bound-parabolic' : ('lowerLimit',),
  'square-well-parabolic-linear' : ('additionalLowerLimit', 'lowerLimit','upperLimit',
                                  'additionalUpperLimit'),
  'upper_bound-parabolic-linear' : ('upperLimit','additionalUpperLimit'),
  'lower_bound-parabolic-linear' : ('additionalLowerLimit', 'lowerLimit'),
  'unknown' : ('additionalLowerLimit', 'lowerLimit','upperLimit','additionalUpperLimit'),
}


# NBNB TBD we might want an exportNmrCalc2Nef wrapper as well

# def exportConstraintStore2Nef(nmrConstraintStore, dataName=None, directory=None):
#   """Export NmrConstraintStore and associated data to NEF"""
#
#   # nmrProject
#   nmrProject = nmrConstraintStore.nmrProject
#
#   # MolSystem
#   aSet = set(y.topObject for x in nmrConstraintStore.fixedAtomSets for y in x.atoms )
#   if len(aSet) == 1:
#     molSystem = aSet.pop()
#   else:
#     raise ValueError("NmrConstraintStore must link to exactly 1 MolSystem - %s found"
#     % len(aSet))
#
#   # PeakLists
#   peakLists = set(z.peakList for x in nmrConstraintStore.constraintLists
#                   for y in x.constraints
#                   for z in y.peaks)
#   peakLists = list(peakLists)
#
#   # NBNB TBD temporary hack to get right result for CASD entries:
#   if not peakLists:
#     peakLists = [z for x in nmrProject.sortedExperiments() for y in x.sortedDataSources()
#                  for z in y.sortedPeakLists()]
#
#   if not dataName:
#     dataName = '%s-%s-%s' % (nmrProject.root.name, nmrProject.name, nmrConstraintStore.serial)
#   else:
#     ll = dataName.rsplit('.',1)
#     if len(ll) == 2 and ll[1] == nefExtension:
#       dataName = ll[0]
#
#   entry = makeStarEntry(nmrProject, molSystem, dataName, peakLists,
#                         nmrConstraintStore.sortedConstraintLists())
#
#   # Export object tree
#   if not directory:
#     # set directory
#     directory = os.getcwd()
#   if not os.path.exists(directory):
#     os.makedirs(directory)
#
#   # write file
#   filePath = os.path.join(directory, dataName)
#   filePath = '.'.join((filePath, nefExtension))
#   open(filePath, 'w').write(entry.exportString())


def makeStarEntry(project, dataName, chains=(), peakLists=(), restraintLists=(),
                  shiftList=None,):
  """Make Bmrb Sans entry for export.
   shift lists are taken from peaklists, otherwise from shiftList parameter"""

  # Set up parameters and sanity check

  # Peak list check
  for peakList in peakLists:
    if peakList._project is not project:
      raise ValueError("PeakList %s does not match Project %s"
                       % (peakList, project))

  # Chain check
  if len(chains) != len(set(chains)):
    raise ValueError("Chains parameter contains duplicates: %s" % chains)
  for chain in chains:
    if chain._project is not project:
      raise ValueError("Chain %s does not match Project %s"
                       % (chain, project))

  # restraint list check
  aSet = set(x.restraintSet for x in restraintLists)
  if len(aSet) == 1:
    rs = aSet.pop()
    if rs._project is not project:
      raise ValueError("Restraint lists do not match Project")
  else:
    raise ValueError("Restraint lists are not from a single RestraintSet")

  # Shift list check
  aSet = set(x.chemicalShiftList for x in peakLists)
  shiftLists = [x for x in sorted(project.chemicalShiftLists) if x in aSet]
  if shiftLists:
    if shiftList is not None:
      raise ValueError("Function takes peakLists or a shiftList, but not both")
  elif shiftList is None:
    raise ValueError("Function must have either peakLists or one shiftList")
  else:
    shiftLists = [shiftList]

  # Make assignment map
  assignmentMap = Nef.mapAllAssignments(nmrProject, molSystem=molSystem)
  for nmrConstraintStore in set(x.topObject for x in constraintLists):
    Nef.mapAllAssignments(nmrConstraintStore, assignmentMap=assignmentMap, molSystem=molSystem)


  # Make BMRB object tree

  # Make Entry
  entry = bmrb.entry.fromScratch(dataName)

  # MetaData saveframe
  entry.addSaveframe(makeMetaDataFrame())

  # Make ccpn-specific saveframe - NBNB dummy - for test only
  saveframe = bmrb.saveframe.fromScratch(saveframe_name='ccpn_specific_test_1',
                                         tag_prefix='ccpn_specific_test')
  entry.addSaveframe(saveframe)

  saveframe.addTags([
    ('sf_category','ccpn_specific_test'),
    ('sf_framecode','ccpn_specific_test_1'),
    ('ccpn_par_1','someEnum'),
    ('ccpn_par_2',42),
  ])

  # Make molecular system
  entry.addSaveframe(makeMolecularSystemFrame(chains))

  # Make shift lists
  for shiftList in shiftLists:
    entry.addSaveframe(makeShiftListFrame(shiftList))

  # Make restraint lists
  for restraintList in sorted(restraintLists):
    # NB sorting will sort by type then name
    entry.addSaveframe(makeRestraintListFrame(restraintList))

  # Make peak list and spectrum frames
  for peakList in peakLists:
    entry.addSaveframe(makePeakListFrame(peakList, assignmentMap, shiftList=shiftList))

  # Make Peak-restraint links frame
  entry.addSaveframe(makePeakRestraintLinksFrame(useConstraintLists, peakLists))

  return entry


def makeMetaDataFrame():
  """Make Metadata singleton saveframe.
  NBNB currently all values are dummy - later the function will need parameters"""

  # Make meta_data
  saveframe = bmrb.saveframe.fromScratch(saveframe_name='nef_nmr_meta_data',
                                         tag_prefix='nef_nmr_meta_data')

  saveframe.addTags([
    ('sf_category','nmr_meta_data'),
    ('sf_framecode','nmr_meta_data'),
    ('format_name','nmr_exchange_format'),
    ('format_version','0.7'),
    ('program_name','CCPN'),
    ('program_version','2.9.0'),
  ])
  saveframe.addTag('creation_date', datetime.datetime.today().isoformat())
  saveframe.addTag('coordinate_file_name', None)

  # related entries loop
  loop = bmrb.loop.fromScratch(category='nef_related_entries')
  saveframe.addLoop(loop)
  for tag in ('database_name', 'database_accession_code'):
    loop.addColumn(tag)
  loop.addData(['PDB', 'fake'])

  # Program script loop
  loop = bmrb.loop.fromScratch(category='nef_program_script')
  saveframe.addLoop(loop)
  for tag in ('program_name', 'script_name', 'script', 'ccpn_special_par'):
    loop.addColumn(tag)
  loop.addData(['CcpNmr Analysis', 'dummy', """ Try \nsomething, then say\n'Booh!'""", 42])

  # Program history loop
  loop = bmrb.loop.fromScratch(category='nef_run_history')
  saveframe.addLoop(loop)
  for tag in ('run_ordinal', 'program_name', 'program_version', 'script_name', 'script'):
    loop.addColumn(tag)
  loop.addData([1, 'CcpNmr Analysis','2.4.1', 'autoSetupRun', None])
  loop.addData([2, 'Cyana', '3.0', 'init.cya',
                "rmsdrange:=1-93\n\ncyanalib\n\nread seq protein.seq\n\n"])
  #
  return saveframe


def makeMolecularSystemFrame(chains):
  """ Make molecular system frame"""

  project = chains[0]._project

  # Header block
  category = 'nef_molecular_system'
  saveframe = bmrb.saveframe.fromScratch(saveframe_name=category,
                                         tag_prefix=category)
  saveframe.addTags([
    ('sf_category',category),
    ('sf_framecode',category),
  ])

  # sequence loop
  loop = bmrb.loop.fromScratch(category='nef_sequence')
  saveframe.addLoop(loop)
  for tag in ('chain_code', 'sequence_code', 'residue_type', 'residue_variant', 'linking',
              'cross_linking'):
    loop.addColumn(tag)

  for chain in set(chains):
    chainCode = chain.shortName
    for residue in chain.residues:
      sequenceCode = residue.sequenceCode
      residueType = residue.name
      # NBNB TBD add residue variants
      residueVariant=None
      linking = residue.linking

      # set crossLinking first, as we modify 'linking' later.
      crossLinking = None
      if linking in ('start', 'middle', 'end'):
        # linear polymer residues - crosslinks are done as part of the descriptor
        descriptor = residue.descriptor
        if 'link' in descriptor:
          if 'link:S' in descriptor:
            # NBNB This could in theory break, if you have e.g. a thioester or thioether link
            # NBNB TBD improve in V3
            crossLinking = 'disulfide'
          else:
            crossLinking = 'link'

      elif linking != 'none':
        # Not a linear polymer, and linking is not None - set to 'link'
        crossLinking = 'link'

      if linking == 'none':
        linking = 'single'
      elif linking not in ('start', 'end'):
        linking = None

      loop.addData([chainCode, sequenceCode, residueType, residueVariant, linking, crossLinking])

  # covalent cross-links loop

  atomPairs = []
  for chain in chains:
    molecule = chain.ccpnChain.molecule
    for molResLink in molecule.findAllMolResLinks(isStdLinear=False):
      atoms = []
      atomPairs.append(atoms)
      for molResLinkEnd in molResLink.molResLinkEnds:
        ccpnResidue = chain.findFirstResidue(seqId=molResLinkEnd.molResidue.serial)
        atomName = molResLinkEnd.linkEnd.boundChemAtom.name
        ccpnAtom = ccpnResidue.findFirstAtom(name=atomName)
        atoms.append(project._data2Obj[ccpnAtom])

  for molSystemLink in project.nmrProject.molSystem.molSystemLinks:
    atoms = []
    atomPairs.append(atoms)
    for molSystemLinkEnd in molSystemLink.molSystemLinkEnds:
      atomName = molSystemLinkEnd.linkEnd.boundChemAtom.name
      ccpnAtom = molSystemLinkEnd.residue.findFirstAtom(name=atomName)
      atoms.append(project._data2Obj[ccpnAtom])

  # NB Loop may be empty. The entry.export_string function takes care of this
  loop = bmrb.loop.fromScratch(category='nef_covalent_links')
  saveframe.addLoop(loop)
  # if atomPairs:
  # NBNB TBD if statement removed, pending query to Eldon whether STAR should
  # not itself refuse to print out empty loops
  for tag in ('chain_code_1', 'sequence_code_1', 'residue_type_1', 'atom_name_1',
              'chain_code_2', 'sequence_code_2', 'residue_type_2', 'atom_name_2',):
    loop.addColumn(tag)


  for ll in atomPairs:
    values = ll[0]._pid.split('.') +  ll[1]._pid.split('.')
    loop.addData(values)
  #
  return saveframe


def makeShiftListFrame(shiftList):
  """make a saveFrame for a shift list"""

  if shiftList.name is None:
    shiftList.name = 'ShiftList_%s' % shiftList.serial
  framecode = shiftList.name
  # NBNB TBD ensure names are unique
  saveframe = bmrb.saveframe.fromScratch(saveframe_name=framecode,
                                         tag_prefix='nef_chemical_shift_list')

  saveframe.addTags([
    ('sf_category','nef_chemical_shift_list'),
    ('sf_framecode',framecode),
  ])

  saveframe.addTag('atom_chemical_shift_units', 'ppm')

  # chemical shift loop
  loop = bmrb.loop.fromScratch(category='nef_chemical_shift')
  saveframe.addLoop(loop)
  for tag in ('chain_code', 'sequence_code', 'residue_type', 'atom_name',
              'value', 'value_uncertainty',):
    loop.addColumn(tag)

  for row in [(x.id.split('.') + [x.value, x.error]) for x in shiftList.chemicalShifts]:
    loop.addData(row)
  #
  return saveframe

def makeRestraintListFrame(restraintList):
  """make a saveFrame for a restraint list of whatever type"""
  restraintType = restraintList.__class__.__name__[:-13]
  potentialType = restraintList.potentialType

  if restraintList.name is None:
    restraintList.name = '%sRestraintList_%s' % (restraintType, restraintList.serial)
  framecode = restraintList.name
  frameCategory = 'nef_%s_restraint_list' % restraintType.lower()
  # NBNB TBD ensure names are unique
  saveframe = bmrb.saveframe.fromScratch(saveframe_name=framecode, tag_prefix=frameCategory)

  saveframe.addTags([
    ('sf_category',frameCategory),
    ('sf_framecode',framecode),
    ('potential_type',restraintList.potentialType)
  ])

  # restraint loop
  loop = bmrb.loop.fromScratch(category=frameCategory[:-5])
  saveframe.addLoop(loop)
  # ID tags:
  for tag in ('restraint_id', 'restraint_combination_id',):
    loop.addColumn(tag)
  # Assignment tags:
  for ii in range(1, restraintList.restraintItemLength+1):
    for tag in ('chain_code_', 'sequence_code_', 'residue_type_', 'atom_name_'):
      ss = str(ii)
      loop.addColumn(tag + ss)
  # fixed tags:
  for tag in ('weight', 'target_value', 'target_value_uncertainty',):
    loop.addColumn(tag)
  # potential tags
  tags = nefTagsByPotentialType.get(potentialType)
  if tags is None:
    tags = nefTagsByPotentialType.get('unknown')
  for tag in tags:
    loop.addColumn(tag)

  # Add data
  for restraint in restraintList.restraints:
    serial = restraint.serial

    for contribution in restraint.contributions:
      row1 = [serial, contribution.combinationId]
      row3 = [contribution.weight, contribution.targetValue, contribution.error]
      for tag in ccpnTagsByPotentialType:
        row3.append(getattr(contribution, tag))

      for restraintItem in contribution.restraintItems:
        row2 = []
        # Assignment tags:
        for fullId in restraintItem:
          row2.extend(fullId.split('.'))
        #
        loop.addData(row1 + row2 + row3)
  #
  return saveframe

def makePeakListFrame(peakList, assignmentMap, shiftList=None):
  """ake saveFrame for peakList an containing spectrum"""

  dataSource = peakList.dataSource
  experiment = dataSource.experiment
  framecode = 'nmr_spectrum_%s_%s_%s' % (experiment.name, dataSource.serial, peakList.serial)
  category = 'nmr_spectrum'
  saveframe = bmrb.saveframe.fromScratch(saveframe_name=framecode,
                                         tag_prefix=category)

  # Top tagged values
  saveframe.addTags([
    ('sf_category',category),
    ('sf_framecode',framecode),
    ('num_dimensions',dataSource.numDim),
    ('chemical_shift_list','$chemical_shift_list_%s'
                           % (experiment.shiftList or shiftList).serial),
  ])

  refExperiment = experiment.refExperiment
  if refExperiment is not None:
    name = refExperiment.name
    synonym = refExperiment.synonym or '?'
  else:
    name =synonym = '?'
  saveframe.addTags([
    ('experiment_classification',name),
    ('expriment_type',synonym),
  ])


  # experiment dimensions loop
  loop = bmrb.loop.fromScratch(category='spectrum_dimension')
  saveframe.addLoop(loop)
  for tag in ('dimension_id', 'axis_unit', 'axis_code', 'spectrometer_frequency',
              'spectral_width', 'value_first_point', 'folding', 'absolute_peak_positions',
              'is_acquisition'):
    loop.addColumn(tag)

  for dim,dataDim in enumerate(dataSource.sortedDataDims()):

    # Find ExpDimRef to use. NB, could break for unusual cases
    expDimRefs = dataDim.expDim.sortedExpDimRefs()
    for expDimRef in expDimRefs:
      if expDimRef.measurementType.lower() == 'shift':
        # unfortunately casing of word is not reliable
        break
    else:
      expDimRef = expDimRefs[0]

    dataDimRef = dataDim.findFirstDataDimRef(expDimRef=expDimRef)

    isotopeCodes = expDimRef.isotopeCodes
    if len(isotopeCodes) == 1:
      isotopeCode = isotopeCodes[0]
    else:
      isotopeCode = '?'

    #
    loop.addDataByColumn('dimension_id', dim+1)
    loop.addDataByColumn('axis_unit', expDimRef.unit or '?')
    loop.addDataByColumn('axis_code', isotopeCode)
    loop.addDataByColumn('spectrometer_frequency', expDimRef.sf or '?')
    loop.addDataByColumn('spectral_width', dataDimRef.spectralWidthOrig)
    loop.addDataByColumn('value_first_point', dataDimRef.pointToValue(1. - dataDim.pointOffset))
    if expDimRef.isFolded:
      folding = 'mirror'
    elif expDimRef.hasAliasedFreq:
      # NBNB in practice people might not have set this correctly, but well ...
      folding = 'circular'
    else:
      folding='none'
    loop.addDataByColumn('folding', folding)
    loop.addDataByColumn('absolute_peak_positions', 'true')  # Always true in CCPN
    loop.addDataByColumn('is_acquisition', expDimRef.expDim.isAcquisition)


  # dimension connection loop
  loop = bmrb.loop.fromScratch(category='spectrum_dimension_transfer')
  saveframe.addLoop(loop)
  for tag in ('dimension_1', 'dimension_2', 'transfer_type', 'is_indirect'):
    loop.addColumn(tag)

  ref2Dim = {}
  for dim,dataDim in enumerate(dataSource.sortedDataDims()):
    # Find ExpDimRef to use. NB, could break for unusual cases
    expDimRefs = dataDim.expDim.sortedExpDimRefs()
    for expDimRef in expDimRefs:
      if expDimRef.measurementType.lower() == 'shift':
        # unfortunately casing of word is not reliable
        break
    else:
      expDimRef = expDimRefs[0]
    ref2Dim[expDimRef] = dim + 1

  rows = []
  for expTransfer in experiment.expTransfers:
    row = [ref2Dim.get(x) for x in expTransfer.expDimRefs]
    if None not in row:
      row.sort()
      row.append(expTransfer.transferType)
      row.append(not expTransfer.isDirect)
      rows.append(row)

  for row in sorted(rows):
    loop.addData(row)


  # main peak loop
  loop = bmrb.loop.fromScratch(category='peak')
  saveframe.addLoop(loop)
  for tag in ('peak_id', 'volume', 'volume_uncertainty', 'height', 'height_uncertainty'):
    loop.addColumn(tag)
  for ii in range(1, dataSource.numDim + 1):
    loop.addColumn('position_%s' % ii)
    loop.addColumn('position_uncertainty_%s' % ii)
  for ii in range(1, dataSource.numDim + 1):
    loop.addColumn('chain_code_%s' % ii)
    loop.addColumn('sequence_code_%s' % ii)
    loop.addColumn('residue_type_%s' % ii)
    loop.addColumn('atom_name_%s' % ii)

  for peak in peakList.sortedPeaks():

    peakDims = peak.sortedPeakDims()

    firstpart = [peak.serial] + Nef._getPeakIntensityData(peak)

    for peakDim in peakDims:
      firstpart.append(peakDim.value)
      firstpart.append(peakDim.valueError)


    mainPeakDimContribs = [sorted(x.mainPeakDimContribs, key=operator.attrgetter('serial'))
                           for x in peakDims]
    combinations = []
    for peakContrib in peak.sortedPeakContribs():
      allAtoms = []
      peakDimContribs = peakContrib.peakDimContribs
      for ii,peakDim in enumerate(peakDims):
        atoms = [list(assignmentMap.get(x.resonance)) for x in mainPeakDimContribs[ii]
                 if x in peakDimContribs and hasattr(x, 'resonance')]
        if not atoms:
          atoms = [[None]*4]
        allAtoms.append(atoms)

      combinations.extend(itertools.product(*allAtoms))

    if combinations:
      # Assigned peak add a line per assignment
      for combination in combinations:
        row = list(firstpart)
        row.extend(itertools.chain(*combination))
        loop.addData(row)
    else:
      # unassigned peak - add one line
      loop.addData(firstpart + (dataSource.numDim * 4 ) * ['.'])

  #
  return saveframe



def makePeakRestraintLinksFrame(constraintLists, peakLists):
  """ Make peak-constraint links frame, with links tha match both constraintLists and peakLists"""

  # header block
  category = 'peak_restraint_links'
  saveframe = bmrb.saveframe.fromScratch(saveframe_name=category,
                                         tag_prefix=category)
  saveframe.addTags([
    ('sf_category',category),
    ('sf_framecode',category),
  ])

  # peak restraint links loop
  loop = bmrb.loop.fromScratch(category='peak_restraint_link')
  saveframe.addLoop(loop)
  for tag in ('nmr_spectrum_id', 'peak_id', 'restraint_list_id', 'restraint_id'):
    loop.addColumn(tag)

  for constraintList in constraintLists:
    junk, restraint_list_id = _getStarFrameCodes(constraintList)
    restraint_list_id = '$' + restraint_list_id
    for constraint in constraintList.sortedConstraints():
      restraint_id = constraint.serial
      peaks = [x.peak for x in constraint.sortedPeakContribs()]
      for peak in peaks:
        if peak is not None and peak.peakList in peakLists:
          peakList = peak.peakList
          dataSource = peakList.dataSource
          peak_id = peak.serial
          nmr_spectrum_id = ('$nmr_spectrum_%s_%s_%s'
          % (dataSource.experiment.name, dataSource.serial, peakList.serial))
          #
          loop.addData([nmr_spectrum_id, peak_id, restraint_list_id, restraint_id])
  #
  return saveframe

def _getStarFrameCodes(constraintList):
  """ get category and framecode for a constraintList
  NBNB necessary because we use differewnt frame codes for H-bond constraints"""

  className = constraintList.className
  if className.startswith('Rdc'):
    restraintType = 'rdc'
    frameformat = 'rdc_restraint_list_%s'
  elif className.startswith('Distance'):
    restraintType = 'distance'
    frameformat = 'distance_restraint_list_%s'
  elif className.startswith('HBond'):
    restraintType = 'distance'
    frameformat = 'hydrogen_bond_restraint_list_%s'
  elif className.startswith('Dihedral'):
    restraintType = 'dihedral'
    frameformat = 'dihedral_restraint_list_%s'
  else:
    raise ValueError("Object %s is not a valid type of ConstraintList" % constraintList)
  #
  return restraintType, frameformat % constraintList.serial

if __name__ == '__main__':

  if len(sys.argv) >= 3:

    from memops.general.Io import loadProject
    # set up input
    junk, projectDir, outputDir = sys.argv[:3]
    ccpnProject = loadProject(projectDir)

    if len(sys.argv) >= 4:
      # set up input
      constraintStoreSerial = int(sys.argv[4])
      constraintStore = ccpnProject.findFirstNmrConstraintStore(serial=constraintStoreSerial)
    else:
      constraintStore = ccpnProject.findFirstNmrConstraintStore()

    exportConstraintStore2Nef(constraintStore, directory=outputDir)

  else:
    print ("Error. Parameters are: ccpnProjectDirectory outputDirectory [constraintStoreSerial] ")