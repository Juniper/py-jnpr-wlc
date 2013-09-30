import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml import etree
from lxml.builder import E 
import jinja2

wlc = WLC_login()

### ---------------------------------------------------------------------------
### Technique that uses Jinja2 templating engine to create the XML RPC command
### to create a new VLAN
### ---------------------------------------------------------------------------

j2_ldr = jinja2.FileSystemLoader( searchpath='.' )
j2_env = jinja2.Environment( loader=j2_ldr )

j2_cr8_vlan = j2_env.get_template( 'create-vlan.j2' )

# the following variable names are used within the 'create-vlan.j2' 
# template file.

vlan_vars = {
  'name': 'Jeremy',
  'number': 100
}

# now merge the template with the vars
cr8_vlan_txt = j2_cr8_vlan.render( vlan_vars )

# now convert the txt to XML
cr8_vlan_xml = etree.XML( cr8_vlan_txt )

# now create the transaction

trans = E.TRANSACTION({'tid': '0'},
  E.SESSION,
  E.SET( cr8_vlan_xml ))

# now perform the transaction

print "Creating VLAN %s ..." % vlan_vars['name']
r = wlc.rpc( trans )

