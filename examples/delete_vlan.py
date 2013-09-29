import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml import etree

wlc = WLC_login()

# delete VLAN with system ID 100

r = wlc.rpc.delete_vlan( number="100" )

