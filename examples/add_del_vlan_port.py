import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from lxml import etree
from jinja2 import Template

wlc = WLC_login()

cmd = wlc.RpcMaker('set')

cmd.data = E('VLAN-TABLE', E.VLAN({'number':'40'}, E('VLAN-MEMBER-TABLE')))
at_table = cmd.data.find('.//VLAN-MEMBER-TABLE')

vlan_port_j2 = Template(u"""
  <VLAN-MEMBER enable-tagging="NO" vlan-tag="0" forward-igmp="NO" multicast-router="NO">
    <PORT-REF type="PORT">
      <PHYS-PORT-REF module="1" port="{{ port }}"/>
    </PORT-REF>
  </VLAN-MEMBER>
""")

# now lets add some ports ...

for port in ['2','3']:
  at_table.append(etree.XML(vlan_port_j2.render( port=port )))

# if we want to add the ports, we do the following

# r = cmd()

# if we want to remove the ports, we do the following

# cmd.trans = 'delete'
# r = cmd()

# viola!

