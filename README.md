# ABOUT

  Python module for Juniper Wireless Lan Controller (WLC) product

**STATUS**: Experimental, under active development.  The WLC XML API is not public, but can be made available to existing customers.

# OVERVIEW

  The Juniper Wireless LAN Controller products implement a comprehensive HTTP/s API using XML as the content-data.  This module provides a *metaprogramming* set of capabilities to fully utilize the API in any easy and consumable manner.  To proficiently use this API, you should be familiar with [XML](http://www.w3schools.com/xml/) and [XPath](http://www.w3schools.com/xpath/) expressions.  This module uses the 3rd-party [lxml](http://lxml.de/index.html) python module for XML processing.
  
  This module is developed and tested with Python 2.7.  If you are using another version and it works, please notify the [maintainer](<a href="mailto:jschulman@juniper.net">Email Me</a>).  If you are using another version and it does **not** work, please open an issue.

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
#          you would use the wlc.RpcMaker() object.
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
  
## WLC Facts

  When you make a call to `open()` the method will retrieve bits of data about the WLC and store them
  into a dictionary called `facts`.  You can access this data as property, as illustrated:

````python
>>> pprint( wlc.facts )
{'auto-config': 'NO',
 'backup-config-location': '',
 'booted-config-location': 'configuration',
 'booted-image-location': 'boot0:WC075106.8XX',
 'booted-version': '7.5.1.6.0',
 'bootflags': '',
 'cluster-active-seed': 'NO',
 'console-timeout': '0',
 'domainsecurity': 'NONE',
 'enablepw': 'b5bacf1baa8e028e858c134e3fd2d306cc3b',
 'fips': 'NO',
 'idle-timeout': '3600',
 'ip-addr': '66.129.246.74',
 'macaddress': '78:19:F7:70:96:76',
 'model': 'WLC880R',
 'mx-secret': '',
 'name': 'WLC880R',
 'next-config-location': 'configuration',
 'next-image-location': 'boot0:WC075106.8XX',
 'next-image-version': '7.5.1.6.0',
 'objectid': '1.3.6.1.4.1.14525.3.3.1',
 'platform': '802',
 'serialnumber': 'JJ0211401124',
 'tunnelsecurity': 'NONE',
 'type': 'DP',
 'uptime': '0'}
 

>>> wlc.facts['serialnumber']
'JJ0211401124'

>>> wlc.facts['macaddress']
'78:19:F7:70:96:76'

````

## METAPROGRAMMING API

   

#### Using `rpc.<cmd>_<target>(<attribs>)` to metaprogram RPC calls
#### Using `RpcMaker()` to metaprogram RPC calls
#### Using `rpc()` to execute existing RPCs

## DEPENDENCIES

  * [Python 2.7](http://www.python.org/)
  * [lxml](http://lxml.de/index.html)

## LICENSE
  Apache 2.0

## CONTRIBUTORS
  Jeremy Schulman, @nwkautomaniac
