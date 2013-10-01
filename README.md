# ABOUT

Python module for Juniper Wireless Lan Controller (WLC) product

**STATUS**: Experimental, under active development.

## Quick Example

````python
from jnprwlc import WirelessLanController as WLC

wlc = WLC( user='jeremy', host='192.168.10.27', password='logmeIn' )

# auth/login to WLC device
wlc.open()

# retrieve the current VLANs and display them.  The RPC
# invocation here is metaprogramming.  The response
# is an lxml Element

vlans = wlc.rpc.get_vlan()

for vlan in vlans.xpath('VLAN'):
  v_num = vlan.attrib['number']
  v_name = vlan.attrib['name']
  print "VLAN(%s) is named: %s" % (v_num, v_name)

# cleanup/close
wlc.close()
````
  For more examples, see the [example](https://github.com/jeremyschulman/py-jnprwlc/tree/master/examples) directory.
  
### LICENSE
  Apache 2.0

### CONTRIBUTORS
  Jeremy Schulman, @nwkautomaniac
