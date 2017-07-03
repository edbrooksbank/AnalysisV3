"""NEF I/O for CCPN V2 release, data model version 2.1.2

Main functions for external use:

loadNefFile(path, memopsRoot=None, overwriteExisting=False):
  '''Load NEF file at path into memopsRoot, creating memopsRoot it not passed in'''

loadProject(nefFilePath, projectName=None, pdbFileType='pdb', *pdbFilePaths):
  '''Create new CCPN project from files at nefFilepath and (optional) pdbFilepaths

  if one pdbFilePath is passed in, the routine reads all models in that file.
  If multiple pdbFilePaths are passed in, the routine reads the first model from each file;
  this is to read ensembles stored with one model per file.

  The project name (determining the project directory) is taken from the NEF file if not passed in

  pdbFileType determines the pdb file format(s) to try:
  Default ('pdb') tries official PDB format, and robust read if that fails.
  Alternatively, 'cns' tries cns format, then robust read,
  and 'rough' tries robust read directly.'''


"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================

# NB must be Python 2.7 and 3.x compatible

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = (
"For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
"or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = ": Rasmus H Fogh $"
__dateModified__ = ": 2017-04-07 11:40:45 +0100 (Fri, April 07, 2017) $"
__version__ = ": 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = ": Rasmus H Fogh $"

__date__ = ": 2017-04-07 10:28:41 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import time
import sys
import os
import itertools
from collections import OrderedDict as OD

from ..nef import StarIo
from . import Constants
from .. import Common as commonUtil
from .. import Constants as genConstants

from ccp.general import Io as generalIo
from ccp.util import Spectrum as spectrumLib
from memops.general import Io as memopsIo
from memops.universal import Io as uniIo
from ccp.lib import MoleculeModify
from ccp.lib import StructureIo
from ccp.lib import NmrExpPrototype as NmrExpPrototypeLib
from ccpnmr.analysis.core import MoleculeBasic
from ccpnmr.analysis.core import AssignmentBasic
from ccpnmr.analysis.core import ExperimentBasic
from ccpnmr.analysis.core import ConstraintBasic

# # Max value used for random integer. Set to be expressible as a signed 32-bit integer.
# maxRandomInt =  2000000000

#  - saveframe category names in reading order
# The order is significant, because setting of crosslinks relies on the order frames are read
# Frames are read in correct order regardless of how they are in the file
saveFrameReadingOrder = [
  # 'nef_nmr_meta_data',  # Nowhere to put information. Ignored.
  'nef_molecular_system',
  # 'ccpn_sample',     # Supported, but reading postponed (indefinitely?)
  # 'ccpn_substance',  # Supported, but reading postponed (indefinitely?)
  'ccpn_assignment',
  'nef_chemical_shift_list',
  # 'ccpn_dataset',    # No supported information - no use or need.
  'nef_distance_restraint_list',
  'nef_dihedral_restraint_list',
  'nef_rdc_restraint_list',
  'nef_nmr_spectrum',
  'nef_peak_restraint_links',
  # 'ccpn_complex',     # Not supported in V2
  # 'ccpn_spectrum_group',     # Not supported in V2
  # 'ccpn_restraint_list',
  # 'ccpn_notes',     # Not supported in V2
  # 'ccpn_additional_data'     # Not supported in V2
]

# TODO: implement residue variants, disulfides. Test

class _isALoop:
  # Dummy value - to be removed
  pass

nef2CcpnMap = {
  'nef_nmr_meta_data':OD((
    ('format_name',None),
    ('format_version',None),
    ('program_name',None),
    ('program_version',None),
    ('creation_date',None),
    ('uuid',None),
    ('coordinate_file_name',None),
    ('ccpn_dataset_serial', None),
    ('ccpn_dataset_comment',None),
    ('nef_related_entries',_isALoop),
    ('nef_program_script',_isALoop),
    ('nef_run_history',_isALoop),
  )),
  'nef_related_entries':OD((
    ('database_name',None),
    ('database_accession_code',None),
  )),
  'nef_program_script':OD((
    ('program_name',None),
    ('script_name',None),
    ('script',None),
  )),
  'nef_run_history':OD((
    ('run_number','serial'),
    ('program_name','programName'),
    ('program_version','programVersion'),
    ('script_name','scriptName'),
    ('script','script'),
    ('ccpn_input_uuid','inputDataUuid'),
    ('ccpn_output_uuid','outputDataUuid'),
  )),

  'nef_molecular_system':OD((
    ('nef_sequence',_isALoop),
    ('nef_covalent_links',_isALoop),
  )),
  'nef_sequence':OD((
    ('index', None),
    ('chain_code','chain.shortName'),
    ('sequence_code','sequenceCode'),
    ('residue_name','residueType'),
    ('linking','linking'),
    ('residue_variant','residueVariant'),
    ('cis_peptide',None),
    ('ccpn_comment','comment'),
    ('ccpn_chain_role','chain.role'),
    ('ccpn_compound_name','chain.compoundName'),
    ('ccpn_chain_comment','chain.comment'),
  )),
  'nef_covalent_links':OD((
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
  )),

  'nef_chemical_shift_list':OD((
    ('ccpn_serial','serial'),
    ('ccpn_auto_update','autoUpdate'),
    ('ccpn_is_simulated','isSimulated'),
    ('ccpn_comment','comment'),
    ('nef_chemical_shift',_isALoop),
  )),
  'nef_chemical_shift':OD((
    ('chain_code',None),
    ('sequence_code',None),
    ('residue_name',None),
    ('atom_name',None),
    ('value','value'),
    ('value_uncertainty','valueError'),
    ('element',None),
    ('isotope_number',None),
    ('ccpn_figure_of_merit','figureOfMerit'),
    ('ccpn_comment','comment'),
  )),

  'nef_distance_restraint_list':OD((
    ('potential_type','potentialType'),
    ('restraint_origin','origin'),
    ('ccpn_tensor_chain_code','tensorChainCode'),
    ('ccpn_tensor_sequence_code','tensorSequenceCode'),
    ('ccpn_tensor_residue_name','tensorResidueType'),
    ('ccpn_tensor_magnitude', 'tensorMagnitude'),
    ('ccpn_tensor_rhombicity', 'tensorRhombicity'),
    ('ccpn_tensor_isotropic_value', 'tensorIsotropicValue'),
    ('ccpn_serial','serial'),
    ('ccpn_dataset_serial','dataSet.serial'),
    ('ccpn_unit','unit'),
    ('ccpn_comment','comment'),
    ('nef_distance_restraint',_isALoop),
  )),
  'nef_distance_restraint':OD((
    ('index',None),
    ('restraint_id','restraint.serial'),
    ('restraint_combination_id','combinationId'),
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
    ('weight','weight'),
    ('target_value','targetValue'),
    ('target_value_uncertainty','error'),
    ('lower_linear_limit','additionalLowerLimit'),
    ('lower_limit','lowerLimit'),
    ('upper_limit','upperLimit'),
    ('upper_linear_limit','additionalUpperLimit'),
    ('ccpn_figure_of_merit','restraint.figureOfMerit'),
    ('ccpn_comment','restraint.comment'),
  )),

  'nef_dihedral_restraint_list':OD((
    ('potential_type','potentialType'),
    ('restraint_origin','origin'),
    ('ccpn_tensor_chain_code','tensorChainCode'),
    ('ccpn_tensor_sequence_code','tensorSequenceCode'),
    ('ccpn_tensor_residue_name','tensorResidueType'),
    ('ccpn_tensor_magnitude', 'tensorMagnitude'),
    ('ccpn_tensor_rhombicity', 'tensorRhombicity'),
    ('ccpn_tensor_isotropic_value', 'tensorIsotropicValue'),
    ('ccpn_serial','serial'),
    ('ccpn_dataset_serial','dataSet.serial'),
    ('ccpn_unit','unit'),
    ('ccpn_comment','comment'),
    ('nef_dihedral_restraint',_isALoop),
  )),
  'nef_dihedral_restraint':OD((
    ('index',None),
    ('restraint_id','restraint.serial'),
    ('restraint_combination_id','combinationId'),
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
    ('chain_code_3',None),
    ('sequence_code_3',None),
    ('residue_name_3',None),
    ('atom_name_3',None),
    ('chain_code_4',None),
    ('sequence_code_4',None),
    ('residue_name_4',None),
    ('atom_name_4',None),
    ('weight','weight'),
    ('target_value','targetValue'),
    ('target_value_uncertainty','error'),
    ('lower_linear_limit','additionalLowerLimit'),
    ('lower_limit','lowerLimit'),
    ('upper_limit','upperLimit'),
    ('upper_linear_limit','additionalUpperLimit'),
    ('name',None),
    ('ccpn_figure_of_merit','restraint.figureOfMerit'),
    ('ccpn_comment','restraint.comment'),
  )),

  'nef_rdc_restraint_list':OD((
    ('potential_type','potentialType'),
    ('restraint_origin','origin'),
    ('tensor_magnitude', 'tensorMagnitude'),
    ('tensor_rhombicity', 'tensorRhombicity'),
    ('tensor_chain_code','tensorChainCode'),
    ('tensor_sequence_code','tensorSequenceCode'),
    ('tensor_residue_name','tensorResidueType'),
    ('ccpn_tensor_isotropic_value', 'tensorIsotropicValue'),
    ('ccpn_serial','serial'),
    ('ccpn_dataset_serial','dataSet.serial'),
    ('ccpn_unit','unit'),
    ('ccpn_comment','comment'),
    ('nef_rdc_restraint',_isALoop),
  )),
  'nef_rdc_restraint':OD((
    ('index',None),
    ('restraint_id','restraint.serial'),
    ('restraint_combination_id','combinationId'),
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
    ('weight','weight'),
    ('target_value','targetValue'),
    ('target_value_uncertainty','error'),
    ('lower_linear_limit','additionalLowerLimit'),
    ('lower_limit','lowerLimit'),
    ('upper_limit','upperLimit'),
    ('upper_linear_limit','additionalUpperLimit'),
    ('scale','scale'),
    ('distance_dependent','isDistanceDependent'),
    ('ccpn_vector_length','restraint.vectorLength'),
    ('ccpn_figure_of_merit','restraint.figureOfMerit'),
    ('ccpn_comment','restraint.comment'),
  )),

  'nef_nmr_spectrum':OD((
    ('num_dimensions','spectrum.dimensionCount'),
    ('chemical_shift_list',None),
    ('experiment_classification','spectrum.experimentType'),
    ('experiment_type','spectrum.experimentName'),
    ('ccpn_positive_contour_count','spectrum.positiveContourCount'),
    ('ccpn_positive_contour_base','spectrum.positiveContourBase'),
    ('ccpn_positive_contour_factor','spectrum.positiveContourFactor'),
    ('ccpn_positive_contour_colour','spectrum.positiveContourColour'),
    ('ccpn_negative_contour_count','spectrum.negativeContourCount'),
    ('ccpn_negative_contour_base','spectrum.negativeContourBase'),
    ('ccpn_negative_contour_factor','spectrum.negativeContourFactor'),
    ('ccpn_negative_contour_colour','spectrum.negativeContourColour'),
    ('ccpn_slice_colour','spectrum.sliceColour'),
    ('ccpn_spectrum_scale','spectrum.scale'),
    ('ccpn_spinning_rate','spectrum.spinningRate'),
    ('ccpn_spectrum_comment','spectrum.comment'),
    ('ccpn_spectrum_file_path', None),
    ('ccpn_sample', None),
    ('ccpn_file_header_size', 'spectrum._wrappedData.dataStore.headerSize'),
    ('ccpn_file_number_type', 'spectrum._wrappedData.dataStore.numberType'),
    ('ccpn_file_complex_stored_by', 'spectrum._wrappedData.dataStore.complexStoredBy'),
    ('ccpn_file_scale_factor', 'spectrum._wrappedData.dataStore.scaleFactor'),
    ('ccpn_file_is_big_endian', 'spectrum._wrappedData.dataStore.isBigEndian'),
    ('ccpn_file_byte_number', 'spectrum._wrappedData.dataStore.nByte'),
    ('ccpn_file_has_block_padding', 'spectrum._wrappedData.dataStore.hasBlockPadding'),
    ('ccpn_file_block_header_size', 'spectrum._wrappedData.dataStore.blockHeaderSize'),
    ('ccpn_file_type', 'spectrum._wrappedData.dataStore.fileType'),
    ('ccpn_peaklist_serial','serial'),
    ('ccpn_peaklist_comment','comment'),
    ('ccpn_peaklist_name','title'),
    ('ccpn_peaklist_is_simulated','isSimulated'),
    ('ccpn_peaklist_symbol_colour','symbolColour'),
    ('ccpn_peaklist_symbol_style','symbolStyle'),
    ('ccpn_peaklist_text_colour','textColour'),
    ('nef_spectrum_dimension',_isALoop),
    ('ccpn_spectrum_dimension',_isALoop),
    ('nef_spectrum_dimension_transfer',_isALoop),
    ('nef_peak',_isALoop),
    ('ccpn_integral_list',_isALoop),
    ('ccpn_integral',_isALoop),
    ('ccpn_spectrum_hit',_isALoop),
  )),
  'nef_spectrum_dimension':OD((
    ('dimension_id',None),
    ('axis_unit','axisUnits'),
    ('axis_code','isotopeCodes'),
    ('spectrometer_frequency','spectrometerFrequencies'),
    ('spectral_width','spectralWidths'),
    ('value_first_point',None),
    ('folding',None),
    ('absolute_peak_positions',None),
    ('is_acquisition',None),
    ('ccpn_axis_code','axisCodes'),
  )),
  # NB PseudoDimensions are not yet supported
  'ccpn_spectrum_dimension':OD((
    ('dimension_id',None),
    ('point_count','pointCounts'),
    ('reference_point','referencePoints'),
    ('total_point_count','totalPointCounts'),
    ('point_offset','pointOffsets'),
    ('assignment_tolerance','assignmentTolerances'),
    ('lower_aliasing_limit',None),
    ('higher_aliasing_limit',None),
    ('measurement_type','measurementTypes'),
    ('phase_0','phases0'),
    ('phase_1','phases1'),
    ('window_function','windowFunctions'),
    ('lorentzian_broadening','lorentzianBroadenings'),
    ('gaussian_broadening','gaussianBroadenings'),
    ('sine_window_shift','sineWindowShifts'),
    ('dimension_is_complex', '_wrappedData.dataStore.isComplex'),
    ('dimension_block_size', '_wrappedData.dataStore.blockSizes'),
  )),
  'nef_spectrum_dimension_transfer':OD((
    ('dimension_1',None),
    ('dimension_2',None),
    ('transfer_type',None),
    ('is_indirect',None),
  )),
  'nef_peak':OD((
    ('index',None),
    ('peak_id','serial'),
    ('volume','volume'),
    ('volume_uncertainty','volumeError'),
    ('height','height'),
    ('height_uncertainty','heightError'),
    ('position_1',None),
    ('position_uncertainty_1',None),
    ('position_2',None),
    ('position_uncertainty_2',None),
    ('position_3',None),
    ('position_uncertainty_3',None),
    ('position_4',None),
    ('position_uncertainty_4',None),
    ('position_5',None),
    ('position_uncertainty_5',None),
    ('position_6',None),
    ('position_uncertainty_6',None),
    ('position_7',None),
    ('position_uncertainty_7',None),
    ('position_8',None),
    ('position_uncertainty_8',None),
    ('position_9',None),
    ('position_uncertainty_9',None),
    ('position_10',None),
    ('position_uncertainty_10',None),
    ('position_11',None),
    ('position_uncertainty_11',None),
    ('position_12',None),
    ('position_uncertainty_12',None),
    ('position_13',None),
    ('position_uncertainty_13',None),
    ('position_14',None),
    ('position_uncertainty_14',None),
    ('position_15',None),
    ('position_uncertainty_15',None),
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
    ('chain_code_3',None),
    ('sequence_code_3',None),
    ('residue_name_3',None),
    ('atom_name_3',None),
    ('chain_code_4',None),
    ('sequence_code_4',None),
    ('residue_name_4',None),
    ('atom_name_4',None),
    ('chain_code_5',None),
    ('sequence_code_5',None),
    ('residue_name_5',None),
    ('atom_name_5',None),
    ('chain_code_6',None),
    ('sequence_code_6',None),
    ('residue_name_6',None),
    ('atom_name_6',None),
    ('chain_code_7',None),
    ('sequence_code_7',None),
    ('residue_name_7',None),
    ('atom_name_7',None),
    ('chain_code_8',None),
    ('sequence_code_8',None),
    ('residue_name_8',None),
    ('atom_name_8',None),
    ('chain_code_9',None),
    ('sequence_code_9',None),
    ('residue_name_9',None),
    ('atom_name_9',None),
    ('chain_code_10',None),
    ('sequence_code_10',None),
    ('residue_name_10',None),
    ('atom_name_10',None),
    ('chain_code_11',None),
    ('sequence_code_11',None),
    ('residue_name_11',None),
    ('atom_name_11',None),
    ('chain_code_12',None),
    ('sequence_code_12',None),
    ('residue_name_12',None),
    ('atom_name_12',None),
    ('chain_code_13',None),
    ('sequence_code_13',None),
    ('residue_name_13',None),
    ('atom_name_13',None),
    ('chain_code_14',None),
    ('sequence_code_14',None),
    ('residue_name_14',None),
    ('atom_name_14',None),
    ('chain_code_15',None),
    ('sequence_code_15',None),
    ('residue_name_15',None),
    ('atom_name_15',None),
    ('ccpn_figure_of_merit','figureOfMerit'),
    ('ccpn_annotation','annotation'),
    ('ccpn_comment','comment'),
  )),
  # NB SpectrumHit crosslink to sample and sampleComponent are derived
  # And need not be stored here.
  'ccpn_spectrum_hit':OD((
    ('ccpn_substance_name','substanceName'),
    ('ccpn_pseudo_dimension_number','pseudoDimensionNumber'),
    ('ccpn_point_number','pointNumber'),
    ('ccpn_figure_of_merit','figureOfMerit'),
    ('ccpn_merit_code','meritCode'),
    ('ccpn_normalised_change','normalisedChange'),
    ('ccpn_is_confirmed_','isConfirmed'),
    ('ccpn_concentration','concentration'),
    ('ccpn_','concentrationError'),
    ('ccpn_concentration_uncertainty','concentrationUnit'),
    ('ccpn_comment','comment'),
  )),

  'nef_peak_restraint_links':OD((
    ('nef_peak_restraint_link',_isALoop),
  )),
  'nef_peak_restraint_link':OD((
    ('nmr_spectrum_id',None),
    ('peak_id',None),
    ('restraint_list_id',None),
    ('restraint_id',None),
  )),

  'ccpn_complex':OD((
    ('name','name'),
    ('ccpn_complex_chain',_isALoop),
  )),
  'ccpn_complex_chain':OD((
    ('complex_chain_code',None),
  )),

  'ccpn_spectrum_group':OD((
    ('name','name'),
    ('ccpn_group_spectrum',_isALoop),
  )),
  'ccpn_group_spectrum':OD((
    ('nmr_spectrum_id',None),
  )),

  'ccpn_integral_list':OD((
    ('serial',None),
    ('name','title'),
    ('symbol_colour','symbolColour'),
    ('text_colour','textColour'),
    ('comment','comment'),
  )),

  'ccpn_integral':OD((
    ('integral_list_serial','integralList.serial'),
    ('integral_serial',None),
    ('value','value'),
    ('value_uncertainty','valueError'),
    ('bias','bias'),
    ('figure_of_merit','figureOfMerit'),
    ('slopes_1',None),
    ('slopes_2',None),
    ('slopes_3',None),
    ('slopes_4',None),
    ('lower_limits_1',None),
    ('upper_limits_1',None),
    ('lower_limits_2',None),
    ('upper_limits_2',None),
    ('lower_limits_3',None),
    ('upper_limits_3',None),
    ('lower_limits_4',None),
    ('upper_limits_4',None),
    ('annotation','annotation'),
    ('comment','comment'),
  )),

  # NB Sample crosslink to spectrum is handled on the spectrum side
  'ccpn_sample':OD((
    ('name','name'),
    ('pH','ph'),
    ('ionic_strength','ionicStrength'),
    ('amount','amount'),
    ('amount_unit','amountUnit'),
    ('is_hazardous','isHazardous'),
    ('is_virtual','isVirtual'),
    ('creation_date','creationDate'),
    ('batch_identifier','batchIdentifier'),
    ('plate_identifier','plateIdentifier'),
    ('row_number','rowNumber'),
    ('column_number','columnNumber'),
    ('comment','comment'),
    ('ccpn_sample_component',_isALoop),
  )),
  'ccpn_sample_component':OD((
    ('name','name'),
    ('labelling','labelling'),
    ('role','role'),
    ('concentration','concentration'),
    ('concentration_error','concentrationError'),
    ('concentration_unit','concentrationUnit'),
    ('purity','purity'),
    ('comment','comment'),
  )),

  'ccpn_substance':OD((
    ('name','name'),
    ('labelling','labelling'),
    ('substance_type', None),
    ('user_code','userCode'),
    ('smiles','smiles'),
    ('inchi','inChi'),
    ('cas_number','casNumber'),
    ('empirical_formula','empiricalFormula'),
    ('sequence_string',None),
    ('mol_type',None),
    ('start_number',None),
    ('is_cyclic',None),
    ('molecular_mass','molecularMass'),
    ('atom_count','atomCount'),
    ('bond_count','bondCount'),
    ('ring_count','ringCount'),
    ('h_bond_donor_count','hBondDonorCount'),
    ('h_bond_acceptor_count','hBondAcceptorCount'),
    ('polar_surface_area','polarSurfaceArea'),
    ('log_partition_coefficient','logPartitionCoefficient'),
    ('comment','comment'),
    ('ccpn_substance_synonym',_isALoop),
  )),
  'ccpn_substance_synonym':OD((
    ('synonym',None),
  )),

  'ccpn_assignment':OD((
    ('nmr_chain',_isALoop),
    ('nmr_residue',_isALoop),
    ('nmr_atom',_isALoop),
  )),

  'nmr_chain':OD((
    ('short_name','shortName'),
    ('serial',None),
    ('label','label'),
    ('is_connected','isConnected'),
    ('comment','comment'),
  )),

  'nmr_residue':OD((
    ('chain_code', 'nmrChain.shortName'),
    ('sequence_code','sequenceCode'),
    ('residue_name','residueType'),
    ('serial',None),
    ('comment','comment'),
  )),

  'nmr_atom':OD((
    ('chain_code','nmrResidue.nmrChain.shortName'),
    ('sequence_code','nmrResidue.sequenceCode'),
    ('serial',None),
    ('name','name'),
    ('isotopeCode','isotopeCode'),
    ('comment','comment'),
  )),

  'ccpn_dataset':OD((
    ('serial','serial'),
    ('title','title'),
    ('program_name','programName'),
    ('program_version','programVersion'),
    ('data_path','dataPath'),
    ('creation_date',None),
    ('uuid','uuid'),
    ('comment','comment'),
    ('ccpn_calculation_step',_isALoop),
    ('ccpn_calculation_data',_isALoop),
  )),

  'ccpn_calculation_step':OD((
    ('serial', None),
    ('program_name','programName'),
    ('program_version','programVersion'),
    ('script_name','scriptName'),
    ('script','script'),
    ('input_data_uuid','inputDataUuid'),
    ('output_data_uuid','outputDataUuid'),
  )),

  'ccpn_calculation_data':OD((
    ('data_name','name'),
    ('attached_object_pid','attachedObjectPid'),
    ('parameter_name', None),
    ('parameter_value', None),
  )),

  'ccpn_restraint_list':OD((
    ('potential_type','potentialType'),
    ('restraint_origin','origin'),
    ('tensor_chain_code','tensorChainCode'),
    ('tensor_sequence_code','tensorSequenceCode'),
    ('tensor_residue_name','tensorResidueType'),
    ('tensor_magnitude', 'tensorMagnitude'),
    ('tensor_rhombicity', 'tensorRhombicity'),
    ('tensor_isotropic_value', 'tensorIsotropicValue'),
    ('ccpn_serial','serial'),
    ('dataset_serial','dataSet.serial'),
    ('name','name'),
    ('restraint_type','restraintType'),
    ('restraint_item_length','restraintItemLength'),
    ('unit','unit'),
    ('measurement_type','measurementType'),
    ('comment','comment'),
    ('ccpn_restraint',_isALoop),
  )),
  'ccpn_restraint':OD((
    ('index',None),
    ('restraint_id','restraint.serial'),
    ('restraint_combination_id','combinationId'),
    ('chain_code_1',None),
    ('sequence_code_1',None),
    ('residue_name_1',None),
    ('atom_name_1',None),
    ('chain_code_2',None),
    ('sequence_code_2',None),
    ('residue_name_2',None),
    ('atom_name_2',None),
    ('chain_code_3',None),
    ('sequence_code_3',None),
    ('residue_name_3',None),
    ('atom_name_3',None),
    ('chain_code_4',None),
    ('sequence_code_4',None),
    ('residue_name_4',None),
    ('atom_name_4',None),
    ('weight','weight'),
    ('target_value','targetValue'),
    ('target_value_uncertainty','error'),
    ('lower_linear_limit','additionalLowerLimit'),
    ('lower_limit','lowerLimit'),
    ('upper_limit','upperLimit'),
    ('upper_linear_limit','additionalUpperLimit'),
    ('scale','scale'),
    ('distance_dependent','isDistanceDependent'),
    ('name',None),
    ('vector_length','restraint.vectorLength'),
    ('figure_of_merit','restraint.figureOfMerit'),
    ('ccpn_comment','restraint.comment'),
  )),

  'ccpn_notes':OD((
    ('ccpn_note',_isALoop),
  )),
  'ccpn_note':OD((
    ('serial',None),
    ('name','name'),
    ('created', None),
    ('last_modified', None),
    ('text','text'),
  )),

  'ccpn_additional_data':OD((
    ('ccpn_internal_data',_isALoop),
  )),
  'ccpn_internal_data':OD((
    ('ccpn_object_pid',None),
    ('internal_data_string',None)
  )),

}
def loadProject(nefFilePath, pdbFilePaths=None, projectName=None, pdbFileType='pdb'):
  """Create new CCPN project from files at nefFilepath and (optional) pdbFilepaths

  if one pdbFilePath is passed in, the routine reads all models in that file.
  If a sequence of pdbFilePaths are passed in, the routine reads the first model from each file;
  this is to read ensembles stored with one model per file.

  The project name (determining the project directory) is taken from the NEF file if not passed in

  pdbFileType determines the pdb file format(s) to try:
  Default ('pdb') tries official PDB format, and robust read if that fails.
  Alternatively, 'cns' tries cns format, then robust read,
  and 'rough' tries robust read directly."""

  nefReader = CcpnNefReader()
  dataBlock = nefReader.getNefData(nefFilePath)
  if not projectName:
    projectName = os.path.splitext(dataBlock.name)[0]
  memopsRoot = memopsIo.newProject(projectName)
  nefReader.importNewProject(memopsRoot, dataBlock)
  if pdbFilePaths:
    if isinstance(pdbFilePaths, str):
      StructureIo.getStructureFromFile(memopsRoot.findFirstMolSystem(), pdbFilePaths,
                                       fileType=pdbFileType)
    else:
      StructureIo.getStructureFromFiles(memopsRoot.findFirstMolSystem(), pdbFilePaths,
                                        fileType=pdbFileType)
  #
  return memopsRoot



def loadNefFile(path, memopsRoot=None, overwriteExisting=False):
  """Load NEF file at path into memopsRoot, creating memopsRoot if not passed in"""

  nefReader = CcpnNefReader()
  dataBlock = nefReader.getNefData(path)
  if memopsRoot is None:
    name = os.path.splitext(dataBlock.name)[0]
    memopsRoot = memopsIo.newProject(name, removeExisting=overwriteExisting)
  nefReader.importNewProject(memopsRoot, dataBlock)
  #
  return memopsRoot


class CcpnNefReader:
  # Importer functions - used for converting saveframes and loops
  importers = {}

  def __init__(self, testing=False):

    self.saveFrameName = None
    self.warnings = []
    self.errors = []
    self.testing = testing

    # Information for mapping NmrExpPrototype dimensions
    self.refExpDimRefCodeMap = None

    # Map for resolving crosslinks in NEF file
    self.frameCode2Object = {}

    # Map for speeding up restraint reading
    self._dataSet2ItemMap = None
    # self._nmrResidueMap = None

    self._chainMapping = None

    self.defaultDataSetSerial = None
    self.defaultNmrChain = None
    self.mainDataSetSerial = None
    self.defaultChemicalShiftList = None


  def getNefData(self, path):
    """Get NEF data structure from file"""
    nmrDataExtent = StarIo.parseNefFile(path)
    dataBlocks = list(nmrDataExtent.values())
    dataBlock = dataBlocks[0]

    # Initialise afresh for every file read
    self._dataSet2ItemMap = {}
    # self._nmrResidueMap = {}

    self._chainMapping = {}
    #
    return dataBlock

  def _getSaveFramesInOrder(self, dataBlock):
    """Get saveframes in fixed reading order as OrderedDict(category:[saveframe,])"""
    result = OD(((x, []) for x in saveFrameReadingOrder))
    result['other'] = otherFrames = []
    for saveFrameName, saveFrame in dataBlock.items():
      sf_category = saveFrame.get('sf_category')
      ll = result.get(sf_category)
      if ll is None:
        ll = otherFrames
      ll.append(saveFrame)
    #
    return result

  def initialiseProject(self, memopsRoot, name):
    """Initialise Project for reading, making new top level objects to
    hold loaded data"""
    # NB These are automatically set as current on the memopsRoot
    nmrProject = memopsRoot.newNmrProject(name=name)
    memopsRoot.newMolSystem(code=name, name=name)
    memopsRoot.newAnalysisProject(name=name, nmrProject=nmrProject)
    self.refExpDimRefCodeMap = dd = NmrExpPrototypeLib.refExpDimRefCodeMap(memopsRoot)
    for key,val in dd.items():
      # V2 has '_' separators in axis codes, but the NmrExpPrototypes and V3 does not
      dd[key] = val.replace('_','')


  def importNewProject(self, memopsRoot, dataBlock):
    """Import entire project from dataBlock into empty Project"""

    t0 = time.time()

    self.warnings = []

    self.memopsRoot = memopsRoot
    name = dataBlock.name
    self.initialiseProject(memopsRoot, name=name)

    self.defaultChainCode = None

    saveframeOrderedDict = self._getSaveFramesInOrder(dataBlock)

    saveFrame = dataBlock.get('nef_molecular_system')
    if saveFrame:
      self.saveFrameName = 'nef_molecular_system'
      self.load_nef_molecular_system(memopsRoot, saveFrame)
    del saveframeOrderedDict['nef_molecular_system']

    # Load CCPN assignments, if present, to preserve connected stretches
    saveFrame = dataBlock.get('ccpn_assignment')
    if saveFrame:
      self.saveFrameName = 'ccpn_assignment'
      self.load_ccpn_assignment(memopsRoot, saveFrame)
      del saveframeOrderedDict['ccpn_assignment']

    for sf_category, saveFrames in saveframeOrderedDict.items():
      if sf_category == 'nef_nmr_meta_data':
        # We are doing nothiing with it, but we do not want a warning
        continue
      for saveFrame in saveFrames:
        saveFrameName = self.saveFrameName = saveFrame.name

        importer = self.importers.get(sf_category)
        if importer is None:
          print ("WARNING, unknown saveframe category", sf_category, saveFrameName)
        else:

          result = importer(self, memopsRoot, saveFrame)
          self.frameCode2Object[saveFrameName] = result
          t2 = time.time()
    print('Loaded NEF file, time = ', t2-t0)

    for msg in self.warnings:
      print ('====> ', msg)
    self.memopsRoot = None

  def load_nef_molecular_system(self, project, saveFrame):
    """load nef_molecular_system saveFrame"""

    self.load_nef_sequence(project, saveFrame.get('nef_sequence'))
    self.load_nef_covalent_links(project, saveFrame.get('nef_covalent_links'))
    #
    return None

  def load_nef_sequence(self, memopsRoot, loop):
    """Load nef_sequence loop"""

    result = []

    chainData = {}
    for row in loop.data:
      chainCode = row['chain_code']
      ll = chainData.get(chainCode)
      if ll is None:
        chainData[chainCode] = [row]
      else:
        ll.append(row)

    # Get default chain code - NB this can break with more than 26 chains, but so what?
    defaultChainCode = None
    if None in chainData:
      defaultChainCode = 'A'
      # Replace chainCode None with default chainCode
      # Selecting the first value that is not already taken.
      while defaultChainCode in chainData:
        defaultChainCode = chr(ord(defaultChainCode)+1)
      chainData[defaultChainCode] = chainData.pop(None)
    self.defaultChainCode = defaultChainCode

    sequence2Chain = {}
    tags =('residue_name', 'linking', 'residue_variant')
    for chainCode, rows in sorted(chainData.items()):
      compoundName = rows[0].get('ccpn_compound_name') or 'Molecule_%s' % chainCode
      role = rows[0].get('ccpn_chain_role')
      comment = rows[0].get('ccpn_chain_comment')

      for row in rows:
        # NB these will be dealt with as unknown residues later, which is what we want
        if row.get('linking') == 'dummy':
          row['residue_name'] = 'dummy.' + row['residue_name']
      sequence = tuple(tuple(row.get(tag) for tag in tags) for row in rows)

      lastChain = sequence2Chain.get(sequence)
      if lastChain is None:
        molecule = createMoleculeFromNef(memopsRoot, name=compoundName, sequence=rows)
        newChain = memopsRoot.currentMolSystem.newChain(code=chainCode, molecule=molecule)
        sequence2Chain[sequence] = newChain

        # TODO implement alternative to this
        # # Set variant codes:
        # for ii, residue in enumerate(newChain.residues):
        #   variantCode = sequence[ii][2]
        #
        #   if variantCode:
        #
        #     atomNamesRemoved, atomNamesAdded = residue._wrappedData.getAtomNameDifferences()
        #
        #
        #     for code in variantCode.split(','):
        #       code = code.strip()  # Should not be necessary but costs nothing to catch those errors
        #       atom = residue.getAtom(code[1:])
        #       if code[0] == '-':
        #         if atom is None:
        #           residue._project._logger.error(
        #             "Incorrect variantCode %s: No atom named %s found in %s. Skipping ..."
        #             % (variantCode, code, residue)
        #           )
        #         else:
        #           atom.delete()
        #
        #       elif code[0] == '+':
        #         if atom is None:
        #           residue.newAtom(name=code[1:])
        #         else:
        #           residue._project._logger.error(
        #             "Incorrect variantCode %s: Atom named %s already present in %s. Skipping ..."
        #             % (variantCode, code, residue)
        #           )
        #
        #       else:
        #         residue._project._logger.error(
        #           "Incorrect variantCode %s: must start with '+' or '-'. Skipping ..."
        #           % variantCode
        #         )

      else:
        from memops.general.Util import copySubTree
        newChain = copySubTree(lastChain, memopsRoot.currentMolSystem,
                               topObjectParameters={'code':chainCode})

      newChain.role = role
      newChain.details = comment

      # set seqCode, seqInsertCode and make mapping dictionary
      self._chainMapping[chainCode] = chainDict = OD()
      for ii, residue in enumerate(newChain.sortedResidues()):

        sequenceCode = rows[ii]['sequence_code']

        # set seqCode, seqInsertCode
        seqCode, seqInsertCode, offset = commonUtil.parseSequenceCode(sequenceCode)
        residue.seqCode = seqCode
        if seqInsertCode:
          residue.seqInsertCode = seqInsertCode

        # Make chainMapping
        chainDict[sequenceCode] = resDict = {'residue':residue, 'resonanceGroup':None}
        atomMappings = resDict['atomMappings'] = {}
        residueMapping = MoleculeBasic.getResidueMapping(residue, aromaticsEquivalent=True)
        for asm in residueMapping.atomSetMappings:
          atDict = {'atomSetMapping':asm}
          for tag in ('name', 'mappingType', 'elementSymbol', 'atomSets'):
            atDict[tag] = getattr(asm, tag)
          atDict['resonances'] = None
          atName = atDict['name'].replace('*', '%').upper()
          if atDict['mappingType'] == 'nonstereo':
            if atName.endswith('A'):
              atName = atName[:-1] + 'x'
            elif atName.endswith('B'):
              atName = atName[:-1] + 'y'
            elif atName.endswith('A%'):
              atName = atName[:-2] + 'x%'
            elif atName.endswith('B%'):
              atName = atName[:-2] + 'y%'
          atomMappings[atName] = atDict
      #
      result.append(newChain)

      # Add Residue comments
      for ii, apiResidue in enumerate(newChain.residues):
        comment = rows[ii].get('ccpn_comment')
        if comment:
          apiResidue.details = comment
    #
    return result
  #
  importers['nef_sequence'] = load_nef_sequence


  def load_nef_covalent_links(self, project, loop):
    """Load nef_sequence loop"""

    # TODO Add reading and setting of disulfides (nothing else here is supported)
    return None

    # result = []
    #
    # for row in loop.data:
    #   id1 = Pid.createId(*(row[x] for x in ('chain_code_1', 'sequence_code_1',
    #                                        'residue_name_1', 'atom_name_1', )))
    #   id2 = Pid.createId(*(row[x] for x in ('chain_code_2', 'sequence_code_2',
    #                                        'residue_name_2', 'atom_name_2', )))
    #   atom1 = project.getAtom(id1)
    #   atom2 = project.getAtom(id2)
    #   if atom1 is None:
    #     self.warning("Unknown atom %s for bond to %s. Skipping..." % (id1, id2))
    #   elif atom2 is None:
    #     self.warning("Unknown atom %s for bond to %s. Skipping..." % (id2, id1))
    #   else:
    #     result.append((atom1, atom2))
    #     atom1.addInterAtomBond(atom2)
    # #
    # return result
  # #
  # importers['nef_covalent_links'] = load_nef_covalent_links


  def load_nef_chemical_shift_list(self, project, saveFrame):
    """load nef_chemical_shift_list saveFrame"""

    # Get ccpn-to-nef mappping for saveframe
    category = saveFrame['sf_category']
    framecode = saveFrame['sf_framecode']
    name = framecode[len(category) + 1:]
    comment = saveFrame.get('ccpn_comment')

    shiftList = project.currentNmrProject.newShiftList(name=name, details=comment)
    if self.defaultChemicalShiftList is None:
      # ChemicalShiftList should default to the unique ChemicalShIftList in the file
      # A file with multiple ChemicalShiftLists MUST have explicit chemical shift lists
      # given for all spectra- but this is not the place for validity checking
      self.defaultChemicalShiftList = shiftList

    # Read shifts loop
    loop = saveFrame.get('nef_chemical_shift') or []
    for row in loop.data:
      name = row['atom_name']
      element = row.get('element')
      isotopeNumber = row.get('isotope_number')

      if not element:
        element = commonUtil.name2ElementSymbol(name)
      if element:
        if isotopeNumber:
          isotopeCode = '%s%s%s' % (isotopeNumber, element[0].upper(), element[1:].lower())
        else:
          isotopeCode = genConstants.DEFAULT_ISOTOPE_DICT.get(element.upper())
      else:
        isotopeCode = None

      atomMap = self.fetchAtomMap(row['chain_code'], row['sequence_code'], name,
                                  isotopeCode=isotopeCode)
      for resonance in atomMap['resonances']:
        # There will be more than one resonance for e.g. Ser HB% or Leu HD%
        shiftList.newShift(resonance=resonance, value=row['value'],
                           error=row.get('value_uncertainty', 0),
                           figOfMerit=row.get('ccpn_figure_of_merit', 1),
                           details=row.get('ccpn_comment'))
    #
    return shiftList

  importers['nef_chemical_shift_list'] = load_nef_chemical_shift_list


  def load_nef_restraint_list(self, project, saveFrame):
    """Serves to load nef_distance_restraint_list, nef_dihedral_restraint_list,
     nef_rdc_restraint_list and ccpn_restraint_list"""

    category = saveFrame['sf_category']
    framecode = saveFrame['sf_framecode']

    defaultSerial = 1
    dataSetSerial = saveFrame.get('ccpn_dataset_serial', defaultSerial)
    nmrConstraintStore = project.findFirstNmrConstraintStore(serial=dataSetSerial)
    if nmrConstraintStore is None:
      nmrConstraintStore = project.newNmrConstraintStore(nmrProject=project.currentNmrProject)
      resetSerial(nmrConstraintStore, dataSetSerial)

    if category == 'nef_distance_restraint_list':
      itemLength = 2
      data = saveFrame.get('nef_distance_restraint').data
      if saveFrame.get('restraint_origin') == 'hbond':
        restraintType = 'HBond'
      else:
        restraintType = 'Distance'
    elif category == 'nef_rdc_restraint_list':
      itemLength = 2
      data = saveFrame.get('nef_rdc_restraint').data
      restraintType = 'Rdc'
    else:
      # For now we do not support any non-standard restraint lists.
      # We could do Csa, JCoupling, and ChemicalShift
      restraintType = saveFrame.get('restraint_type')
      if restraintType == 'JCoupling':
        itemLength = 2
      elif restraintType in ('Csa', 'ChemicalShift'):
        itemLength = 1
      else:
        # Other types are not recognised
        return None
      data = saveFrame.get('ccpn_restraint').data

    # Get name from framecode, add type disambiguation, and correct for ccpn dataSetSerial addition
    name = framecode[len(category) + 1:]
    comment = saveFrame.get('comment')
    newListFunc = getattr(nmrConstraintStore,"new%sConstraintList" % restraintType)
    restraintList = newListFunc(name=name, details=comment)
    newRestraintFunc = getattr(restraintList, "new%sConstraint" % restraintType)
    newItemFuncName =  "new%sConstraintItem" % restraintType

    restraints = {}
    # assignTags = ('chain_code', 'sequence_code', 'residue_name', 'atom_name')

    max = itemLength + 1
    multipleAttributes = OD((
      ('chainCodes', tuple('chain_code_%s' % ii for ii in range(1, max))),
      ('sequenceCodes', tuple('sequence_code_%s' % ii for ii in range(1, max))),
      ('residueTypes', tuple('residue_name_%s' % ii for ii in range(1, max))),
      ('atomNames', tuple('atom_name_%s' % ii for ii in range(1, max))),
    ))

    defaultChainCode = self.defaultChainCode
    for row in data:
      # get or make restraint
      serial = row.get('restraint_id')
      restraint = restraints.get(serial)
      if restraint is None:
        # First line in restraint
        restraintParams = {}
        val = row.get('weight')
        if val is not None:
          restraintParams['weight'] = val
        val = row.get('ccpn_comment')
        if val is not None:
          restraintParams['details'] = val
        val = row.get('target_value')
        if val is not None:
          restraintParams['targetValue'] = val
        val = row.get('target_value_uncertainty')
        if val is not None:
          restraintParams['error'] = val
        val = row.get('lower_limit')
        if val is not None:
          restraintParams['lowerLimit'] = val
        val = row.get('upper_limit')
        if val is not None:
          restraintParams['upperLimit'] = val
        if restraintType == 'Rdc':
          val = row.get('ccpn_vector_length')
          if val is not None:
            restraintParams['vectorLength'] = val
        if itemLength != 1:
          restraint = newRestraintFunc(**restraintParams)
          # Must be reset after the fact, as serials cannot be passed in normally
          resetSerial(restraint, serial)
          restraints[serial] = restraint
      elif itemLength == 1:
        raise RuntimeError("One-resonance restraint type %s, is %s has more than one item"
                           % (restraintType, serial))

      # Add item
      ll = [list(row.get(x) for x in y) for y in multipleAttributes.values()]
      fixedResonances = []
      for chainCode, sequenceCode, residueName, atomName in zip(*ll):
        chainCode = chainCode or defaultChainCode
        resonances = self.fetchAtomMap(chainCode, sequenceCode, atomName)['resonances']
        fixedResonances.append(
          tuple(ConstraintBasic.getFixedResonance(nmrConstraintStore,x) for x in resonances)
        )
      # NB the appended resonances may be of length 2 in case of ambiguous
      # resonances like Val HG%. Therefor we need to do the product.
      if itemLength == 1:
        # These have no items, and have a single resonance attribute linked to the restraint
        # They also can only ever have a single line per restraint
        # NB if we get here restraintParams are knoown to be set
        restraint = newRestraintFunc(resonance=fixedResonances[0][0], **restraintParams)
        # Must be reset after the fact, as serials cannot be passed in normally
        resetSerial(restraint, serial)
        restraints[serial] = restraint
      else:
        for tt in itertools.product(*fixedResonances):
          getattr(restraint, newItemFuncName)(resonances=tt)
    #
    return restraintList

  importers['nef_distance_restraint_list'] = load_nef_restraint_list
  importers['nef_rdc_restraint_list'] = load_nef_restraint_list
  importers['ccpn_restraint_list'] = load_nef_restraint_list

  def load_nef_dihedral_restraint_list(self, project, saveFrame):
    """Serves to load nef_distance_restraint_list, nef_dihedral_restraint_list,
     nef_rdc_restraint_list and ccpn_restraint_list"""

    category = saveFrame['sf_category']
    framecode = saveFrame['sf_framecode']

    # Get name from framecode, add type disambiguation, and correct for ccpn dataSetSerial addition
    name = framecode[len(category) + 1:]
    comment = saveFrame.get('comment')

    defaultSerial = 1
    dataSetSerial = saveFrame.get('ccpn_dataset_serial', defaultSerial)
    nmrConstraintStore = project.findFirstNmrConstraintStore(serial=dataSetSerial)
    if nmrConstraintStore is None:
      nmrConstraintStore = project.newNmrConstraintStore()
      resetSerial(nmrConstraintStore, dataSetSerial)

    restraintList = nmrConstraintStore.newDihedralConstraintList(name=name, details=comment)
    newRestraintFunc = restraintList.newDihedralConstraint
    newItemFuncName =  "newDihedralConstraintItem"
    itemLength = 4
    data = saveFrame.get('nef_dihedral_restraint').data

    restraints = {}

    max = itemLength + 1
    multipleAttributes = OD((
      ('chainCodes', tuple('chain_code_%s' % ii for ii in range(1, max))),
      ('sequenceCodes', tuple('sequence_code_%s' % ii for ii in range(1, max))),
      ('residueTypes', tuple('residue_name_%s' % ii for ii in range(1, max))),
      ('atomNames', tuple('atom_name_%s' % ii for ii in range(1, max))),
    ))

    defaultChainCode = self.defaultChainCode
    for row in data:

      # get or make restraint
      serial = row.get('restraint_id')
      restraint = restraints.get(serial)
      if restraint is None:
        # First line in restraint
        dd = {}
        val = row.get('weight')
        if val is not None:
          dd['weight'] = val
        val = row.get('ccpn_comment')
        if val is not None:
          dd['details'] = val

        # For dihedral restraints the resonance are on the restraint, not the item
        ll = [list(row.get(x) for x in y) for y in multipleAttributes.values()]
        fixedResonances = []
        for chainCode, sequenceCode, residueName, atomName in zip(*ll):
          chainCode = chainCode or defaultChainCode
          resonances = self.fetchAtomMap(chainCode, sequenceCode, atomName)['resonances']
          fixedResonances.append(
            tuple(ConstraintBasic.getFixedResonance(nmrConstraintStore,x) for x in resonances)
          )
        # NB We maek only one restraint, as we otehrwise mess up the restraint serials.
        # Anyway the risk of a diedral restraint involving an ambiguous atom set is minuscule.
        tt = list(itertools.product(*fixedResonances))[0]
        restraint = newRestraintFunc(resonances=tt, **dd)
        # Must be reset after the fact, as serials cannot be passed in normally
        resetSerial(restraint, serial)
        restraints[serial] = restraint

      # Add item
      dd2 = {}
      val = row.get('target_value')
      if val is not None:
        dd2['targetValue'] = val
      val = row.get('target_value_uncertainty')
      if val is not None:
        dd2['error'] = val
      val = row.get('lower_limit')
      if val is not None:
        dd2['lowerLimit'] = val
      val = row.get('upper_limit')
      if val is not None:
        dd2['upperLimit'] = val
      restraint.newDihedralConstraintItem(**dd2)
    #
    return restraintList

  importers['nef_dihedral_restraint_list'] = load_nef_dihedral_restraint_list

  # # Default parameters - 10Hz/pt, 0.1ppm/point for 1H; 10 Hz/pt, 1ppm/pt for 13C
  # # NB this is in order to give simple numbers. it does NOT match the gyromagnetic ratios
  # DEFAULT_SPECTRUM_PARAMETERS = {
  #   '1H':{'numPoints':128, 'sf':100., 'sw':1280, 'refppm':11.8, 'refpt':1, },
  #   '2H':{'numPoints':128, 'sf':100., 'sw':1280, 'refppm':11.8, 'refpt':1, },
  #   '3H':{'numPoints':128, 'sf':100., 'sw':1280, 'refppm':11.8, 'refpt':1, },
  #   '13C':{'numPoints':256, 'sf':10., 'sw':2560, 'refppm':236., 'refpt':1, }
  # }

  # def createSpectrum(project:Project, spectrumName:str, spectrumParameters:dict,
  #                          dimensionData:dict, transferData:Sequence[Tuple] = None):
  # """Get or create spectrum using dictionaries of attributes, such as read in from NEF.
  #
  # :param spectrumParameters keyword-value dictionary of attribute to set on resulting spectrum
  #
  # :params Dictionary of keyword:list parameters, with per-dimension parameters.
  # Either 'axisCodes' or 'isotopeCodes' must be present and fully populated.
  # A number of other dimensionData are
  # treated specially (see below)
  # """
  #
  # spectrum = project.getSpectrum(spectrumName)
  # if spectrum is None:
  #   # Spectrum did not already exist
  #
  #   dimTags = list(dimensionData.keys())
  #
  #   # First try to load it - we override the loaded attribute values below
  #   # but loading gives a more complete parameter set.
  #   spectrum = None
  #   filePath = spectrumParameters.get('filePath')
  #   if filePath and os.path.exists(filePath):
  #     try:
  #       dataType, subType, usePath = ioFormats.analyseUrl(path)
  #       if dataType == 'Spectrum':
  #         spectra = project.loadSpectrum(usePath, subType)
  #         if spectra:
  #           spectrum = spectra[0]
  #     except:
  #       # Deliberate - any error should be skipped
  #       pass
  #     if spectrum is None:
  #       project._logger.warning("Failed to load spectrum from spectrum path %s" % filePath)
  #     elif 'axisCodes' in dimensionData:
  #       # set axisCodes
  #       spectrum.axisCodes = dimensionData['axisCodes']
  #
  #   acquisitionAxisIndex = None
  #   if 'is_acquisition' in dimensionData:
  #     dimTags.remove('is_acquisition')
  #     values = dimensionData['is_acquisition']
  #     if values.count(True) == 1:
  #       acquisitionAxisIndex = values.index(True)
  #
  #   if spectrum is None:
  #     # Spectrum could not be loaded - now create a dummy spectrum
  #
  #     if 'axisCodes' in dimTags:
  #       # We have the axisCodes, from ccpn
  #       dimTags.remove('axisCodes')
  #       axisCodes = dimensionData['axisCodes']
  #
  #     else:
  #       if transferData is None:
  #         raise ValueError("Function needs either axisCodes or transferData")
  #
  #       dimensionIds = dimensionData['dimension_id']
  #
  #       # axisCodes were not set - produce a serviceable set
  #       axisCodes = makeNefAxisCodes(isotopeCodes=dimensionData['isotopeCodes'],
  #                                    dimensionIds=dimensionIds,
  #                                    acquisitionAxisIndex=acquisitionAxisIndex,
  #                                    transferData=transferData)
  #
  #     # make new spectrum with default parameters
  #     spectrum = project.createDummySpectrum(axisCodes, spectrumName,
  #                                            chemicalShiftList=spectrumParameters.get(
  #                                              'chemicalShiftList')
  #                                            )
  #     if acquisitionAxisIndex is not None:
  #       spectrum.acquisitionAxisCode = axisCodes[acquisitionAxisIndex]
  #
  #     # Delete autocreated peaklist  and reset - we want any read-in peakList to be the first
  #     # If necessary an empty PeakList is added downstream
  #     spectrum.peakLists[0].delete()
  #     spectrum._wrappedData.__dict__['_serialDict']['peakLists'] = 0
  #
  #   # (Re)set all spectrum attributes
  #
  #   # First per-dimension ones
  #   dimTags.remove('dimension_id')
  #   if 'absolute_peak_positions' in dimensionData:
  #     # NB We are not using these. What could we do with them?
  #     dimTags.remove('absolute_peak_positions')
  #   if 'folding' in dimensionData:
  #     dimTags.remove('folding')
  #     values = [None if x == 'none' else x for x in dimensionData['folding']]
  #     spectrum.foldingModes = values
  #   if 'pointCounts' in dimensionData:
  #     dimTags.remove('pointCounts')
  #     spectrum.pointCounts = pointCounts = dimensionData['pointCounts']
  #     if 'totalPointCounts' in dimensionData:
  #       dimTags.remove('totalPointCounts')
  #       spectrum.totalPointCounts = dimensionData['totalPointCounts']
  #     else:
  #       spectrum.totalPointCounts = pointCounts
  #   # Needed below:
  #   if 'value_first_point' in dimensionData:
  #     dimTags.remove('value_first_point')
  #   if 'referencePoints' in dimensionData:
  #     dimTags.remove('referencePoints')
  #   # value_first_point = dimensionData.get('value_first_point')
  #   # if value_first_point is not None:
  #   #   dimensionData.pop('value_first_point')
  #   # referencePoints = dimensionData.get('referencePoints')
  #   # if referencePoints is not None:
  #   #   dimensionData.pop('referencePoints')
  #
  #   # Remaining per-dimension values match the spectrum. Set them.
  #   # NB we use the old (default) values where the new value is None
  #   # - some attributes like spectralWidths do not accept None.
  #   if 'spectrometerFrequencies' in dimTags:
  #     # spectrometerFrequencies MUST be set before spectralWidths,
  #     # as the spectralWidths are otherwise modified
  #     dimTags.remove('spectrometerFrequencies')
  #     dimTags.insert(0, 'spectrometerFrequencies')
  #   for tag in dimTags:
  #     vals = dimensionData[tag]
  #     # Use old values where new ones are None
  #     oldVals = getattr(spectrum, tag)
  #     vals = [x if x is not None else oldVals[ii] for ii, x in enumerate(vals)]
  #     setattr(spectrum, tag, vals)
  #
  #   # Set referencing.
  #   value_first_point = dimensionData.get('value_first_point')
  #   referencePoints = dimensionData.get('referencePoints')
  #   if value_first_point is None:
  #     # If reading NEF we must get value_first_point,
  #     #  but in other uses we might be getting referencePoints, referenceValues directly
  #     referenceValues = dimensionData.get('referenceValues')
  #     if referenceValues and referencePoints:
  #       spectrum.referencePoints = referencePoints
  #       spectrum.referenceValues = referenceValues
  #   else:
  #     if referencePoints is None:
  #       # not CCPN data
  #       referenceValues = spectrum.referenceValues
  #       for ii, val in enumerate(value_first_point):
  #         if val is None:
  #           value_first_point[ii] = referenceValues[ii]
  #       spectrum.referenceValues = value_first_point
  #       spectrum.referencePoints = [1] * len(referenceValues)
  #     else:
  #       points = list(spectrum.referencePoints)
  #       values = list(spectrum.referenceValues)
  #       sw = spectrum.spectralWidths
  #       pointCounts = spectrum.pointCounts
  #       for ii, refVal in enumerate(value_first_point):
  #         refPoint = referencePoints[ii]
  #         if refVal is not None and refPoint is not None:
  #           # if we are here refPoint should never be None, but OK, ...
  #           # Set reference to use refPoint
  #           points[ii] = refPoint
  #           refVal -= ((refPoint - 1) * sw[ii] / pointCounts[ii])
  #           values[ii] = refVal
  #       spectrum.referencePoints = points
  #       spectrum.referenceValues = values
  #
  #   # Then spectrum-level ones
  #   for tag, val in spectrumParameters.items():
  #     if tag != 'dimensionCount':
  #       # dimensionCount is handled already and not settable
  #       setattr(spectrum, tag, val)
  #   #
  #   return spectrum
  #
  # else:
  #   raise ValueError("Spectrum named %s already exists" % spectrumName)


  def load_nef_nmr_spectrum(self, memopsRoot, saveFrame):

    nmrProject = memopsRoot.currentNmrProject

    # Get ccpn-to-nef mappping for saveframe
    category = saveFrame['sf_category']
    framecode = saveFrame['sf_framecode']

    experimentMapping = OD((
      ('num_dimensions','numDim'),
      # ('chemical_shift_list',None),
      # ('experiment_classification','experiment.type'),
      ('experiment_type','name'),
      ('ccpn_spinning_rate','spinningRate'),
      # ('ccpn_sample', None),
    ))
    experimentParams = {}
    for key,tag in experimentMapping.items():
      val = saveFrame.get(key)
      if val is not None:
        experimentParams[tag] = val

    dataSourceMapping = OD((
      ('ccpn_spectrum_scale','scale'),
      ('ccpn_spectrum_comment','details'),
    ))
    dataSourceParams = {'numDim':experimentParams['numDim'], 'dataType':'processed'}
    for key,tag in dataSourceMapping.items():
      val = saveFrame.get(key)
      if val is not None:
        dataSourceParams[tag] = val

    dataStoreMapping = OD((
      # ('ccpn_spectrum_file_path', 'filePath'),
      ('ccpn_file_header_size', 'headerSize'),
      ('ccpn_file_number_type', 'numberType'),
      ('ccpn_file_complex_stored_by', 'complexStoredBy'),
      ('ccpn_file_scale_factor', 'scaleFactor'),
      ('ccpn_file_is_big_endian', 'isBigEndian'),
      ('ccpn_file_byte_number', 'nByte'),
      ('ccpn_file_has_block_padding', 'hasBlockPadding'),
      ('ccpn_file_block_header_size', 'blockHeaderSize'),
      ('ccpn_file_type', 'fileType'),
    ))
    dataStoreParams = {}
    for key,tag in dataStoreMapping.items():
      val = saveFrame.get(key)
      if val is not None:
        dataStoreParams[tag] = val
    peakListMapping = OD((
      ('ccpn_peaklist_serial','serial'),
      ('ccpn_peaklist_comment','details'),
      ('ccpn_peaklist_name','name'),
      ('ccpn_peaklist_is_simulated','isSimulated'),
    ))
    peakListParams = {}
    for key,tag in peakListMapping.items():
      val = saveFrame.get(key)
      if val is not None:
        peakListParams[tag] = val


    # Get name from spectrum parameters, or from the framecode
    spectrumName = framecode[len(category) + 1:]
    if spectrumName.endswith('`'):
      peakListSerial = peakListParams.get('serial')
      if peakListSerial:
        ss = '`%s`' % peakListSerial
        # Remove peakList serial suffix (which was added for disambiguation)
        # So that multiple peakLists all go to one Spectrum
        if spectrumName.endswith(ss):
          spectrumName = spectrumName[:-len(ss)]
      else:
        ll = spectrumName.rsplit('`',2)
        if len(ll) == 3:
          # name is of form abc`xyz`
          try:
            peakListParams['serial'] = int(ll[1])
          except ValueError:
            pass
          else:
            spectrumName = ll[0]
    dataSourceParams['name'] = spectrumName

    for experiment in nmrProject.sortedExperiments():
      dataSource = experiment.findFirstDataSource(name=spectrumName)
      if dataSource is not None:
        break
    else:
      dataSource = None
    if dataSource is None:
      # Spectrum does not already exist - create it.
      # NB For CCPN-exported projects spectra with multiple peakLists are handled this way

      framecode = saveFrame.get('chemical_shift_list')
      if framecode:
        experimentParams['shiftList'] = self.frameCode2Object[framecode]
      else:
        # Defaults to first (there should be only one, but we want the read to work) ShiftList
        experimentParams['shiftList'] = self.defaultChemicalShiftList

      refExperimentName = saveFrame.get('experiment_classification')
      if refExperimentName is not None:
        for expPrototype in memopsRoot.sortedNmrExpPrototypes():
          refExperiment = expPrototype.findFirstRefExperiment(name=refExperimentName)
          if refExperiment is not None:
            break
        else:
          refExperiment = None
        if refExperiment is None:
          # Should not happen. But at least we are preserving the information
          experimentParams['userExpCode'] = refExperimentName
        else:
          experimentParams['refExperiment'] = refExperiment

      # framecode = saveFrame.get('ccpn_sample')
      # if framecode:
      #   experimentParams['sample'] = self.frameCode2Object[framecode]

      nmrExperiment = nmrProject.newExperiment(**experimentParams)
      dataSource = nmrExperiment.newDataSource(**dataSourceParams)

      expDimRefParams = {}
      dataDimParams = {}
      dataDimRefParams = {}
      axisCodesRead = False
      acquisitionDim = None
      for row in saveFrame['nef_spectrum_dimension'].data:
        dim = row['dimension_id']

        if row.get('is_acquisition'):
          nmrExperiment.findFirstExpDim(dim=dim).isAcquisition = True
          acquisitionDim = dim

        dd = expDimRefParams[dim] = {}
        val = isotopeCode = row.get('axis_code')
        if val:
          dd['isotopeCodes'] = (isotopeCode,)
        val = row.get('spectrometer_frequency')
        if val:
          dd['sf'] = val
        val = row.get('axis_unit')
        if val:
          dd['unit'] = val
        val = row.get('ccpn_axis_code')
        if val:
          dd['name'] = val
          dd['displayName'] = val
          axisCodesRead = True
        dd['isFolded'] = (row.get('folding') == 'mirror')

        dd = dataDimParams[dim] = {}
        val = row.get('spectral_width')
        if val:
          dd['spectralWidth'] = val

        dd = dataDimRefParams[dim] = {}
        val = row.get('value_first_point')
        dd['refPoint'] = 1
        if val:
          dd['refValue'] = val

      loop = saveFrame.get('ccpn_spectrum_dimension')
      referencePointDict = {}
      isComplexDict = {}
      blockSizesDict = {}
      if loop:
        for row in loop.data:
          dim = row['dimension_id']

          val = row.get('dimension_is_complex')
          if val is not None:
            isComplexDict[dim] = val
          val = row.get('dimension_block_size')
          if val:
            blockSizesDict[dim] = val
          val = row.get('reference_point')
          if val:
            referencePointDict[dim] = val

          dd = expDimRefParams[dim]
          val = row.get('lower_aliasing_limit')
          if val is not None:
            dd['minAliasedFreq'] = val
          val = row.get('upper_aliasing_limit')
          if val is not None:
            dd['maxAliasedFreq'] = val
          val = row.get('measurement_type')
          if val:
            dd['measurementType'] = val

          dd = dataDimParams[dim]
          val = row.get('point_count')
          if val:
            dd['numPoints'] = val
          val = row.get('total_point_count')
          if val:
            dd['numPointsOrig'] = val
          else:
            dd['numPointsOrig'] = dd['numPoints']
          val = row.get('point_offset')
          if val is not None:
            dd['pointOffset'] = val
          val = row.get('phase_0')
          if val is not None:
            dd['phase0'] = val
          val = row.get('phase_1')
          if val is not None:
            dd['phase1'] = val

        if isComplexDict:
          ll = list(isComplexDict.items())
          ll.sort()
          dataStoreParams['isComplex'] = [tt[1] for tt in ll]
        if blockSizesDict:
          ll = list(blockSizesDict.items())
          ll.sort()
          dataStoreParams['blockSizes'] = [tt[1] for tt in ll]

      # Make Per-dimension objects
      for expDim in nmrExperiment.sortedExpDims():
        dim = expDim.dim
        params = expDimRefParams[dim]

        # Set default parameters - not consistent but you need something:
        isotopeCodes =  params.get('isotopeCodes')
        if isotopeCodes:
          isotopeCode = isotopeCodes[0]
        else:
          isotopeCode = '1H'
          params['isotopeCodes'] = (isotopeCode,)
        sf = params.get('sf')
        if not sf:
          if isotopeCode == '1H':
            params['sf'] = sf = 100.
          else:
            params['sf'] = sf = 10.
        #
        expDim.newExpDimRef(**params)

        # Make DataDims and DataDimRefs
        params = dataDimParams[dim]
        numPoints = params.get('numPoints')
        if not numPoints:
          if isotopeCode == '1H':
            numPoints = params['numPoints'] = 1280
          else:
            numPoints = params['numPoints'] = 2560
        params['numPointsOrig'] =  params['numPoints']
        if params.get('spectralWidth'):
          spectralWidth = params.pop('spectralWidth')
          params['valuePerPoint'] = spectralWidth * sf / numPoints
        else:
          # 10 z per point, arbitrarily
          params['valuePerPoint'] = 10.

        dataDim = dataSource.newFreqDataDim(dim=dim, expDim=nmrExperiment.findFirstExpDim(dim=dim),
                                            isComplex=isComplexDict.get(dim, False), **params)

        expDimRef = nmrExperiment.findFirstExpDim(dim=dim).findFirstExpDimRef()
        dataDim.newDataDimRef(expDimRef=expDimRef, **dataDimRefParams[dim])

      # Reset referencing to use referencePoint
      for dim, refPoint in referencePointDict.items():
        dataDimRef = dataSource.findFirstDataDim(dim=dim).findFirstDataDimRef()
        refValue = dataDimRef.pointToValue(refPoint)
        dataDimRef.refPoint = refPoint
        dataDimRef.refValue = refValue

      # read dimension transfer data
      transferData = []
      loop = saveFrame.get('nef_spectrum_dimension_transfer')
      if loop:
        for row in loop.data:
          dims = [row.get(x) for x in ('dimension_1','dimension_2')]
          xdr = [nmrExperiment.findFirstExpDim(dim=dim).findFirstExpDimRef() for dim in dims]
          transferType = row.get('transfer_type')
          isDirect = not row.get('is_indirect')
          nmrExperiment.newExpTransfer(expDimRefs=xdr, transferType=transferType,
                                       isDirect=isDirect)
          transferData.append(dims + [transferType, not isDirect])

      # Make data storage object
      filePath = saveFrame.get('ccpn_spectrum_file_path')
      if filePath:
        # create dataLocationStore
        dataLocationStore = memopsRoot.findFirstDataLocationStore()
        if not dataLocationStore:
          dataLocationStore = memopsRoot.newDataLocationStore(name='default')
          addDataStore(dataSource, filePath,
                       numPoints= [x.numPoints for x in dataSource.sortedDataDims()],
                                  **dataStoreParams)
        # dataSource.dataStore = dataLocationStore.newBlockedBinaryMatrix(
        #   path=filePath, numPoints= [x.numPoints for x in dataSource.sortedDataDims()],
        #   **dataStoreParams
        # )

      # Set refExpDimRef links
      if refExperiment is not None:

        if axisCodesRead:
          # We have ccpn axis codes read - use them to set up refExpDim links
          for refExpDim in refExperiment.sortedRefExpDims():
            for refExpDimRef in refExpDim.sortedRefExpDimRefs():
              name =self.refExpDimRefCodeMap[refExpDimRef]
              for expDim in nmrExperiment.sortedExpDims():
                expDimRef = expDim.findFirstExpDimRef(name=name)
                if expDimRef is not None:
                  expDimRef.refExpDimRef = refExpDimRef
        else:
          # we need to do a heuristic match
          expDims = nmrExperiment.sortedExpDims()
          expDimRefs = [x.findFirstExpDimRef() for x in expDims]
          if None not in expDimRefs:
            isotopeCodes = [x.isotopeCodes[0] if  x.isotopeCodes else 'unknown'
                            for x in expDimRefs]
            dimensionIds = [x.dim for x in expDims]
            acquisitionAxisIndex = (None if acquisitionDim is None
                                    else dimensionIds.index(acquisitionDim))

            axisCodes = makeNefAxisCodes(isotopeCodes, dimensionIds, acquisitionAxisIndex,
                                         transferData)

            refExpDimRefNames = self.matchRefExpDimRefNames(refExperiment, axisCodes)
            if refExpDimRefNames:
              for ii,expDimRef in enumerate(expDimRefs):
                expDimRef.name = refExpDimRefNames[ii]
            axisCodesRead = True
        if not axisCodesRead:
          # try setting dimension links with heuristics
          ExperimentBasic.setRefExperiment(nmrExperiment, refExperiment)

    # Make PeakList
    if 'serial' in peakListParams:
      serial = peakListParams.pop('serial')
    else:
      serial = None
    peakList = dataSource.newPeakList(**peakListParams)
    if serial is not None:
      resetSerial(peakList, serial)

    # Load peaks
    self.load_nef_peak(peakList, saveFrame.get('nef_peak'))
    #
    return peakList
  #
  importers['nef_nmr_spectrum'] = load_nef_nmr_spectrum


  def load_nef_peak(self, peakList, loop):
    """Serves to load nef_peak loop"""

    dimensionCount = peakList.dataSource.numDim
    # Get name map for per-dimension attributes
    max = dimensionCount + 1
    multipleAttributes = {
      'position':tuple('position_%s' % ii for ii in range(1, max)),
      'positionError':tuple('position_uncertainty_%s' % ii for ii in range(1, max)),
      'chainCodes':tuple('chain_code_%s' % ii for ii in range(1, max)),
      'sequenceCodes':tuple('sequence_code_%s' % ii for ii in range(1, max)),
      'residueTypes':tuple('residue_name_%s' % ii for ii in range(1, max)),
      'atomNames':tuple('atom_name_%s' % ii for ii in range(1, max)),
    }


    result = []
    peaks = {}
    assignedResonances = []

    dataDimRefMap = {}
    for dataDim in peakList.dataSource.dataDims:
      # Add dataDimRef link
      dataDimRefMap[dataDim.dim] = dataDim.findFirstDataDimRef()

    for row in loop.data:

      serial = row['peak_id']
      parameters = {}
      parameters['volume'] = row.get('volume')
      parameters['height'] = row.get('height')
      parameters['annotation'] = row.get('ccpn_annotation')
      parameters['details'] = row.get('ccpn_comment')#
      val = row.get('ccpn_figure_of_merit')
      if val is not None:
        parameters['figOfMerit'] = val

      # get or make peak
      peak = peaks.get(serial)

      # For now we simply use the first row that appears - V2 cannot handle different rows anyway
      if peak is None:
        # start of a new peak

        # finalise previous peak
        if result and assignedResonances:
          # There is a peak in result, and the peak has assignments to set
          assignPeak(result[-1], assignedResonances)
          del assignedResonances[:]

        # Make new peak
        peak = peakList.newPeak(**parameters)
        resetSerial(peak, serial)
        peaks[serial] = peak
        result.append(peak)

        # Add dimension attributes
        values = tuple(row.get(x) for x in multipleAttributes['position'])
        errors = tuple(row.get(x) for x in multipleAttributes['positionError'])
        for ii,peakDim in enumerate(peak.sortedPeakDims()):
          peakDim.value = values[ii]
          peakDim.valueError = errors[ii]
          # add dataDimRef
          peakDim.dataDimRef = dataDimRefMap.get(peakDim.dim)

      # Add assignment
      chainCodes = tuple(row.get(x) for x in multipleAttributes['chainCodes'])
      sequenceCodes = tuple(row.get(x) for x in multipleAttributes['sequenceCodes'])
      residueTypes = tuple(row.get(x) for x in multipleAttributes['residueTypes'])
      atomNames = tuple(row.get(x) for x in multipleAttributes['atomNames'])
      assignments = zip(chainCodes, sequenceCodes, residueTypes, atomNames)
      resonancesPerDimension = []
      foundAssignment = False
      for tt in assignments:
        if all(x is None for x in tt):
          # No assignment
          resonancesPerDimension.append(())
        elif tt[1] and tt[3]:
          # Enough for an assignment - make it
          foundAssignment = True
          # Necessary to first create ResonanceGroup, if it does not exist:
          dummy = self.fetchResidueMap(tt[0] or self.defaultChainCode, tt[1], tt[2])
          atomMap = self.fetchAtomMap(tt[0] or self.defaultChainCode, tt[1], tt[3])
          resonancesPerDimension.append(tuple(atomMap['resonances']))
        else:
          # partial and unusable assignment
          self.warning("Uninterpretable Peak assignment for peak %s: %s. Set to None"
                       % (peak.serial, tt))
          resonancesPerDimension.append(())
      if foundAssignment:
        # resonanceTuples = itertools.product(*nmrAtoms)
        assignedResonances.append(resonancesPerDimension)

    # finalise last peak
    if result and assignedResonances:
      # There is a peak in result, and the peak has assignments to set
      assignPeak(peak, assignedResonances)
      del assignedResonances[:]
    #
    return result
  #
  importers['nef_peak'] = load_nef_peak

  def load_nef_peak_restraint_links(self, project, saveFrame):
    """load nef_peak_restraint_links saveFrame"""

    links = {}

    loop = saveFrame.get('nef_peak_restraint_link', ())
    for row in loop.data:
      peakList = self.frameCode2Object.get(row.get('nmr_spectrum_id'))
      if peakList is None:
        self.warning(
          "No Spectrum saveframe found with framecode %s. Skipping peak_restraint_link"
          % row.get('nmr_spectrum_id')
        )
        continue
      restraintList = self.frameCode2Object.get(row.get('restraint_list_id'))
      if restraintList is None:
        self.warning(
          "No RestraintList saveframe found with framecode %s. Skipping peak_restraint_link"
          % row.get('restraint_list_id')
        )
        continue
      peak = peakList.findFirstPeak(serial=row.get('peak_id'))
      if peak is None:
        self.warning(
          "No peak %s found in %s Skipping peak_restraint_link"
          % (row.get('peak_id'), row.get('nmr_spectrum_id'))
        )
        continue
      restraint = restraintList.findFirstConstraint(serial=row.get('restraint_id'))
      if restraint is None:
        self.warning(
          "No restraint %s found in %s Skipping peak_restraint_link"
          % (row.get('restraint_id'), row.get('restraint_list_id'))
        )
        continue

      # Is all worked, now accumulate the links
      ll = links.get(restraint, [])
      ll.append(peak)
      links[restraint] = ll

    # Set the actual links
    for restraint, peaks in links.items():
      restraint.peaks = peaks
    #
    return project
  #
  importers['nef_peak_restraint_links'] = load_nef_peak_restraint_links

  # # NBNB TODO? Sample and Substance could potentially be incorporated
  # # in the reading. Left for later, maybe.
  # def load_ccpn_sample(self, project, saveFrame):
  #
  #   # Not updated. Invalid
  #   raise NotImplementedError()
  #
  #   # NBNB TODO add crosslinks to spectrum (also for components)
  #
  #   # Get ccpn-to-nef mappping for saveframe
  #   category = saveFrame['sf_category']
  #   framecode = saveFrame['sf_framecode']
  #   mapping = nef2CcpnMap[category]
  #
  #   parameters, loopNames = self._parametersFromSaveFrame(saveFrame, mapping)
  #
  #   # Make main object
  #   result = project.newSample(**parameters)
  #
  #   # Load loops, with object as parent
  #   for loopName in loopNames:
  #     loop = saveFrame.get(loopName)
  #     if loop:
  #       importer = self.importers[loopName]
  #       importer(self, result, loop)
  #   #
  #   return result
  # #
  # importers['ccpn_sample'] = load_ccpn_sample
  #
  #
  # def load_ccpn_sample_component(self, parent, loop):
  #   """load ccpn_sample_component loop"""
  #
  #   # Not updated. Invalid
  #   raise NotImplementedError()
  #
  #   result = []
  #
  #   creatorFunc = parent.newSampleComponent
  #
  #   mapping = nef2CcpnMap[loop.name]
  #   map2 = dict(item for item in mapping.items() if item[1] and '.' not in item[1])
  #   for row in loop.data:
  #     parameters = self._parametersFromLoopRow(row, map2)
  #     result.append(creatorFunc(**parameters))
  #   #
  #   return result
  # #
  # importers['ccpn_sample_component'] = load_ccpn_sample_component
  #
  #
  # def load_ccpn_substance(self, project, saveFrame):
  #
  #   # Not updated. Invalid
  #   raise NotImplementedError()
  #
  #   # Get ccpn-to-nef mappping for saveframe
  #   category = saveFrame['sf_category']
  #   framecode = saveFrame['sf_framecode']
  #   mapping = nef2CcpnMap[category]
  #   parameters, loopNames = self._parametersFromSaveFrame(saveFrame, mapping)
  #
  #   name = parameters.pop('name')
  #   if 'labelling' in parameters:
  #     labelling = parameters.pop('labelling')
  #   else:
  #     labelling = None
  #   previous = [x for x in project.substances if x.name == name]
  #   sequence = saveFrame.get('sequence_string')
  #   if sequence and not previous:
  #     # We have a 'Molecule' type substance with a sequence and no previous occurrence
  #     # Create it as new polymer
  #     if ',' in sequence:
  #       sequence = list(sequence.split(','))
  #     params = {'molType':saveFrame.get('mol_type')}
  #     startNumber = saveFrame.get('start_number')
  #     if startNumber is not None:
  #       params['startNumber'] = startNumber
  #     isCyclic = saveFrame.get('is_cyclic')
  #     if isCyclic is not None:
  #       params['isCyclic'] = isCyclic
  #     #
  #     result = project.createPolymerSubstance(sequence, name, labelling, **params)
  #
  #   else:
  #     # find or create substance
  #     # NB substance could legitimately be existing already, since substances are created
  #     # when a chain is created.
  #     result = project.fetchSubstance(name, labelling)
  #     if previous:
  #       # In case this is a new Substance, (known name, different labelling)
  #       # set the sequenceString, if any, to the same as previous
  #       sequenceString = previous[0].sequenceString
  #       if sequenceString is not None:
  #         result._wrappedData.seqString = sequenceString
  #
  #   # Whether substance was pre-existing or not
  #   # overwrite the missing substance-specific parameters
  #   for tag, val in parameters.items():
  #     setattr(result, tag, val)
  #
  #   # Load loops, with object as parent
  #   for loopName in loopNames:
  #     loop = saveFrame.get(loopName)
  #     if loop:
  #       importer = self.importers[loopName]
  #       importer(self, result, loop)
  # #
  # importers['ccpn_substance'] = load_ccpn_substance
  #
  # def load_ccpn_substance_synonym(self, parent, loop):
  #   """load ccpn_substance_synonym loop"""
  #
  #   # Not updated. Invalid
  #   raise NotImplementedError()
  #
  #   result = [row['synonym'] for row in loop.data]
  #   parent.synonyms = result
  #   #
  #   return result
  # #
  # importers['ccpn_substance_synonym'] = load_ccpn_substance_synonym

  def fetchAtomMap(self, chainCode, sequenceCode, name, isotopeCode=None, comment=None):


    # TODO HACK: names like HBX, HBY should not really be supported, but temporarily...
    # There is test data with upper case instead of the correct (HBx, HBy),
    # and for now we want that to pass
    modifyNameEndings = {'X':'x', 'Y':'y', 'X%':'x%', 'Y%':'y%'}
    if name:
      for tag, val in modifyNameEndings.items():
        if name.endswith(tag):
          name = name[:-len(tag)] + val
          break
    else:
      raise ValueError("AtomName must be given")

    # First do non-offset residues, to make sure main residue maps are ready
    if isotopeCode is None:
      isotopeCode = commonUtil.name2IsotopeCode(name) or 'unknown'
    residueMap = self.fetchResidueMap(chainCode, sequenceCode)
    atomMappings = residueMap['atomMappings']
    atomMap = atomMappings.get(name)

    if atomMap is None:
      # we have no preceding map. Make one, but we clearly can have only simple atoms,
      # with no atomSets or provision for prochirals etc.
      fixedName = name.replace('%','*')  # convert pseudoatom marker
      fixedName = fixedName.replace('@', '__') # necessary as names like H@123 are reserved
      atomMap = atomMappings[name] = {'name':fixedName, 'mappingType':'simple',
                                      'atomSets':[],}
      atomMap['elementSymbol'] = commonUtil.isotopeCode2Nucleus(isotopeCode)

    if atomMap.get('resonances') is None:
      # Make resonance
      resonanceGroup = residueMap['resonanceGroup']
      resonance = self.memopsRoot.currentNmrProject.newResonance(name=atomMap['name'],
                                                                 isotopeCode=isotopeCode,
                                                                 resonanceGroup=resonanceGroup,
                                                                 details=comment)
      atomMap['resonances'] = [resonance]

      atomSets = atomMap.get('atomSets')
      if atomSets:
        resonanceSet = AssignmentBasic.assignAtomsToRes(atomSets, resonance)
        asm = atomMap['atomSetMapping']
        # assert asm is not None  # This is set together with the atomSets
        if name[-1] == '%':
          if asm.mappingType == 'ambiguous':
            # This is e.g. Lys HG%, Val CG% or Ley HG% - we need two resonances here
            resonance2 = self.memopsRoot.currentNmrProject.newResonance(name=atomMap['name'],
                                                                        isotopeCode=isotopeCode,
                                                                        resonanceGroup=resonanceGroup,
                                                                        details=comment)
            atomMap['resonances'].append(resonance2)
            AssignmentBasic.assignAtomsToRes(atomSets, resonance2, resonanceSet)
            # AssignmentBasic.assignAtomsToRes(atomSets, resonance2)
      else:
        resonance.assignNames = [atomMap['name']]
    #
    return atomMap

  def fetchResidueMap(self, chainCode, sequenceCode, residueType=None, linkToMap=None):
    """Return _chainMapping entry (if necessary)"""
    nmrProject = self.memopsRoot.currentNmrProject

    chainMapping = self._chainMapping.get(chainCode)
    if chainMapping is None:
      chainMapping = self._chainMapping[chainCode] = OD()
    result = chainMapping.get(sequenceCode)
    if result is None:
      result = chainMapping[sequenceCode] = {'atomMappings':{}}

    if result.get('resonanceGroup') is None:
      if chainCode == '@-':
        # default chain
        name = sequenceCode
      else:
        name = '%s.%s' % (chainCode, sequenceCode)
      resonanceGroup = result['resonanceGroup'] = nmrProject.newResonanceGroup(name=name)
      residue = result.get('residue')
      if residue is None:
        # ResonanceGroup is unassigned
        tt = Constants.residueName2chemCompId.get(residueType)
        if tt is None:
          #residueType not recognised - put in as ccpCode without molType
          tt = (None, residueType)
        resonanceGroup.molType, resonanceGroup.ccpCode = tt
      else:
        # ResonanceGroup is assigned
        resonanceGroup.molType = residue.molType
        resonanceGroup.ccpCode = residue.ccpCode
        resonanceGroup.linking = residue.linking
        resonanceGroup.descriptor = residue.descriptor

      seqCode, seqInsertCode, offset = commonUtil.parseSequenceCode(sequenceCode)
      if offset is not None:
        # Offset residue - add to main residue
        mainResidueMap = self.fetchResidueMap(chainCode, '%s.%s' % (seqCode, seqInsertCode))
        mainResonanceGroup = mainResidueMap['resonanceGroup']
        if offset == 0:
          linkType = 'identity'
        else:
          linkType = 'sequential'
        mainResonanceGroup.newResonanceGroupProb(linkType=linkType, sequenceOffset=offset,
                                                 possibility=resonanceGroup)
      elif linkToMap is not None:
        # This is a residue in a continuous stretch - and linkToMap is the map for the i-1 residue
        previousResonanceGroup = linkToMap['resonanceGroup']
        previousResonanceGroup.newResonanceGroupProb(linkType='sequential', sequenceOffset=1,
                                                     possibility=resonanceGroup)

    #
    return result

  def load_ccpn_assignment(self, project, saveFrame):
    nmrChainTypes = {}
    for row in saveFrame['nmr_chain']:
      chainCode = row['chain_code']
      isConnected = row['is_connected']
      if chainCode in self._chainMapping:
        # NB This assumes that the chainMapping is set for MolSystem chains,
        # and not for any other chains
        nmrChainTypes[chainCode] = 'assigned'
      else:
        self._chainMapping[chainCode] = OD()
        if isConnected:
          nmrChainTypes[chainCode] = 'connected'
        elif chainCode == '@-':
          nmrChainTypes[chainCode] = 'default'
        else:
          nmrChainTypes[chainCode] = 'unassigned'

    offsetRows = []
    previousConnectedMaps = {}
    for row in saveFrame['nmr_residue']:
      # First do non-offset residues, to make sure main residue maps are ready
      chainCode = row['chain_code']
      sequenceCode = row['sequenceCode']
      seqCode, seqInsertCode, offset = commonUtil.parseSequenceCode(sequenceCode)
      if offset is None:
        chainType = nmrChainTypes[chainCode]
        if sequenceCode in nmrChainTypes[chainCode] and chainType != 'assigned':
          raise ValueError("Invalid data, chain_code %s, sequence_code %s appear twice"
                           % (chainCode, sequenceCode))
        if chainType == 'connected':
          linkToMap = previousConnectedMaps.get(chainCode)
        else:
          linkToMap = None
        newMap = self.fetchResidueMap(chainCode, sequenceCode, residueType=row['residue_name'],
                                      linkToMap=linkToMap)
        newMap['resonanceGroup'].details = row.get('comment')
        if chainType == 'connected':
          previousConnectedMaps[chainCode] = newMap
      else:
        offsetRows.append(row)

    for row in offsetRows:
      chainCode = row['chain_code']
      sequenceCode = row['sequenceCode']
      newMap = self.fetchResidueMap(chainCode, sequenceCode, row['residue_name'])
      newMap['resonanceGroup'].details = row.get('comment')

    for row in saveFrame['nmr_atom']:
      self.fetchAtomMap(row['chain_code'], row['sequenceCode'], row['name'],
                        isotopeCode=row['isotope_code'], comment=row.get('comment'))
  # #
  # importers['ccpn_assignment'] = load_ccpn_assignment




  def warning(self, message):
    template = "WARNING in saveFrame%s\n%s"
    self.warnings.append(template % (self.saveFrameName, message))

  def matchRefExpDimRefNames(self, refExperiment, axisCodes):
    """return the best set of RefExpDimRef.name matching axisCodes (in order)

    WARNING - this may give incorrect matchings for cases where
    there are several dimensions with the same nucleus and the axisCodes
    have been regenerated (from a native NEF file). E.g. HCcH will be vulnerable."""

    matchStrings = []
    for refExpDim in refExperiment.sortedRefExpDims():
      matchStrings.append(tuple(self.refExpDimRefCodeMap[x] for x in refExpDim.sortedRefExpDimRefs()))

    data = []
    for permutation in itertools.permutations(matchStrings):
      score = 0
      ll = []
      for ii,tt in enumerate(permutation):
        match = ''
        name = axisCodes[ii]
        for ss in tt:
          overlap = os.path.commonprefix((ss,name))
          if len(overlap) > len(match):
            match = ss
        if match:
          score += len(overlap)
          ll.append(match)
        else:
          break
      else:
        data.append((score, ll))

    if data:
      return sorted(data)[-1][1]
    else:
      return []


