"""
#######################################################################

CCPN Data Model version 2.1.2

Autogenerated by PyXmlMapWrite revision 1.29 on Mon Mar  2 17:24:14 2015
  from data model element cambridge.WmsQuery revision ?

#######################################################################
======================COPYRIGHT/LICENSE START==========================

WmsQuery.py: python XML-I/O-mapping for CCPN data model, MetaPackage cambridge.WmsQuery

Copyright (C) 2007  (CCPN Project)

=======================================================================

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
 
A copy of this license can be found in ../../../license/LGPL.license
 
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
 
You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)

- email: ccpn@bioc.cam.ac.uk

=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
Rasmus H. Fogh, Wayne Boucher, Wim F. Vranken, Anne
Pajon, Tim J. Stevens, T.N. Bhat, John Westbrook, John M.C. Ionides and
Ernest D. Laue (2005). A framework for scientific data modeling and automated
software development. Bioinformatics 21, 1678-1684.


This file was generated with the Memops software generation framework,
and contains original contributions embedded in the framework

===========================REFERENCE END===============================
"""
from memops.general.Constants import baseDataTypeModule as basicDataTypes
# 
#  Current package api
import cambridge.api.WmsQuery

def makeMapping(globalMap):
  """
  generates XML I/O mapping for package WMSQ, adding it to globalMap
  """
  
  from memops.xml.Implementation import bool2str, str2bool

  # Set up top level dictionaries
  loadMaps = globalMap.get('loadMaps')
  mapsByGuid = globalMap.get('mapsByGuid')

  abstractTypes = globalMap.get('WMSQ').get('abstractTypes')
  exolinks = globalMap.get('WMSQ').get('exolinks')

  # Class AbstractQuery
  currentMap = {}
  abstractTypes['AbstractQuery'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00008'] = currentMap
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00008'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.AbstractQuery
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute AbstractQuery.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute AbstractQuery.criteria
  currentMap = {}
  contentMap['criteria'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00019'] = currentMap
  loadMaps['WMSQ.AbstractQuery.criteria'] = currentMap
  currentMap['tag'] = 'WMSQ.AbstractQuery.criteria'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00019'
  currentMap['name'] = 'criteria'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['proc'] = 'direct'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00035')

  # Attribute AbstractQuery.date
  currentMap = {}
  contentMap['date'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00020'] = currentMap
  loadMaps['WMSQ.AbstractQuery.date'] = currentMap
  currentMap['tag'] = 'WMSQ.AbstractQuery.date'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00020'
  currentMap['name'] = 'date'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['proc'] = 'direct'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00029')

  # Attribute AbstractQuery.userName
  currentMap = {}
  contentMap['userName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00021'] = currentMap
  loadMaps['WMSQ.AbstractQuery.userName'] = currentMap
  currentMap['tag'] = 'WMSQ.AbstractQuery.userName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00021'
  currentMap['name'] = 'userName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Role AbstractQuery.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')
  # End of AbstractQuery

  currentMap = abstractTypes.get('AbstractQuery')
  aList = ['criteria', 'date', 'userName']
  currentMap['simpleAttrs'] = aList
  aList = ['access', 'applicationData']
  currentMap['cplxAttrs'] = aList

  # Class ProjectResult
  currentMap = {}
  abstractTypes['ProjectResult'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00012'] = currentMap
  loadMaps['WMSQ.ProjectResult'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectResult'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00012'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'projectResults'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectResult
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute ProjectResult.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute ProjectResult.projectName
  currentMap = {}
  contentMap['projectName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00029'] = currentMap
  loadMaps['WMSQ.ProjectResult.projectName'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectResult.projectName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00029'
  currentMap['name'] = 'projectName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Attribute ProjectResult.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00027'] = currentMap
  loadMaps['WMSQ.ProjectResult.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectResult.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00027'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute ProjectResult.wmsSegmentName
  currentMap = {}
  contentMap['wmsSegmentName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00028'] = currentMap
  loadMaps['WMSQ.ProjectResult.wmsSegmentName'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectResult.wmsSegmentName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00028'
  currentMap['name'] = 'wmsSegmentName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Role ProjectResult.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role ProjectResult.project
  currentMap = {}
  contentMap['project'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00026'] = currentMap
  loadMaps['WMSQ.ProjectResult.project'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectResult.project'
  currentMap['type'] = 'exolink'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00026'
  currentMap['name'] = 'project'
  currentMap['hicard'] = 1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['copyOverride'] = True
  currentMap['content'] = globalMap.get('WMS').get('exolinks')
  # End of ProjectResult

  currentMap = abstractTypes.get('ProjectResult')
  aList = ['serial']
  currentMap['headerAttrs'] = aList
  aList = ['projectName', 'wmsSegmentName']
  currentMap['simpleAttrs'] = aList
  aList = ['access', 'applicationData']
  currentMap['cplxAttrs'] = aList

  # Class ProjectVersionResult
  currentMap = {}
  abstractTypes['ProjectVersionResult'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00013'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00013'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'projectVersionResults'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectVersionResult
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute ProjectVersionResult.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute ProjectVersionResult.projectName
  currentMap = {}
  contentMap['projectName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00038'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult.projectName'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult.projectName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00038'
  currentMap['name'] = 'projectName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Attribute ProjectVersionResult.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00036'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00036'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute ProjectVersionResult.versionTag
  currentMap = {}
  contentMap['versionTag'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00039'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult.versionTag'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult.versionTag'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00039'
  currentMap['name'] = 'versionTag'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00037')

  # Attribute ProjectVersionResult.wmsSegmentName
  currentMap = {}
  contentMap['wmsSegmentName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00037'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult.wmsSegmentName'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult.wmsSegmentName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00037'
  currentMap['name'] = 'wmsSegmentName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Role ProjectVersionResult.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role ProjectVersionResult.projectVersion
  currentMap = {}
  contentMap['projectVersion'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00035'] = currentMap
  loadMaps['WMSQ.ProjectVersionResult.projectVersion'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionResult.projectVersion'
  currentMap['type'] = 'exolink'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00035'
  currentMap['name'] = 'projectVersion'
  currentMap['hicard'] = 1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['copyOverride'] = True
  currentMap['content'] = globalMap.get('WMS').get('exolinks')
  # End of ProjectVersionResult

  currentMap = abstractTypes.get('ProjectVersionResult')
  aList = ['serial', 'versionTag']
  currentMap['headerAttrs'] = aList
  aList = ['projectName', 'wmsSegmentName']
  currentMap['simpleAttrs'] = aList
  aList = ['access', 'applicationData']
  currentMap['cplxAttrs'] = aList

  # Class TaskResult
  currentMap = {}
  abstractTypes['TaskResult'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00014'] = currentMap
  loadMaps['WMSQ.TaskResult'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskResult'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00014'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'taskResults'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.TaskResult
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute TaskResult.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute TaskResult.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00046'] = currentMap
  loadMaps['WMSQ.TaskResult.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskResult.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00046'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute TaskResult.taskSerial
  currentMap = {}
  contentMap['taskSerial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00048'] = currentMap
  loadMaps['WMSQ.TaskResult.taskSerial'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskResult.taskSerial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00048'
  currentMap['name'] = 'taskSerial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['proc'] = 'direct'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute TaskResult.wmsSegmentName
  currentMap = {}
  contentMap['wmsSegmentName'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00047'] = currentMap
  loadMaps['WMSQ.TaskResult.wmsSegmentName'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskResult.wmsSegmentName'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00047'
  currentMap['name'] = 'wmsSegmentName'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['eType'] = 'cplx'
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033')

  # Role TaskResult.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role TaskResult.task
  currentMap = {}
  contentMap['task'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00045'] = currentMap
  loadMaps['WMSQ.TaskResult.task'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskResult.task'
  currentMap['type'] = 'exolink'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00045'
  currentMap['name'] = 'task'
  currentMap['hicard'] = 1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['copyOverride'] = True
  currentMap['content'] = globalMap.get('WMS').get('exolinks')
  # End of TaskResult

  currentMap = abstractTypes.get('TaskResult')
  aList = ['serial', 'taskSerial']
  currentMap['headerAttrs'] = aList
  aList = ['wmsSegmentName']
  currentMap['simpleAttrs'] = aList
  aList = ['access', 'applicationData']
  currentMap['cplxAttrs'] = aList

  # Class WmsQueryStore
  currentMap = {}
  abstractTypes['WmsQueryStore'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00007'] = currentMap
  loadMaps['WMSQ.WmsQueryStore'] = currentMap
  currentMap['tag'] = 'WMSQ.WmsQueryStore'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00007'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'wmsQueryStores'
  currentMap['isTop'] = True
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.WmsQueryStore
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute WmsQueryStore.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute WmsQueryStore.createdBy
  contentMap['createdBy'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:00:59_00002__www.ccpn.ac.uk_Fogh_2007-10-03-14:53:27_00001__www.ccpn.ac.uk_Fogh_2006-09-14-16:28:57_00002')

  # Attribute WmsQueryStore.guid
  contentMap['guid'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:26_00002')

  # Attribute WmsQueryStore.isModifiable
  contentMap['isModifiable'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-17-14:16:26_00010__www.ccpn.ac.uk_Fogh_2007-10-03-14:53:27_00001__www.ccpn.ac.uk_Fogh_2006-09-14-16:28:57_00002')

  # Attribute WmsQueryStore.lastUnlockedBy
  contentMap['lastUnlockedBy'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:00:59_00003__www.ccpn.ac.uk_Fogh_2007-10-03-14:53:27_00001__www.ccpn.ac.uk_Fogh_2006-09-14-16:28:57_00002')

  # Attribute WmsQueryStore.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00057'] = currentMap
  loadMaps['WMSQ.WmsQueryStore.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.WmsQueryStore.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00057'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Role WmsQueryStore.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role WmsQueryStore.projectQueries
  currentMap = {}
  contentMap['projectQueries'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00052'] = currentMap
  loadMaps['WMSQ.WmsQueryStore.projectQueries'] = currentMap
  currentMap['tag'] = 'WMSQ.WmsQueryStore.projectQueries'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00052'
  currentMap['name'] = 'projectQueries'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['implSkip'] = True
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')

  # Role WmsQueryStore.projectVersionQueries
  currentMap = {}
  contentMap['projectVersionQueries'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00054'] = currentMap
  loadMaps['WMSQ.WmsQueryStore.projectVersionQueries'] = currentMap
  currentMap['tag'] = 'WMSQ.WmsQueryStore.projectVersionQueries'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00054'
  currentMap['name'] = 'projectVersionQueries'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['implSkip'] = True
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')

  # Role WmsQueryStore.taskQueries
  currentMap = {}
  contentMap['taskQueries'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00056'] = currentMap
  loadMaps['WMSQ.WmsQueryStore.taskQueries'] = currentMap
  currentMap['tag'] = 'WMSQ.WmsQueryStore.taskQueries'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00056'
  currentMap['name'] = 'taskQueries'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['implSkip'] = True
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')
  # End of WmsQueryStore

  currentMap = abstractTypes.get('WmsQueryStore')
  aList = ['createdBy', 'guid', 'isModifiable', 'lastUnlockedBy', 'serial']
  currentMap['headerAttrs'] = aList
  aList = ['taskQueries', 'projectVersionQueries', 'projectQueries', 'access', 'applicationData']
  currentMap['cplxAttrs'] = aList
  aList = ['projectQueries', 'projectVersionQueries', 'taskQueries']
  currentMap['children'] = aList

  # Class TaskQuery
  currentMap = {}
  abstractTypes['TaskQuery'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00011'] = currentMap
  loadMaps['WMSQ.TaskQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskQuery'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00011'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'taskQueries'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.TaskQuery
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute TaskQuery.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute TaskQuery.criteria
  contentMap['criteria'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00019')

  # Attribute TaskQuery.date
  contentMap['date'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00020')

  # Attribute TaskQuery.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00044'] = currentMap
  loadMaps['WMSQ.TaskQuery.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskQuery.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00044'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute TaskQuery.userName
  contentMap['userName'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00021')

  # Role TaskQuery.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role TaskQuery.taskResults
  currentMap = {}
  contentMap['taskResults'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00043'] = currentMap
  loadMaps['WMSQ.TaskQuery.taskResults'] = currentMap
  currentMap['tag'] = 'WMSQ.TaskQuery.taskResults'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00043'
  currentMap['name'] = 'taskResults'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')
  # End of TaskQuery

  currentMap = abstractTypes.get('TaskQuery')
  aList = ['serial']
  currentMap['headerAttrs'] = aList
  aList = ['criteria', 'date', 'userName']
  currentMap['simpleAttrs'] = aList
  aList = ['taskResults', 'access', 'applicationData']
  currentMap['cplxAttrs'] = aList
  aList = ['taskResults']
  currentMap['children'] = aList

  # Class ProjectVersionQuery
  currentMap = {}
  abstractTypes['ProjectVersionQuery'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00010'] = currentMap
  loadMaps['WMSQ.ProjectVersionQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionQuery'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00010'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'projectVersionQueries'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectVersionQuery
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute ProjectVersionQuery.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute ProjectVersionQuery.criteria
  contentMap['criteria'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00019')

  # Attribute ProjectVersionQuery.date
  contentMap['date'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00020')

  # Attribute ProjectVersionQuery.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00034'] = currentMap
  loadMaps['WMSQ.ProjectVersionQuery.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionQuery.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00034'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute ProjectVersionQuery.userName
  contentMap['userName'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00021')

  # Role ProjectVersionQuery.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role ProjectVersionQuery.projectVersionResults
  currentMap = {}
  contentMap['projectVersionResults'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00033'] = currentMap
  loadMaps['WMSQ.ProjectVersionQuery.projectVersionResults'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectVersionQuery.projectVersionResults'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00033'
  currentMap['name'] = 'projectVersionResults'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')
  # End of ProjectVersionQuery

  currentMap = abstractTypes.get('ProjectVersionQuery')
  aList = ['serial']
  currentMap['headerAttrs'] = aList
  aList = ['criteria', 'date', 'userName']
  currentMap['simpleAttrs'] = aList
  aList = ['projectVersionResults', 'access', 'applicationData']
  currentMap['cplxAttrs'] = aList
  aList = ['projectVersionResults']
  currentMap['children'] = aList

  # Class ProjectQuery
  currentMap = {}
  abstractTypes['ProjectQuery'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00009'] = currentMap
  loadMaps['WMSQ.ProjectQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectQuery'
  currentMap['type'] = 'class'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00009'
  currentMap['eType'] = 'cplx'
  currentMap['fromParent'] = 'projectQueries'
  currentMap['objkey'] = 'serial'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectQuery
  contentMap = {}
  currentMap['content'] = contentMap

  # Attribute ProjectQuery.applicationData
  contentMap['applicationData'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-09-14-18:48:27_00007')

  # Attribute ProjectQuery.criteria
  contentMap['criteria'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00019')

  # Attribute ProjectQuery.date
  contentMap['date'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00020')

  # Attribute ProjectQuery.serial
  currentMap = {}
  contentMap['serial'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00025'] = currentMap
  loadMaps['WMSQ.ProjectQuery.serial'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectQuery.serial'
  currentMap['type'] = 'attr'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00025'
  currentMap['name'] = 'serial'
  currentMap['hicard'] = 1
  currentMap['locard'] = 1
  currentMap['data'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032')

  # Attribute ProjectQuery.userName
  contentMap['userName'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00021')

  # Role ProjectQuery.access
  contentMap['access'] = mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-12-31-09:03:01_00014')

  # Role ProjectQuery.projectResults
  currentMap = {}
  contentMap['projectResults'] = currentMap
  mapsByGuid['www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00024'] = currentMap
  loadMaps['WMSQ.ProjectQuery.projectResults'] = currentMap
  currentMap['tag'] = 'WMSQ.ProjectQuery.projectResults'
  currentMap['type'] = 'child'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-13:30:17_00024'
  currentMap['name'] = 'projectResults'
  currentMap['hicard'] = -1
  currentMap['locard'] = 0
  currentMap['eType'] = 'cplx'
  currentMap['content'] = globalMap.get('WMSQ').get('abstractTypes')
  # End of ProjectQuery

  currentMap = abstractTypes.get('ProjectQuery')
  aList = ['serial']
  currentMap['headerAttrs'] = aList
  aList = ['criteria', 'date', 'userName']
  currentMap['simpleAttrs'] = aList
  aList = ['projectResults', 'access', 'applicationData']
  currentMap['cplxAttrs'] = aList
  aList = ['projectResults']
  currentMap['children'] = aList

  # Out-of-package link to ProjectResult
  currentMap = {}
  exolinks['ProjectResult'] = currentMap
  loadMaps['WMSQ.exo-ProjectResult'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-ProjectResult'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00012'
  currentMap['name'] = 'ProjectResult'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectResult
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))

  # Out-of-package link to ProjectVersionResult
  currentMap = {}
  exolinks['ProjectVersionResult'] = currentMap
  loadMaps['WMSQ.exo-ProjectVersionResult'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-ProjectVersionResult'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00013'
  currentMap['name'] = 'ProjectVersionResult'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectVersionResult
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))

  # Out-of-package link to TaskResult
  currentMap = {}
  exolinks['TaskResult'] = currentMap
  loadMaps['WMSQ.exo-TaskResult'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-TaskResult'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00014'
  currentMap['name'] = 'TaskResult'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.TaskResult
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))

  # Out-of-package link to WmsQueryStore
  currentMap = {}
  exolinks['WmsQueryStore'] = currentMap
  loadMaps['WMSQ.exo-WmsQueryStore'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-WmsQueryStore'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00007'
  currentMap['name'] = 'WmsQueryStore'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.WmsQueryStore
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))

  # Out-of-package link to TaskQuery
  currentMap = {}
  exolinks['TaskQuery'] = currentMap
  loadMaps['WMSQ.exo-TaskQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-TaskQuery'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00011'
  currentMap['name'] = 'TaskQuery'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.TaskQuery
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))

  # Out-of-package link to ProjectVersionQuery
  currentMap = {}
  exolinks['ProjectVersionQuery'] = currentMap
  loadMaps['WMSQ.exo-ProjectVersionQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-ProjectVersionQuery'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00010'
  currentMap['name'] = 'ProjectVersionQuery'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectVersionQuery
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))

  # Out-of-package link to ProjectQuery
  currentMap = {}
  exolinks['ProjectQuery'] = currentMap
  loadMaps['WMSQ.exo-ProjectQuery'] = currentMap
  currentMap['tag'] = 'WMSQ.exo-ProjectQuery'
  currentMap['type'] = 'exo'
  currentMap['guid'] = 'www.ccpn.ac.uk_Fogh_2010-05-06-12:26:54_00009'
  currentMap['name'] = 'ProjectQuery'
  currentMap['eType'] = 'cplx'
  currentMap['class'] = cambridge.api.WmsQuery.ProjectQuery
  aList = list()
  currentMap['keyMaps'] = aList
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2008-06-30-16:30:50_00001'))
  aList.append(mapsByGuid.get('www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'))
