import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

##### -------------------------------------------------------------------------
##### helper functions
##### -------------------------------------------------------------------------

bar = '-'*70

def show_vlan( vlan ):
  """
    pretty print VLAN information
  """
  attrs = vlan.attrib

  print "VLAN name: %s (%s)" % (attrs['name'], attrs['number'])
  print "    state: %s" % attrs['state']

  vlan_mbr = vlan.xpath(".//VLAN-MEMBER")[0]
  vlan_tagid = vlan_mbr.attrib['vlan-tag']

  print "    tagid: {}".format( vlan_tagid )

##### -------------------------------------------------------------------------
##### =========================================================================
#####
#####                               MAIN SCRIPT
#####
##### =========================================================================
##### -------------------------------------------------------------------------

wlc = WLC_login()

print bar
print "Getting all VLANs:"
print bar

vlans = wlc.rpc.get_vlan()

vlans_elist = vlans.xpath('VLAN')
print "There are a total of %d VLANS." % len(vlans_elist)

for vlan in vlans_elist:
  show_vlan(vlan)

first_vlan_name = vlans_elist[0].attrib['name']

print bar
print "Showing Just one VLAN, using 'name' as key"
print bar

vlans = wlc.rpc.get_vlan( name = first_vlan_name )

vlans_elist = vlans.xpath('VLAN')
print "There is %d VLANs in this response" % len(vlans_elist)
show_vlan(vlans_elist[0])