def makeNefAxisCodes(isotopeCodes, dimensionIds, acquisitionAxisIndex, transferData):
  """Returns axisCodes sorted in order of dimensionId.
  NB this will NOT be fully correct, as we are lacking information about
  transfers between unmeasured frequencies, as well as hte C/CA/CO ditinction.
  NB generated e.g. H_1 instead of H1, as per V2 convention."""

  nuclei = [commonUtil.splitIntFromChars(x)[1] for x in isotopeCodes]
  dimensionToNucleus = dict((zip(dimensionIds, nuclei)))
  dimensionToAxisCode = dimensionToNucleus.copy()

  oneBondConnections = {}
  for startNuc in 'FH':
    # look for onebond to F or H, the latter taking priority
    for dim1, dim2, transferType, isIndirect in transferData:
      if transferType == 'onebond':
        nuc1, nuc2 = dimensionToNucleus[dim1], dimensionToNucleus[dim2]
        if startNuc in (nuc1, nuc2):
          if startNuc == nuc1:
            oneBondConnections[dim1] = dim2
          else:
            oneBondConnections[dim2] = dim1
          dimensionToAxisCode[dim1] = nuc1 + nuc2.lower()
          dimensionToAxisCode[dim2] = nuc2 + nuc1.lower()

  resultMap = {}
  if acquisitionAxisIndex is not None:

    # Put acquisition axis first, to make sure it gets the lowest number
    # even if it is not the first to start with.
    acquisitionAxisId = dimensionIds[acquisitionAxisIndex]
    dimensionIds.remove(acquisitionAxisId)
    dimensionIds.insert(0, acquisitionAxisId)
  for dim in dimensionIds:
    axisCode = dimensionToAxisCode[dim]
    if axisCode in resultMap.values():
      ii = 0
      ss = axisCode
      while ss in resultMap.values():
        ii += 1
        ss = '%s%s' % (axisCode, ii)
      otherDim = oneBondConnections.get(dim)
      if otherDim is not None:
        # We are adding a suffix to e.g. Hc. Add the same suffix to equivalent Ch
        # NB this should only happen for certain 4D experiments.
        # NB not well tested, but better than leaving in a known error.
        ss = '%s%s' % (dimensionToAxisCode[otherDim], ii)
        if otherDim < dim:
          resultMap[otherDim] = ss
        dimensionToAxisCode[otherDim] = ss

    resultMap[dim] = axisCode

  if acquisitionAxisIndex is not None:
    # HACK (or heuristic). If the acquisition code is duplicated
    # (it might be if we do not have all necessary transfers)
    # This ensures that the duplicates get a suffix.
    # This should help with mapping e.g. 2D NOESY or HCcH
    acquisitoniAxisCode = resultMap[acquisitionAxisId]
    for dim, val in resultMap.items():
      if val == acquisitoniAxisCode and dim != acquisitionAxisId:
        resultMap[dim] = val + '1'

  dimensionIds.sort()
  result = list(resultMap[ii] for ii in dimensionIds)
  #
  return result


