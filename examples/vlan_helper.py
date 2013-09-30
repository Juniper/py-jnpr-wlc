
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
import jinja2
from lxml import etree

wlc = WLC_login()

def show_vlans( wlc, *vargs, **kvargs ):

  if 'name' in kvargs:
    vlan_xml = wlc.rpc.get_vlan( name = kvargs['name'])
  else:
    vlan_xml = wlc.rpc.get_vlan()

  return [ dict(vlan.attrib) for vlan in vlan_xml.xpath('VLAN')]
  
##### -------------------------------------------------------------------------
##### MAIN BLOCK
##### -------------------------------------------------------------------------

j2_ldr = jinja2.FileSystemLoader( searchpath='.' )
j2_env = jinja2.Environment( loader=j2_ldr )

def j2_to_xml( filename, env_vars ):
  """
    render jinja2 template into XML
  """
  # build the j2 template
  template = j2_env.get_template( filename )
  # now merge the template with the vars
  as_txt = template.render( env_vars )
  # now convert the txt to XML
  return etree.XML( as_txt )

def create_vlan( wlc, *vargs, **kvargs ):
  vlan_vars = {
    'name': kvargs['name'],
    'number': kvargs['number']
  }
  rpc = wlc.RpcMaker( trans='SET', target='vlan-table' )
  rpc.data = j2_to_xml( 'create-vlan.j2.xml', vlan_vars )
  return wlc.rpc( rpc.as_xml )

# bind the helper to the WLC
wlc.ez( show_vlans, alias="vinfo")
wlc.ez( create_vlan )

vlan_create_list = [
  {'name': 'Bob1', 'number': '1001'},
  {'name': 'Bob2', 'number': '1002'},
  {'name': 'Bob3', 'number': '1003'},
  {'name': 'Bob4', 'number': '1004'},
  {'name': 'Bob5', 'number': '1005'},
]
  
# then you could do something like:
#>>> for vlan in vlan_create_list:
#...    wlc.ez.create_vlan( **vlan )

