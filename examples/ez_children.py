import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

def vlan_create( wlc, *vargs, **kvargs ):
  print "So you want to CREATE a VLAN"
  print "Take a look at the create_vlan_j2.py file ..."
  return True

def vlan_delete( wlc, *vargs, **kvargs ):
  if 'number' in kvargs:
    r = wlc.rpc.delete_vlan( number = kvargs['number'] )
  elif 'name' in kvargs:
    # need to translate name to number since we can
    # only delete a VLAN by its number
    v = wlc.rpc.get_vlan( name = kvargs['name'])
    num = v.find('VLAN').attrib['number']
    r = wlc.rpc.delete_vlan( number = num )
  else:
    raise ValueError("You must provide either 'name' or 'number'")

  return True

def vlan_list( wlc, *vargs, **kvargs ):
  vlans = wlc.rpc.get_vlan()
  return [vlan.attrib['name'] for vlan in vlans.xpath('VLAN')]

def vlan_details( wlc, *vargs, **kvargs ):
  vlan = wlc.rpc.get_vlan( **kvargs )
  if not len(kvargs):
    # all VLAN in a list of Element
    return vlan.xpath('VLAN')
  else:
    # just one VLAN as Element
    return vlan.find('VLAN')

vlan_helpers = {
  'create': vlan_create,
  'list': vlan_list,
  'delete': vlan_delete,
  'info': vlan_details
}

wlc.ez( child='vlan', load=vlan_helpers )

# now you can do things like:
# wlc.ez.vlan.list()
# wlc.ez.vlan.delete()
# ...

