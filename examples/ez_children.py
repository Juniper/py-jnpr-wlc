import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

def vlan_create( wlc, *vargs, **kvargs ):
  print "So you want to CREATE a VLAN"
  return True

def vlan_delete( wlc, *vargs, **kvargs ):
  print "So you want to DELETE a VLAN"
  return True

def vlan_list( wlc, *vargs, **kvargs ):
  print "So youw want a LIST of VLANS"
  return True

def vlan_details( wlc, *vargs, **kvargs ):
  print "So you want a lot of DETAIL on VLANS"
  return True

vlan_helpers = {
  'create': vlan_create,
  'list': vlan_list,
  'delete': vlan_delete,
  'details': vlan_details
}

wlc.ez( child='vlan', load=vlan_helpers )

# now you can do things like:
# wlc.ez.vlan.list()
# wlc.ez.vlan.delete()
# ...

