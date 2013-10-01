# ABOUT

Python module for Juniper Wireless Lan Controller (WLC) product

**STATUS**: Experimental, under active development.

## Quick Example

````python
from jnprwlc import WirelessLanController as WLC

wlc = WLC( user='jeremy', host='192.168.10.27', password='logmeIn' )

# auth/login to WLC device
wlc.open()

# Retrieve the current VLANs and display them.  The RPC
# invocation here is metaprogramming.  The `rpc` object
# metraprograms whatever comes after, using the following
# conventions:
#
#    wlc.rpc.get_xyz()        -- GET
#    wlc.rpc.get_stat_xyz()   -- GET-STAT
#    wlc.rpc.act_xyz()        -- ACT
#    wlc.rpc.delete_xyz()     -- DELETE (ACT+DELETE)
#    wlc.rpc.set_xyz()        -- SET (for basic things)
#
#    Note: For more complicated create/set metaprogramming
#          you would use the wlc.rpc.RpcMaker() object.
#          Documentation on that to follow shortly, but
#          you can see examples in the example directory
#
# The response is an lxml Element

# -------------------------------------------
# Get all VLANS
# -------------------------------------------

vlans = wlc.rpc.get_vlan()

for vlan in vlans.xpath('VLAN'):
  v_num = vlan.attrib['number']
  v_name = vlan.attrib['name']
  print "VLAN(%s) is named: %s" % (v_num, v_name)

# -------------------------------------------
# Get only one VLAN
# -------------------------------------------

resp = wlc.rpc.get_vlan( name="VoIP" )
vlan = resp.find('VLAN')
print "VoIP vlan number is %s" % vlan.attrib['number']


# cleanup/close
wlc.close()
````
  For more examples, see the [example](https://github.com/jeremyschulman/py-jnprwlc/tree/master/examples) directory.
  
### LICENSE
  Apache 2.0

### CONTRIBUTORS
  Jeremy Schulman, @nwkautomaniac