def createMoleculeFromNef(project, name, sequence, defaultType='UNK'):
  """Create a Molecule from a sequence of NEF row dictionaries (or equivalent)"""

  stretches = StarIo.splitNefSequence(sequence)
  molecule =  project.newMolecule(name=name)

  for stretch in stretches:

    # Try setting start number
    sequenceCode = stretch[0]['sequence_code']
    seqCode, seqInsertCode,offset = commonUtil.parseSequenceCode(sequenceCode)
    if seqCode is None:
      startNumber = 1
    else:
      startNumber = seqCode

    # Create new MolResidues
    residueTypes = [row.get('residue_name', defaultType) for row in stretch]
    firstLinking = stretch[0].get('linking')
    if len(residueTypes) > 1:
      lastLinking = stretch[-1].get('linking')
      if (firstLinking in ('start', 'single', 'nonlinear', 'dummy') or
          lastLinking == 'end'):
        isCyclic = False
      else:
        # We use isCyclic to set the ends to 'middle'. It gets sorted out below
        isCyclic = True

      molResidues = extendMolResidues(molecule, sequence=residueTypes, startNumber=startNumber,
                                                isCyclic=isCyclic)

      # Adjust linking and descriptor
      if isCyclic:
        if firstLinking != 'cyclic' or lastLinking != 'cyclic':
          # not cyclic after all - remove cyclising link
          cyclicLink = molResidues[-1].findFirstMolResLinkEnd(linkCode='next').molResLink
          cyclicLink.delete()
      else:
        if firstLinking != 'start':
          ff = molResidues[0].chemComp.findFirstChemCompVar
          chemCompVar = (ff(linking='middle', isDefaultVar=True) or ff(linking='middle'))
          molResidues[0].__dict__['linking'] = 'middle'
          molResidues[0].__dict__['descriptor'] = chemCompVar.descriptor
        if lastLinking != 'end':
          ff = molResidues[-1].chemComp.findFirstChemCompVar
          chemCompVar = (ff(linking='middle', isDefaultVar=True) or ff(linking='middle'))
          molResidues[-1].__dict__['linking'] = 'middle'
          molResidues[-1].__dict__['descriptor'] = chemCompVar.descriptor
    else:
      # Only one residue
      # residueType = residueTypes[0]
      # if residueType.startswith('dummy.'):
      #   tt = ('dummy',residueType[6:])
      # else:
      tt = Constants.residueName2chemCompId.get(residueTypes[0])
      if not tt:
        print("""Could not access ChemComp for %s - replacing with %s
NB - could be a failure in fetching remote information.
Are you off line?""" % (residueTypes[0], defaultType))
        tt = Constants.residueName2chemCompId.get(defaultType)
      if tt:
        chemComp = generalIo.getChemComp(project, tt[0], tt[1])
        if chemComp:
          chemCompVar  = (chemComp.findFirstChemCompVar(linking='none') or
                          chemComp.findFirstChemCompVar()) # just a default
          if chemCompVar:
            molecule.newMolResidue(seqCode=startNumber, chemComp=chemCompVar.chemComp,
                                   chemCompVar=chemCompVar)
          else:
            raise ValueError("No chemCompVar found for %s. Vars should be in  %s"
                             % (chemComp, chemComp.chemCOmpVars))

        else:
          raise ValueError("Residue type %s %s: Error in getting template information"
                           % (residueTypes[0], tt))

      else:
        raise ValueError("Residue type %s not recognised" % residueTypes[0])

    startNumber += len(residueTypes)
  #
  return molecule



