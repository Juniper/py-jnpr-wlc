import demowlcutils
from demowlcutils import ppxml, WLC_login
import jinja2
from lxml import etree

from jnprwlc import WirelessLanController as WLC

#wlc = WLC_login()

wlc = WLC( host='a', user='b', password='c')

### ---------------------------------------------------------------------------
### Technique that uses Jinja2 templating engine to create the XML RPC command
### to create a new VLAN
### ---------------------------------------------------------------------------

j2_ldr = jinja2.FileSystemLoader( searchpath='.' )
j2_env = jinja2.Environment( loader=j2_ldr )

def render_j2( filename, env_vars ):
  """
    render jinja2 template into XML
  """
  # build the j2 template
  template = j2_env.get_template( filename )
  # now merge the template with the vars
  as_txt = template.render( env_vars )
  # now convert the txt to XML
  return etree.XML( as_txt )

# -----------------------------------------------------------------------------

vlan_vars = {
  'name': 'Jeremy',
  'number': '100'
}

cr8_vlan_xml = render_j2( 'create-vlan.j2.xml', vlan_vars )

trans = wlc.RpcMaker( trans='SET', target='vlan-table' )
trans.data = cr8_vlan_xml

# now perform the transaction
rpc = trans.as_xml

print "Creating VLAN %s ..." % vlan_vars['name']

# r = wlc.rpc( rpc )

