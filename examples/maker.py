import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

from jnprwlc import WirelessLanController as WLC
from jnprwlc.builder import RpcMaker
from jnprwlc import RpcFactory

wlc = WLC(host='a', user='b', password='c')

r = wlc.RpcMaker( target='vlan')
r.args = dict( name='Jeremy' )