def extendMolResidues(molecule, sequence, startNumber=1, isCyclic=False):
  """Descrn: Adds MolResidues for a sequence of residueNames to Molecule.
             Consecutive protein or DNA/RNA residues are connected, other residues remain unlinked

     Inputs: Ccp.Molecule.Molecule,
             List of Words (residueName),
             Int (first MolResidue.seqCode)
             bool (is molecule cyclic?)

     Output: List of new Ccp.Molecule.MolResidues
  """

  root = molecule.root

  if not sequence:
    return []

  # Reset startNumber to match pre-existing MolResidues
  oldMolResidues = molecule.molResidues
  if oldMolResidues:
    nn = max([x.seqCode for x in oldMolResidues]) + 1
    startNumber = max(startNumber, nn)

  # Convert to sequence of (molType, ccpCode) and check for known residueNames
  residueName2chemCompId = Constants.residueName2chemCompId
  seqInput = [residueName2chemCompId.get(x) for x in sequence]
  # seqInput = []
  # for x in sequence:
  #   if x.startswith('dummy.'):
  #     # Dummy residue, special handling
  #     seqInput.append(('dummy',x[6:]))
  #   else:
  #     seqInput.append(residueName2chemCompId.get(x))

  if None in seqInput:
    ii = seqInput.index(None)
    raise ValueError("Unknown residueName %s at position %s in sequence"
                     % (sequence[ii], ii))

  # Divide molecule in stretches by type, and add the residues one stretch at a time
  result = []

  offset1 = 0
  while offset1 < len(seqInput):
    molType1, ccpCode = seqInput[offset1]

    if molType1 in Constants.LINEAR_POLYMER_TYPES:
      # Linear polymer stretch - add to stretch
      offset2 = offset1 + 1
      while offset2 < len(seqInput):
        molType2 = seqInput[offset2][0]
        if (molType2 in Constants.LINEAR_POLYMER_TYPES
            and (molType1 == 'protein') == (molType2 == 'protein')):
          # Either both protein or both RNA/DNA
          offset2 += 1
        else:
          break

      if offset2 - offset1 > 1:
        result.extend(MoleculeModify.makeLinearSequence(molecule, seqInput[offset1:offset2],
                                                        seqCodeStart=startNumber+offset1,
                                                        isCyclic=isCyclic))
        offset1 = offset2
        # End of stretch. Skip rest of loop and go on to next residue
        continue

    # No linear polymer stretch was found. Deal with residue by itself
    # assert  molType1 not in LINEAR_POLYMER_TYPES or offset2 - offset1 == 1
    chemComp = generalIo.getChemComp(root, molType1, ccpCode)
    if chemComp:
      chemCompVar  = (chemComp.findFirstChemCompVar(linking='none') or
                      chemComp.findFirstChemCompVar()) # just a default

      result.append(molecule.newMolResidue(seqCode=startNumber+offset1, chemCompVar=chemCompVar))
      offset1 += 1

    else:
      raise ValueError('ChemComp %s,%s cannot be found.' % (molType1, ccpCode))

  #
  return result

