
from ccpn.framework.lib.Plugin import Plugin

class AutoGeneratedDevPlugin(Plugin):
  PLUGINNAME = 'Development Plugin...Custom Gui'

  def run(self, **kwargs):
    print('Run', kwargs)