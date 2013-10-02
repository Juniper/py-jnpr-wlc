import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

from jnprwlc import WirelessLanController as WLC

wlc = WLC(host='a', user='b', password='c')

r = wlc.RpcMaker( target='vlan', name='Jeremy')

# you can access the following attributes, refer to the jnprwlc.builder
# file for more details

# r.cmd
# r.target
# r.args


