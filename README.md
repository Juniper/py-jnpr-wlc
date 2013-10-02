# ABOUT

  Python module for Juniper Wireless LAN Controller (WLC)

**STATUS**: Experimental, under active development.  
The WLC XML API is not public, but can be made available to existing customers.

# OVERVIEW

  The Juniper Wireless LAN Controller products implement a comprehensive HTTP/s API using XML as the content-data.  This module provides a *metaprogramming* set of capabilities to fully utilize the API in any easy and consumable manner.  To proficiently use this API, you should be familiar with [XML](http://www.w3schools.com/xml/) and [XPath](http://www.w3schools.com/xpath/) expressions.  This module uses the 3rd-party [lxml](http://lxml.de/index.html) python module for XML processing.
  
  This module is developed and tested with Python 2.7.  If you are using another version and it works, please notify the maintainer.  If you are using another version and it does **not** work, please open an issue.

## Quick Example

````python
from jnprwlc import WirelessLanController as WLC

wlc = WLC( user='jeremy', host='192.168.10.27', password='logmeIn' )

# auth/login to WLC device
wlc.open()

# -----------------------------------------------------
# Get all VLANS
# -----------------------------------------------------
# Retrieve the current VLANs and display them.  The RPC
# invocation here is metaprogramming.  The `rpc` object
# metraprograms whatever comes afte.  The response is 
# an lxml Element

vlans = wlc.rpc.get_vlan()

for vlan in vlans.xpath('VLAN'):
  v_num = vlan.attrib['number']
  v_name = vlan.attrib['name']
  print "VLAN(%s) is named: %s" % (v_num, v_name)

# -----------------------------------------------------
# Get only one VLAN
# -----------------------------------------------------

resp = wlc.rpc.get_vlan( name="VoIP" )
vlan = resp.find('VLAN')
print "VoIP vlan number is %s" % vlan.attrib['number']


# cleanup/close
wlc.close()
````
  For more examples, see the [example](https://github.com/jeremyschulman/py-jnprwlc/tree/master/examples) directory.
  
## "FACTS"

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

## RPC METAPROGRAMMING

  You can issue WLC XML RPCs in a few different ways.  These methods use Python metaprogramming techniques.  
  Metapgramming means the this module automatically generates the XML RPC commands on-the-fly without
  having to maintain a specific set of functions.  The benefit of this approach is that the module will
  work with any version of the WLC; i.e. there is no static binding to specific WLC XML libraries.
  
  For _simple_ XML RPCs, you can do following way:

````  
    rsp = wlc.rpc.<cmd>_<target>( <attribs> )
    
    <cmd>: get, act, delete
    <target>: a target specified in the WLC XML DTD
    <attribs>: name=value pairs that are set within the <target> element
````    

  For example, let's say that you want to perform the "GET" command on a "VLAN" target and set
  the VLAN attribute 'name' to the value 'Jeremy'.  You would do the following:
  
````
  rsp = wlc.rpc.get_vlan( name="Jeremy" )
````

  Simple!  The return value, `rsp`, is an etree Element.  You can dump this to the screen for debugging:
  
```
  from lxml import etree
  
  etree.tostring(rsp, pretty_print=True)
```

  A _simple_ RPC is one that doesn't contain any further XML beyond the <target> element.  
  
  If you need to a _complex_ RPC, i.e. one that has XML elements within the <target> element, then you can use
  the `RpcMaker` mechanism.  You will generally need to use this mechanism when you want to create 
  things (like a VLAN), or set things within other things (like ports within a VLAN).  There are some
  examples of using `RpcMaker` in the [example](https://github.com/jeremyschulman/py-jnprwlc/tree/master/examples) directory.


## DEPENDENCIES

  * [Python 2.7](http://www.python.org/)
  * [lxml](http://lxml.de/index.html)

## LICENSE
  Apache 2.0

## CONTRIBUTORS
  Jeremy Schulman, @nwkautomaniac