def resetSerial(apiObject, newSerial):
  """ADVANCED Reset serial of object to newSerial, resetting parent link
  and the nextSerial of the parent.

  Raises ValueError for objects that do not have a serial
  (or, more precisely, where the _wrappedData does not have a serial)."""

  if not hasattr(apiObject, 'serial'):
    raise ValueError("Cannot reset serial, %s does not have a 'serial' attribute"
                     % apiObject)
  downlink = apiObject.__class__._metaclass.parentRole.otherRole.name

  parentDict = apiObject.parent.__dict__
  downdict = parentDict[downlink]
  oldSerial = apiObject.serial
  serialDict = parentDict['_serialDict']

  if newSerial == oldSerial:
    return

  elif newSerial in downdict:
    raise ValueError("Cannot reset serial to %s - value already in use" % newSerial)

  else:
    maxSerial = serialDict[downlink]
    apiObject.__dict__['serial'] = newSerial
    downdict[newSerial] = apiObject
    del downdict[oldSerial]
    if newSerial > maxSerial:
      serialDict[downlink] = newSerial
    elif oldSerial == maxSerial:
      serialDict[downlink] = max(downdict)


def addDataStore(dataSource, spectrumPath, **params):
  """Create and set DataSource.dataStore.
  The values of params are given by the 'tags' tuple, below"""

  dirName, fileName = os.path.split(spectrumPath)
  dataUrl = fetchDataUrl(dataSource.root, dirName)
  tags = ('numPoints', 'blockSizes', 'isBigEndian', 'numberType')
  attributeDict = dict((x, params.get(x)) for x in tags)
  blockMatrix = spectrumLib.createBlockedMatrix(dataUrl, spectrumPath, **attributeDict)
  for tag in ('headerSize', 'nByte', 'fileType', 'complexStoredBy'):
    val = params.get(tag)
    if val is not None:
      setattr(blockMatrix, tag, val)
  dataSource.dataStore = blockMatrix

