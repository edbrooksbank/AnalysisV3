"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - $Date: 2015-03-16 16:57:10 +0000 (Mon, 16 Mar 2015) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
              "or ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                " or ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = "$Author: skinnersp $"
__date__ = "$Date: 2015-03-16 16:57:10 +0000 (Mon, 16 Mar 2015) $"
__version__ = "$Revision: 8180 $"

#=========================================================================================
# Start of code
#=========================================================================================

### TBD: update to Python 3

def fetchUrl(url, values=None, headers=None, timeout=None):

  import socket
  import urllib
  import urllib.parse
  import urllib.request

  if not headers:
    headers = {}

  if values:
    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')
  else:
    data = None
    
  request = urllib.request.Request(url, data, headers)
  response = urllib.request.urlopen(request, timeout=timeout)
  result = response.read().decode('utf-8')

  return result