def fetchDataUrl(memopsRoot, fullPath):
  """Get or create DataUrl that matches fullPath, prioritising insideData, alongsideDta, remoteData
  and existing dataUrls"""
  from memops.api.Implementation import Url
  standardStore = (memopsRoot.findFirstDataLocationStore(name='standard')
  or memopsRoot.newDataLocationStore(name='standard'))
  fullPath = uniIo.normalisePath(fullPath, makeAbsolute=True)
  standardTags = ('insideData', 'alongsideData', 'remoteData')
  # Check standard DataUrls first
  checkUrls = [standardStore.findFirstDataUrl(name=tag) for tag in standardTags]
  # Then check other existing DataUrls
  checkUrls += [x for x in standardStore.sortedDataUrls() if x.name not in standardTags]
  for dataUrl in checkUrls:
    if dataUrl is not None:
      print ("%s-%s-%s" % (dataUrl.name, dataUrl.url, dataUrl))
      directoryPath = os.path.join(dataUrl.url.path, '')
      if fullPath.startswith(directoryPath):
        break
  else:
    # No matches found, make a new one
    dirName, path = os.path.split(fullPath)
    dataUrl = standardStore.newDataUrl(url=Url(path=dirName))
  #
  return dataUrl


def assignPeak(peak, assignedResonances):
  """Assign all dimensions of peak to each of the assignments in the assignedResonances tuples

  assignedResonances is a list of tuple of tuples of resonances - the inner tuple may be empty.
  The list gives the alternative assignments.
  The first tuple gives one assignment per dimension
  The inner tuple gives teh resonances that match the dimension for that assignment
  (there may be more than one, e.g. from wildcard assignments)
  """

  peakDims = peak.sortedPeakDims()

  for peakContrib in peak.sortedPeakContribs()[1:]:
    # We keep one peakContrib (otherwise an empty one is create anyway),
    # but additional ones are in the way
    peakContrib.delete()

  # Assign each dimension to all resonances
  combinationCount = 1
  for ii, resonancesPerDimension in enumerate(zip(*assignedResonances)):
    peakDimContribs = set()
    peakDim = peakDims[ii]
    xx = set(resonancesPerDimension)
    combinationCount *= len(xx)
    for resonance in set(resonance for tt in xx for resonance in tt):
        peakDimContribs.add(AssignmentBasic.newPeakDimContrib(peakDim, resonance))

    for peakDimContrib in peakDim.peakDimContribs:
      if peakDimContrib not in peakDimContribs:
        # remove peakDimContribs left over from earlier times
        # NB done here to avoid deleting and re-creating peakDimContribs for the same resonance
        peakDimContrib.delete()

  if len(assignedResonances) != combinationCount:
    # the number of assignment tuples does not match the number of combinations
    # We must set individual PeakContribs for each assignment tuple
    previousContrib = peak.findFirstPeakContrib()  # for later deletion - there will be exactly one

    for assignmentTuple in assignedResonances:
      peakDimContribs = []
      for ii, tt in enumerate(assignmentTuple):
        peakDim = peakDims[ii]
        for resonance in tt:
          # NB, there is always a peakDimContrib taht matches, as it was set jsut above
          peakDimContribs.append(peakDim.findFirstPeakDimContrib(resonance=resonance))
      peak.newPeakContrib(peakDimContribs=peakDimContribs)
    #
    previousContrib.delete()

if __name__ == '__main__':
  path = sys.argv[1]
  memopsRoot = loadNefFile(path, overwriteExisting=True)
  memopsRoot.saveModified()